---
name: model-drift
description: Detect and respond to model drift in production. Use when monitoring deployed models, diagnosing performance degradation, detecting feature or label distribution shift, or setting retraining triggers.
---

# Model Drift Detection

## Drift taxonomy

```
Data drift (covariate shift)
  → Input feature distribution changes; model weights unchanged
  → Detect: statistical tests on feature distributions

Concept drift (label shift)
  → Relationship between features and target changes
  → Detect: model performance degrades on recent data

Label drift (prior probability shift)
  → Class frequencies change in prod vs. training
  → Detect: compare prediction distribution over time

Prediction drift
  → Model output distribution shifts even if inputs look stable
  → Early warning: often precedes measurable performance drop
```

## Detection methods

### Feature drift (data drift)

```python
from scipy.stats import ks_2samp
import pandas as pd

def feature_drift_report(df_train, df_prod, columns, alpha=0.05):
    results = []
    for col in columns:
        stat, p_value = ks_2samp(df_train[col].dropna(), df_prod[col].dropna())
        results.append({
            "feature": col,
            "ks_stat": round(stat, 4),
            "p_value": round(p_value, 4),
            "drift": p_value < alpha,
        })
    return pd.DataFrame(results).sort_values("ks_stat", ascending=False)
```

Population Stability Index (PSI) — better for categorical + monitoring over time:
```python
def psi(expected, actual, buckets=10):
    # PSI < 0.10: no shift; 0.10–0.25: moderate; > 0.25: significant shift
    ...
```

### Concept drift (performance degradation)

```python
# Rolling window performance — requires ground truth labels (lagged)
window = 7   # days
perf_history = (
    df_prod.groupby(pd.Grouper(key="date", freq=f"{window}D"))
    .apply(lambda g: metric_fn(g["label"], g["pred"]))
    .reset_index(name="score")
)
# Alert if score drops > 5% absolute vs. training baseline
```

### Prediction / label drift (no ground truth needed)

```python
# Compare prediction distribution: training vs. recent prod window
from scipy.stats import chi2_contingency

train_pred_dist = pd.Series(y_train_pred).value_counts(normalize=True)
prod_pred_dist  = pd.Series(y_prod_pred_recent).value_counts(normalize=True)

# For continuous scores: KS test on predicted probabilities
ks_stat, p = ks_2samp(y_train_prob, y_prod_prob_recent)
# Alert if p < 0.01
```

## Drift severity levels

| PSI / KS | Severity | Action |
|---|---|---|
| PSI < 0.10 / KS p > 0.05 | None | Monitor |
| PSI 0.10–0.25 / KS p 0.01–0.05 | Moderate | Investigate; watch performance |
| PSI > 0.25 / KS p < 0.01 | Significant | Trigger retraining evaluation |
| Performance drop > 5% absolute | Critical | Retrain + rollback candidate ready |

## Retraining triggers (prescriptive)

```
Trigger retraining when ANY of:
  □ PSI > 0.25 on ≥ 2 top-10 important features
  □ Performance drops > 5% absolute vs. deployment baseline (rolling 30d)
  □ Prediction distribution KS p < 0.01 for 3 consecutive days
  □ Calendar trigger: monthly minimum regardless of drift (freshness floor)
```

## Monitoring pipeline skeleton

```python
# Run daily; store results in monitoring table
def daily_drift_check(df_train_ref, df_prod_today, model, top_features):
    # 1. Feature drift
    drift_report = feature_drift_report(df_train_ref, df_prod_today, top_features)
    
    # 2. Prediction drift
    prod_scores = model.predict_proba(df_prod_today[top_features])[:, 1]
    ks_stat, p = ks_2samp(train_scores_ref, prod_scores)
    
    # 3. Performance (if labels available with lag)
    # perf = metric_fn(df_prod_today["label"], prod_scores)
    
    # 4. Alert
    critical_features = drift_report[drift_report["drift"]]["feature"].tolist()
    if len(critical_features) >= 2 or p < 0.01:
        send_alert(f"Drift detected: {critical_features}; pred KS p={p:.4f}")
    
    return drift_report
```

## Failure modes

- No reference distribution saved at training time: can't compute drift without a baseline; save train feature stats at deploy
- Alerting on p-value alone (large datasets): with 100K rows, trivial shifts are statistically significant; use PSI or effect size
- No ground truth pipeline: performance drift is invisible without label collection; design label feedback loop at deploy time
- Retraining on drifted data without investigation: if drift is a data error, retraining propagates the error

Pair with `/feedback-loop` to design label collection for performance monitoring and `/model-validation` to validate the retrained model before swapping.
