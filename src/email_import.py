"""
Email Ingestion and Validation Engine for Invoice Digest
Handles CSV validation, deduplication via SHA-256 content hashes,
and database persistence.
"""

from datetime import datetime
import io
import os
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
from src.database import DEFAULT_DB_PATH, insert_email, save_human_label
from src.preprocessing import compute_content_hash, clean_email_text, SentimentClass

REQUIRED_COLUMNS = {"subject", "sender", "received_at", "body_text"}


def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """Validates that incoming DataFrame has all required columns and non-empty rows."""
    if df.empty:
        return False, "CSV file contains no data."

    # Normalize column names to lowercase stripped
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return False, f"Missing required columns: {', '.join(sorted(missing))}"

    return True, None


def import_emails_from_df(
    df: pd.DataFrame,
    db_path: str = DEFAULT_DB_PATH,
    import_ground_truth: bool = True
) -> Dict[str, Any]:
    """
    Imports emails from a pandas DataFrame into SQLite.
    Performs duplicate checking, validation, and optional ground truth label ingestion.
    """
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    valid, error_msg = validate_csv_structure(df)
    if not valid:
        return {
            "success": False,
            "error": error_msg,
            "total_rows": len(df) if not df.empty else 0,
            "imported": 0,
            "duplicates": 0,
            "failed": len(df) if not df.empty else 0
        }

    imported_count = 0
    duplicate_count = 0
    failed_count = 0
    imported_ids = []

    for idx, row in df.iterrows():
        subject = str(row.get("subject", "")).strip()
        sender = str(row.get("sender", "")).strip()
        body_text = str(row.get("body_text", "")).strip()
        received_at_raw = str(row.get("received_at", "")).strip()
        source_id = str(row.get("source_id", f"csv_{idx}")).strip()

        # Reject records with empty essential content
        if not subject or not body_text or not sender:
            failed_count += 1
            continue

        # Format received_at
        try:
            # Try parsing ISO or standard date formats
            dt = pd.to_datetime(received_at_raw)
            received_at = dt.isoformat()
        except Exception:
            received_at = datetime.utcnow().isoformat()

        content_hash = compute_content_hash(subject, body_text, sender)

        email_id = insert_email(
            subject=subject,
            sender=sender,
            received_at=received_at,
            body_text=body_text,
            content_hash=content_hash,
            source_id=source_id,
            db_path=db_path
        )

        if email_id is not None:
            imported_count += 1
            imported_ids.append(email_id)

            # Check if optional ground truth sentiment is provided
            if import_ground_truth and "sentiment" in row and pd.notna(row["sentiment"]):
                try:
                    canonical_sentiment = SentimentClass.from_str(str(row["sentiment"])).value
                    save_human_label(
                        email_id=email_id,
                        sentiment=canonical_sentiment,
                        labeled_by="csv_dataset",
                        db_path=db_path
                    )
                except Exception:
                    pass
        else:
            duplicate_count += 1

    return {
        "success": True,
        "total_rows": len(df),
        "imported": imported_count,
        "duplicates": duplicate_count,
        "failed": failed_count,
        "imported_ids": imported_ids
    }


def import_emails_from_csv(
    file_path_or_buffer: Union[str, io.BytesIO, io.StringIO],
    db_path: str = DEFAULT_DB_PATH,
    import_ground_truth: bool = True
) -> Dict[str, Any]:
    """Imports emails from a CSV file path or file-like buffer."""
    try:
        df = pd.read_csv(file_path_or_buffer)
        return import_emails_from_df(df, db_path=db_path, import_ground_truth=import_ground_truth)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read CSV: {str(e)}",
            "total_rows": 0,
            "imported": 0,
            "duplicates": 0,
            "failed": 0
        }
