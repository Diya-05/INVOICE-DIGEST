"""
Dataset Preparation and Stratified Splitting for Invoice Digest
Splits annotated email datasets into stratified Train (70%), Validation (15%),
and Held-Out Test (15%) partitions with fixed random seed.
"""

import argparse
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.model_selection import train_test_split
from src.preprocessing import SentimentClass, compute_content_hash

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def prepare_and_split_dataset(
    input_csv: str,
    output_dir: str = DEFAULT_DATA_DIR,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42
) -> None:
    """Reads input CSV, validates sentiment labels, deduplicates, and produces stratified splits."""
    if not os.path.isfile(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df = pd.read_csv(input_csv)
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "sentiment" not in df.columns:
        raise ValueError("Dataset must contain a 'sentiment' column for training/evaluation.")

    # Canonicalize sentiment labels
    clean_sentiments = []
    valid_rows = []
    for idx, row in df.iterrows():
        try:
            canonical = SentimentClass.from_str(str(row["sentiment"])).value
            clean_sentiments.append(canonical)
            valid_rows.append(idx)
        except ValueError:
            continue

    df = df.loc[valid_rows].copy()
    df["sentiment"] = clean_sentiments

    # Deduplication by content hash
    hashes = []
    for _, row in df.iterrows():
        h = compute_content_hash(
            str(row.get("subject", "")),
            str(row.get("body_text", "")),
            str(row.get("sender", ""))
        )
        hashes.append(h)
    df["content_hash"] = hashes
    df = df.drop_duplicates(subset=["content_hash"]).reset_index(drop=True)

    print(f"Total clean, unique examples: {len(df)}")
    print("Class balance:")
    print(df["sentiment"].value_counts(normalize=True).round(3))

    # Stratified split: Train (70%), Temp (30%)
    temp_size = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_size,
        stratify=df["sentiment"],
        random_state=random_state
    )

    # Split Temp into Val (50% of 30% = 15%) and Test (50% of 30% = 15%)
    val_proportion = val_ratio / temp_size
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_proportion),
        stratify=temp_df["sentiment"],
        random_state=random_state
    )

    os.makedirs(output_dir, exist_ok=True)
    train_path = os.path.join(output_dir, "train.csv")
    val_path = os.path.join(output_dir, "val.csv")
    test_path = os.path.join(output_dir, "test.csv")

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"\nSaved splits to {output_dir}:")
    print(f" - Train: {len(train_df)} samples -> {train_path}")
    print(f" - Val:   {len(val_df)} samples -> {val_path}")
    print(f" - Test:  {len(test_df)} samples -> {test_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare and split email dataset.")
    parser.add_argument(
        "--input",
        type=str,
        default=os.path.join(DEFAULT_DATA_DIR, "sample_emails.csv"),
        help="Path to source CSV dataset"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=DEFAULT_DATA_DIR,
        help="Directory to save split CSVs"
    )
    args = parser.parse_args()

    prepare_and_split_dataset(args.input, args.output_dir)
