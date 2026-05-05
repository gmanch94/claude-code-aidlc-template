---
name: model-validation
description: Validate an ML model before deployment. Use when deciding if a model is ready to ship, running a pre-deploy checklist, performing slice analysis, or stress-testing on edge cases.
---

# Model Validation

## Quick start

Tell me: task type + primary metric + what the model will replace (baseline or previous model version).

## Pre-deploy validation checklist

```
□ 1. Held-out test performance ≥ threshold
□ 2. Beats baseline (trivial predictor OR production incumbent)
□ 3. Confidence intervals computed — not just point estimate
□ 4. Slice analysis on critical subgroups
□ 5. Calibration check (if probabilities are used downstream)
□ 6. Edge case / stress test coverage
□ 7. Latency + memory within SLA
□ 8. No data leakage confirmed (see /leakage-audit)
□ 9. Training-serving feature parity verified
```

## 1. Performance thresholds by task type

| Task | Minimum bar | Strong signal |
|---|---|---|
| Binary classification | AUC > 0.70; F1 > 0.60 on minority | AUC > 0.85 |
| Multi-class | Macro F1 > 0.65 | Macro F1 > 0.80 |
| Regression | R² > 0.60; RMSE < 20% of target range | R² > 0.85 |
| Ranking | NDCG@10 > 0.70 | NDCG@10 > 0.85 |
| NER / seq label | F1 > 0.75 per entity type | F1 > 0.90 |

Always compare to: (a) majority-class / mean baseline, (b) current prod model if one exists.

## 2. Confidence intervals

```python
from sklearn.utils import resample
import numpy as np

def bootstrap_metric(y_true, y_pred, metric_fn, n_iterations=1000):
    scores = []
    for _ in range(n_iterations):
        idx = resample(range(len(y_true)), random_state=None)
        scores.append(metric_fn(y_true[idx], y_pred[idx]))
    return np.percentile(scores, [2.5, 97.5])   # 95% CI

ci = bootstrap_metric(y_test, y_pred, roc_auc_score)
print(f"AUC: {roc_auc_score(y_test, y_pred):.3f}  95% CI [{ci[0]:.3f}, {ci[1]:.3f}]")
```

Never report a single number without a CI. Wide CI (> 0.10) = too little test data.

## 3. Slice analysis

```python
# Evaluate on critical subgroups — don't let aggregate metric hide failures
slices = {
    "mobile_users":    df_test["platform"] == "mobile",
    "new_users":       df_test["tenure_days"] < 30,
    "high_value":      df_test["spend_tier"] == "high",
    "minority_class":  df_test["target"] == 1,
}
for name, mask in slices.items():
    subset = df_test[mask]
    score = metric_fn(subset["target"], subset["pred"])
    print(f"{name}: n={mask.sum()}, score={score:.3f}")

# Flag: if any slice degrades > 10% vs. overall → do not deploy until explained
```

## 4. Edge case / stress tests

```python
# Boundary inputs — model should not crash or produce nonsense
edge_cases = [
    {"description": "all-null features",      "input": X_test.iloc[[0]].fillna(0)},
    {"description": "max cardinality value",  "input": X_test.iloc[[0]]},
    {"description": "single row inference",   "input": X_test.iloc[[0:1]]},
    {"description": "unseen category",        "input": ...},  # new value in categorical col
]
for case in edge_cases:
    try:
        pred = model.predict(case["input"])
        assert not np.isnan(pred).any(), "NaN prediction"
    except Exception as e:
        print(f"FAIL [{case['description']}]: {e}")
```

## 5. Latency + memory gate

```python
import time, tracemalloc

tracemalloc.start()
t0 = time.perf_counter()
_ = model.predict(X_test[:100])
latency_ms = (time.perf_counter() - t0) / 100 * 1000
_, peak_mb = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"p50 latency: {latency_ms:.1f}ms  peak memory: {peak_mb/1e6:.1f}MB")
# Gate: latency < SLA; memory < serving container limit
```

## Go / No-Go verdict

```
PASS all □ items → deploy candidate
FAIL performance threshold → retrain or collect more data
FAIL slice analysis → investigate slice before deploying
FAIL latency/memory → optimize (quantize, distill, reduce features)
FAIL leakage audit → fix pipeline; re-train from scratch
```

## Failure modes

- Evaluating on validation set: optimistic bias from model selection; always use held-out test
- Aggregate metric only: 0.92 AUC hides 0.45 F1 on minority class in a slice
- No baseline comparison: a model beating 0.72 AUC baseline is very different from one beating 0.95 prod model
- Skipping calibration for probabilistic decisions: uncalibrated scores cause bad threshold choices

Pair with `/model-calibration` for probability reliability, `/model-comparison` for A/B significance test, `/leakage-audit` to close checklist item 8.
