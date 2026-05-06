# Data Engineering Templates

Reference script templates for common data engineering tasks.
Copy a file into your project, fill in the TODO sections, and adapt as needed.

---

## Templates

| File | What it does | Key dependencies |
|---|---|---|
| `etl_pipeline.py` | Extract → validate → transform → load skeleton with structured logging and CLI entry-point | stdlib only (add your own IO libs) |
| `data_validation.py` | Schema, null-rate, uniqueness, range, and referential checks; returns a `ValidationReport`; raises on CRITICAL failures | `pandas` |
| `split_dedup.py` | Hash-based dedup + stratified train/val/test split + cross-split overlap assertion | `pandas`, `scikit-learn` |
| `schema_diff.py` | Diff two DataFrames or schema dicts; classifies changes as breaking vs non-breaking; CLI mode for CI checks | `pandas` |

---

## How to use

1. Copy the file into your project:
   ```
   cp templates/data-engineering/etl_pipeline.py src/pipelines/my_pipeline.py
   ```
2. Search for `# TODO` and fill in each section.
3. Run the smoke test in the file's docstring to verify your implementation.

---

## Design principles shared across all templates

- **Fail-fast validation** — quality checks run before any transform or load.
- **Idempotent loads** — write/overwrite, not append-by-default.
- **Structured logging** — every stage logs row counts and elapsed time.
- **Reproducible splits** — `random_state` is always fixed and explicit.
- **No silent data loss** — overlap checks and null checks raise, not warn, when the threshold is zero.

---

## What's NOT here (by design)

- Orchestration (Airflow, Prefect, Dagster DAGs) — too project-specific.
- Streaming / Kafka consumers — see `/streaming-pipeline` skill for design guidance.
- dbt models — see `/dbt-review` skill.
- Feature store writes — see `/feature-store-design` skill.
