"""Train / validation / test split with deduplication template.

Copy this file and fill in every TODO section.

What this script does:
  1. Load the full dataset.
  2. Deduplicate rows by a content hash (or explicit key columns).
  3. Split into train / val / test with no overlap between splits.
  4. Assert zero cross-split overlap before saving.
  5. Write each split to its own file.

Design decisions baked in:
  - Hash-based dedup: no dependency on row order or index.
  - Stratified split: preserves class distribution (set STRATIFY_COL = None to disable).
  - Overlap check: raises if any row appears in more than one split.
  - Reproducible: RANDOM_STATE is fixed.

TODO: install scikit-learn if not already present (for train_test_split).
"""

from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

log = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s — %(message)s", level=logging.INFO, stream=sys.stdout)


# ---------------------------------------------------------------------------
# Config — fill in before running
# ---------------------------------------------------------------------------

# TODO: path to your input dataset.
INPUT_PATH = Path("data/raw/dataset.parquet")

# TODO: output directory — each split written as <OUTPUT_DIR>/<split>.parquet
OUTPUT_DIR = Path("data/splits")

# TODO: column(s) to use as the dedup key.
# Set to [] to hash all columns (full-row dedup).
DEDUP_KEY_COLS: list[str] = []

# TODO: column to stratify splits on (e.g. label column).
# Set to None to disable stratification.
STRATIFY_COL: str | None = None

# TODO: fraction of data in val and test splits respectively.
# Train gets the remainder: 1 - VAL_FRAC - TEST_FRAC.
VAL_FRAC: float = 0.10
TEST_FRAC: float = 0.10

RANDOM_STATE: int = 42


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def load(path: Path) -> pd.DataFrame:
    """TODO: adapt the reader to your file format."""
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in (".jsonl", ".ndjson"):
        return pd.read_json(path, lines=True)
    raise ValueError(f"Unsupported format: {suffix!r}. Add a reader branch.")


def deduplicate(df: pd.DataFrame, key_cols: list[str]) -> pd.DataFrame:
    """Remove duplicate rows based on *key_cols* (or full-row hash if empty)."""
    if key_cols:
        before = len(df)
        df = df.drop_duplicates(subset=key_cols)
        log.info("Dedup on %s: %d → %d rows (removed %d)", key_cols, before, len(df), before - len(df))
    else:
        # Hash all columns for full-row dedup.
        row_hash = df.apply(
            lambda row: hashlib.md5(str(row.values.tobytes()).encode()).hexdigest(),  # nosec
            axis=1,
        )
        before = len(df)
        df = df[~row_hash.duplicated()]
        log.info("Full-row dedup: %d → %d rows (removed %d)", before, len(df), before - len(df))
    return df.reset_index(drop=True)


def split(
    df: pd.DataFrame,
    val_frac: float,
    test_frac: float,
    stratify_col: str | None,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (train, val, test) DataFrames with no overlap."""
    stratify = df[stratify_col] if stratify_col else None

    # Split off test first, then split remainder into train/val.
    train_val, test = train_test_split(
        df,
        test_size=test_frac,
        stratify=stratify,
        random_state=random_state,
    )

    val_frac_adjusted = val_frac / (1.0 - test_frac)
    stratify_tv = train_val[stratify_col] if stratify_col else None
    train, val = train_test_split(
        train_val,
        test_size=val_frac_adjusted,
        stratify=stratify_tv,
        random_state=random_state,
    )

    return train, val, test


def assert_no_overlap(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    key_cols: list[str],
) -> None:
    """Raise if any row appears in more than one split."""
    cols = key_cols if key_cols else list(train.columns)

    def _key_set(df: pd.DataFrame) -> set[tuple]:
        return set(map(tuple, df[cols].values.tolist()))

    train_keys = _key_set(train)
    val_keys = _key_set(val)
    test_keys = _key_set(test)

    tv_overlap = train_keys & val_keys
    tt_overlap = train_keys & test_keys
    vt_overlap = val_keys & test_keys

    errors: list[str] = []
    if tv_overlap:
        errors.append(f"train ∩ val: {len(tv_overlap)} row(s)")
    if tt_overlap:
        errors.append(f"train ∩ test: {len(tt_overlap)} row(s)")
    if vt_overlap:
        errors.append(f"val ∩ test: {len(vt_overlap)} row(s)")

    if errors:
        raise AssertionError("Cross-split overlap detected: " + "; ".join(errors))

    log.info("Overlap check passed — splits are disjoint.")


def save(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame, output_dir: Path) -> None:
    """TODO: adapt the writer to your target format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in [("train", train), ("val", val), ("test", test)]:
        out = output_dir / f"{name}.parquet"
        df.to_parquet(out, index=False)
        log.info("Saved %s: %d rows → %s", name, len(df), out)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run() -> None:
    log.info("Loading %s", INPUT_PATH)
    df = load(INPUT_PATH)
    log.info("Loaded %d rows × %d cols", len(df), len(df.columns))

    df = deduplicate(df, DEDUP_KEY_COLS)

    train, val, test = split(df, VAL_FRAC, TEST_FRAC, STRATIFY_COL, RANDOM_STATE)
    log.info("Split sizes — train: %d, val: %d, test: %d", len(train), len(val), len(test))

    assert_no_overlap(train, val, test, DEDUP_KEY_COLS)

    save(train, val, test, OUTPUT_DIR)
    log.info("Done.")


if __name__ == "__main__":
    run()
