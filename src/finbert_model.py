"""
FinBERT Sentiment Inference Pipeline for Invoice Digest
Loads pretrained FinBERT checkpoint, handles tokenization, runs batched inference,
and returns calibrated probabilities mapped to canonical sentiment classes.
"""

import time
from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from src.database import DEFAULT_DB_PATH, insert_prediction
from src.preprocessing import CANONICAL_SENTIMENTS, SentimentClass, prepare_email_for_model

DEFAULT_FINBERT_CHECKPOINT = "ProsusAI/finbert"


class FinBERTClassifier:
    """Wrapper for Hugging Face FinBERT model with GPU/MPS/CPU device management."""

    def __init__(self, model_name: str = DEFAULT_FINBERT_CHECKPOINT, device: Optional[str] = None):
        self.model_name = model_name
        if device is None:
            if torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        self.tokenizer = None
        self.model = None
        self.id2label = {}

    def load_model(self) -> None:
        """Loads tokenizer and weights from Hugging Face hub or local cache."""
        if self.model is not None and self.tokenizer is not None:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()

        # Standardize model label mapping
        raw_id2label = self.model.config.id2label or {0: "positive", 1: "negative", 2: "neutral"}
        self.id2label = {}
        for idx, lbl in raw_id2label.items():
            self.id2label[int(idx)] = SentimentClass.from_str(lbl).value

    def predict_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict[str, Any]]:
        """
        Runs batched inference on a list of prepared text strings.
        Returns a list of dicts with sentiment, probabilities, and inference latency.
        """
        self.load_model()
        results: List[Dict[str, Any]] = []

        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            start_time = time.perf_counter()

            inputs = self.tokenizer(
                chunk,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = F.softmax(outputs.logits, dim=-1).cpu().numpy()

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            per_sample_ms = elapsed_ms / len(chunk)

            for p_row in probs:
                prob_dict = {}
                for idx, p_val in enumerate(p_row):
                    lbl = self.id2label.get(idx, f"class_{idx}")
                    prob_dict[lbl] = float(p_val)

                # Determine best class
                best_class = max(prob_dict, key=prob_dict.get)

                results.append({
                    "model_name": self.model_name,
                    "sentiment": best_class,
                    "positive_score": prob_dict.get("positive", 0.0),
                    "negative_score": prob_dict.get("negative", 0.0),
                    "neutral_score": prob_dict.get("neutral", 0.0),
                    "inference_ms": round(per_sample_ms, 2)
                })

        return results

    def predict_email(self, subject: str, body: str) -> Dict[str, Any]:
        """Convenience method to predict a single email."""
        prepared = prepare_email_for_model(subject, body)
        return self.predict_batch([prepared])[0]


# Cached singleton instance for fast reuse in Streamlit
_finbert_instance: Optional[FinBERTClassifier] = None


def get_finbert_classifier() -> FinBERTClassifier:
    """Returns singleton FinBERTClassifier instance."""
    global _finbert_instance
    if _finbert_instance is None:
        _finbert_instance = FinBERTClassifier()
    return _finbert_instance


def run_finbert_on_emails(
    emails: List[Dict[str, Any]],
    db_path: str = DEFAULT_DB_PATH,
    progress_callback=None
) -> List[Dict[str, Any]]:
    """
    Runs FinBERT on a list of email dicts from SQLite and persists predictions.
    Calls optional progress_callback(current, total).
    """
    clf = get_finbert_classifier()
    clf.load_model()

    texts = [prepare_email_for_model(e["subject"], e["body_text"]) for e in emails]
    total = len(texts)
    results = []

    batch_size = 16
    for i in range(0, total, batch_size):
        chunk_texts = texts[i : i + batch_size]
        chunk_emails = emails[i : i + batch_size]
        preds = clf.predict_batch(chunk_texts, batch_size=batch_size)

        for email, pred in zip(chunk_emails, preds):
            e_id = email.get("id") or email.get("email_id")
            insert_prediction(
                email_id=e_id,
                model_name=pred["model_name"],
                sentiment=pred["sentiment"],
                positive_score=pred["positive_score"],
                negative_score=pred["negative_score"],
                neutral_score=pred["neutral_score"],
                inference_ms=pred["inference_ms"],
                db_path=db_path
            )
            merged = {**email, **pred}
            results.append(merged)

        if progress_callback:
            progress_callback(min(i + batch_size, total), total)

    return results
