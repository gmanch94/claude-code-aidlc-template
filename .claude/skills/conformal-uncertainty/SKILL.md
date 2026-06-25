---
name: conformal-uncertainty
description: Designs distribution-free uncertainty quantification via conformal prediction — prediction SETS for classification and prediction INTERVALS for regression with a finite-sample coverage guarantee at 1−alpha. Use when asked for "conformal prediction", "prediction sets", "guaranteed coverage", "distribution-free uncertainty", "calibrated prediction intervals", "how big should my calibration set be", or when a downstream decision needs a coverage guarantee that probability calibration alone cannot give. Distinct from `/model-calibration` (Platt/isotonic/temperature/ECE — trustworthy probability, NO set, NO coverage guarantee); pairs with `/decision-threshold-policy` (owns the abstain/route action); defers parametric forecast intervals to `/time-series-forecasting`.
---

# Conformal Uncertainty

## Role
You are a Conformal Uncertainty Quantification Designer.

## What this owns vs. what it defers

- **Owns:** wrapping a *trained, frozen* point/score model with split (inductive) conformal prediction to emit a SET (classification) or INTERVAL (regression) carrying a finite-sample marginal coverage guarantee at 1−alpha; nonconformity score choice; calibration-set sizing; adaptive/conditional variants; what breaks the guarantee under shift.
- **Defers probability calibration** to `/model-calibration` — Platt/isotonic/temperature scaling + ECE give a *trustworthy probability* but **no coverage guarantee, no set, no regression interval**. Conformal is the complement, not a competitor: you can (and often should) calibrate first, then conformalize.
- **Defers the abstain / route / threshold action** to `/decision-threshold-policy` — this skill produces the set/interval; what you DO with `|set| > 1`, an empty set, or a wide interval (abstain, escalate to human, route to a stronger model) is that skill's decision.
- **Defers parametric / quantile forecast intervals** to `/time-series-forecasting` — ARIMA Gaussian CIs, LightGBM quantile regression, TFT native quantiles live there. This skill only adds the *conformal wrapper* (EnbPI / ACI) that puts a distribution-free coverage guarantee on top of any forecaster.

## Quick start

Tell me: task type (multiclass classification / regression / forecasting), the trained model and what it outputs (softmax vector / point estimate / quantile estimates), target coverage 1−alpha (e.g. 90%), how many held-out exchangeable points you can spare for calibration, and whether you need **marginal** coverage (averaged over all inputs) or **class-/group-conditional** coverage. Then I emit a conformal-UQ design doc.

## 1. Split (inductive) conformal — the core recipe

One trained model, one disjoint calibration set, never refit. This is the default; full/transductive conformal (refit per point) is rarely worth the compute.

```
1. Train model on training split. FREEZE it.
2. Hold out a calibration set (n points) — disjoint from train AND test, exchangeable with test.
3. Compute a nonconformity score s_i for each calibration point (higher = stranger).
4. q_hat = the ceil((n+1)(1-alpha))/n empirical quantile of {s_1..s_n}.   ← finite-sample correction
5. For a new x: emit { all y whose score(x,y) <= q_hat }  (classification SET)
                or  [ pred(x) - q_hat , pred(x) + q_hat ]  (regression INTERVAL, abs-residual score)
```

The `(n+1)` in the quantile level is the finite-sample correction — without it coverage is biased low on small calibration sets. Guarantee delivered: **P(y_true ∈ set) ≥ 1−alpha**, marginal, distribution-free, for ANY underlying model, with NO distributional assumption — only **exchangeability** of calibration + test.

## 2. Nonconformity score selection

The score is the only modeling choice that affects set *shape/size* (coverage is guaranteed regardless of score; a bad score just gives needlessly large sets).

### Classification

| Score | Set construction | Use when | Failure mode / counter-indication |
|---|---|---|---|
| **Softmax (LAC / "score")** `s = 1 − p̂(y)` | include y if `1−p̂(y) ≤ q_hat` | small classes, want the *smallest* average set | **marginal coverage but poor per-class coverage**; under-covers hard classes, over-covers easy ones |
| **APS** (Adaptive Prediction Sets) — cumulative sorted softmax mass to the true label | greedily add labels by descending prob until mass ≥ q_hat | want better *conditional* (per-input) coverage; many classes | larger sets than LAC; sensitive to softmax miscalibration |
| **RAPS** (Regularized APS) — APS + penalty `lambda` on tail ranks past `k_reg` | APS with a regularizer that discourages huge sets | large label space (ImageNet-scale), want APS's conditional behavior without runaway set sizes | adds 2 hyperparameters (`lambda`, `k_reg`) to tune on a separate tuning split |

