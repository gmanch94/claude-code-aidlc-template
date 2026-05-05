---
name: feature-selection
description: Select the most predictive features for ML models. Use when reducing dimensionality, removing redundant features, fighting overfitting, or auditing feature importance.
---

# Feature Selection

## Role
You are a Feature Selection Advisor.

## Quick start

Tell me: number of features + dataset size + algorithm family + whether interpretability is required.

## Method selection

```
Dataset size?
├── < 1K rows     → Filter methods only (correlation, variance threshold)
│                   Wrapper methods too unstable on small data
├── 1K–50K rows   → Filter first → embedded (LASSO / tree importance)
└── > 50K rows    → Embedded or wrapper (RFE) — enough data to be reliable

Algorithm family?
├── Linear / logistic → LASSO (L1) embedded — zero-weight = removed
├── Tree / boosting   → Permutation importance or SHAP values
└── Neural net        → Dropout acts as implicit selection; use permutation importance post-hoc

Interpretability required?
├── Yes → Filter + LASSO; avoid black-box wrappers
└── No  → Any method; permutation importance most reliable
```

## Filter methods (no model needed)

```python
# 1. Variance threshold — remove near-zero variance features
from sklearn.feature_selection import VarianceThreshold
sel = VarianceThreshold(threshold=0.01)
X_filtered = sel.fit_transform(X_train)

# 2. Correlation — remove one of each highly correlated pair
corr = pd.DataFrame(X_train).corr().abs()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
drop_cols = [c for c in upper.columns if any(upper[c] > 0.95)]

# 3. Mutual information (non-linear correlation with target)
from sklearn.feature_selection import mutual_info_classif
mi = mutual_info_classif(X_train, y_train)
```

## Embedded methods (fit model, read importance)

```python
# LASSO — zero-coefficient features are selected out
from sklearn.linear_model import LassoCV
lasso = LassoCV(cv=5).fit(X_train, y_train)
selected = np.where(lasso.coef_ != 0)[0]

# Tree importance (use permutation, not impurity — impurity biased toward high-cardinality)
from sklearn.inspection import permutation_importance
result = permutation_importance(model, X_val, y_val, n_repeats=10)
importance_df = pd.DataFrame({"feature": feature_names, "importance": result.importances_mean})
```

## Wrapper methods (expensive but thorough)

```python
# RFE — iteratively removes least important features
from sklearn.feature_selection import RFECV
rfecv = RFECV(estimator=model, step=1, cv=5, scoring="f1")
rfecv.fit(X_train, y_train)
selected = X.columns[rfecv.support_]
```

## Multicollinearity check (for linear models)

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = [variance_inflation_factor(X_train, i) for i in range(X_train.shape[1])]
# VIF > 10: high multicollinearity — drop or combine
```

## Selection rules

1. Always do selection **inside CV** — fitting on full train set introduces selection bias
2. Use permutation importance over impurity importance — impurity favors high-cardinality
3. Remove zero-importance features first; investigate near-zero before removing
4. For SHAP: `shap.summary_plot` shows direction + magnitude — more useful than bare importance
5. Minimum retained features: enough that test set has at least 10 samples per feature

## Failure modes

- Selecting features on full dataset then splitting: leaks target signal into selection → inflated performance
- Using impurity importance for high-cardinality features: biased toward those features regardless of signal
- Removing correlated features without domain check: two correlated features may have different causal roles
- Over-pruning: validate final feature count with CV before committing

Pair with `/feature-engineering` to generate candidate features before selection, `/leakage-audit` to verify selection is inside CV.
