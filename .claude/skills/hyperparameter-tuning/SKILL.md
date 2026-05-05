---
name: hyperparameter-tuning
description: Design hyperparameter tuning strategy for ML models. Use when optimizing model performance, choosing between grid/random/Bayesian search, or setting up tuning pipelines.
---

# Hyperparameter Tuning

## Quick start

Tell me: algorithm + compute budget (time or trials) + metric to optimize.

## Strategy selection

```
Compute budget?
├── < 20 trials               → Random search (beats grid search at same budget)
├── 20–200 trials             → Bayesian optimization (Optuna or Hyperopt)
└── > 200 trials / parallel   → Async Bayesian (Optuna with TPESampler + pruning)

Parameter space?
├── Continuous ranges          → Bayesian (gradient info usable)
├── Mostly categorical         → Random search first; Bayesian if time allows
└── Conditional (nested)       → Optuna with suggest_categorical + conditional logic
```

## Top parameters by algorithm

**Gradient boosting (XGBoost/LightGBM):**
1. `n_estimators` + `learning_rate` (trade-off: more trees → lower LR)
2. `max_depth` or `num_leaves` (LGB) — controls overfitting
3. `subsample` + `colsample_bytree` — regularization via sampling

**Neural networks:**
1. Learning rate (most impactful; use log scale 1e-5 to 1e-1)
2. Batch size (affects generalization, not just speed)
3. Weight decay / dropout rate

**SVM:**
1. `C` (regularization) — log scale
2. `gamma` for RBF kernel — log scale
3. Kernel type (linear vs. RBF vs. poly)

**Random forest:**
1. `n_estimators` (more is better up to diminishing returns ~200)
2. `max_features` (sqrt for classification, 1/3 for regression)
3. `min_samples_leaf` — controls overfitting

## Tuning rules

1. Use nested CV — inner loop tunes, outer loop evaluates. Never report inner loop score.
2. Fix random seeds for reproducibility.
3. Log every trial (Optuna storage or MLflow).
4. Set early stopping — don't let bad trials waste compute.
5. Scale budget proportional to parameter count: ~10× trials per free parameter minimum.

## Search space design

- Use log scale for learning rates, regularization, gamma
- Use integer constraints for tree depth, estimator count
- Set realistic bounds — don't tune `n_estimators` from 1 to 10000

## Optuna minimal pattern

```python
import optuna

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
    }
    # Cross-validate with these params
    return cross_val_score(model(**params), X_train, y_train, cv=5).mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

## Failure modes

- Tuning on full dataset: test set contamination — always tune inside CV
- Tuning too many params at once: interaction effects mask signal; tune in order of importance
- No early stopping: small `n_estimators` + high `learning_rate` combos waste trials

Pair with `/cross-validation` for the evaluation loop and `/model-comparison` to compare tuned models.
