"""
PyTorch LSTM Training Pipeline for Invoice Digest
Trains embedding + bidirectional LSTM on training set, evaluates on validation set,
saves best checkpoint, and logs run metadata.
"""

import argparse
import json
import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Dict, List, Tuple
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from src.database import DEFAULT_DB_PATH
from src.evaluation import compute_classification_metrics, log_experiment_to_db
from src.lstm_model import DEFAULT_CHECKPOINT_DIR, LSTMClassifier, LSTMNet, TextVocabulary
from src.preprocessing import prepare_email_for_model


class EmailDataset(Dataset):
    """PyTorch Dataset for tokenized email texts and sentiment labels."""

    def __init__(self, texts: List[str], labels: List[int], vocab: TextVocabulary, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.vocab = vocab
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        encoded = self.vocab.encode(self.texts[idx], max_length=self.max_length)
        return torch.tensor(encoded, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)


def train_lstm_model(
    train_csv: str,
    val_csv: str,
    checkpoint_dir: str = DEFAULT_CHECKPOINT_DIR,
    epochs: int = 15,
    batch_size: int = 8,
    lr: float = 0.001,
    embedding_dim: int = 100,
    hidden_dim: int = 64,
    num_layers: int = 2,
    max_length: int = 128,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, float]:
    """Trains LSTM classifier with validation checkpointing."""
    start_train_time = time.time()

    # Load data
    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)

    label_map = LSTMClassifier.REVERSE_LABEL_MAPPING

    train_texts = [prepare_email_for_model(r.get("subject", ""), r.get("body_text", "")) for _, r in train_df.iterrows()]
    train_labels = [label_map[str(r["sentiment"]).lower()] for _, r in train_df.iterrows()]

    val_texts = [prepare_email_for_model(r.get("subject", ""), r.get("body_text", "")) for _, r in val_df.iterrows()]
    val_labels = [label_map[str(r["sentiment"]).lower()] for _, r in val_df.iterrows()]

    # Fit vocabulary ONLY on training corpus
    vocab = TextVocabulary(min_freq=1).fit(train_texts)

    # DataLoaders
    train_ds = EmailDataset(train_texts, train_labels, vocab, max_length=max_length)
    val_ds = EmailDataset(val_texts, val_labels, vocab, max_length=max_length)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    # Device
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    model = LSTMNet(
        vocab_size=len(vocab),
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        num_classes=3
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    os.makedirs(checkpoint_dir, exist_ok=True)
    best_val_f1 = -1.0
    best_metrics = {}

    print(f"Training LSTM on {device} ({len(train_texts)} train, {len(val_texts)} val samples, vocab={len(vocab)})...")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0

        for x_batch, y_batch in train_loader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            logits = model(x_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(y_batch)

        avg_train_loss = total_loss / len(train_texts)

        # Validation phase
        model.eval()
        val_preds = []
        val_targets = []
        with torch.no_grad():
            for x_val, y_val in val_loader:
                x_val = x_val.to(device)
                logits = model(x_val)
                preds = torch.argmax(logits, dim=-1).cpu().tolist()
                val_preds.extend(preds)
                val_targets.extend(y_val.tolist())

        val_pred_names = [LSTMClassifier.LABEL_MAPPING[p] for p in val_preds]
        val_true_names = [LSTMClassifier.LABEL_MAPPING[t] for t in val_targets]

        metrics = compute_classification_metrics(val_true_names, val_pred_names)
        val_f1 = metrics["macro_f1"]
        val_acc = metrics["accuracy"]

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train_loss:.4f} | Val Acc: {val_acc:.3f} | Val Macro F1: {val_f1:.3f}")

        # Checkpoint selection based on validation Macro F1
        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            best_metrics = metrics

            torch.save(model.state_dict(), os.path.join(checkpoint_dir, "lstm_weights.pt"))
            vocab.save(os.path.join(checkpoint_dir, "vocab.json"))

            meta = {
                "embedding_dim": embedding_dim,
                "hidden_dim": hidden_dim,
                "num_layers": num_layers,
                "max_length": max_length,
                "epochs_trained": epoch,
                "best_val_macro_f1": best_val_f1,
                "best_val_accuracy": val_acc
            }
            with open(os.path.join(checkpoint_dir, "meta.json"), "w") as f:
                json.dump(meta, f, indent=2)

    train_duration = time.time() - start_train_time
    print(f"Training complete in {train_duration:.1f}s. Best Val Macro F1: {best_val_f1:.3f}")

    # Log to SQLite
    try:
        log_experiment_to_db(
            model_name="LSTM-BiLSTM",
            dataset_name="InvoiceEmails-Val",
            metrics=best_metrics,
            model_version="v1.0",
            train_time_seconds=round(train_duration, 2),
            db_path=db_path
        )
    except Exception as e:
        print(f"Note: Could not log to DB: {e}")

    return best_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train PyTorch LSTM model.")
    parser.add_argument("--train_csv", type=str, default="data/train.csv")
    parser.add_argument("--val_csv", type=str, default="data/val.csv")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=0.001)
    args = parser.parse_args()

    train_lstm_model(
        train_csv=args.train_csv,
        val_csv=args.val_csv,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
