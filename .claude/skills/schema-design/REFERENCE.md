# /schema-design — Reference

## SCD type comparison

| Type | Behavior | Storage | Current-record query | When to use |
|---|---|---|---|---|
| Type 0 | Never changes | Single row | Trivial | Static reference data (country codes, currencies) |
| Type 1 | Overwrite in place | Single row | Trivial | Corrections; history not needed |
| Type 2 | Add new row per change | Row per version + effective_from / effective_to | `WHERE is_current = true` | Full history needed (customer address, product price) |
| Type 3 | Add previous_value column | Current + previous columns | Direct | Only last change matters; rarely used |
| Type 4 | Separate history table | Current table + audit/history table | JOIN optional | High-churn attributes on large tables |

**Default: Type 2.** Choose another type only with an explicit reason documented in the schema contract.

## Common partitioning patterns

| Pattern | Partition key | When to use |
|---|---|---|
| Date-based | event_date, created_at::date | Most analytical tables — time-range queries dominate |
| Status-based | is_processed, status | One partition queried >> others; rarely optimal |
| Region / tenant | country_code, org_id | Multi-tenant or geo-filtered workloads |
| Hash range | user_id % N | Even distribution needed; no natural time key |

Default to date-based partitioning. Override only with a measured query pattern.

## Warehouse layer architecture

```
raw/        ← source data as-is; no transformations; immutable; owned by ingestion
staging/    ← cleaned, typed, deduplicated; source-shaped; no business logic
mart/       ← business-shaped; star schemas, aggregations, OBTs; BI-queryable
```

Rules:
- BI tools and analysts query mart/ only
- Staging owns deduplication and type casting — marts trust staging
- Raw is append-only — never update or delete from raw/

## Modeling anti-patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| Source natural key as DW PK | Keys change in source; orphaned FKs | Generate surrogate keys in staging |
| Nullable everywhere | Impossible to enforce quality | null = unknown only; add NOT NULL + DEFAULT where applicable |
| Logic in the final SELECT | Hard to test; unclear grain | All logic in CTEs; final SELECT is projection only |
| No partition key on large tables | Full scans on every query | Always partition by dominant filter column |
| Renaming columns without deprecation | Silently breaks downstream | Add new column → migrate consumers → drop old after deprecation period |
| SCD Type 2 without is_current flag | Slow "current record" queries | Always add is_current boolean + index on it |
