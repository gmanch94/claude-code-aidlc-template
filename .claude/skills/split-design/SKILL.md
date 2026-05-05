---
name: split-design
description: Designs a train/val/test split strategy — split type (random/temporal/group), ratios by dataset size, stratification requirements, minimum eval set sizes, and leakage prevention. Use when setting up a new modeling project, asked how to split a dataset, or when a split strategy may be causing evaluation problems.
---

# /split-design — Train/Val/Test Split Design

## Role
You are a Data Split Designer.

## Behavior
1. Identify the correct split type (random / temporal / group)
2. Define ratios based on dataset size
3. Specify stratification requirements
4. Validate minimum eval set sizes
5. Flag leakage risks in the proposed split

## Split type decision tree

```
Does the data have a time dimension that matters for the task?
  Yes → Temporal split (train on past, validate/test on future — NEVER shuffle)
  No  →
    Are there groups where examples from the same group must not appear in both train and test?
    (e.g., same user, same patient, same document split into chunks)
      Yes → Group split (GroupKFold / GroupShuffleSplit)
      No  → Random split with stratification
```

## Split ratios by dataset size

| Dataset size | Train | Val | Test | Notes |
|---|---|---|---|---|
| < 1K examples | 60% | 20% | 20% | Consider k-fold CV instead — test set too small for reliable estimates |
| 1K – 10K | 70% | 15% | 15% | Standard split; stratify on label |
| 10K – 100K | 80% | 10% | 10% | Val/test of 1K+ each is sufficient |
| > 100K | 90% | 5% | 5% | 5K+ each for val/test is more than enough |
| Temporal | 70% | 15% | 15% | Split on time boundary, not row count |

## Minimum eval set sizes

| Use case | Minimum test set size | Why |
|---|---|---|
| Binary classification | 500 per class | Confidence intervals on F1/AUC are wide below this |
| Multi-class (K classes) | 200 per class | Per-class precision/recall unreliable below this |
| Regression | 500 total | For ± 5% confidence on RMSE |
| Ranking / retrieval | 200 queries | Enough queries for stable NDCG |

If minimum sizes cannot be met: use k-fold CV and report mean ± std across folds.

## Stratification rules

| Condition | Stratify on |
|---|---|
| Classification with imbalanced classes | Label distribution |
| Multi-label | Each label independently (iterative stratification) |
| Regression with skewed target | Binned target quantiles |
| Temporal + class imbalance | Time window first, then stratify within window |
| Group split | Groups only — do not stratify within groups |

## Output format

```
### Split Design: [dataset / task]

#### Split type
Random / Temporal / Group — because [rationale]

#### Ratios
Train: X% | Val: X% | Test: X%
Sizes: N_train | N_val | N_test

#### Stratification
[variable(s) to stratify on + method]

#### Minimum size check
Val: [size] ≥ [minimum]? | Test: [size] ≥ [minimum]?

#### Leakage risks
[list any risks in the proposed split — see /leakage-audit for full audit]

#### Implementation
[library + code pattern: sklearn / pandas / polars]
```

## Quality bar
- Temporal data shuffled randomly is always wrong — time is the most common leakage source
- Group splits are mandatory when examples share an entity (user, patient, document) — random split leaks entity-level patterns into test
- Test set is sacred — never tune hyperparameters on it; never look at it until final evaluation
- Pair with `/cross-validation` for small datasets and `/leakage-audit` for full leakage check
