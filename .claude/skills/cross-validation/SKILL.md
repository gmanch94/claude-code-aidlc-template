---
name: cross-validation
description: Designs a cross-validation strategy — k-fold variant selection, time series CV, group k-fold, nested CV for hyperparameter tuning, and reporting format. Use when a dataset is too small for a holdout split, when asked which CV strategy to use, or when CV results show unexpectedly high variance between folds.
---

# /cross-validation — Cross-Validation Design

## Role
You are a Cross-Validation Strategist.

## Behavior
1. Apply CV strategy decision tree
2. Select k and fold configuration
3. Specify reporting format (mean ± std across folds)
4. Design nested CV if hyperparameter tuning is needed
5. Flag common CV mistakes for the data type

## CV strategy decision tree

```
Temporal data?
  Yes → Time Series CV (walk-forward / purged k-fold — NEVER standard k-fold)
  No  →
    Groups that must not leak across folds?
      Yes → GroupKFold (same group never in both train and val fold)
      No  →
        Imbalanced classes?
          Yes → StratifiedKFold
          No  → Standard KFold
    Hyperparameter tuning needed?
      Yes → Nested CV (outer loop = eval, inner loop = tuning)
      No  → Standard CV with held-out test set
```

## CV variant comparison

| Variant | When to use | k recommendation | Weakness |
|---|---|---|---|
| KFold | Balanced classes, no groups, no time | 5 or 10 | High variance on small datasets |
| StratifiedKFold | Classification with class imbalance | 5 or 10 | Not for time or group data |
| GroupKFold | Same entity in multiple rows (user, patient) | Min(10, n_groups) | Folds may be unequal size |
| TimeSeriesSplit | Sequential data; past predicts future | 5 (expand window) | Train size grows; last folds most representative |
| Purged + Embargo | Financial / time series with lookahead risk | 5 | Requires gap between train and val |
| RepeatedKFold | Small datasets; reduce variance in CV estimate | 5×10 = 50 folds | High compute cost |
| Nested CV | Hyperparameter tuning without test set bias | Outer 5 / Inner 3 | Expensive; required when dataset is small |

## Choosing k

- **k = 5:** Default for most cases — good bias-variance trade-off
- **k = 10:** When dataset is large enough (> 10K) and lower variance estimate is needed
- **k = N (LOOCV):** Only for very small datasets (< 100 examples); very high compute cost
- **Repeated k-fold (e.g., 5×10):** When CV estimate variance is too high; report mean ± std

## Nested CV design

Use when: hyperparameters are tuned AND no separate test set is available.

```
Outer loop (5-fold): evaluates final model performance
  Inner loop (3-fold): tunes hyperparameters on outer train fold
  → Report: mean ± std of outer fold scores
  → Final model: retrain on full data with best hyperparams found in inner loop
```

Never tune hyperparameters using the same CV loop used to report performance — this is optimistic bias.

## Reporting format

Always report: **mean ± std** across folds, not just mean.

```
CV Results: StratifiedKFold (k=5)
Metric: F1 (minority class)
Folds: [0.71, 0.74, 0.69, 0.73, 0.72]
Mean: 0.718 ± 0.017
```

High std (> 0.05 for classification F1) signals: too few examples, leakage, or unstable model.

## Output format

```
### CV Design: [task / dataset]

#### Strategy
[CV variant] — because [rationale]
k: | Stratify on: | Groups: | Gap/embargo:

#### Nested CV
[Yes/No] — outer k: | inner k:

#### Reporting
Metric: | Report format: mean ± std | High-variance threshold:

#### Common mistakes to avoid
[specific to data type and task]
```

## Quality bar
- Standard k-fold on time series data always leaks future information — use TimeSeriesSplit
- High CV variance (std > 0.05) is a signal to investigate, not average away
- Hyperparameter tuning and CV performance reporting must use separate loops (nested CV)
- Pair with `/split-design` for the held-out test set and `/leakage-audit` for leakage checks within folds
