"""
Preprocessing and Text Utilities for Invoice Digest
Provides canonical sentiment enums, text cleaning, email hashing,
and data normalization.
"""

from enum import Enum
import hashlib
import re
from typing import Dict, Optional, Tuple


class SentimentClass(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

    @classmethod
    def from_str(cls, val: str) -> "SentimentClass":
        clean_val = str(val).strip().lower()
        if clean_val in ("positive", "pos", "1"):
            return cls.POSITIVE
        elif clean_val in ("negative", "neg", "-1"):
            return cls.NEGATIVE
        elif clean_val in ("neutral", "neu", "0"):
            return cls.NEUTRAL
        raise ValueError(f"Unknown sentiment class: {val}")


CANONICAL_SENTIMENTS = [
    SentimentClass.POSITIVE.value,
    SentimentClass.NEGATIVE.value,
    SentimentClass.NEUTRAL.value,
]


def compute_content_hash(subject: str, body_text: str, sender: str = "") -> str:
    """Computes a SHA-256 hash for deduplication of incoming emails."""
    raw = f"{sender.strip().lower()}|{subject.strip().lower()}|{body_text.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def clean_email_text(text: str) -> str:
    """
    Cleans raw email text by removing signatures, disclaimer boilerplates,
    excessive whitespace, and quoted reply headers.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text

    # Remove standard email quote replies like "> ..."
    lines = cleaned.split("\n")
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        # Cut off signature markers and standard disclaimer starters
        if stripped in ("--", "___", "Best regards,", "Warm regards,", "Kind regards,"):
            break
        if stripped.lower().startswith("this email and any files transmitted with it are confidential"):
            break
        if stripped.startswith(">"):
            continue
        filtered_lines.append(line)

    cleaned = "\n".join(filtered_lines)

    # Normalize whitespace
    cleaned = re.sub(r"\r\n", "\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def prepare_email_for_model(subject: str, body: str, max_length: int = 1000) -> str:
    """
    Combines subject and cleaned body into a formatted prompt for classification.
    Subject is preserved with high priority.
    """
    cleaned_body = clean_email_text(body)
    cleaned_subj = (subject or "").strip()

    if cleaned_subj and cleaned_body:
        combined = f"Subject: {cleaned_subj}\nBody: {cleaned_body}"
    elif cleaned_subj:
        combined = f"Subject: {cleaned_subj}"
    else:
        combined = cleaned_body

    # Clip to reasonable character length before tokenization
    if len(combined) > max_length:
        combined = combined[:max_length] + "..."

    return combined
