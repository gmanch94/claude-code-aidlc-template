---
name: eda
description: Systematic exploratory data analysis — target distribution, missingness, cardinality, correlation matrix, time coverage, anomalies. Use when asked to "explore data", "understand the dataset", "what's in this data?", "profile the dataset", or at the start of any ML project before feature engineering.
---

# Exploratory Data Analysis (EDA)

## Quick start

Run the full profiling sequence on the raw dataset before any preprocessing or modeling.

## Workflow

### 1. Shape + schema audit

```python
df.shape              # rows × columns
df.dtypes             # confirm expected types
df.head(5)            # sanity check values
df.duplicated().sum() # exact duplicate rows
```

Flag: > 5% duplicates = investigate source before dedup.

### 2. Target variable analysis

**Classification:**
```python
df[target].value_counts(normalize=True)  # class balance
```
- < 10:1 ratio → standard training
- 10:1–100:1 → class weights or SMOTE
- > 100:1 → anomaly detection framing

**Regression:**
```python
df[target].describe()
df[target].hist(bins=50)
```
- Right-skewed (skewness > 1) → consider log transform
- Bimodal → investigate if two separate populations

### 3. Missingness audit

```python
miss = df.isnull().mean().sort_values(ascending=False)
miss[miss > 0]
```

| Missing rate | Action |
|---|---|
| < 5% | Impute (mean/median/mode) |
| 5–30% | Impute + add `is_missing` indicator |
| > 30% | Investigate source; consider dropping feature |
| > 50% | Drop feature unless domain-critical |

Check for non-null missingness codes: -1, 999, "N/A", "unknown" — replace before analysis.

### 4. Cardinality audit

```python
for col in df.select_dtypes("object"):
    print(col, df[col].nunique(), df[col].value_counts().head(3).to_dict())
```

| Unique values | Encoding strategy |
|---|---|
| 2–5 | One-hot |
| 6–15 | One-hot (watch feature explosion) |
| 16–50 | Target encoding (inside CV) |
| > 50 | Frequency encoding or embedding |
| Near-unique (> 90% unique) | Free text or ID — likely not useful as-is |

### 5. Numeric distribution audit

```python
df.describe(percentiles=[.01, .05, .25, .5, .75, .95, .99])
```

Flag: p1 vs. p5 gap → likely outliers. p99 vs. max → extreme tail.

Skewness:
```python
df[numeric_cols].skew().sort_values()
```

### 6. Correlation analysis

```python
import seaborn as sns
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=False, cmap="RdBu", center=0)
```

- |r| > 0.95 between features → drop one (multicollinearity)
- |r| > 0.30 with target → likely useful feature

### 7. Time coverage (if time series / temporal data)

```python
df[date_col].min(), df[date_col].max()
df[date_col].dt.year.value_counts().sort_index()   # coverage by year
df.set_index(date_col).resample("M").size()        # gaps?
```

Check for: gaps in coverage, seasonality patterns, data freshness lag.

### 8. Leakage candidates

Flag any feature with suspiciously high correlation to target (|r| > 0.9):
```python
corr[target].abs().sort_values(ascending=False).head(10)
```

Features recorded AFTER the prediction point are leakage. Cross-reference feature definitions against event timeline.

### 9. EDA summary report (output)

```
Dataset:        [name, N rows, M features, date range]
Target:         [distribution, balance ratio if classification]
Missingness:    [top missing cols + rates; action per col]
Cardinality:    [high-cardinality cols + recommended encoding]
Outliers:       [cols flagged, % flagged]
Correlations:   [top features correlated with target; any |r|>0.95 pairs]
Time coverage:  [date range, gaps found, seasonality noted]
Leakage risk:   [features to investigate before modeling]
Recommended next step: [feature engineering / more data / data quality fix]
```

## Rules

- Run EDA on raw data, before any preprocessing — transforms hide problems.
- Never share raw distributions in reports if data is PII-sensitive — use aggregate stats only.
- EDA on train split only; do not peek at test distribution to inform decisions.
- Document every finding — "no issues found" is a valid entry.
