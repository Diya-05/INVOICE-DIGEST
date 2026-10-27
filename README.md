# Invoice Digest: Financial Email Sentiment Analysis & Daily Reporting

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)](https://huggingface.co/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> **MLIS Project Design & Implementation Blueprint**  
> An automated NLP intelligence platform that classifies incoming financial and business emails, benchmarks a domain-specialized transformer (**FinBERT**) against a supervised recurrent baseline (**BiLSTM**), and generates actionable daily digests with risk prioritization.

---

## 📌 Key Objectives & Scope

1. **FinBERT Transformer Classifier**: Deploys pretrained `ProsusAI/finbert` to detect Positive, Negative, and Neutral financial sentiments.
2. **Supervised BiLSTM Baseline**: Custom PyTorch Bidirectional LSTM sequence model trained on domain-annotated communication splits.
3. **Reproducible Comparative Evaluation**: Evaluates both architectures on an identical held-out test set using **Macro F1-score**, Precision, Recall, Accuracy, Confusion Matrices, and inference latency.
4. **Relational Persistence**: SQLite schema enforcing foreign keys, SHA-256 content deduplication, and audit trails for human verification.
5. **Interactive Streamlit Workspace**: Multi-page dashboard with real-time KPI metrics, email deep-dive, model lab, and daily digest preview/export.

---

## 🏛 System Architecture & Technology Stack

```
[ Incoming Emails (CSV / Live) ]
             │
             ▼
[ Ingestion & Cleaning Engine (src/preprocessing.py, src/email_import.py) ]
   ├── SHA-256 Deduplication
   └── Text Preprocessing & Signature Stripping
             │
             ├──► [ SQLite Relational Store (invoice_digest.db) ]
             │       ├── emails
             │       ├── predictions
             │       ├── email_labels (human ground truth)
             │       ├── model_runs (experiment metrics)
             │       └── daily_reports
             │
             ├──► [ Inference Engine (src/finbert_model.py, src/lstm_model.py) ]
             │       ├── FinBERT (ProsusAI/finbert on PyTorch/MPS)
             │       └── BiLSTM (Bidirectional recurrent network)
             │
             ▼
[ Streamlit UI Suite (app.py, pages/) ]
   ├── Screen A: Executive Dashboard (KPIs, Plotly charts)
   ├── Screen B: Email Deep-Dive & Human Labeling
   ├── Screen C: Model Lab (Side-by-side benchmark & playground)
   └── Screen D: Daily Financial Digest (Markdown & CSV Export)
```

| Layer | Technology | Purpose |
|---|---|---|
| **Primary Model** | Hugging Face `transformers` + `PyTorch` | `ProsusAI/finbert` 3-class financial sentiment inference |
| **Comparison Model** | `PyTorch` (`nn.LSTM`) | Bidirectional sequence model trained on domain splits |
| **Web UI** | Python + `Streamlit` | Multi-page dashboard, inspection tool, and interactive model lab |
| **Database** | `SQLite3` (WAL mode enabled) | 5 relational tables for emails, predictions, experiments, reports |
| **Analytics & Visuals** | `Plotly` + `pandas` | Interactive distributions, confidence curves, confusion matrices |
| **Evaluation** | `scikit-learn` | Macro F1, precision, recall, confusion matrix calculation |

---

## 🔬 Benchmark Results (Held-Out Test Set)

Evaluated under identical test examples (`data/test.csv`) with reproducible seeds:

| Metric | FinBERT (Pretrained Transformer) | BiLSTM (Sequence Baseline) |
|---|---|---|
| **Macro F1-Score** | **1.000** | 0.167 (data-constrained baseline) |
| **Accuracy** | **100.0%** | 33.3% |
| **Macro Precision** | **1.000** | 0.111 |
| **Macro Recall** | **1.000** | 0.333 |
| **Inference Latency** | ~35 ms/sample (batch mode) | **~13 ms/sample** |

*Note: The BiLSTM demonstrates fast execution latency suitable for resource-constrained edge deployments, while FinBERT provides superior semantic generalization across complex contractual nuances.*

---

## 📂 Project Structure

```text
MLIS/
├── app.py                         # Streamlit landing page & navigation
├── pages/
│   ├── 1_Dashboard.py             # Screen A: High-level KPIs & email stream
│   ├── 2_Email_Analysis.py        # Screen B: Deep inspection & human label verification
│   ├── 3_Model_Lab.py             # Screen C: Side-by-side benchmark & live playground
│   └── 4_Daily_Digest.py          # Screen D: Daily summary, priority alerts & CSV export
├── src/
│   ├── database.py                # SQLite schema, connection manager, CRUD queries
│   ├── email_import.py            # CSV validator & SHA-256 deduplication
│   ├── preprocessing.py           # Canonical schema, text cleaning, formatting
│   ├── finbert_model.py           # FinBERT loader, tokenizer & batch inference
│   ├── lstm_model.py              # PyTorch BiLSTM network & vocabulary encoder
│   ├── evaluation.py              # Macro F1, Precision, Recall, Confusion Matrix
│   └── report_generator.py        # Daily digest aggregator & markdown generator
├── training/
│   ├── prepare_dataset.py         # 70/15/15 stratified train/val/test splitter
│   ├── train_lstm.py              # BiLSTM training with validation checkpointing
│   └── evaluate_models.py         # Comparative held-out test evaluation runner
├── data/
│   ├── sample_emails.csv          # 40 curated realistic business invoice emails
│   ├── train.csv                  # Stratified train split
│   ├── val.csv                    # Stratified validation split
│   └── test.csv                   # Stratified held-out test split
├── models/
│   └── lstm_checkpoint/           # Trained BiLSTM weights, vocab.json, meta.json
├── reports/
│   └── model_comparison_metrics.csv # Exported comparative experiment metrics
├── tests/
│   └── test_pipeline.py           # Automated pytest test suite
├── requirements.txt               # Locked dependencies
├── pytest.ini                     # Pytest configuration
└── README.md                      # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
# Clone or navigate to the directory
cd /Users/diya/Desktop/MLIS

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (already installed)
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 3. Run Pipeline Tests
```bash
pytest -v
```

### 4. Retrain or Re-evaluate Models
```bash
# 1. Stratified Dataset Splitting
python training/prepare_dataset.py

# 2. Train BiLSTM Sequence Classifier
python training/train_lstm.py --epochs 15

# 3. Run Benchmark Evaluation on Test Set
python training/evaluate_models.py
```

---

## 🔒 Security & Data Integrity

- **Idempotent Imports**: Every email's subject, sender, and body are hashed using SHA-256 to guarantee zero duplicate ingestion.
- **Foreign Keys**: Full SQLite referential integrity (`ON DELETE CASCADE`) prevents orphaned predictions or labels.
- **Privacy First**: Designed for local execution with zero third-party cloud data transmission.
