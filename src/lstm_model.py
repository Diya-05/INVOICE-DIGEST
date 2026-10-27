"""
PyTorch LSTM Sequence Classifier for Invoice Digest
Provides vocabulary building, embedding + bidirectional LSTM architecture,
checkpoint persistence, and batch inference.
"""

import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from src.preprocessing import CANONICAL_SENTIMENTS, SentimentClass, prepare_email_for_model

DEFAULT_CHECKPOINT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models", "lstm_checkpoint"
)


class TextVocabulary:
    """Manages word-to-index mapping and text numericalization."""

    def __init__(self, min_freq: int = 1):
        self.min_freq = min_freq
        self.pad_token = "<PAD>"
        self.unk_token = "<UNK>"
        self.word2idx = {self.pad_token: 0, self.unk_token: 1}
        self.idx2word = {0: self.pad_token, 1: self.unk_token}

    def tokenize(self, text: str) -> List[str]:
        """Simple alphanumeric tokenizer."""
        return re.findall(r"\b\w+\b", str(text).lower())

    def fit(self, texts: List[str]) -> "TextVocabulary":
        """Fits vocabulary exclusively on training texts."""
        freqs: Dict[str, int] = {}
        for text in texts:
            tokens = self.tokenize(text)
            for tok in tokens:
                freqs[tok] = freqs.get(tok, 0) + 1

        for tok, cnt in freqs.items():
            if cnt >= self.min_freq and tok not in self.word2idx:
                new_idx = len(self.word2idx)
                self.word2idx[tok] = new_idx
                self.idx2word[new_idx] = tok

        return self

    def encode(self, text: str, max_length: int = 128) -> List[int]:
        """Encodes text into a fixed-length sequence of token IDs."""
        tokens = self.tokenize(text)
        unk_id = self.word2idx[self.unk_token]
        pad_id = self.word2idx[self.pad_token]

        seq = [self.word2idx.get(t, unk_id) for t in tokens[:max_length]]
        if len(seq) < max_length:
            seq.extend([pad_id] * (max_length - len(seq)))
        return seq

    def save(self, file_path: str) -> None:
        """Saves vocabulary mapping to JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"word2idx": self.word2idx}, f)

    @classmethod
    def load(cls, file_path: str) -> "TextVocabulary":
        """Loads vocabulary from JSON file."""
        vocab = cls()
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            vocab.word2idx = data["word2idx"]
            vocab.idx2word = {int(v): k for k, v in vocab.word2idx.items()}
        return vocab

    def __len__(self) -> int:
        return len(self.word2idx)


class LSTMNet(nn.Module):
    """Bidirectional LSTM Sequence Classification Network."""

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 100,
        hidden_dim: int = 64,
        num_layers: int = 2,
        num_classes: int = 3,
        dropout: float = 0.3
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, 32)
        self.fc2 = nn.Linear(32, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, seq_len)
        embedded = self.dropout(self.embedding(x))
        lstm_out, (hn, _) = self.lstm(embedded)
        # Concatenate forward and backward final hidden states
        # hn is (num_layers * 2, batch_size, hidden_dim)
        forward_hn = hn[-2, :, :]
        backward_hn = hn[-1, :, :]
        cat_hn = torch.cat((forward_hn, backward_hn), dim=1)

        dense = F.relu(self.fc1(self.dropout(cat_hn)))
        logits = self.fc2(dense)
        return logits


class LSTMClassifier:
    """High-level wrapper for PyTorch LSTM sequence model training and inference."""

    LABEL_MAPPING = {
        0: SentimentClass.NEGATIVE.value,
        1: SentimentClass.NEUTRAL.value,
        2: SentimentClass.POSITIVE.value
    }
    REVERSE_LABEL_MAPPING = {v: k for k, v in LABEL_MAPPING.items()}

    def __init__(
        self,
        checkpoint_dir: str = DEFAULT_CHECKPOINT_DIR,
        device: Optional[str] = None
    ):
        self.checkpoint_dir = checkpoint_dir
        if device is None:
            if torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        self.vocab: Optional[TextVocabulary] = None
        self.model: Optional[LSTMNet] = None
        self.max_length = 128

    def is_trained(self) -> bool:
        """Checks if a trained checkpoint exists."""
        weights_file = os.path.join(self.checkpoint_dir, "lstm_weights.pt")
        vocab_file = os.path.join(self.checkpoint_dir, "vocab.json")
        return os.path.isfile(weights_file) and os.path.isfile(vocab_file)

    def load_checkpoint(self) -> None:
        """Loads trained weights and vocabulary from disk."""
        if self.model is not None and self.vocab is not None:
            return

        vocab_file = os.path.join(self.checkpoint_dir, "vocab.json")
        weights_file = os.path.join(self.checkpoint_dir, "lstm_weights.pt")
        meta_file = os.path.join(self.checkpoint_dir, "meta.json")

        if not os.path.isfile(vocab_file) or not os.path.isfile(weights_file):
            raise FileNotFoundError(f"LSTM checkpoint not found in {self.checkpoint_dir}. Run training first.")

        self.vocab = TextVocabulary.load(vocab_file)

        # Load metadata
        with open(meta_file, "r") as f:
            meta = json.load(f)
            self.max_length = meta.get("max_length", 128)

        self.model = LSTMNet(
            vocab_size=len(self.vocab),
            embedding_dim=meta.get("embedding_dim", 100),
            hidden_dim=meta.get("hidden_dim", 64),
            num_layers=meta.get("num_layers", 2),
            num_classes=3
        )
        self.model.load_state_dict(torch.load(weights_file, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Runs batched sequence prediction using the trained LSTM."""
        self.load_checkpoint()
        results = []

        start_time = time.perf_counter()
        encoded = [self.vocab.encode(t, max_length=self.max_length) for t in texts]
        tensor_x = torch.tensor(encoded, dtype=torch.long).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor_x)
            probs = F.softmax(logits, dim=-1).cpu().numpy()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        per_sample_ms = elapsed_ms / len(texts) if texts else 0.0

        for p_row in probs:
            neg_score = float(p_row[0])
            neu_score = float(p_row[1])
            pos_score = float(p_row[2])

            scores = {"negative": neg_score, "neutral": neu_score, "positive": pos_score}
            best_sentiment = max(scores, key=scores.get)

            results.append({
                "model_name": "LSTM-Classifier",
                "sentiment": best_sentiment,
                "negative_score": neg_score,
                "neutral_score": neu_score,
                "positive_score": pos_score,
                "inference_ms": round(per_sample_ms, 2)
            })

        return results

    def predict_email(self, subject: str, body: str) -> Dict[str, Any]:
        """Convenience single email predictor."""
        prepared = prepare_email_for_model(subject, body)
        return self.predict_batch([prepared])[0]
