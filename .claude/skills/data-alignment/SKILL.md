---
name: data-alignment
description: Designs multi-source data alignment — instance-level matching, timestamp synchronization, scale/encoding harmonization, batch effect mitigation. Use when consolidating data from multiple sources (sensors, sites, vendors, platforms) into a unified ML training matrix. Distinct from `/schema-harmonization` which resolves schema-level conflicts; this skill resolves *row-level* alignment.
---

# /data-alignment — Multi-Source Data Alignment

## Role
You are a Data Alignment Architect.

## Behavior
1. Identify the alignment topology (how sources relate: by entity, by time, by both)
2. Resolve unique-identifier strategy for entity matching
3. Specify timestamp alignment strategy when exact times don't match
4. Harmonize scales and encodings across sources
5. Detect and mitigate batch effect when sources are collection-correlated
6. Output an alignment spec with one row per consolidated instance

## Alignment topology — pick the shape first

| Topology | Sources differ by | Example | Primary challenge |
|---|---|---|---|
| **Column-wise (horizontal)** | Features per entity (same entities, different attributes) | CRM + billing + support tickets per customer | Entity ID resolution |
| **Row-wise (vertical / stacked)** | Same features, different entities | Branch A sales + Branch B sales | Feature/unit consistency |
| **Time-aligned** | Time-stamped events per entity from different streams | Sensor stream + maintenance log | Timestamp sync |
| **Hybrid** | Multiple of the above | Multi-site clinical trial with labs + imaging + EHR | All three, in order |

Apply alignment in this order: **entity → time → features → batch effect**.

## Step 1 — Entity matching (unique identifier resolution)

| Situation | Strategy |
|---|---|
| Shared canonical ID (customer_id, patient_id) across sources | Direct join; verify no orphans on either side |
| Different IDs per source, mapping table exists | Map first, then join; audit unmapped rows |
| No ID, but shared natural key (email, phone, MRN) | Normalize key (lowercase, strip whitespace, E.164 for phones), then join; expect ~5–15% miss |
| No reliable key | Fuzzy match via `/dedup` skill (name + DOB + zip); accept uncertainty + manual review tier |

Always log: rows joined, rows orphaned per source, match rate. Orphan rate > 10% is a quality red flag.

## Step 2 — Timestamp alignment

When events from different sources don't share exact timestamps:

| Pattern | Strategy | Watch out for |
|---|---|---|
| **As-of join** (point-in-time) | For each row in primary stream, attach most-recent value from secondary stream prior to primary timestamp | Look-back window must be bounded; otherwise stale data |
| **Window aggregation** | Aggregate secondary stream over a window (e.g., 5-min avg) aligned to primary | Window edge effects; pick alignment (centered/lagged) deliberately |
| **Resampling to common cadence** | Up/downsample both streams to a shared grid (1-min, 1-hour); see `/timeseries-resample` | Up-sampling fabricates data — never up-sample the target |
| **Event-to-event with tolerance** | Match events within ±N seconds | Many-to-many matches; pick deterministic rule (nearest, first, last) |
| **Manual alignment with SME** | Domain expert provides mapping (rare; for one-off historical data) | Document the mapping; not reproducible without docs |

**Hard rule:** never align using future data. The look-back window may extend backward in time only.

## Step 3 — Scale and encoding harmonization

When the same logical feature uses different scales across sources:

| Mismatch | Resolution |
|---|---|
| Different units (km vs miles, USD vs local currency, °C vs °F) | Convert to canonical unit; document conversion factor + asof-date for currency |
| Different rating scales (1–5 vs 1–10 vs A–F) | Pick canonical scale; map via linear or rank-based transform; document mapping |
| Different category vocabularies (region codes, ICD-9 vs ICD-10) | Build crosswalk table; flag many-to-one collapses; SME sign-off on lossy mappings |
| Different precision (timestamps to second vs millisecond; coordinates to 4 vs 6 decimals) | Down-sample to coarsest precision; do not up-sample (fake precision) |
| Different missing-value sentinels (NULL, -1, 999, "N/A") | Normalize to single sentinel (NULL or NaN); see `/data-cleanse` |
| Different text encodings (UTF-8, Latin-1, GB18030) | Re-encode to UTF-8; log re-encoding failures |

## Step 4 — Batch effect detection and mitigation

Batch effect = technical noise specific to a source / site / instrument / time period that varies between batches but is consistent within. Model learns the batch instead of the signal.

Detection (run BEFORE feature engineering):
- PCA on raw features → color by source → first PCs separate by source ⇒ batch effect present
- Classifier `predict(source) ~ features` — AUC > 0.7 ⇒ source is encoded in features
- Compare per-feature distributions across sources — KS test p < 0.01 with effect size > 0.1 ⇒ shifted

Mitigation by scenario:

| Scenario | Mitigation |
|---|---|
| Source ⊥ outcome (balanced) | Include source as a covariate; tree models adjust naturally |
| Source partially correlated with outcome | Within-source z-score / robust scaling; ComBat (empirical Bayes); leave-one-source-out CV as a stress test |
| Source determines outcome (e.g., all positives from one site) | **Stop.** The experiment is confounded; collect balanced data or drop the source from features |
| Imaging / sequencing data | Domain-standard pipelines (ComBat-Seq for RNA, harmonization networks for MRI); never roll your own |

## Output format

```
### Data Alignment Spec: [project / dataset]

#### Sources
| Source | Rows | Key fields | Cadence | Notes |

#### Topology
[Column-wise / Row-wise / Time-aligned / Hybrid]

#### Entity matching
- Strategy: [shared ID / mapping table / natural key / fuzzy]
- Join key(s):
- Expected match rate: __% | Orphan handling: [exclude / quarantine / impute]

#### Timestamp alignment (if time-aligned)
- Strategy: [as-of / window agg / resample / event-to-event]
- Look-back window: [N seconds/minutes/hours]
- Tie-breaking rule: [nearest / first / last]

#### Scale & encoding harmonization
| Feature | Source A format | Source B format | Canonical | Conversion rule |

#### Batch effect
- Detection result: [present / not detected]
- Severity: [confounded / partial / clean]
- Mitigation: [strategy]

#### Audit trail requirements
- Per-row source tag preserved as a column
- Join statistics logged (matched / orphan / fuzzy)
- Unit conversion factors versioned

#### Go/no-go for training
[Proceed / Fix N items / Discard source X]
```

## Quality bar
- Always log orphan rates per source — silent drops are the most common data alignment bug
- Look-back windows must be bounded — unbounded as-of joins create temporal leakage; pair with `/leakage-audit`
- Up-sampling the *target* is forbidden — fabricates labels
- Batch-effect check is mandatory whenever sources differ by site, instrument, or collection period
- Currency conversion factors and ICD/region crosswalks must be versioned — they change over time and silent updates break reproducibility
- Pair with `/schema-harmonization` for schema-level conflicts, `/metadata-audit` for unit and provenance docs, `/timeseries-resample` for temporal alignment detail
