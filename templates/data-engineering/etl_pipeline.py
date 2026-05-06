"""ETL pipeline template.

Copy this file, rename it, and fill in every TODO section.
Pattern: extract → validate → transform → load.

Design decisions baked in:
- Idempotent: load step should overwrite, not append, unless you change it.
- Fail-fast validation: pipeline aborts before transform if data quality fails.
- Structured logging: every stage logs row counts and elapsed time.
- CLI entry-point: accepts --source and --destination so it can be scheduled.

TODO: add source/destination-specific imports below (pandas, boto3, psycopg2, etc.)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Any

# TODO: replace Any with your actual data type (pd.DataFrame, list[dict], etc.)
Data = Any

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Stages — implement each function; keep them pure where possible
# ---------------------------------------------------------------------------

def extract(source: str) -> Data:
    """Load raw data from *source*.

    TODO: implement.
    Examples: read a CSV, query a database, call an API, read from S3.
    Return the raw data unchanged — no business logic here.
    """
    raise NotImplementedError(f"extract({source!r}) not implemented")


def validate(data: Data) -> None:
    """Raise ValueError if *data* fails quality checks.

    TODO: implement.
    Check at minimum: expected columns present, row count > 0,
    no nulls in required fields, value ranges in bounds.
    Raise ValueError with a clear message on failure.
    """
    raise NotImplementedError("validate() not implemented")


def transform(data: Data) -> Data:
    """Apply business logic and return the processed dataset.

    TODO: implement.
    Keep this a pure function (no I/O). Chain smaller helpers here.
    """
    raise NotImplementedError("transform() not implemented")


def load(data: Data, destination: str) -> None:
    """Write *data* to *destination* idempotently.

    TODO: implement.
    Examples: write parquet to S3, upsert to Postgres, overwrite a BigQuery table.
    Idempotency rule: the same run twice must produce the same result.
    """
    raise NotImplementedError(f"load(..., {destination!r}) not implemented")


# ---------------------------------------------------------------------------
# Orchestration — wire the stages together
# ---------------------------------------------------------------------------

def run(source: str, destination: str) -> None:
    """Execute the full extract → validate → transform → load pipeline."""
    t0 = time.monotonic()

    log.info("EXTRACT  source=%s", source)
    raw = extract(source)

    log.info("VALIDATE")
    validate(raw)  # raises on failure

    log.info("TRANSFORM")
    result = transform(raw)

    log.info("LOAD  destination=%s", destination)
    load(result, destination)

    log.info("DONE  elapsed=%.1fs", time.monotonic() - t0)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", required=True, help="Input path, URI, or connection string")
    p.add_argument("--destination", required=True, help="Output path, URI, or table reference")
    # TODO: add pipeline-specific flags here (--date, --env, --dry-run, etc.)
    return p


if __name__ == "__main__":
    args = _build_parser().parse_args()
    run(args.source, args.destination)
