---
name: data-quality
description: Designs data quality validation rules, anomaly detection thresholds, quarantine strategy, and SLAs for data pipelines. Use when designing quality gates for a new pipeline, auditing an existing pipeline for quality gaps, or asked to prevent bad data from reaching downstream consumers.
---

# /data-quality — Data Quality Design

## Behavior
1. Map data elements to quality dimensions
2. Define validation rules per dimension
3. Design anomaly detection thresholds
4. Specify quarantine and remediation strategy
5. Set SLAs and alerting

## Quality dimensions

| Dimension | What it checks | Example rule |
|---|---|---|
| Completeness | Non-null on required fields | `order_id IS NOT NULL` |
| Uniqueness | No duplicate primary keys | `COUNT(*) = COUNT(DISTINCT id)` |
| Validity | Values within expected domain | `status IN ('active','inactive','pending')` |
| Consistency | Cross-field / cross-table agreement | `end_date >= start_date` |
| Timeliness | Data arrives within SLA | `MAX(event_time) > NOW() - INTERVAL '2 hours'` |
| Accuracy | Values match source of truth | Row count matches source ± 0.1% |

## Validation rule tiers

| Tier | Failure action | Examples |
|---|---|---|
| **BLOCK** | Halt pipeline; quarantine batch | Null PK, duplicate PK, schema mismatch |
| **WARN** | Continue; alert on-call; log anomaly | Volume drop > 20%, null rate spike |
| **MONITOR** | Log only; review in weekly report | Minor distribution shift, new enum value |

## Anomaly detection thresholds (defaults — tune per pipeline)

| Signal | Threshold | Tier |
|---|---|---|
| Row volume | < 80% or > 120% of 7-day rolling average | WARN |
| Null rate per column | Increases > 5pp vs. prior run | WARN |
| Duplicate rate | > 0.1% | BLOCK |
| Schema drift | Any unexpected column add / remove / type change | BLOCK |
| Freshness | Latest record > expected SLA window | WARN |

## Quarantine strategy

```
Validation fails (BLOCK tier) →
  Route failed records to quarantine table (same schema + error_reason column)
  Halt downstream loads until quarantine is cleared
  Alert: data owner + on-call
  SLA: acknowledge within 1 hour; resolve within 4 hours

Quarantine clearance:
  Fix root cause → replay from quarantine → revalidate
  If source data unfixable: exclude with audit trail; document permanently
```

Quarantine without replay is useless — design the replay mechanism on day one.

## Output format

```
### Data Quality Design: [pipeline / table]

#### Validation rules
| Column / check | Dimension | Rule | Tier |

#### Anomaly thresholds
[volume, null rate, duplicate rate, schema drift — with tuned values]

#### Quarantine config
Table: | Routing logic: | Alert recipients: | Resolve SLA:

#### Freshness SLA
Data available by: | Alert if breached by: | Owner:

#### Gaps
[columns without rules, missing source-of-truth for accuracy checks]
```

## Quality bar
- Every pipeline needs at minimum: PK uniqueness, not-null on required fields, row volume check
- Accuracy checks require a source-of-truth — document what it is or flag the gap explicitly
- BLOCK tier rules must be automated — manual checks are not quality gates
- Pair with `/data-contract` for SLA ownership and `/feedback-loop` for routing failures into improvement cycle
