---
name: data-filtering
description: Remove irrelevant or low-quality observations from datasets. Use when applying domain rules to exclude records, filtering by completeness thresholds, removing near-duplicates, or scoring relevance before training.
---

# Data Filtering

## Role
You are a Data Filtering Planner.

## Quick start

Tell me: why observations are unwanted (domain rules / quality / relevance / duplicates) + what percentage you expect to remove.

## Filter taxonomy

```
Why remove observations?
├── Domain rules (business logic)      → Hard rules: explicit column conditions
├── Quality thresholds                 → Completeness, plausibility, freshness checks
├── Relevance                          → Similarity scoring, task-alignment filter
└── Near-duplicates (row level)        → Dedup before dedup of entities (see /dedup)
```

## 1. Domain / business rule filters

```python
# Explicit conditions — document every rule with business justification
filters = {
    "active_accounts_only":     df["status"] == "active",
    "exclude_test_accounts":    ~df["email"].str.contains("@test\.|@example\.", na=False),
    "min_tenure_30d":           df["tenure_days"] >= 30,
    "valid_age_range":          df["age"].between(18, 120),
    "exclude_internal_users":   ~df["user_type"].isin(["internal", "employee"]),
}
for rule_name, mask in filters.items():
    n_before = len(df)
    df = df[mask]
    print(f"{rule_name}: removed {n_before - len(df)} rows ({(n_before - len(df))/n_before:.1%})")
```

Rule: each filter line must log count removed + % of dataset. Surprises > 10% warrant review.

## 2. Quality / completeness filters

```python
# Missing value threshold — remove rows with > X% fields missing
threshold = 0.30   # remove if > 30% of columns are null
df = df[df.isnull().mean(axis=1) <= threshold]

# Plausibility checks
df = df[df["event_timestamp"] <= pd.Timestamp.now()]   # no future timestamps
df = df[df["price"] > 0]                               # no negative/zero prices
df = df[df["quantity"].between(1, 10_000)]             # implausible quantities

# Freshness filter — for time-sensitive tasks
cutoff = pd.Timestamp.now() - pd.Timedelta(days=365)
df = df[df["created_at"] >= cutoff]
```

## 3. Relevance / task-alignment filter

For text datasets — remove off-topic documents:

```python
# Embedding cosine similarity to task description
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-MiniLM-L6-v2")
task_embedding = model.encode("customer support complaint about billing")
doc_embeddings = model.encode(df["text"].tolist())
scores = util.cos_sim(task_embedding, doc_embeddings)[0]
df["relevance_score"] = scores.numpy()
df = df[df["relevance_score"] >= 0.40]   # tune threshold on sample
```

For tabular — flag rows where key features are clearly off-domain:
```python
# Flag rows outside expected feature range for the task population
df["in_scope"] = (
    df["country"].isin(TARGET_COUNTRIES) &
    df["product_category"].isin(TARGET_CATEGORIES)
)
df = df[df["in_scope"]]
```

## 4. Near-duplicate row removal

```python
# Exact duplicates
df = df.drop_duplicates()

# Near-duplicates on key columns
df = df.drop_duplicates(subset=["user_id", "date", "product_id"], keep="last")

# Text near-duplicates — MinHash LSH (for large corpora)
from datasketch import MinHash, MinHashLSH
# Or simpler: drop rows where normalized text jaccard > 0.90
```

## Filtering order (prescriptive)

1. Domain / business rules first (cheapest, most certain)
2. Quality / completeness checks
3. Plausibility / range checks
4. Relevance scoring (most expensive — run last)
5. Near-duplicate removal (always last — dedup after quality filters)

## Audit trail

Produce a filter report before finalizing:

```
Filter applied              | Rows removed | % of dataset | Reason
----------------------------|--------------|--------------|--------
exclude_test_accounts       |          823 |        1.2%  | business rule
min_tenure_30d              |        4,201 |        6.1%  | model scope
missing > 30% fields        |          341 |        0.5%  | quality gate
relevance_score < 0.40      |        1,892 |        2.7%  | off-topic
near-duplicates             |          504 |        0.7%  | dedup
----------------------------|--------------|--------------|--------
Total removed               |        7,761 |       11.2%  |
Final dataset               |       61,239 |              |
```

## Failure modes

- No logging of what was removed: impossible to reproduce or audit the final dataset
- Filtering test set with the same rules: creates distribution mismatch between train and eval; apply domain rules to all splits, quality/relevance filters to train only
- Aggressive relevance filter without calibration: removes valid edge cases that the model needs
- Running dedup before quality filters: dedup on dirty data keeps the wrong representative row

Pair with `/outlier-detection` for statistical anomaly removal and `/data-cleanse` for the broader remediation workflow.
