"""Data validation template.

Copy this file and fill in every TODO section.
Returns a structured ValidationReport; raises on CRITICAL failures.

Checks provided out of the box (add/remove as needed):
  - Schema: required columns present, dtypes match expected
  - Completeness: null rate per column within threshold
  - Uniqueness: specified columns have no duplicates
  - Range: numeric columns within [min, max]
  - Referential: values in a column belong to an allowed set

Usage:
    from data_validation import validate, ValidationReport
    report = validate(df)          # raises on CRITICAL
    print(report.summary())        # human-readable
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config — fill in your expected schema and thresholds
# ---------------------------------------------------------------------------

# TODO: list every column the pipeline requires and its expected dtype.
# Use pandas dtype strings: "int64", "float64", "object", "bool", "datetime64[ns]"
REQUIRED_COLUMNS: dict[str, str] = {
    # "user_id": "int64",
    # "event_ts": "datetime64[ns]",
    # "amount": "float64",
}

# TODO: maximum fraction of nulls allowed per column (0.0 = no nulls allowed).
NULL_THRESHOLDS: dict[str, float] = {
    # "user_id": 0.0,
    # "amount": 0.05,   # up to 5% nulls OK
}

# TODO: columns whose combination must be unique (list of column-name lists).
UNIQUE_KEYS: list[list[str]] = [
    # ["user_id", "event_ts"],
]

# TODO: numeric range bounds per column.  Both limits are inclusive.
RANGE_CHECKS: dict[str, tuple[float, float]] = {
    # "amount": (0.0, 1_000_000.0),
    # "score": (0.0, 1.0),
}

# TODO: allowed value sets per column.
ALLOWED_VALUES: dict[str, set[Any]] = {
    # "status": {"active", "inactive", "pending"},
}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    severity: str   # "CRITICAL" | "WARNING"
    check: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.severity}] {self.check}: {self.detail}"


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, severity: str, check: str, detail: str) -> None:
        self.issues.append(ValidationIssue(severity, check, detail))
        log.warning("%s — %s: %s", severity, check, detail)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "CRITICAL")

    def summary(self) -> str:
        if not self.issues:
            return "Validation passed — no issues found."
        lines = [f"Validation found {len(self.issues)} issue(s):"]
        lines += [f"  {issue}" for issue in self.issues]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _check_schema(df: pd.DataFrame, report: ValidationReport) -> None:
    for col, expected_dtype in REQUIRED_COLUMNS.items():
        if col not in df.columns:
            report.add("CRITICAL", "schema.missing_column", f"'{col}' not found")
        elif not str(df[col].dtype).startswith(expected_dtype.split("[")[0]):
            report.add(
                "WARNING",
                "schema.dtype_mismatch",
                f"'{col}' expected {expected_dtype}, got {df[col].dtype}",
            )


def _check_nulls(df: pd.DataFrame, report: ValidationReport) -> None:
    for col, threshold in NULL_THRESHOLDS.items():
        if col not in df.columns:
            continue
        null_rate = df[col].isna().mean()
        if null_rate > threshold:
            severity = "CRITICAL" if threshold == 0.0 else "WARNING"
            report.add(
                severity,
                "completeness.null_rate",
                f"'{col}' null rate {null_rate:.1%} exceeds threshold {threshold:.1%}",
            )


def _check_uniqueness(df: pd.DataFrame, report: ValidationReport) -> None:
    for key_cols in UNIQUE_KEYS:
        missing = [c for c in key_cols if c not in df.columns]
        if missing:
            report.add("CRITICAL", "uniqueness.missing_column", f"Key columns not found: {missing}")
            continue
        n_dupes = df.duplicated(subset=key_cols).sum()
        if n_dupes > 0:
            report.add(
                "CRITICAL",
                "uniqueness.duplicates",
                f"{n_dupes} duplicate row(s) on key {key_cols}",
            )


def _check_ranges(df: pd.DataFrame, report: ValidationReport) -> None:
    for col, (lo, hi) in RANGE_CHECKS.items():
        if col not in df.columns:
            continue
        out_of_range = ((df[col] < lo) | (df[col] > hi)).sum()
        if out_of_range > 0:
            report.add(
                "WARNING",
                "range.out_of_bounds",
                f"'{col}' has {out_of_range} value(s) outside [{lo}, {hi}]",
            )


def _check_allowed_values(df: pd.DataFrame, report: ValidationReport) -> None:
    for col, allowed in ALLOWED_VALUES.items():
        if col not in df.columns:
            continue
        unexpected = set(df[col].dropna().unique()) - allowed
        if unexpected:
            report.add(
                "WARNING",
                "referential.unexpected_values",
                f"'{col}' contains unexpected value(s): {sorted(unexpected)[:10]}",
            )


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

def validate(df: pd.DataFrame) -> ValidationReport:
    """Run all checks. Raises ValueError if any CRITICAL issues are found."""
    report = ValidationReport()

    log.info("Validating DataFrame: %d rows × %d cols", len(df), len(df.columns))

    _check_schema(df, report)
    _check_nulls(df, report)
    _check_uniqueness(df, report)
    _check_ranges(df, report)
    _check_allowed_values(df, report)

    log.info(report.summary())

    if report.critical_count > 0:
        raise ValueError(
            f"Validation failed with {report.critical_count} CRITICAL issue(s).\n"
            + report.summary()
        )

    return report
