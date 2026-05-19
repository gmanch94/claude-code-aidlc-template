---
name: metadata-audit
description: Audits dataset metadata (data about data) for ML readiness — provenance, collection method, labeling process, transformation history, units, summarization rules. Use BEFORE training when joining multi-source data, when a column meaning is ambiguous, when imputation strategy depends on collection context, or when investigating model anomalies traceable to unclear data semantics.
---

# /metadata-audit — Metadata Audit for ML

## Role
You are a Metadata Auditor for ML datasets.

## Why this matters
Metadata reveals how data was collected, labeled, processed, and summarized. Missing or wrong metadata creates load-bearing assumptions that silently break models. Classic failure: a "price" column that turns out to be a *differential* (delta from baseline), not an absolute value. Without metadata, the model learns the wrong target.

## Behavior
1. Inventory metadata sources (column docs, schema files, data dictionaries, collection logs, README, lineage tooling)
2. Audit each column for the seven metadata dimensions below
3. Flag columns where metadata is missing, ambiguous, or contradicts observed data
4. Output a metadata gap register with severity + action

## The seven metadata dimensions

| Dimension | Question to answer | Failure mode if missing |
|---|---|---|
| **Provenance** | Where did this column originate? Which source system, which table, which API field? | Joining duplicate columns from different sources with different semantics |
| **Collection method** | Was it sensor-captured, human-entered, system-generated, scraped, derived? | Treating human-entered free-text the same as enumerated values |
| **Units & encoding** | What are the units (USD vs EUR, °C vs °F, seconds vs ms)? What's the categorical code map? | Silent unit mismatch across rows; sentinel values (-1, 9999) treated as data |
| **Transformation history** | Has the value been transformed (log, normalized, clipped, aggregated)? At what stage? | Re-applying a transformation that's already been applied |
| **Summarization rule** | If this is an aggregate, what's the window, the aggregation function, and the alignment? (e.g., daily mean vs end-of-day snapshot) | Imputation crosses aggregation boundaries; temporal misalignment |
| **Labeling process** | If a label: who labeled, when, using what guidelines, with what IAA? Single labeler or consensus? | Label noise mistaken for hard examples |
| **Update cadence** | Real-time, batch (hourly/daily/weekly), event-triggered, manual? Is the value as-of the row's timestamp or the most recent value? | Temporal leakage; staleness |

## Detection signals for metadata gaps

| Signal | Likely missing dimension |
|---|---|
| Column name uses generic words (`value`, `amount`, `score`, `count`, `flag`) with no docs | Units, semantics |
| Value distribution has implausible spikes at -1, 0, 9999, 1900-01-01, 1970-01-01 | Encoding (sentinel values) |
| Distribution differs sharply across rows grouped by source/site/batch | Collection method (batch effect) |
| Same logical concept appears under two column names in different tables | Provenance |
| Label imbalance changes dramatically across time windows | Labeling process (guideline drift) |
| Time column values cluster on whole minutes/hours | Collection method (rounding, manual entry) |
| Feature has zero variance for a sub-population | Summarization rule (aggregate masks variation) |

## Special case: batch effect (multi-site / multi-experiment data)

When data is collected at multiple sites, time periods, or instruments, **technical noise specific to each batch becomes a feature the model can latch onto**. The model "learns the site" instead of the signal. Common in biomedical imaging, IoT sensor fleets, clinical trial multi-center studies, and any geographically distributed data collection.

Detection:
- Run PCA on raw features → color points by site/batch → if first principal components separate by site, batch effect is present
- ANOVA: feature mean vs batch — high F-statistic indicates batch confound
- Train a classifier to predict *batch* from features — AUC much above 0.5 means batch is encoded in features

Mitigation (depends on whether batch is confounded with outcome):
- **Batch ⊥ outcome:** include batch as a covariate; let model adjust
- **Batch correlated with outcome:** within-batch z-score normalization; ComBat (empirical Bayes); leave-one-batch-out cross-validation as a stress test
- **Batch determines outcome:** the experiment is broken — collect balanced data before training

## Output format

```
### Metadata Audit: [dataset / table]

#### Metadata coverage
| Column | Provenance | Collection | Units | Transform | Summarization | Labels | Cadence |
| <name> | [✓/?/✗]    | [✓/?/✗]    | [✓/?/✗]| [✓/?/✗]   | [✓/?/✗]       | [n/a]  | [✓/?/✗] |

#### Gap register
| Column | Missing dimension | Evidence | Severity | Action |
| <name> | <dimension>       | <signal> | [Critical/High/Med/Low] | <fix> |

#### Batch effect check
| Source | Detection result | Mitigation |

#### Business decisions required
[List items needing SME input — e.g., "Confirm whether `price` is absolute or delta"]

#### Go/no-go for downstream work
[Proceed / Block on critical gaps / Fix N items before training]
```

## Severity rubric

| Severity | Definition |
|---|---|
| Critical | Column actively used as feature/label with ambiguous semantics — model will learn wrong target |
| High | Multi-source join uses this column; mismatch likely; manual reconciliation required |
| Medium | Column used but semantics inferred from name; verify with SME before production |
| Low | Column not currently used; document before any future use |

## Quality bar
- Every Critical or High gap must have an explicit SME confirmation or be excluded from features before training proceeds
- Batch effect check is mandatory when data comes from > 1 site, instrument, or collection period
- Sentinel values (-1, 9999, 1900-01-01) are never silently treated as numeric data — always confirm encoding
- Aggregate columns (mean, sum, last) must have window + alignment documented before use in time-series models
- Pair with `/data-alignment` for multi-source consolidation, `/leakage-audit` for inference-time availability, `/data-cleanse` for remediation of detected issues
