"""
Daily Digest and Report Generation Engine for Invoice Digest
Aggregates daily predictions, flags negative communications for human review,
formats markdown/CSV digests, and saves/updates snapshots in SQLite without duplicate proliferation.
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
    identifies negative communications for human review, builds a markdown digest,
    and updates/records the snapshot in daily_reports idempotently.
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
                COALESCE(p.sentiment, 'unclassified') AS sentiment,
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
    unclassified_emails = [e for e in email_records if e["sentiment"] == "unclassified"]

    pos_count = len(positive_emails)
    neg_count = len(negative_emails)
    neu_count = len(neutral_emails)
    unclass_count = len(unclassified_emails)

    # Format Markdown Report
    md_lines = [
        f"# Invoice Digest — Daily Financial Intelligence Briefing",
        f"**Reporting Period:** {report_date}  |  **Compiled (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Executive Summary",
        f"- **Total Indexed Communications:** {total_emails}",
        f"- **Negative Sentiment (Review Recommended):** {neg_count} ({(neg_count/total_emails*100):.1f}%" if total_emails else "- **Negative Sentiment:** 0",
        f"- **Neutral Sentiment (Standard Invoicing/Operations):** {neu_count} ({(neu_count/total_emails*100):.1f}%" if total_emails else "- **Neutral Sentiment:** 0",
        f"- **Positive Sentiment (Confirmations/Discounts):** {pos_count} ({(pos_count/total_emails*100):.1f}%" if total_emails else "- **Positive Sentiment:** 0",
    ]
    if unclass_count > 0:
        md_lines.append(f"- **Pending Classification:** {unclass_count} ({(unclass_count/total_emails*100):.1f}%)")

    md_lines.extend([
        "",
        "---",
        "## Communications with Negative Polarity (Human Review Recommended)",
    ])

    if not negative_emails:
        md_lines.append("*No negative sentiment communications identified for this date.*")
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
        "## Operational & Transactional Summary",
        f"Contains **{neu_count}** neutral transactional messages and **{pos_count}** positive confirmations.",
        "",
        "> **Notice:** Sentiment polarity reflects language and counterparty affect, not absolute accounting priority. Please perform human verification before adjusting financial ledgers."
    ])

    report_markdown = "\n".join(md_lines)

    report_id = None
    if save_snapshot and total_emails > 0:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            # Prevent duplicate report snapshots on normal reruns:
            cursor.execute(
                "SELECT id FROM daily_reports WHERE report_date = ? ORDER BY id DESC LIMIT 1;",
                (report_date,)
            )
            existing = cursor.fetchone()
            if existing:
                report_id = existing["id"]
                cursor.execute(
                    """
                    UPDATE daily_reports 
                    SET total_emails = ?, positive_count = ?, negative_count = ?, neutral_count = ?, report_content = ?
                    WHERE id = ?;
                    """,
                    (total_emails, pos_count, neg_count, neu_count, report_markdown, report_id)
                )
            else:
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
        "unclassified_count": unclass_count,
        "negative_emails": negative_emails,
        "positive_emails": positive_emails,
        "neutral_emails": neutral_emails,
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
