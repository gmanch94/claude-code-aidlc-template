---
name: feature-store-design
description: Design a feature store for ML feature sharing and serving. Use when features are reused across models, real-time serving is needed, point-in-time correctness is required, or training-serving skew is a problem.
---

# Feature Store Design

## Role
You are a Feature Store Architect.

## Do you need a feature store?

Build one when ≥ 2 of these are true:
- Same features reused across ≥ 2 models
- Real-time feature serving required (< 100ms lookup)
- Point-in-time correctness required (time-travel joins)
- Training-serving skew is a current bug source
- Feature computation cost is high (aggregation over large tables)

Skip it when: single model, batch-only inference, features computed fresh at training time.

## Architecture decision

```
Serving latency requirement?
├── < 100ms (real-time inference)
│   → Online store (Redis / DynamoDB) + offline store (warehouse)
│   → Write path: feature pipeline → offline → sync to online
│   → Read path: inference service → online store
└── Minutes acceptable (batch inference)
    → Offline store only (warehouse table or Delta/Iceberg)
    → Read path: batch job reads offline store at scoring time
```

## Core components

| Component | Purpose | Tool options |
|---|---|---|
| Offline store | Historical features for training | Snowflake, BigQuery, Delta Lake, Parquet |
| Online store | Low-latency serving | Redis, DynamoDB, Bigtable |
| Feature registry | Metadata, ownership, versioning | Feast registry, Tecton, custom YAML |
| Transformation layer | Compute features from raw data | dbt, Spark, Flink, pandas |
| Serving API | Unified read interface | Feast SDK, Tecton SDK, custom FastAPI |

## Point-in-time correct joins (critical)

Training data must use only features available **before** the label timestamp.

```python
# Feast example — as-of join
feature_store.get_historical_features(
    entity_df=entity_df,  # entity_id + event_timestamp (label time)
    features=["user_stats:mean_spend_30d", "user_stats:login_count_7d"],
)
# Returns feature values as of event_timestamp, not current values
```

Never do a standard JOIN between features and labels — it will use future feature values.

## Feature definition standard

Each feature must have:
- `name`: globally unique, snake_case
- `entity`: what it describes (user_id, product_id, etc.)
- `source_table`: where raw data comes from
- `transformation`: SQL or code that computes it
- `owner`: team that maintains it
- `freshness_sla`: how stale is acceptable (e.g., 1 hour)
- `version`: semantic version; breaking changes → new version

## Backfill strategy

```
New feature added?
├── Historical data available    → Backfill from source; stamp with correct event_timestamp
├── No history (derived feature) → Compute from existing features or proxy; document gap
└── Real-time only               → Accept cold-start gap; document minimum lookback needed
```

## Training-serving skew prevention

1. Use the same transformation code for training and serving — no duplicated logic
2. Monitor: log feature values at inference time; compare distribution to training features monthly
3. Alert: KL divergence > threshold on any high-importance feature = skew detected

## Failure modes

- Joining features at current time for training: future leakage on time-series tasks — use point-in-time join
- Different transformation code in training vs. serving: silent skew that degrades model over time
- No feature versioning: upstream schema change silently breaks downstream models
- Online/offline sync lag ignored: online features are staler than offline — monitor sync lag

Pair with `/feature-engineering` for transformation design and `/leakage-audit` to verify no temporal leakage in training joins.
