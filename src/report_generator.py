"""
Daily Digest and Report Generation Engine for Invoice Digest
Aggregates daily predictions, flags negative communications for immediate human review,
formats markdown/CSV digests, and saves snapshots to SQLite.
"""

from datetime import datetime, timezone
import io
import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from src.database import DEFAULT_DB_PATH, get_db_connection, get_utc_now


def generate_daily_digest(
    report_date: str,
    db_path: str = DEFAULT_DB_PATH,
    save_snapshot: bool = True
) -> Dict[str, Any]:
    """
    Aggregates emails and predictions for a specific calendar date (YYYY-MM-DD),
    identifies urgent negative communications, builds a human-readable digest,
    and optionally records the snapshot in daily_reports.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Query emails received on the specified date
        # Matching substring on ISO format: YYYY-MM-DD
        cursor.execute(
            """
            SELECT 
                e.id,
                e.source_id,
                e.subject,
                e.sender,
                e.received_at,
                e.body_text,
                COALESCE(p.sentiment, 'neutral') AS sentiment,
                COALESCE(p.negative_score, 0.0) AS negative_score,
                COALESCE(p.positive_score, 0.0) AS positive_score,
                COALESCE(p.neutral_score, 0.0) AS neutral_score,
                p.model_name
            FROM emails e
            LEFT JOIN predictions p ON p.id = (
                SELECT id FROM predictions 
                WHERE email_id = e.id 
                ORDER BY created_at DESC LIMIT 1
            )
            WHERE e.received_at LIKE ?
            ORDER BY e.received_at ASC;
            """,
            (f"{report_date}%",)
        )
        rows = cursor.fetchall()

    email_records = [dict(r) for r in rows]
    total_emails = len(email_records)

    positive_emails = [e for e in email_records if e["sentiment"] == "positive"]
    negative_emails = [e for e in email_records if e["sentiment"] == "negative"]
    neutral_emails = [e for e in email_records if e["sentiment"] == "neutral"]

    pos_count = len(positive_emails)
    neg_count = len(negative_emails)
    neu_count = len(neutral_emails)

    # Format Markdown Report
    md_lines = [
        f"# Invoice Digest — Daily Financial Communication Report",
        f"**Date:** {report_date}  |  **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Executive Summary",
        f"- **Total Communications Analyzed:** {total_emails}",
        f"- **Negative (Action / Dispute / Risk):** {neg_count} ({(neg_count/total_emails*100):.1f}%" if total_emails else "- **Negative:** 0",
        f"- **Neutral (Operational / Invoices / POs):** {neu_count} ({(neu_count/total_emails*100):.1f}%" if total_emails else "- **Neutral:** 0",
        f"- **Positive (Settled / Discounts / Confirmations):** {pos_count} ({(pos_count/total_emails*100):.1f}%" if total_emails else "- **Positive:** 0",
        "",
        "---",
        "## Priority Review: Negative & High-Risk Communications",
    ]

    if not negative_emails:
        md_lines.append("*No negative communications detected for this date.*")
    else:
        for idx, item in enumerate(negative_emails, 1):
            md_lines.extend([
                f"### {idx}. {item['subject']}",
                f"- **Sender:** `{item['sender']}`",
                f"- **Received:** {item['received_at']}",
                f"- **Model Confidence (Negative):** {item['negative_score']:.2%}",
                f"- **Excerpt:** *{item['body_text'][:250]}...*",
                ""
            ])

    md_lines.extend([
        "---",
        "## Standard Invoicing & Operational Items",
        f"There are **{neu_count}** neutral transactional messages and **{pos_count}** positive confirmations.",
        "",
        "*(Note: Sentiment indicates emotional and contractual tone, not transactional urgency. Human review recommended.)*"
    ])

    report_markdown = "\n".join(md_lines)

    report_id = None
    if save_snapshot and total_emails > 0:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO daily_reports (
                    report_date, total_emails, positive_count, negative_count, neutral_count, report_content, delivery_status
                ) VALUES (?, ?, ?, ?, ?, ?, 'draft');
                """,
                (report_date, total_emails, pos_count, neg_count, neu_count, report_markdown)
            )
            report_id = cursor.lastrowid

    return {
        "report_id": report_id,
        "report_date": report_date,
        "total_emails": total_emails,
        "positive_count": pos_count,
        "negative_count": neg_count,
        "neutral_count": neu_count,
        "negative_emails": negative_emails,
        "all_emails": email_records,
        "report_markdown": report_markdown
    }


def export_digest_to_csv(email_records: List[Dict[str, Any]]) -> str:
    """Exports daily digest email records to a CSV string."""
    df = pd.DataFrame(email_records)
    if df.empty:
        return "id,source_id,subject,sender,received_at,sentiment,negative_score\n"
    export_cols = [c for c in ["id", "source_id", "subject", "sender", "received_at", "sentiment", "negative_score", "positive_score", "neutral_score"] if c in df.columns]
    return df[export_cols].to_csv(index=False)