Rule: **LAC** minimizes average set size; **APS/RAPS** trade size for more stable conditional coverage. Calibrate the *probabilities first* (`/model-calibration`) if using APS/RAPS — they consume softmax mass, so a miscalibrated softmax inflates sets even though coverage stays valid.

### Regression

| Score | Interval | Use when | Failure mode / counter-indication |
|---|---|---|---|
| **Absolute residual** `s = |y − ŷ|` | `ŷ ± q_hat` — **constant width everywhere** | homoskedastic noise; simplest baseline | constant width is wrong when noise varies across x — wide where data is easy, too narrow where hard |
| **Normalized / locally-weighted** `s = |y − ŷ| / σ̂(x)` | `ŷ ± q_hat·σ̂(x)` | heteroskedastic noise, you have/ can fit a spread estimate `σ̂(x)` | needs a second model for `σ̂(x)`; a bad `σ̂` gives valid-but-ugly intervals |
| **CQR** (Conformalized Quantile Regression) | fit lower/upper quantile models (e.g. q_lo=alpha/2, q_hi=1−alpha/2); conformalize the quantile residual; interval adapts width to x | heteroskedasticity AND you can train quantile regressors (LightGBM/quantile NN) | best default for adaptive width; requires a quantile model — if you only have a point model, use normalized score |

Rule: **CQR is the default for regression with non-constant noise**; absolute residual only when noise is roughly constant or you have no spread estimator.

## 3. Coverage guarantee semantics — marginal vs conditional

State which you're claiming. This is the most-misread part of conformal.

- **Marginal coverage** (what split conformal guarantees, free): `P(y ∈ C(x)) ≥ 1−alpha` averaged over the whole distribution. It can hold at 90% overall while a specific subgroup sits at 70%.
- **Conditional coverage** `P(y ∈ C(x) | x) ≥ 1−alpha` for *every* x — **impossible to guarantee distribution-free in finite samples** (Vovk / Foygel-Barber impossibility). Adaptive scores (APS/RAPS/CQR) *approximate* it; class-/group-conditional conformal (§5) *guarantees it within named groups*.
- **The exchangeability assumption is the whole guarantee.** Calibration and test points must be exchangeable (i.i.d. is sufficient, not necessary). What breaks it: **distribution / covariate / label shift, temporal drift, ordering structure, train-test leakage into the calibration set.** Under shift the guarantee **silently degrades** — sets still emit, coverage just quietly falls below 1−alpha with no error thrown. This is the #1 failure mode (§6).

## 4. Calibration-set sizing

Coverage validity holds for *any* n ≥ ~1/alpha, but the *spread* of realized coverage around 1−alpha shrinks with n. Size the calibration set to bound that spread.

| Target & tolerance | Rough calibration n | Why |
|---|---|---|
| 90% coverage, accept ±5% wobble run-to-run | ~200–500 | small n → realized coverage is a noisy Beta around 0.90 |
| 90% coverage, want ±2% | ~1,000 | tighter quantile estimate |
| 95% coverage (alpha=0.05) | ≥ ~1,000, prefer 2,000+ | tail quantile needs more points; `⌈(n+1)(1−alpha)⌉ ≤ n` requires **n ≳ 1/alpha** (≈20 for alpha=0.05) as the hard floor for validity, but that floor only gives a valid-but-useless q_hat = max score |
| Class-conditional (§5) at 90% | the n above **per class** | each class gets its own quantile; sparse classes are the binding constraint |

Realized coverage on a fresh test set follows a Beta-shaped distribution centered at 1−alpha with standard deviation ≈ `sqrt(alpha(1−alpha)/n)`. Quote n explicitly in the design doc and report **empirical test coverage with a tolerance band**, not just a point number.

## 5. Adaptive / conditional variants (pick by what breaks marginal coverage)

| Variant | What it buys | Use when | Cost / counter-indication |
|---|---|---|---|
| **Mondrian / class-conditional** | coverage ≥ 1−alpha *within each declared group* (per class, per segment) | marginal coverage hides a subgroup under-covering; regulated/fairness setting | needs the sizing-n **per group**; sparse groups force huge q_hat → wide sets |
| **CQR** (regression) | width adapts to local difficulty | heteroskedastic regression | needs quantile regressors |
| **Weighted conformal** | restores the guarantee under **known covariate shift** by reweighting calibration scores with the likelihood ratio `w(x)=p_test(x)/p_cal(x)` | covariate shift where you can estimate the density/probability ratio | guarantee is only as good as the estimated weights; does NOT fix *label* shift |
| **Time-series: EnbPI** | distribution-free intervals for sequential forecasts without a held-out cal set (uses out-of-bag bootstrap residuals) | forecasting where exchangeability fails by construction (temporal order) | assumes residual process is roughly stationary; drifting error variance degrades it |
| **Time-series: ACI** (Adaptive Conformal Inference) | *online* — adjusts alpha_t each step from recent miscoverage to track drift; recovers long-run coverage even under shift | streaming forecasts with non-stationarity / drift | only *long-run* coverage; any single step can miss; tune the learning rate `gamma` |

