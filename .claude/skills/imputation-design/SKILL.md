---
name: imputation-design
description: Designs a missing-value imputation strategy — missingness-mechanism diagnosis (MCAR/MAR/MNAR), method selection (deletion / mean-median-mode / KNN / MICE / model-based / domain / time-aware), the missingness-indicator decision, fit-on-train-only mechanics, and a post-imputation distortion check. Use when a dataset has nulls and you must decide how to fill them before training, when mean-imputation is distorting variance or correlations, or when missingness itself may be informative. Defers heavy temporal gap-fill to /timeseries-resample and leakage enforcement to /leakage-audit.
---

# Imputation Design

## Role
You are an Imputation Strategist.

## Quick start

Tell me: (1) which columns have missing values and the missing rate per column, (2) column types (numeric / categorical / datetime), (3) the downstream model family (linear / tree / neural / distance-based), (4) whether you have a time index, and (5) whether missingness might be informative (a value is missing *because* of what it would have been). The mechanism drives everything — never pick a method before diagnosing why the data is missing.

## Step 1 — Diagnose the missingness mechanism

The mechanism dictates which methods are valid. Diagnose before imputing.

| Mechanism | Definition | How to detect | Consequence for method |
|---|---|---|---|
| **MCAR** (missing completely at random) | Missingness independent of all values, observed or not | Little's MCAR test (p > 0.05 supports MCAR); missingness uncorrelated with any other column | Deletion is unbiased; any imputation OK |
| **MAR** (missing at random) | Missingness depends only on *observed* columns | Missingness correlates with observed features (regress `is_missing` on the rest — significant predictors = MAR) | Model-based / MICE / KNN can recover unbiased estimates; mean-impute biases |
| **MNAR** (missing not at random) | Missingness depends on the *unobserved* value itself | Cannot prove from data alone — needs domain reasoning (income missing more for high earners; sensor drops out at extremes) | No imputation is unbiased; ALWAYS add a missingness indicator; consider modeling the mechanism |

```python
# Missingness-correlation probe — is missingness predictable from observed columns? (MAR signal)
miss = df.isna().astype(int)
for col in df.columns[df.isna().any()]:
    # AUC of predicting is_missing(col) from the other columns
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    X = df.drop(columns=[col]).select_dtypes("number").fillna(-999)
    auc = cross_val_score(RandomForestClassifier(n_estimators=100, random_state=42),
                          X, miss[col], scoring="roc_auc", cv=3).mean()
    print(f"{col}: missingness AUC = {auc:.2f}")   # > 0.65 → MAR-like; design an indicator
```

```python
# Little's MCAR test — pyampute ships a working implementation
from pyampute.exploration.mcar_statistical_tests import MCARTest
p = MCARTest(method="little")(df)   # chi-square over missingness patterns
print(f"Little's MCAR p={p:.3f}")   # p > 0.05 → consistent with MCAR (do NOT read p < 0.05 as proof of MNAR)
```

Rule: you can never *prove* MNAR from the data. If domain reasoning says the value is missing because of what it would be, treat as MNAR regardless of the test.

## Step 2 — Select the imputation method

```
Missing rate on the column?
├── < 5% AND mechanism is MCAR
│   └── Listwise deletion is defensible (drop rows). Pairwise deletion only for correlation matrices.
├── Mechanism MAR / MNAR, OR rate ≥ 5%, OR rows are scarce → IMPUTE (don't delete):
│   ├── Need a fast, simple baseline → mean/median (numeric) / mode (categorical)
│   │     ⚠ collapses variance + attenuates correlations — baseline only, never final for MAR
│   ├── Local structure matters, mixed types, moderate dims → KNN imputation (k=5–10)
│   ├── Want principled multiple imputation + uncertainty → MICE / IterativeImputer
│   ├── One column predictable from others → model-based (regression / tree) single imputation
│   ├── Domain constant is the correct fill ("no prior visit" → 0; "unknown" category) → domain/constant
│   └── Gap in a time series → forward/back-fill / interpolate (HEAVY temporal → /timeseries-resample)
```

