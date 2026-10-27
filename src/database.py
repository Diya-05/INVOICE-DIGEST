"""
Database Management Module for Invoice Digest
Handles SQLite schema creation, foreign-key constraints, thread safety,
and CRUD operations for emails, predictions, labels, model runs, and reports.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "invoice_digest.db")


def get_utc_now() -> str:
    """Returns current UTC ISO timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_db_connection(db_path: str = DEFAULT_DB_PATH):
    """
    Context manager for SQLite database connection.
    Enforces foreign keys, thread-safety, and commits/rollbacks automatically.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes all 5 tables specified in the MLIS blueprint."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. emails table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                received_at TEXT NOT NULL,
                body_text TEXT NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_received_at ON emails(received_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_content_hash ON emails(content_hash);")

        # 2. predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                sentiment TEXT NOT NULL CHECK(sentiment IN ('positive', 'negative', 'neutral')),
                positive_score REAL NOT NULL,
                negative_score REAL NOT NULL,
                neutral_score REAL NOT NULL,
                inference_ms REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_email_id ON predictions(email_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_name);")

        # 3. email_labels table (human verified ground truth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                sentiment TEXT NOT NULL CHECK(sentiment IN ('positive', 'negative', 'neutral')),
                labeled_by TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_labels_email_id ON email_labels(email_id);")

        # 4. model_runs table (experiments and metrics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                accuracy REAL NOT NULL,
                macro_precision REAL NOT NULL,
                macro_recall REAL NOT NULL,
                macro_f1 REAL NOT NULL,
                train_time_seconds REAL,
                created_at TEXT NOT NULL
            );
        """)

        # 5. daily_reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                total_emails INTEGER NOT NULL,
                positive_count INTEGER NOT NULL,
                negative_count INTEGER NOT NULL,
                neutral_count INTEGER NOT NULL,
                report_content TEXT NOT NULL,
                delivery_status TEXT NOT NULL DEFAULT 'draft' CHECK(delivery_status IN ('draft', 'sent', 'failed')),
                sent_at TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(report_date);")


def insert_email(
    subject: str,
    sender: str,
    received_at: str,
    body_text: str,
    content_hash: str,
    source_id: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Optional[int]:
    """
    Inserts a single email into the database with idempotent duplicate checking.
    Returns the new email id, or None if already exists.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO emails (source_id, subject, sender, received_at, body_text, content_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (source_id, subject, sender, received_at, body_text, content_hash, get_utc_now())
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Duplicate content_hash
            return None


def insert_prediction(
    email_id: int,
    model_name: str,
    sentiment: str,
    positive_score: float,
    negative_score: float,
    neutral_score: float,
    inference_ms: float,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Inserts a sentiment prediction for an email."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO predictions (email_id, model_name, sentiment, positive_score, negative_score, neutral_score, inference_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (email_id, model_name, sentiment, positive_score, negative_score, neutral_score, inference_ms, get_utc_now())
        )
        return cursor.lastrowid


def save_human_label(
    email_id: int,
    sentiment: str,
    labeled_by: str = "human_reviewer",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Records human verification label for an email."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO email_labels (email_id, sentiment, labeled_by, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (email_id, sentiment, labeled_by, get_utc_now())
        )
        return cursor.lastrowid


def record_model_run(
    model_name: str,
    dataset_name: str,
    model_version: str,
    accuracy: float,
    macro_precision: float,
    macro_recall: float,
    macro_f1: float,
    train_time_seconds: Optional[float] = None,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Logs an experiment run and its metrics."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO model_runs (model_name, dataset_name, model_version, accuracy, macro_precision, macro_recall, macro_f1, train_time_seconds, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (model_name, dataset_name, model_version, accuracy, macro_precision, macro_recall, macro_f1, train_time_seconds, get_utc_now())
        )
        return cursor.lastrowid


def get_emails_with_latest_predictions(
    model_filter: Optional[str] = None,
    sentiment_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 100,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Retrieves emails joined with their latest predictions and human labels."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        sql = """
            SELECT 
                e.id AS email_id,
                e.source_id,
                e.subject,
                e.sender,
                e.received_at,
                e.body_text,
                p.model_name,
                p.sentiment AS pred_sentiment,
                p.positive_score,
                p.negative_score,
                p.neutral_score,
                p.inference_ms,
                l.sentiment AS human_label
            FROM emails e
            LEFT JOIN predictions p ON p.id = (
                SELECT id FROM predictions 
                WHERE email_id = e.id 
                ORDER BY created_at DESC LIMIT 1
            )
            LEFT JOIN email_labels l ON l.id = (
                SELECT id FROM email_labels 
                WHERE email_id = e.id 
                ORDER BY created_at DESC LIMIT 1
            )
            WHERE 1=1
        """
        params: List[Any] = []
        if sentiment_filter and sentiment_filter.lower() != "all":
            sql += " AND p.sentiment = ?"
            params.append(sentiment_filter.lower())
        if model_filter and model_filter.lower() != "all":
            sql += " AND p.model_name LIKE ?"
            params.append(f"%{model_filter}%")
        if search_query:
            sql += " AND (e.subject LIKE ? OR e.sender LIKE ? OR e.body_text LIKE ?)"
            term = f"%{search_query}%"
            params.extend([term, term, term])

        sql += " ORDER BY e.received_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_dashboard_kpis(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Calculates summary KPIs for the dashboard."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM emails;")
        total_emails = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT 
                COALESCE(p.sentiment, 'unclassified') AS sentiment, 
                COUNT(*) AS count
            FROM emails e
            LEFT JOIN predictions p ON p.id = (
                SELECT id FROM predictions 
                WHERE email_id = e.id 
                ORDER BY created_at DESC LIMIT 1
            )
            GROUP BY COALESCE(p.sentiment, 'unclassified');
        """)
        rows = cursor.fetchall()
        counts = {row["sentiment"]: row["count"] for row in rows}

        return {
            "total_emails": total_emails,
            "positive_count": counts.get("positive", 0),
            "negative_count": counts.get("negative", 0),
            "neutral_count": counts.get("neutral", 0),
            "unclassified_count": counts.get("unclassified", 0)
        }
