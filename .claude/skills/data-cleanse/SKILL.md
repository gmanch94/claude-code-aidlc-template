---
name: data-cleanse
description: Designs a systematic data cleansing workflow — dirty data taxonomy, detection rules, remediation strategy per issue type, and auditability. Use when asked to clean a dataset, identify data quality issues, standardize formats, or handle nulls/outliers/encoding problems in a pipeline.
---

# /data-cleanse — Data Cleansing Design

## Role
You are a Data Cleansing Planner.

## Behavior
1. Inventory dirty data categories present (or likely) in the dataset
2. Define detection rules per category
3. Specify remediation strategy with auditability
4. Flag decisions that require business input
5. Output cleansing spec ready to implement

## Dirty data taxonomy

| Category | Examples | Detection |
|---|---|---|
| Missing values | NULL, empty string, "N/A", "unknown", "0" used as null | IS NULL, `= ''`, `IN ('n/a','none','null','unknown')` |
| Duplicates | Exact or near-duplicate rows | COUNT(DISTINCT key) vs COUNT(*); see `/dedup` for fuzzy |
| Format inconsistency | Dates as `MM/DD/YYYY` and `YYYY-MM-DD` mixed; phones with/without country code | Regex pattern audit; length distribution |
| Type mismatch | Numeric stored as string; boolean as 0/1 vs. true/false | Schema inspection + CAST failure rate |
| Case inconsistency | `ACME CORP`, `Acme Corp`, `acme corp` for same entity | `LOWER()` grouping; frequency distribution |
| Whitespace / encoding | Leading/trailing spaces; non-breaking spaces; UTF-8 / Latin-1 mix | `TRIM()` != original; `CHARINDEX(CHAR(160), col)` |
| Outliers | Age = 999; amount = -1; date = 1900-01-01 | Z-score > 3; range violations; sentinel value audit |
| Referential integrity | FK values with no matching PK in parent table | LEFT JOIN + IS NULL check |
| Domain violation | Status = 'ACTVE'; country code = 'ZZ' | NOT IN (valid_values); regex; lookup join |
| Batch effect | Site/instrument/period-specific noise; same logical feature distributes differently across sources | PCA colored by source; per-source KS test; classifier `predict(source) ~ features` AUC > 0.7 |
| Sparse classes | Categorical values with very few observations (e.g., country code present 3 times in 1M rows) | Frequency histogram per categorical column; tail mass below threshold |
| Metadata-flagged anomaly | Column semantics revealed by metadata don't match observed distribution (e.g., "price" is actually a delta; sentinel -1 means "not measured") | Cross-check metadata docs against value distribution; pair with `/metadata-audit` |

## Remediation rules per category

| Category | Strategy options | Auditability requirement |
|---|---|---|
| Missing values | Impute (mean/mode/forward-fill) / flag + exclude / reject | Log imputation rule + count per column |
| Duplicates | Deduplicate (keep first/last/highest-confidence) | Log duplicate count + chosen record rationale |
| Format inconsistency | Standardize to canonical format (ISO 8601 for dates, E.164 for phones) | Log input → output mapping |
| Type mismatch | CAST with SAFE_CAST / TRY_CAST; log failures | Log cast failure count + sample failures |
| Case inconsistency | UPPER() / LOWER() / INITCAP() — document chosen standard | Document standard; apply uniformly |
| Whitespace / encoding | TRIM() + REGEXP_REPLACE for non-printable; re-encode to UTF-8 | Log rows modified |
| Outliers | Cap (winsorize) / exclude / flag for review — never silently drop | Log outlier count + threshold used |
| Referential integrity | Exclude orphaned rows / route to quarantine | Log orphan count + FK column |
| Domain violation | Reject invalid values → quarantine; never coerce silently | Log violation count + sample values |
| Batch effect | Within-source z-score or robust scaling; ComBat (empirical Bayes) for biomedical; include source as covariate; if source confounded with outcome, **stop** and rebalance collection | Log per-source statistics pre/post; preserve source tag column |
| Sparse classes | Group into "Other" via frequency cutoff; collapse via domain hierarchy; target-rate binning (see `/sparse-class-grouping`) | Log original → grouped mapping; fit only on training fold |
| Metadata-flagged anomaly | Confirm with SME, then re-interpret column / rebuild feature / exclude — never silently fix | Document the corrected semantics in data dictionary |

## Output format

```
### Cleansing Spec: [table / dataset]

#### Dirty data inventory
| Category | Column(s) | Detection rule | Estimated prevalence |

#### Remediation plan
| Category | Column(s) | Strategy | Audit log |

#### Business decisions required
[List rules that require domain input — e.g., "What is the valid range for amount_usd?"]

#### Cleansing order
1. Schema / type fixes (before any other checks)
2. Encoding / whitespace (before string comparisons)
3. Null handling
4. Domain + referential integrity
5. Format standardization
6. Outlier handling
7. Deduplication (last — after all other fixes applied)
```

## Quality bar
- Never silently drop records — every exclusion needs an audit trail and a count
- Outlier removal requires a documented threshold and business sign-off
- Deduplication is always last — deduplicate clean data, not dirty data
- Batch effect remediation must be applied within-fold (fit on train only); fitting global stats leaks test info
- Metadata-flagged anomalies require SME confirmation before remediation — never silently re-interpret a column
- Pair with `/data-quality` for ongoing validation rules, `/dedup` for fuzzy deduplication, `/metadata-audit` for column semantics, `/sparse-class-grouping` for low-frequency category handling
