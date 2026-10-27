"""
Comparable Test-Set Evaluation Pipeline for Invoice Digest
Evaluates both FinBERT and trained LSTM on the exact same held-out test set,
computes comparative metrics, latency, confusion matrices, and logs results to SQLite.
"""

import argparse
import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Any, Dict, List
import pandas as pd
from src.database import DEFAULT_DB_PATH
from src.evaluation import compute_classification_metrics, log_experiment_to_db
from src.finbert_model import FinBERTClassifier
from src.lstm_model import LSTMClassifier
from src.preprocessing import prepare_email_for_model


def evaluate_both_models_on_test_set(
    test_csv: str = "data/test.csv",
    db_path: str = DEFAULT_DB_PATH,
    export_dir: str = "reports"
) -> Dict[str, Any]:
    """Runs synchronous benchmark comparison between FinBERT and LSTM."""
    if not os.path.isfile(test_csv):
        raise FileNotFoundError(f"Held-out test set not found: {test_csv}. Run training/prepare_dataset.py first.")

    df = pd.read_csv(test_csv)
    y_true = [str(s).strip().lower() for s in df["sentiment"]]
    texts = [prepare_email_for_model(r.get("subject", ""), r.get("body_text", "")) for _, r in df.iterrows()]

    comparison_results: Dict[str, Any] = {}

    # 1. FinBERT Evaluation
    print("Evaluating FinBERT on held-out test set...")
    finbert = FinBERTClassifier()
    finbert_start = time.perf_counter()
    finbert_preds = finbert.predict_batch(texts, batch_size=16)
    finbert_time = (time.perf_counter() - finbert_start) * 1000.0
    finbert_pred_labels = [p["sentiment"] for p in finbert_preds]

    finbert_metrics = compute_classification_metrics(y_true, finbert_pred_labels)
    finbert_metrics["mean_latency_ms"] = round(finbert_time / len(texts), 2)
    comparison_results["finbert"] = finbert_metrics

    # Log to SQLite
    try:
        log_experiment_to_db(
            model_name="FinBERT (Pretrained)",
            dataset_name="HeldOut-Test",
            metrics=finbert_metrics,
            model_version="ProsusAI/finbert",
            db_path=db_path
        )
    except Exception as e:
        print(f"FinBERT DB log notice: {e}")

    # 2. LSTM Evaluation
    print("Evaluating LSTM on held-out test set...")
    lstm = LSTMClassifier()
    if not lstm.is_trained():
        print("Warning: LSTM checkpoint not found. Train LSTM before running full comparative evaluation.")
        lstm_metrics = {
            "accuracy": 0.0,
            "macro_f1": 0.0,
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "mean_latency_ms": 0.0,
            "confusion_matrix": {"labels": ["negative", "neutral", "positive"], "matrix": [[0,0,0],[0,0,0],[0,0,0]]},
            "sample_count": len(texts),
            "status": "not_trained"
        }
        comparison_results["lstm"] = lstm_metrics
    else:
        lstm_start = time.perf_counter()
        lstm_preds = lstm.predict_batch(texts)
        lstm_time = (time.perf_counter() - lstm_start) * 1000.0
        lstm_pred_labels = [p["sentiment"] for p in lstm_preds]

        lstm_metrics = compute_classification_metrics(y_true, lstm_pred_labels)
        lstm_metrics["mean_latency_ms"] = round(lstm_time / len(texts), 2)
        comparison_results["lstm"] = lstm_metrics

        try:
            log_experiment_to_db(
                model_name="BiLSTM (Supervised)",
                dataset_name="HeldOut-Test",
                metrics=lstm_metrics,
                model_version="v1.0",
                db_path=db_path
            )
        except Exception as e:
            print(f"LSTM DB log notice: {e}")

    # Export comparison dataframe
    os.makedirs(export_dir, exist_ok=True)
    comp_data = [
        {
            "Model": "FinBERT (Pretrained Transformer)",
            "Accuracy": finbert_metrics["accuracy"],
            "Macro F1": finbert_metrics["macro_f1"],
            "Macro Precision": finbert_metrics["macro_precision"],
            "Macro Recall": finbert_metrics["macro_recall"],
            "Latency (ms/email)": finbert_metrics["mean_latency_ms"]
        },
        {
            "Model": "BiLSTM (Sequence Baseline)",
            "Accuracy": comparison_results["lstm"]["accuracy"],
            "Macro F1": comparison_results["lstm"]["macro_f1"],
            "Macro Precision": comparison_results["lstm"]["macro_precision"],
            "Macro Recall": comparison_results["lstm"]["macro_recall"],
            "Latency (ms/email)": comparison_results["lstm"]["mean_latency_ms"]
        }
    ]
    comp_df = pd.DataFrame(comp_data)
    csv_path = os.path.join(export_dir, "model_comparison_metrics.csv")
    comp_df.to_csv(csv_path, index=False)
    print(f"\nModel Comparison Summary:\n{comp_df.to_string(index=False)}")
    print(f"\nSaved CSV report to: {csv_path}")

    return comparison_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate FinBERT and LSTM on test set.")
    parser.add_argument("--test_csv", type=str, default="data/test.csv")
    args = parser.parse_args()

    evaluate_both_models_on_test_set(test_csv=args.test_csv)
