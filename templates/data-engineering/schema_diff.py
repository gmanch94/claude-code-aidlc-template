"""Schema diff template.

Copy this file and adapt as needed.
Compares two DataFrames (or two schema dicts) and reports:
  - Columns added in *new* vs *old*
  - Columns removed from *old*
  - Dtype changes
  - Nullable changes (columns that gained / lost nulls)

Use cases:
  - CI check: assert a pipeline output matches the expected schema
  - Migration guard: confirm a schema change is intentional before deploying
  - Data contract validation: compare producer schema vs consumer expectation

Usage:
    from schema_diff import diff_dataframes, diff_schemas, SchemaDiff

    # From two DataFrames:
    result = diff_dataframes(df_old, df_new)

    # From two schema dicts {col: dtype_str}:
    result = diff_schemas({"id": "int64", "name": "object"}, {"id": "int64", "age": "int64"})

    print(result.summary())
    result.assert_compatible()  # raises if breaking changes exist
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Change types
# ---------------------------------------------------------------------------

@dataclass
class ColumnAdded:
    column: str
    dtype: str

    def __str__(self) -> str:
        return f"ADDED    '{self.column}' ({self.dtype})"

    @property
    def is_breaking(self) -> bool:
        return False  # additions are backward-compatible


@dataclass
class ColumnRemoved:
    column: str
    dtype: str

    def __str__(self) -> str:
        return f"REMOVED  '{self.column}' ({self.dtype})"

    @property
    def is_breaking(self) -> bool:
        return True  # removals break consumers that expect the column


@dataclass
class DtypeChanged:
    column: str
    old_dtype: str
    new_dtype: str

    def __str__(self) -> str:
        return f"DTYPE    '{self.column}' {self.old_dtype} → {self.new_dtype}"

    @property
    def is_breaking(self) -> bool:
        return True  # type changes may break downstream casts


@dataclass
class NullabilityChanged:
    column: str
    was_nullable: bool
    is_nullable: bool

    def __str__(self) -> str:
        direction = "non-null → nullable" if self.is_nullable else "nullable → non-null"
        return f"NULLABLE '{self.column}' {direction}"

    @property
    def is_breaking(self) -> bool:
        # Gaining nulls is breaking for consumers that assume non-null.
        return self.is_nullable


Change = ColumnAdded | ColumnRemoved | DtypeChanged | NullabilityChanged


# ---------------------------------------------------------------------------
# Diff result
# ---------------------------------------------------------------------------

@dataclass
class SchemaDiff:
    changes: list[Change] = field(default_factory=list)

    @property
    def breaking_changes(self) -> list[Change]:
        return [c for c in self.changes if c.is_breaking]

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return "Schemas are identical — no changes detected."
        lines = [f"Schema diff: {len(self.changes)} change(s), {len(self.breaking_changes)} breaking:"]
        for change in self.changes:
            lines.append(f"  {change}")
        return "\n".join(lines)

    def assert_compatible(self) -> None:
        """Raise if any breaking changes exist."""
        breaking = self.breaking_changes
        if breaking:
            detail = "\n".join(f"  {c}" for c in breaking)
            raise AssertionError(
                f"{len(breaking)} breaking schema change(s):\n{detail}"
            )


# ---------------------------------------------------------------------------
# Core diff logic
# ---------------------------------------------------------------------------

Schema = dict[str, str]  # {column_name: dtype_string}


def diff_schemas(old: Schema, new: Schema) -> SchemaDiff:
    """Diff two schema dicts. Returns a SchemaDiff with all detected changes."""
    result = SchemaDiff()

    old_cols = set(old)
    new_cols = set(new)

    for col in sorted(old_cols - new_cols):
        result.changes.append(ColumnRemoved(col, old[col]))

    for col in sorted(new_cols - old_cols):
        result.changes.append(ColumnAdded(col, new[col]))

    for col in sorted(old_cols & new_cols):
        if old[col] != new[col]:
            result.changes.append(DtypeChanged(col, old[col], new[col]))

    log.info(result.summary())
    return result


def diff_dataframes(old: pd.DataFrame, new: pd.DataFrame) -> SchemaDiff:
    """Diff two DataFrames by schema and nullability."""
    result = SchemaDiff()

    old_schema = {col: str(dtype) for col, dtype in old.dtypes.items()}
    new_schema = {col: str(dtype) for col, dtype in new.dtypes.items()}

    old_cols = set(old_schema)
    new_cols = set(new_schema)

    for col in sorted(old_cols - new_cols):
        result.changes.append(ColumnRemoved(col, old_schema[col]))

    for col in sorted(new_cols - old_cols):
        result.changes.append(ColumnAdded(col, new_schema[col]))

    for col in sorted(old_cols & new_cols):
        if old_schema[col] != new_schema[col]:
            result.changes.append(DtypeChanged(col, old_schema[col], new_schema[col]))

        old_nullable = old[col].isna().any()
        new_nullable = new[col].isna().any()
        if old_nullable != new_nullable:
            result.changes.append(NullabilityChanged(col, bool(old_nullable), bool(new_nullable)))

    log.info(result.summary())
    return result


# ---------------------------------------------------------------------------
# CLI — compare two parquet / CSV files
# ---------------------------------------------------------------------------

def _load(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Compare schemas of two data files.")
    parser.add_argument("old", help="Path to old file (parquet or CSV)")
    parser.add_argument("new", help="Path to new file (parquet or CSV)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any breaking changes")
    args = parser.parse_args()

    diff = diff_dataframes(_load(args.old), _load(args.new))
    print(diff.summary())

    if args.strict and diff.breaking_changes:
        sys.exit(1)
