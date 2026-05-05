---
name: outlier-detection
description: Detect and treat outliers in datasets. Use when diagnosing skewed distributions, choosing between removal/capping/imputation, or selecting between univariate vs multivariate outlier methods.
---

# Outlier Detection

## Quick start

Tell me: data type (tabular/time-series), number of features, whether labels are available, and what to do with detected outliers (remove / cap / impute / flag).

## Method selection

```
How many features?
├── 1–2 features (univariate / bivariate)
│   ├── Normal distribution assumed  → Z-score (|z| > 3)
│   ├── Skewed / non-normal          → IQR fence (Q1 − 1.5×IQR, Q3 + 1.5×IQR)
│   └── Time series                  → Rolling IQR or STL decomposition residuals
└── Many features (multivariate)
    ├── Linear relationships          → Mahalanobis distance (χ² threshold)
    ├── Non-linear / unknown shape   → Isolation Forest (contamination=0.01–0.05)
    ├── Density-based clusters       → LOF (Local Outlier Factor, n_neighbors=20)
    └── Labels available (supervised) → Train classifier: inlier vs. outlier class

Labels available?
├── Yes → One-Class SVM or supervised classifier on labeled anomalies
└── No  → Unsupervised (Isolation Forest / LOF / Mahalanobis)
```

## Detection code patterns

```python
# Univariate — IQR fence
Q1, Q3 = df[col].quantile([0.25, 0.75])
IQR = Q3 - Q1
outlier_mask = (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)

# Univariate — Z-score (normal distribution only)
from scipy.stats import zscore
outlier_mask = zscore(df[col]).abs() > 3

# Multivariate — Isolation Forest
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.02, random_state=42)
df["outlier_score"] = iso.fit_predict(X)   # -1 = outlier, 1 = inlier
df["outlier_flag"] = df["outlier_score"] == -1

# Multivariate — Mahalanobis distance
from scipy.spatial.distance import mahalanobis
import numpy as np
cov = np.cov(X.T)
inv_cov = np.linalg.inv(cov)
mean = X.mean(axis=0)
dist = [mahalanobis(row, mean, inv_cov) for row in X]
threshold = np.percentile(dist, 97.5)   # χ²(df, 0.975) for formal test
```

## Treatment decision

| Situation | Treatment |
|---|---|
| Outlier is a data error (impossible value) | Remove or correct |
| Outlier is real but extreme — regression target | Cap (Winsorize) at 1st/99th percentile |
| Outlier is real — classification feature | Cap or keep; tree models are robust |
| Outlier is real — linear model feature | Cap or log-transform before fitting |
| Outlier is rare but valid signal (fraud, anomaly) | Keep + flag; it IS the signal |
| Time series spike — sensor error | Interpolate; mark as `is_imputed=True` |

```python
# Winsorizing (cap, don't remove)
from scipy.stats.mstats import winsorize
df[col] = winsorize(df[col], limits=[0.01, 0.01])  # cap bottom/top 1%
```

## Audit trail (required)

Always produce an outlier report before removing anything:
- Count + % of rows flagged per column / method
- Sample of flagged rows for domain review
- Threshold used + method name

Never silently drop rows — document every removal decision.

## Failure modes

- Z-score on non-normal data: misses asymmetric outliers; IQR is safer default
- Removing outliers in test set: biases evaluation; flag in test, don't remove
- Setting contamination too high in Isolation Forest: flags valid observations as anomalies
- Treating all outliers as errors: in fraud/anomaly tasks, outliers ARE the signal — verify domain intent

Pair with `/data-filtering` for rule-based removal and `/data-cleanse` for the broader cleaning workflow.
