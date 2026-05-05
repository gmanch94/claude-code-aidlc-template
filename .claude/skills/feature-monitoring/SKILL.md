---
name: feature-monitoring
description: Design production feature quality monitoring covering freshness, schema drift, null rate, and distribution shift per feature. Use when setting up feature store monitoring, diagnosing unexplained model degradation, or building feature health dashboards. Complements /model-drift (model-level) with feature-level signals.
---

# Feature Monitoring

## Role
You are a Feature Health Monitor.

## Quick start

Gather: feature list (name, type, source system, expected freshness SLA), serving stack (feature store / direct DB / real-time pipeline), current monitoring gaps.

Output: feature health dashboard spec + alert rules + anomaly taxonomy.

---

## Feature health dimensions

Monitor all 4 per feature; prioritize by feature importance rank.

| Dimension | What it catches | Measurement |
|---|---|---|
| **Freshness** | Stale features from pipeline delays | Age of latest value vs. SLA |
| **Null rate** | Missing values at serving time | % null over rolling window |
| **Schema drift** | Type changes, renamed fields, dropped features | Schema version hash comparison |
| **Distribution shift** | Numeric mean/std change; categorical frequency shift | PSI or KS test vs. baseline |

---

## Freshness monitoring

```python
from datetime import datetime, timezone

def check_freshness(feature_name: str, latest_ts: datetime,
                     sla_minutes: int) -> dict:
    age_min = (datetime.now(timezone.utc) - latest_ts).total_seconds() / 60
    status = "OK" if age_min <= sla_minutes else (
        "WARN" if age_min <= sla_minutes * 2 else "ALERT"
    )
    return {"feature": feature_name, "age_min": age_min,
            "sla_min": sla_minutes, "status": status}
```

**SLA tiers:**
- Real-time features (event streams): < 5 min
- Near-real-time (micro-batch): < 30 min
- Daily batch features: < 26 hours (buffer for pipeline latency)

Alert at 2× SLA exceeded. Page at 4× SLA.

---

## Null rate monitoring

```python
import pandas as pd

def null_rate_check(df: pd.DataFrame, feature: str,
                    baseline_null_rate: float,
                    warn_threshold: float = 0.10,
                    alert_threshold: float = 0.25) -> dict:
    current_rate = df[feature].isna().mean()
    delta = current_rate - baseline_null_rate
    status = (
        "OK" if delta < warn_threshold else
        "WARN" if delta < alert_threshold else "ALERT"
    )
    return {"feature": feature, "current_null_rate": current_rate,
            "baseline_null_rate": baseline_null_rate,
            "delta": delta, "status": status}
```

**Thresholds:**
- Absolute null rate > 50%: always ALERT (feature effectively missing)
- Delta from baseline > 10%: WARN
- Delta from baseline > 25%: ALERT

---

## Schema drift detection

```python
import hashlib, json

def schema_fingerprint(schema: dict) -> str:
    canonical = json.dumps(schema, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]

def detect_schema_drift(current_schema: dict,
                         baseline_schema: dict) -> dict:
    added = set(current_schema) - set(baseline_schema)
    removed = set(baseline_schema) - set(current_schema)
    type_changed = {
        k for k in current_schema
        if k in baseline_schema and current_schema[k] != baseline_schema[k]
    }
    return {
        "status": "OK" if not (added or removed or type_changed) else "ALERT",
        "added": list(added),
        "removed": list(removed),
        "type_changed": list(type_changed)
    }
```

Any schema change = ALERT. Removed features and type changes are BLOCK (break serving); added features are WARN.

---

## Distribution shift (PSI)

```python
import numpy as np

def psi(expected: np.ndarray, actual: np.ndarray,
        buckets: int = 10) -> float:
    """Population Stability Index. < 0.10 stable; 0.10-0.25 warn; > 0.25 alert."""
    def bucketize(arr, bins):
        counts, _ = np.histogram(arr, bins=bins)
        return (counts + 1e-6) / len(arr)  # avoid log(0)

    bins = np.quantile(expected, np.linspace(0, 1, buckets + 1))
    bins[0], bins[-1] = -np.inf, np.inf
    p = bucketize(expected, bins)
    q = bucketize(actual, bins)
    return float(np.sum((p - q) * np.log(p / q)))

def categorical_psi(expected_counts: dict, actual_counts: dict) -> float:
    categories = set(expected_counts) | set(actual_counts)
    total_e = sum(expected_counts.values())
    total_a = sum(actual_counts.values())
    psi_val = 0.0
    for cat in categories:
        p = (expected_counts.get(cat, 0) + 1e-6) / total_e
        q = (actual_counts.get(cat, 0) + 1e-6) / total_a
        psi_val += (p - q) * np.log(p / q)
    return psi_val
```

| PSI | Status | Action |
|---|---|---|
| < 0.10 | OK | No action |
| 0.10 – 0.25 | WARN | Investigate source system |
| > 0.25 | ALERT | Escalate + trigger retraining check |

---

## Feature health dashboard spec

Per-feature row:

| Column | Source | Refresh |
|---|---|---|
| Feature name | Registry | Static |
| Importance rank | Model explainability | On retrain |
| Freshness (min) | Pipeline timestamp | Real-time |
| Null rate (today vs. baseline) | Serving logs | Hourly |
| PSI (7-day rolling) | Serving logs vs. training window | Daily |
| Schema match | Schema registry | On each pipeline run |
| Overall status | Worst of above | Derived |

**Prioritize top-N features by importance rank** — full monitoring on top 20; spot checks on the rest.

---

## Alert routing

| Severity | Condition | Route |
|---|---|---|
| P1 | Schema change (removed/type changed), null rate > 50%, freshness > 4× SLA | On-call ML engineer + PagerDuty |
| P2 | PSI > 0.25, null rate delta > 25%, freshness > 2× SLA | ML Lead (Slack alert) |
| P3 | PSI 0.10–0.25, null rate delta > 10% | Monitoring dashboard + daily digest |

---

## Anomaly taxonomy

| Anomaly | Root cause candidates | First check |
|---|---|---|
| Sudden null spike | Source table drop/rename; upstream pipeline fail | Check pipeline logs |
| Gradual null increase | Deprecating source field; schema migration in progress | Check source system changelog |
| PSI spike (numeric) | Seasonality, promotion event, data bug | Check raw source + business calendar |
| PSI spike (categorical) | New category introduced; category merged/renamed | Check source system schema changelog |
| Freshness alert | Pipeline SLA breach; backfill in progress | Check orchestrator job status |
| Schema mismatch | Breaking change in upstream system | Compare with source schema registry |

---

## Output

Deliver:
1. **Feature health spec** — per-feature: SLA, null baseline, schema fingerprint, importance rank
2. **Alert rules** — threshold table with routing
3. **Dashboard layout** — column spec with refresh cadence
4. **Anomaly playbook** — per-anomaly root cause checklist
