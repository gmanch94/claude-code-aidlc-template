---
name: data-versioning
description: Dataset versioning strategy — snapshot vs. pointer versioning, lineage tracking, DVC setup, data registration, reproducibility between training runs. Use when asked about "data versioning", "DVC", "dataset version", "reproducible training data", "which data was used to train this model?", or auditing what data produced a model.
---

# Data Versioning

## Role
You are a Dataset Versioning Specialist.

## Quick start

Every training run must be reproducible from a version-pinned dataset. "We trained on last month's data" is not a version.

## Versioning approaches

| Approach | When to use | Tool |
|---|---|---|
| File hash + path | Small datasets (< 1GB); files don't move | MD5/SHA256 in experiment tracker |
| Pointer versioning | Large datasets in cloud storage | DVC, Delta Lake, Iceberg |
| Snapshot versioning | Moderate size; immutable snapshots needed | DVC, S3 versioning |
| Table versioning | SQL warehouse; time-travel queries | Delta Lake, Snowflake time travel, BigQuery snapshots |

## DVC setup (file-based)

```bash
# Initialize
dvc init
git add .dvc .gitignore && git commit -m "init DVC"

# Track dataset
dvc add data/train.parquet
git add data/train.parquet.dvc data/.gitignore
git commit -m "add train dataset v1"
git tag dataset-v1

# Push data to remote storage
dvc remote add -d s3remote s3://my-bucket/dvc-store
dvc push
```

Reproduce a specific version:
```bash
git checkout dataset-v1
dvc pull         # fetches exact data version
```

## SQL warehouse versioning (Delta Lake / Snowflake)

```sql
-- Snapshot at training time (Delta Lake)
CREATE TABLE churn_train_v20250101
AS SELECT * FROM churn_features
WHERE event_date < '2025-01-01';

-- OR: use time travel for reproducibility
SELECT * FROM churn_features
TIMESTAMP AS OF '2025-01-01 00:00:00'
WHERE event_date < '2025-01-01';
```

Register dataset version in experiment tracker:
```python
mlflow.set_tags({
    "dataset_name":    "churn_train",
    "dataset_version": "v20250101",
    "dataset_path":    "s3://data-lake/churn/train/v20250101/",
    "dataset_hash":    sha256_of_file,
    "row_count":       len(df),
    "date_range":      f"{df.date.min()} / {df.date.max()}",
})
```

## Dataset registration schema

Every versioned dataset should have a registration record:

```yaml
# dataset-registry/churn_train_v20250101.yaml
name: churn_train
version: v20250101
created: 2025-01-02T08:00:00Z
owner: ml-platform-team

source:
  table: churn_features
  filter: "event_date < '2025-01-01'"
  warehouse: snowflake-prod

stats:
  row_count: 487_230
  positive_rate: 0.083
  date_range: "2024-01-01 / 2024-12-31"
  feature_count: 47

storage:
  path: s3://data-lake/churn/train/v20250101/
  format: parquet
  hash_sha256: abc123def456...

lineage:
  upstream_sources: [events_raw, user_profiles_v3, product_catalog_v8]
  transform_commit: git:abc1234   # commit of feature engineering code

used_in_runs: []  # populated when a training run uses this version
```

## Lineage tracking

Link dataset version → training run → model version:

```
churn_train_v20250101
    └── MLflow run: abc123def
            └── Model registry: churn-classifier v2.1.0
                    └── Deployment: prod-2026-04-21
```

Implement as tags in the experiment tracker (see `/experiment-tracking`):
- Run tags: `dataset_version`, `dataset_path`, `dataset_hash`
- Model registry tags: `training_run_id`, `dataset_version`

## Reproducibility checklist

A training run is data-reproducible when:
- [ ] Dataset version tag recorded in experiment run
- [ ] Dataset path + hash stored (hash verifies no silent mutation)
- [ ] Feature engineering code pinned to git commit
- [ ] Upstream data sources versioned or time-travel query recorded
- [ ] Label definition documented (what event, what lag, what cutoff date)

## Rules

- Never train on a mutable table without a time-travel snapshot or explicit hash. Live tables change; your training run doesn't record what changed.
- `dataset_hash` is the source of truth for reproducibility — path alone is not enough (file may be overwritten).
- Datasets used in production model training are subject to the same retention policy as the model artifact (3 years minimum for regulated industries).
- Don't version evaluation/test sets separately from train — version the full split together with the split seed.
