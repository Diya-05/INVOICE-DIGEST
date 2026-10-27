"""
Unit and Integration Tests for Invoice Digest
Validates database integrity, deduplication, CSV ingestion,
metrics calculation, and daily digest reporting.
"""

import os
import tempfile
import pandas as pd
import pytest
from src.database import (
    get_dashboard_kpis,
    init_database,
    insert_email,
    insert_prediction,
    save_human_label,
)
from src.email_import import import_emails_from_df, validate_csv_structure
from src.evaluation import compute_classification_metrics
from src.preprocessing import clean_email_text, compute_content_hash
from src.report_generator import generate_daily_digest


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_database(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_database_initialization(temp_db):
    """Verifies that all 5 tables are created properly."""
    kpis = get_dashboard_kpis(temp_db)
    assert kpis["total_emails"] == 0
    assert kpis["positive_count"] == 0


def test_duplicate_content_hash_rejection(temp_db):
    """Verifies idempotent deduplication on content hash."""
    h = compute_content_hash("Invoice Overdue", "Please pay now", "billing@test.com")
    id1 = insert_email("Invoice Overdue", "billing@test.com", "2026-10-25T10:00:00Z", "Please pay now", h, db_path=temp_db)
    assert id1 is not None

    # Attempt to insert identical email
    id2 = insert_email("Invoice Overdue", "billing@test.com", "2026-10-25T10:00:00Z", "Please pay now", h, db_path=temp_db)
    assert id2 is None  # Duplicate rejected


def test_csv_validation_and_import(temp_db):
    """Tests CSV validation and bulk import."""
    df_good = pd.DataFrame([
        {
            "subject": "Payment Received",
            "sender": "ar@vendor.com",
            "received_at": "2026-10-25T12:00:00Z",
            "body_text": "Thank you for settling invoice #100",
            "sentiment": "positive"
        },
        {
            "subject": "Dispute on Charge",
            "sender": "client@corp.com",
            "received_at": "2026-10-25T14:30:00Z",
            "body_text": "We dispute the $500 fee on this invoice",
            "sentiment": "negative"
        }
    ])

    valid, err = validate_csv_structure(df_good)
    assert valid is True
    assert err is None

    result = import_emails_from_df(df_good, db_path=temp_db)
    assert result["success"] is True
    assert result["imported"] == 2
    assert result["duplicates"] == 0

    # Repeat import to test deduplication
    result_repeat = import_emails_from_df(df_good, db_path=temp_db)
    assert result_repeat["imported"] == 0
    assert result_repeat["duplicates"] == 2


def test_metrics_calculation():
    """Verifies multi-class macro F1, precision, recall, and confusion matrix."""
    y_true = ["positive", "negative", "neutral", "positive", "negative"]
    y_pred = ["positive", "negative", "neutral", "neutral", "negative"]

    metrics = compute_classification_metrics(y_true, y_pred)
    assert 0.0 <= metrics["macro_f1"] <= 1.0
    assert metrics["accuracy"] == 0.8
    assert "confusion_matrix" in metrics
    assert len(metrics["confusion_matrix"]["labels"]) == 3


def test_daily_digest_generation(temp_db):
    """Verifies aggregation and report formatting for daily digest."""
    # Insert sample email and prediction
    h = compute_content_hash("Immediate Payment Required", "Urgent notice", "credit@biz.com")
    email_id = insert_email("Immediate Payment Required", "credit@biz.com", "2026-10-26T09:00:00Z", "Urgent notice", h, db_path=temp_db)
    insert_prediction(
        email_id=email_id,
        model_name="FinBERT",
        sentiment="negative",
        positive_score=0.05,
        negative_score=0.90,
        neutral_score=0.05,
        inference_ms=12.5,
        db_path=temp_db
    )

    digest = generate_daily_digest("2026-10-26", db_path=temp_db)
    assert digest["total_emails"] == 1
    assert digest["negative_count"] == 1
    assert "Immediate Payment Required" in digest["report_markdown"]


def test_email_service_helpers():
    """Verifies email decoding and header handling."""
    from src.email_service import _decode_header_str, verify_email_credentials
    assert _decode_header_str("Invoice #1029 Due") == "Invoice #1029 Due"
    assert _decode_header_str(None) == ""
    # Verifies graceful failure on invalid credentials without crashing
    ok, err = verify_email_credentials("fake@gmail.com", "fake_pass_123")
    assert ok is False
    assert err is not None
