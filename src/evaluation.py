"""
Evaluation and Metrics Tracking Module for Invoice Digest
Computes Macro F1, Precision, Recall, Accuracy, Confusion Matrices,
and records experiments to SQLite.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from src.database import DEFAULT_DB_PATH, record_model_run
from src.preprocessing import CANONICAL_SENTIMENTS


def compute_classification_metrics(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes comprehensive multi-class classification metrics:
    Macro F1, Precision, Recall, Accuracy, Per-class breakdown,
    and normalized Confusion Matrix.
    """
    if labels is None:
        labels = CANONICAL_SENTIMENTS

    y_true_clean = [str(y).strip().lower() for y in y_true]
    y_pred_clean = [str(y).strip().lower() for y in y_pred]

    acc = float(accuracy_score(y_true_clean, y_pred_clean))
    macro_f1 = float(f1_score(y_true_clean, y_pred_clean, labels=labels, average="macro", zero_division=0))
    macro_prec = float(f1_score(y_true_clean, y_pred_clean, labels=labels, average="macro", zero_division=0))
    
    # Calculate precision, recall, f1 per class
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true_clean, y_pred_clean, labels=labels, zero_division=0
    )

    per_class = {}
    for i, label in enumerate(labels):
        per_class[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1_score": float(f1[i]),
            "support": int(support[i])
        }

    macro_precision = float(np.mean(precision))
    macro_recall = float(np.mean(recall))

    # Confusion Matrix
    cm = confusion_matrix(y_true_clean, y_pred_clean, labels=labels)
    cm_dict = {
        "labels": labels,
        "matrix": cm.tolist()
    }

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "per_class": per_class,
        "confusion_matrix": cm_dict,
        "sample_count": len(y_true_clean)
    }


def log_experiment_to_db(
    model_name: str,
    dataset_name: str,
    metrics: Dict[str, Any],
    model_version: str = "v1.0",
    train_time_seconds: Optional[float] = None,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Stores experiment run metrics in SQLite model_runs table."""
    return record_model_run(
        model_name=model_name,
        dataset_name=dataset_name,
        model_version=model_version,
        accuracy=metrics.get("accuracy", 0.0),
        macro_precision=metrics.get("macro_precision", 0.0),
        macro_recall=metrics.get("macro_recall", 0.0),
        macro_f1=metrics.get("macro_f1", 0.0),
        train_time_seconds=train_time_seconds,
        db_path=db_path
    )
