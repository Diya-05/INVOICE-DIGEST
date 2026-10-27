"""
Personal Email Service for Invoice Digest
Handles fetching live invoice/billing emails via IMAP (e.g., Gmail)
and dispatching formatted daily digest reports via SMTP.
"""

from datetime import datetime, timezone
import email
from email.header import decode_header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import os
import smtplib
from typing import Any, Dict, List, Optional, Tuple
from src.database import DEFAULT_DB_PATH, get_db_connection, get_utc_now, insert_email
from src.preprocessing import clean_email_text, compute_content_hash


def _decode_header_str(header_val: Optional[str]) -> str:
    """Decodes MIME encoded header strings (e.g. =?utf-8?b?...?=)."""
    if not header_val:
        return ""
    decoded_fragments = decode_header(header_val)
    parts = []
    for text, encoding in decoded_fragments:
        if isinstance(text, bytes):
            try:
                parts.append(text.decode(encoding or "utf-8", errors="replace"))
            except Exception:
                parts.append(text.decode("latin1", errors="replace"))
        else:
            parts.append(str(text))
    return " ".join(parts).strip()


def _extract_body_from_message(msg: email.message.Message) -> str:
    """Extracts plain text content from MIME email parts."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in disposition:
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    break
                except Exception:
                    continue
        if not body:
            # Fallback to HTML part stripped of tags if plain text missing
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        body = payload.decode(charset, errors="replace")
                        break
                    except Exception:
                        continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="replace")
        except Exception:
            body = str(msg.get_payload())

    return body


def verify_email_credentials(
    email_address: str,
    app_password: str,
    imap_server: str = "imap.gmail.com"
) -> Tuple[bool, str]:
    """Tests IMAP authentication with the provided credentials."""
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address.strip(), app_password.strip())
        mail.logout()
        return True, "Authentication successful!"
    except Exception as e:
        return False, str(e)


def fetch_invoice_emails_from_inbox(
    email_address: str,
    app_password: str,
    imap_server: str = "imap.gmail.com",
    mailbox: str = "INBOX",
    search_keyword: str = "invoice",
    max_emails: int = 25,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Connects to IMAP inbox, queries emails matching keyword (invoice, bill, payment),
    extracts metadata, and ingests into SQLite with SHA-256 deduplication.
    """
    clean_email = email_address.strip()
    clean_pass = app_password.strip()

    fetched_count = 0
    imported_count = 0
    duplicate_count = 0
    imported_ids = []

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(clean_email, clean_pass)
        mail.select(mailbox)

        # Search query: search for keyword in SUBJECT or BODY
        # e.g., (OR (SUBJECT "invoice") (SUBJECT "payment"))
        status, messages = mail.search(None, f'(SUBJECT "{search_keyword}")')
        if status != "OK" or not messages[0]:
            # Try searching all recent emails if keyword filter returned empty
            status, messages = mail.search(None, "ALL")

        if status != "OK" or not messages[0]:
            mail.logout()
            return {
                "success": True,
                "message": "No matching emails found in mailbox.",
                "fetched": 0,
                "imported": 0,
                "duplicates": 0
            }

        msg_ids = messages[0].split()
        # Take the most recent N messages
        recent_ids = msg_ids[-max_emails:]
        recent_ids.reverse()  # Newest first

        for m_id in recent_ids:
            res_code, msg_data = mail.fetch(m_id, "(RFC822)")
            if res_code != "OK" or not msg_data:
                continue

            fetched_count += 1
            raw_msg = msg_data[0][1]
            msg = email.message_from_bytes(raw_msg)

            subject = _decode_header_str(msg.get("Subject", "(No Subject)"))
            sender = _decode_header_str(msg.get("From", "unknown@sender.com"))
            date_raw = msg.get("Date", "")
            
            try:
                parsed_date = email.utils.parsedate_to_datetime(date_raw)
                received_at = parsed_date.astimezone(timezone.utc).isoformat()
            except Exception:
                received_at = get_utc_now()

            raw_body = _extract_body_from_message(msg)
            cleaned_body = clean_email_text(raw_body)
            if not cleaned_body:
                cleaned_body = raw_body[:500] if raw_body else "(Empty body)"

            content_hash = compute_content_hash(subject, cleaned_body, sender)
            source_id = f"imap_{m_id.decode('utf-8', errors='ignore')}"

            new_id = insert_email(
                subject=subject,
                sender=sender,
                received_at=received_at,
                body_text=cleaned_body,
                content_hash=content_hash,
                source_id=source_id,
                db_path=db_path
            )

            if new_id is not None:
                imported_count += 1
                imported_ids.append(new_id)
            else:
                duplicate_count += 1

        mail.close()
        mail.logout()

        return {
            "success": True,
            "message": f"Fetched {fetched_count} emails. Imported {imported_count} new, {duplicate_count} already existed.",
            "fetched": fetched_count,
            "imported": imported_count,
            "duplicates": duplicate_count,
            "imported_ids": imported_ids
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fetched": fetched_count,
            "imported": imported_count,
            "duplicates": duplicate_count
        }


def send_daily_digest_email(
    recipient_email: str,
    sender_email: str,
    app_password: str,
    report_date: str,
    report_markdown: str,
    csv_content: Optional[str] = None,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    report_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """
    Sends the generated daily digest email formatted in HTML and Markdown,
    with an attached CSV, updating the daily_reports delivery status in SQLite.
    """
    try:
        msg = MIMEMultipart("mixed")
        msg["Subject"] = f"📊 Invoice Digest Daily Financial Summary — {report_date}"
        msg["From"] = sender_email.strip()
        msg["To"] = recipient_email.strip()

        # HTML and Plain Text formatting
        alt_container = MIMEMultipart("alternative")
        
        # Simple HTML convert
        html_body = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6; max-width: 680px; margin: 0 auto; padding: 20px;">
            <div style="background: #0f172a; color: #ffffff; padding: 18px 24px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0; color: #ffffff;">💼 Invoice Digest</h2>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 14px;">Daily Financial Sentiment & Risk Monitoring Report — {report_date}</p>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
                <div style="white-space: pre-wrap; font-size: 15px;">{report_markdown}</div>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
                <p style="font-size: 12px; color: #64748b; margin: 0;">Automated report generated by Invoice Digest MLIS Platform. Confidential financial document.</p>
            </div>
        </body>
        </html>
        """
        alt_container.attach(MIMEText(report_markdown, "plain"))
        alt_container.attach(MIMEText(html_body, "html"))
        msg.attach(alt_container)

        # Attach CSV if provided
        if csv_content:
            part = MIMEApplication(csv_content.encode("utf-8"), Name=f"invoice_digest_{report_date}.csv")
            part["Content-Disposition"] = f'attachment; filename="invoice_digest_{report_date}.csv"'
            msg.attach(part)

        # Send via SMTP
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
        server.login(sender_email.strip(), app_password.strip())
        server.sendmail(sender_email.strip(), [recipient_email.strip()], msg.as_string())
        server.quit()

        # Update report status in SQLite
        if report_id:
            with get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE daily_reports 
                    SET delivery_status = 'sent', sent_at = ?
                    WHERE id = ?;
                    """,
                    (get_utc_now(), report_id)
                )

        return True, f"Digest successfully sent to {recipient_email}!"

    except Exception as e:
        if report_id:
            with get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE daily_reports 
                    SET delivery_status = 'failed' 
                    WHERE id = ?;
                    """,
                    (report_id,)
                )
        return False, str(e)
