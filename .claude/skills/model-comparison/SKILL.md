---
name: model-comparison
description: Statistically compare ML models and select a winner. Use when choosing between trained models, validating that model B beats model A, or presenting results to stakeholders.
---

# Model Comparison

## Quick start

Tell me: models to compare + metric + dataset size + whether models trained on same folds.

## Comparison framework

### Step 1 — Establish common ground
- Same test set for all models (never re-split)
- Same metric (decide before looking at results)
- Same CV folds if comparing on CV scores

### Step 2 — Statistical test selection

```
Paired scores (same CV folds)?
├── Yes → Paired t-test (5×2 CV) or Wilcoxon signed-rank
└── No  → McNemar's test (classification) or bootstrap CI

Dataset size?
├── < 100 test examples → Bootstrap CI (5000 iterations); t-test unreliable
├── 100–10K            → 5×2 CV + paired t-test; p < 0.05 threshold
└── > 10K              → McNemar's (classification); standard errors are small
```

### Step 3 — Effect size check

Statistical significance ≠ practical significance.

| Metric | Meaningful difference (typical) |
|---|---|
| Accuracy | ≥ 1% absolute |
| AUC-ROC | ≥ 0.01 |
| F1 (minority) | ≥ 0.02 |
| RMSE | ≥ 5% relative |

If p < 0.05 but delta < meaningful threshold → report "statistically significant but practically equivalent."

### Step 4 — Report format

```
Model A vs. Model B — [metric] on [test set]
  Model A: 0.847 ± 0.012 (mean ± std, 5-fold)
  Model B: 0.861 ± 0.009
  Delta:   +0.014 (p = 0.023, paired t-test)
  Verdict: Model B wins — delta exceeds 0.01 practical threshold
  Failure mode of Model B: [name it]
  Recommendation: [deploy B / more data needed / further tuning]
```

## Multi-model comparison

When comparing 3+ models: use Friedman test first (non-parametric ANOVA). If significant, use Nemenyi post-hoc for pairwise. Avoids inflated false positive rate from multiple comparisons.

## Production decision criteria

Performance alone insufficient. Also compare:
- Inference latency (p50/p99)
- Memory footprint
- Retraining cost
- Interpretability requirement
- Dependency complexity (simpler model wins if close)

## Failure modes

- Cherry-picking test sets: always pre-register metric + test set before running comparison
- Comparing on validation set: model selection inflates validation scores; use held-out test
- Ignoring variance: reporting only mean; a high-variance model is risky even if mean is best
- Not naming the failure mode: every recommendation must name what breaks the winner

Pair with `/eval-design` for the evaluation framework and `/split-design` for proper test set design.
