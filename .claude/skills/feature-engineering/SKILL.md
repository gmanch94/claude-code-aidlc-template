---
name: feature-engineering
description: Design and implement feature engineering for ML pipelines. Use when creating new features, encoding categoricals, transforming numerics, handling dates/text, or building aggregation features.
---

# Feature Engineering

## Quick start

Tell me: data types present + target type + algorithm family (tree vs. linear vs. neural).

## Encoding by data type

### Categorical
| Cardinality | Algorithm | Method |
|---|---|---|
| Low (≤ 10) | Any | One-hot encoding |
| Medium (10–50) | Tree | Ordinal (label) encoding |
| Medium (10–50) | Linear/neural | One-hot or target encoding |
| High (> 50) | Any | Target encoding (with CV smoothing) or embedding |
| High + rare categories | Any | Frequency encoding or group rare → "other" |

Target encoding rule: **always fit inside CV folds** — fit on train fold only. Use `category_encoders.TargetEncoder` with `smoothing` param.

### Numeric transformations
| Distribution | Transformation |
|---|---|
| Right-skewed, positive | Log1p or Box-Cox |
| Bounded [0, 1] | Logit transform |
| Heavy outliers | RobustScaler (median + IQR) |
| Normal, unit scale needed | StandardScaler |
| Neural net input | MinMaxScaler or StandardScaler |
| Tree models | No scaling needed |

### Date / time
Extract: `year`, `month`, `day_of_week`, `hour`, `is_weekend`, `is_holiday`
Cyclical encoding for circular features: `sin(2π * feature / period)` + `cos(...)` pair
Time since event: `(now - event_date).days` — more useful than raw date

### Text
Quick features: `char_count`, `word_count`, `sentence_count`, `avg_word_length`
Semantic: TF-IDF (sparse, interpretable) or sentence embeddings (dense, powerful)
Baseline first: TF-IDF + logistic regression before reaching for transformers

### Aggregation (groupby) features
```python
df.groupby("user_id")["amount"].agg(["mean", "std", "max", "count"])
```
Key aggregations: mean, std, min, max, count, last N, rolling window
**Must be computed on training data only, joined to val/test.** Never aggregate across split boundary.

## Interaction features

Only add when domain knowledge suggests multiplicative effect or linear model is used:
```python
df["amount_per_day"] = df["amount"] / (df["tenure_days"] + 1)
df["high_value_new_user"] = (df["amount"] > threshold) & (df["tenure_days"] < 30)
```

For tree models: interactions emerge automatically — don't add unless interpretability required.

## Pipeline rule

ALL fit operations (scalers, encoders, imputers) must be inside a `sklearn.Pipeline` and fit on training data only. Never call `fit_transform` on full X before split.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
pipe.fit(X_train, y_train)  # correct
```

## Failure modes

- Target encoding without CV smoothing: overfits on high-cardinality columns
- Scaling before split: test set statistics leak into scaler — use `/leakage-audit` to verify
- Adding too many interaction features: curse of dimensionality; follow with `/feature-selection`
- Date features as raw integers: model learns spurious ordinal patterns; extract semantic components

Pair with `/feature-selection` to trim engineered features and `/leakage-audit` to verify no fit-before-split errors.