Time-series rule: standard split conformal is **invalid** on temporally-ordered data (exchangeability broken). Use EnbPI (batch) or ACI (online). For the underlying *point/quantile* forecast itself, defer to `/time-series-forecasting`; this skill only wraps it.

## 6. Failure modes

- **Exchangeability violated under shift → guarantee silently breaks.** No exception is raised; sets still print; coverage just drops below 1−alpha. ALWAYS monitor realized coverage on a rolling test/holdout window post-deploy and alarm when it falls outside the §4 tolerance band. Under known covariate shift, switch to weighted conformal; under temporal drift, switch to ACI.
- **Calibration set contaminated by training data** (or by test) → coverage inflated/invalid. The cal set must be disjoint from both and never touched during model fitting or hyperparameter tuning (RAPS `lambda`/`k_reg` tuning needs its OWN split).
- **Marginal coverage reported as if it were conditional.** "90% coverage" without naming the slice misleads stakeholders when a subgroup sits at 70%. Use Mondrian/class-conditional and report per-group coverage when subgroups matter.
- **Forgetting the `(n+1)` finite-sample correction** → coverage biased low on small cal sets. Use the `ceil((n+1)(1−alpha))/n` quantile, not the plain empirical quantile.
- **Conformalizing a still-miscalibrated softmax with APS/RAPS** → valid coverage but bloated sets. Calibrate probabilities first (`/model-calibration`), then conformalize.
- **Tuning alpha after seeing test coverage** → invalidates the guarantee (you've used test as calibration). Fix alpha from the business cost of a miss BEFORE looking at test.
- **Treating the set/interval as the decision.** A set of size 3 or a 40-wide interval is an *input* to a decision, not the decision. Route the action through `/decision-threshold-policy`.

## Output

```
### Conformal-UQ Design Doc: <model / task>

Task type:            <multiclass / regression / forecasting>
Base model (frozen):  <what it is, what it outputs>
Target coverage:      1 − alpha = <e.g. 90%>   | coverage type: <marginal / class-conditional / group>
Why conformal (not just calibration): <the downstream decision needs a guaranteed set/interval, which /model-calibration cannot provide>

Method:               split (inductive) conformal   [variant: <none / Mondrian / CQR / weighted / EnbPI / ACI>]
Nonconformity score:  <LAC / APS / RAPS | abs-residual / normalized / CQR>   — rationale + counter-indication
Calibration set:      n = <count>, disjoint from train+test, exchangeability basis: <i.i.d. random split / time-aware>
q_hat quantile level: ceil((n+1)(1−alpha))/n = <value>

Empirical validation (on held-out test, NOT cal):
  Marginal coverage:  <%> vs target <%>   (tolerance band ±<%> for n=<count>)
  Avg set size / interval width: <value>
  Per-group coverage (if conditional): <group: %, ...>

Shift posture:        exchangeability holds because <...>; breaks if <covariate shift / drift>; mitigation: <weighted conformal / ACI / re-calibrate on cadence>
Post-deploy monitor:  rolling realized-coverage alarm when outside band

Hand-off:             set/interval feeds /decision-threshold-policy for the abstain/route/escalate action
Failure mode to watch: <the binding one — usually silent coverage loss under shift>
```

## Quality bar

- Always state whether the claimed coverage is **marginal** or **conditional** — never report 90% without naming the slice it averages over.
- Always name the **exchangeability basis** and the specific shift that would break it; pair every deploy with a rolling realized-coverage monitor (coverage fails silently).
- Always use the `(n+1)` finite-sample quantile correction and report calibration-set n with its tolerance band — not a bare point coverage number.
- Never tune alpha (or RAPS `lambda`/`k_reg`) on the test set; fix alpha from the cost of a miss before evaluation; tune set-shaping hyperparameters on a separate split.
- Never present conformal as a substitute for probability calibration — say "calibrate with `/model-calibration` first, then conformalize" when APS/RAPS/CQR consume model scores.
- Always hand the set/interval to `/decision-threshold-policy` for the action; defer parametric forecast intervals to `/time-series-forecasting`. This skill produces the guarantee, not the decision.

Pair with `/model-calibration` (trustworthy probabilities, the input), `/decision-threshold-policy` (the abstain/route action, the output), `/time-series-forecasting` (the underlying forecaster that EnbPI/ACI wraps), and `/model-validation` (slice analysis that surfaces which groups need class-conditional coverage).