| Method | When | Cost / failure mode |
|---|---|---|
| **Listwise deletion** | MCAR + low rate (< 5%) + rows abundant | Discards data; biases under MAR/MNAR; shrinks sample / power |
| **Pairwise deletion** | Correlation/covariance estimation, MCAR | Produces non-positive-definite covariance matrices; inconsistent N per cell |
| **Mean / median** | Numeric baseline only | **Collapses variance, attenuates correlations toward 0**, distorts distribution; median is robust-to-skew but same correlation cost |
| **Mode** | Categorical baseline | Over-inflates the majority category; destroys minority signal |
| **KNN imputation** | Mixed/local structure, moderate dimensionality | Slow at scale (O(n²) neighbor search); degrades in high dimensions (distance dilution); needs scaling first |
| **MICE / IterativeImputer** | MAR, want uncertainty via multiple imputations | Compute-heavy; convergence not guaranteed; must POOL across `m` imputations (Rubin's rules), not average-then-fit |
| **Model-based (regression / tree)** | One column strongly predicted by others | Single imputation understates variance (too confident); a tree imputer (e.g. `IterativeImputer` w/ tree estimator) handles non-linearity |
| **Domain / constant fill** | A real-world default exists (`0`, `"none"`, `-1` sentinel) | Wrong default poisons the feature; sentinel `-1` must be paired with an indicator or the model reads it as a magnitude |
| **Time-aware (ffill / bfill / interpolate)** | Ordered time index, short gaps | ffill leaks the last value across a long gap; interpolation invents a trend; **heavy resampling/alignment → defer to /timeseries-resample** |

```python
# KNN imputation — scale first, fit on train only
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(X_train)
imputer = KNNImputer(n_neighbors=5).fit(scaler.transform(X_train))
X_train_imp = imputer.transform(scaler.transform(X_train))
X_test_imp  = imputer.transform(scaler.transform(X_test))   # same fitted objects

# MICE — multiple imputation, then POOL (do not collapse to one set silently)
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
mice = IterativeImputer(max_iter=10, sample_posterior=True, random_state=42).fit(X_train)
# For inference (Rubin's rules): fit the model on each of m imputed sets, pool estimates + variance
```

## Step 3 — The missingness-indicator decision

Add a binary `<col>_is_missing` flag when **the fact of being missing carries signal** — i.e. MNAR, or MAR where missingness predicts the target. This lets the model learn from the pattern instead of pretending the imputed value is real.

```python
from sklearn.impute import SimpleImputer
imp = SimpleImputer(strategy="median", add_indicator=True)  # appends missing-indicator columns
```

| Add an indicator when | Skip the indicator when |
|---|---|
| Mechanism is MNAR (missingness ⟂ value) | Mechanism is MCAR and rate is low — flag is pure noise, adds dimensionality |
| `is_missing` correlates with the target (check before deciding) | The downstream model is a linear model and the flag is collinear with another feature |
| Missingness is operationally meaningful ("not measured", "skipped question") | You already encode "missing" as its own category for a categorical column |

Failure mode: imputing an MNAR column with the mean AND omitting the indicator erases the only signal the missingness carried — the model is then biased toward the imputed center.

## Step 4 — Fit-on-train-only mechanics

Every imputation parameter (mean, median, mode, KNN neighbor set, MICE regression coefficients, learned category) is **learned on the training fold and applied unchanged to val/test**. Fitting on the full dataset bleeds val/test distribution into train.

```python
# CORRECT — inside a Pipeline so the imputer refits per CV fold
from sklearn.pipeline import Pipeline
pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median", add_indicator=True)),
    ("scale", StandardScaler()),
    ("model", model),
])
# cross_val_score(pipe, X, y) refits the imputer on each train fold — no leakage

# WRONG — global fit before split leaks test statistics into train
X_imputed = SimpleImputer().fit_transform(X)   # uses test means; DO NOT
X_train, X_test = train_test_split(X_imputed)
```

This skill specifies the mechanics; the **enforcement and audit of leakage (preprocessing-before-split, the broader leakage taxonomy) is owned by `/leakage-audit`** — run it before training to confirm no imputation step fit on the full set.

## Step 5 — Post-imputation distortion check

Imputation that silently warps the distribution is worse than a flagged gap. Compare pre/post and test downstream sensitivity.

```python
# Distribution shift — did mean-impute collapse the variance?
print("std  before:", df[col].std(), " after:", df_imp[col].std())   # large drop = variance collapse
print("corr before:", df.corr()[col]["target"], " after:", df_imp.corr()[col]["target"])  # attenuation

# Downstream sensitivity — does the chosen method change the model metric vs a baseline?
for name, imputer in [("median", SimpleImputer(strategy="median")),
                      ("knn", KNNImputer(n_neighbors=5)),
                      ("mice", IterativeImputer(random_state=42))]:
    score = cross_val_score(Pipeline([("i", imputer), ("m", model)]), X, y, cv=5).mean()
    print(f"{name}: {score:.4f}")   # if methods diverge > a few %, mechanism + method matter — don't default to mean
```

Acceptance: variance retention (post/pre std ratio) reported per column; correlation attenuation < ~10% relative or the indicator carries the lost signal; downstream metric stable across at least two methods.

## Output format

```
### Imputation Spec: [dataset]

#### Missingness diagnosis
| Column | Missing % | Mechanism (MCAR/MAR/MNAR) | Evidence |

#### Method plan
| Column | Method | Indicator? | Fit-on-train | Rationale |

#### Distortion check
| Column | std ratio (post/pre) | corr Δ | Downstream metric Δ |

#### Decisions requiring domain input
[e.g. "Is income-missing MNAR (high earners decline)?" — affects indicator + method]

#### Pipeline order
1. Drop columns above the un-imputable threshold (e.g. > 60% missing, no signal)
2. Add missingness indicators (before imputation overwrites the pattern)
3. Fit imputer on TRAIN fold only (inside a Pipeline / per CV fold)
4. Transform val/test with the fitted imputer
5. Post-imputation distortion check → sign off
```

## Quality bar
- Diagnose the mechanism (MCAR/MAR/MNAR) before choosing a method — never default to mean-impute
- Mean/median/mode is a BASELINE only; for MAR data it collapses variance and attenuates correlations — report the std ratio
- Add a missingness indicator whenever missingness is informative (MNAR, or `is_missing` predicts the target)
- Every imputation parameter is fit on the training fold only and applied unchanged to val/test — global fit leaks
- Never silently impute MNAR with a central value and drop the indicator — that erases the signal and biases the model
- For multiple imputation (MICE) pool across the `m` sets (Rubin's rules) — do not average then fit once
- Defer: dirty-data taxonomy → `/data-cleanse`; preprocessing-leakage enforcement/audit → `/leakage-audit`; heavy time-series gap-fill / resampling / alignment → `/timeseries-resample`. Pair with `/feature-engineering` for encoding the indicator and `/cross-validation` to keep the imputer inside the fold.
