---
name: retraining-strategy
description: ML model retraining strategy — trigger types (drift/calendar/performance), data window design, incremental vs. full retrain, retraining pipeline, validation gates before promotion. Use when asked about "when to retrain?", "retraining schedule", "model decay", "continuous training", "online learning", or keeping a production model fresh.
---

# Retraining Strategy

## Role
You are a Model Retraining Strategist.

## Quick start

Match retraining frequency to data drift velocity. Over-retraining wastes compute; under-retraining allows silent degradation.

## Retraining trigger types

### 1. Drift-triggered (reactive)

Fire retraining when monitoring detects:
- PSI > 0.25 on ≥ 2 input features (sustained 3 days)
- Performance drop > 5% on primary metric (vs. deployment baseline, with lagged labels)
- Prediction distribution KS test p < 0.01 for 3 consecutive days

Minimum latency: drift detection → retrain → validate → deploy = 2–5 days. Set alert thresholds conservatively to avoid noise-triggered retrains.

### 2. Calendar-triggered (proactive)

Default cadence by data velocity:

| Data type | Suggested cadence |
|---|---|
| User behavior (e-commerce, streaming) | Weekly or bi-weekly |
| Financial transactions | Monthly |
| Healthcare / clinical | Quarterly (+ manual review) |
| Industrial sensor data | Weekly |
| Static documents / text | Only on content change |

Calendar retraining is insurance; it does NOT replace drift monitoring.

### 3. Performance-triggered (label-lagged)

Requires labeled outcomes to be available with a lag (e.g., churn labels available 30 days after prediction):
```python
# Daily evaluation on recent labeled window
recent_perf = evaluate_model(model, X_last_30d, y_last_30d)
if recent_perf["auc"] < deployment_baseline["auc"] - 0.05:
    trigger_retraining()
```

### 4. Event-triggered (manual)

Trigger manually on:
- Major product change (new features added, old features removed from prod pipeline)
- Upstream data schema change
- Regulatory change affecting label definition
- Data quality incident (corrupted training data discovered)

## Data window design

### Full retrain vs. incremental

| Approach | When to use | Risk |
|---|---|---|
| Full retrain on rolling window | Default; concept drift suspected | Loses long-tail patterns if window too short |
| Full retrain on expanding window | Stable concept; more data = better | Stale old data dilutes recent patterns |
| Incremental / warm-start | High-frequency retrain (daily); gradient boosting addtrees | Model drift if base is stale; harder to debug |
| Online learning | Streaming; ultra-fast concept drift | Noisy labels corrupt model quickly |

### Rolling window sizing

Rule: window should span ≥ 2 complete seasonal cycles.

```python
# Example: weekly model with 6-month rolling window
cutoff_date = today - timedelta(days=180)
train_df = df[df["event_date"] >= cutoff_date]

# Validate: minimum N still met?
assert len(train_df) >= min_training_rows, f"Window too short: {len(train_df)} rows"
```

Flag if window produces < 80% of baseline training set size — consider expanding.

## Retraining pipeline

```
Trigger received
    ↓
1. Data pull: fetch [window_start, today - label_lag]
2. Data validation: schema check + quality gates (run /data-quality)
3. Feature engineering: same Pipeline as production (load from artifact store)
4. Train: same hyperparameters as current model (no re-tuning unless triggered)
5. Offline evaluation: compare vs. current production model on holdout
   Gate: new model must not degrade primary metric > 1% vs. current
6. Validation suite: /model-validation 9-gate checklist
7. Shadow deploy: run new model in shadow for 24–48h; compare predictions
8. Promote if gates pass; else alert + hold
```

### Re-tuning rule

Do NOT re-tune hyperparameters on every retrain — it wastes compute and destabilizes behavior.

Re-tune when:
- Scheduled quarterly review
- Dataset size has changed > 2×
- Drift-triggered retrain + performance still doesn't recover after 2 cycles

### Validation gate before promotion

```python
# Must pass all:
assert new_model_auc >= current_model_auc - 0.01,        "Performance regression"
assert new_model_ece < 0.05,                              "Calibration failure"
assert new_model_p99_ms < latency_sla,                    "Latency SLA breach"
assert fairness_check(new_model) == "PASS",               "Fairness regression"
assert prediction_distribution_check(new_model) == "OK",  "Prediction shift"
```

## Retraining strategy document (output)

```
Model:              [name + version]
Primary trigger:    [drift / calendar / performance / event]
Calendar cadence:   [frequency if calendar trigger]
Drift thresholds:   [PSI > X on ≥ N features; perf drop > Y%]
Data window:        [rolling N days / expanding from date]
Retrain approach:   [full / incremental / warm-start]
Re-tune schedule:   [quarterly / on 2× data change / drift recovery failure]
Pipeline:           [data pull → validate → train → eval → shadow → promote]
Promotion gates:    [list of pass/fail checks]
Alert owner:        [team + contact]
Estimated cost:     [compute time × frequency × cost/hour]
```

## Rules

- Never retrain and immediately promote without a shadow period — prediction shift can break downstream consumers silently.
- Log every retrain as a new MLflow run (see `/experiment-tracking`) — maintain full audit trail.
- Retraining more than once per day with full retrain = design smell. Consider feature freshness vs. model freshness trade-off.
- Set a retrain budget cap: if drift triggers > N retrains/month, investigate root cause (upstream data issue) rather than burning compute.
