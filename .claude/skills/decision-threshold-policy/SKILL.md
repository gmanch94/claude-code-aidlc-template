---
name: decision-threshold-policy
description: Turns calibrated model scores into operational decisions — operating-point selection from a confusion-cost matrix (expected-cost minimization, not default 0.5), threshold-vs-prevalence and prevalence-drift shift, ROC-vs-PR operating-point choice by imbalance (Youden's J / F-beta / cost curves), multi-tier auto-approve/review/auto-reject bands, and an abstention / reject-option that routes low-confidence cases to humans sized against review capacity. Emits a threshold-policy design doc. Use when asked "what threshold should I use", "is 0.5 right", how to set an operating point, how to band scores into auto/review/reject, when to send a case to human review, or why a tuned threshold broke after prevalence drifted. Defers calibrated-probability production to `/model-calibration`, deployment wiring to `/model-deployment`, drift-detection math to `/model-drift`.
---

# /decision-threshold-policy — Decision Threshold Designer

## Role
You are a Decision Threshold Designer. You sit downstream of a calibrated classifier and upstream of an action: your job is to turn a score into a decision (act / don't act, or a tiered band) at the operating point that minimizes realized cost — and to keep that operating point valid as class prevalence and the score distribution drift.

## Behavior
1. Ask if not provided: the task (binary / multi-class one-vs-rest), whether scores are **calibrated** (if not → run `/model-calibration` FIRST; an expected-cost threshold on uncalibrated scores is meaningless), the four confusion costs or their ratio (cost of a false positive vs a false negative, in business units), the **prevalence** of the positive class in the population the model will score in production (NOT the training prevalence if it was resampled), whether a human-review capacity exists (cases/day) for an abstention band, and the deployment shape (single threshold / tiered bands).

2. Run the **operating-point gate** — is a cost-optimal threshold even the right tool here?

| Situation | This skill | Redirect to |
|---|---|---|
| One classifier score → act/don't-act or tiered bands | **Yes — design the threshold policy here** | — |
| Scores aren't calibrated yet | Not yet — fix calibration first | `/model-calibration`, then return here to set the operating point |
| A *constrained multi-variable* decision (order qty, price, route) from a prediction | No — that's an optimizer, not a threshold | `/decision-optimization` |
| Choosing *which metric* to optimize at all | Adjacent | `/metric-gaming-audit` on the objective, then return here |
| Sequential / online allocation where the action changes future data | No | `/bandit-design` / `/rl-design` |

3. **Derive the operating point from expected cost — not 0.5.** The default 0.5 threshold is optimal ONLY when FP and FN cost the same AND prevalence is 50%. Neither usually holds. For a calibrated score `p` and costs `C_FP`, `C_FN`, the expected-cost-minimizing threshold is:

```
t* = C_FP / (C_FP + C_FN)
```

(Acting when `p ≥ t*`. Derivation: act iff expected cost of acting `< (1−p)·C_FP` is below expected cost of not acting `p·C_FN`.) This threshold depends ONLY on the cost ratio — it is **prevalence-free in score space** *because the score is calibrated*. The prevalence dependence re-enters through the score distribution (step 5) and through any rate constraint. Worked example: if a false negative (missed fraud) costs 10× a false positive (a needless review), `t* = 1 / (1 + 10) = 0.091` — act on anything above 9% fraud probability, far below 0.5.

When you have the full 2×2 (including benefits of TP/TN), minimize total expected cost over a threshold sweep instead of the closed form:

```python
import numpy as np
def expected_cost(y_true, p, t, c_fp, c_fn, c_tp=0, c_tn=0):
    pred = (p >= t).astype(int)
    tp = ((pred==1)&(y_true==1)).sum(); fp = ((pred==1)&(y_true==0)).sum()
    fn = ((pred==0)&(y_true==1)).sum(); tn = ((pred==0)&(y_true==0)).sum()
    return tp*c_tp + fp*c_fp + fn*c_fn + tn*c_tn

ts = np.linspace(0.001, 0.999, 999)
costs = [expected_cost(y_val, p_val, t, c_fp=1, c_fn=10) for t in ts]
t_star = ts[int(np.argmin(costs))]   # tune on VALIDATION, evaluate on a held-out TEST
```

**Tune the threshold on a validation split, never on test** — picking `t` on test leaks and inflates the chosen operating point's apparent performance. Re-confirm on held-out test before shipping.

4. **ROC vs PR for the operating-point search — pick by imbalance.**

| Imbalance | Curve to read | Operating-point method | Counter-indication |
|---|---|---|---|
| Balanced (~30–70% positive) | ROC | Youden's J: `argmax(TPR − FPR)` — maximizes the balanced separation, equivalent to equal misclassification cost | Youden ignores cost asymmetry and prevalence — never use it when FP/FN costs differ or the positive class is rare |
| Imbalanced (<10% positive) | **Precision-Recall** | F-beta at the target precision/recall trade (`beta>1` favors recall, `<1` favors precision) OR the cost curve directly | ROC looks deceptively good under heavy imbalance — a 0.95 AUC can hide 0.10 precision at the operating point; read PR, not ROC |
| Cost ratio is known and stable | either | **Cost curve** — sweep `t`, plot expected cost, take the minimum (step 3); dominates J and F-beta because it optimizes the actual objective | Requires trustworthy costs; if costs are guesses, sensitivity-test `t*` across a cost-ratio range and report the band |

Default ladder: if you have costs → cost curve. If you have a precision OR recall target but no costs → F-beta / fix-one-vary-other on the PR curve. Only fall back to Youden's J when the problem is genuinely balanced and symmetric.

5. **Threshold shifts when prevalence drifts — this is the silent killer.** A calibrated-score threshold `t*` from step 3 is prevalence-robust *only while the model stays calibrated*. Two distinct failure modes:
   - **Prevalence drift breaks the realized rate.** Even with a fixed, still-valid `t*`, if production prevalence rises from 2% to 8%, the *volume* of positives (and thus the absolute count of FPs hitting your review queue) quadruples — a threshold that sized a review band to capacity now floods it. The operating point is still cost-optimal per-case but the *capacity* assumption is broken (step 6).
   - **Prevalence drift breaks calibration.** If the score distribution itself shifts (covariate or concept drift), the scores are no longer calibrated, and `t*` no longer corresponds to the cost-optimal point at all. This is the dangerous case: the threshold *looks* fine but silently produces costly errors.
   - **Threshold tuned on a re-balanced training set is wrong on arrival.** If training used SMOTE / class weights / undersampling to ~50/50 but production is 3% positive, a threshold picked on the balanced validation set is calibrated to the wrong base rate. Either calibrate scores back to the production prevalence (prior-correction) before thresholding, or tune `t` on a validation split that preserves the *real* production prevalence. State which you did.

   Prior-correction when training prevalence `π_train` ≠ production prevalence `π_prod`:
   ```
   p_corrected = (p · π_prod / π_train) /
                 (p · π_prod / π_train + (1−p) · (1−π_prod)/(1−π_train))
   ```
   Threshold the *corrected* probability. Re-derive `t*` after correction.

6. **Multi-tier thresholds — auto-approve / review / auto-reject bands.** When a human-review channel exists, a single threshold wastes it. Use two cut-points to carve three bands:

```
score < t_low        → auto-reject  (confident negative — no human touches it)
t_low ≤ score < t_high → REVIEW     (uncertain — route to human)
score ≥ t_high       → auto-approve (confident positive — no human touches it)
```

Set `t_low` and `t_high` so the auto bands meet a target error rate (e.g. auto-approve precision ≥ 99%, auto-reject FN rate ≤ 1%) and the middle band's *volume* fits review capacity (step 7). The auto bands trade coverage for safety: tighten them (widen the review band) when an auto-error is expensive; loosen them when reviewers are the bottleneck. Counter-indication: tiering only pays when human review is materially more accurate than the model in the uncertain band — if reviewers are no better than the model at `p≈0.5`, the review band burns money for no accuracy gain; verify review-vs-model accuracy in the band before building tiers.

7. **Abstention / reject-option — size the review band against capacity, not just confidence.** The reject-option (route low-confidence cases to a human instead of forcing an automated decision) is the highest-value lever this skill owns and no other skill covers. Two coupled constraints:
   - **Confidence:** abstain where the decision is closest to the cost-optimal threshold (the band around `t*` where a small score error flips the decision), or where calibrated confidence `max(p, 1−p)` is below a floor.
   - **Capacity:** the abstention band's *width* is bounded by review throughput. If reviewers handle `K` cases/day and the band as drawn produces `2K`, you cannot route them all — either narrow the band (accept more automated risk on the least-uncertain abstentions) or queue with a priority order (abstain on the highest-cost-at-risk cases first).

```python
# Size the abstention band to capacity: widen outward from t* until volume hits the review budget
order = np.argsort(np.abs(p_val - t_star))     # most-uncertain (nearest t*) first
review_idx = order[:review_capacity_per_day]   # take exactly what reviewers can absorb
band_lo, band_hi = p_val[review_idx].min(), p_val[review_idx].max()
# cases outside [band_lo, band_hi] get the automated decision via t_star
```

   **Track the abstention rate as a first-class metric.** A reject-option that abstains on 40% of traffic isn't a model serving decisions — it's a queue with extra steps. Set a max abstention rate (e.g. ≤ 15%) as an acceptance gate; if the model can only hit the cost target by abstaining on a third of cases, the model isn't ready, not the threshold. Counter-indication: abstention silently shifts cost from FP/FN onto review labor and latency — a "zero-error" policy that abstains on everything hard has just hidden the cost, not removed it.

8. **Monitoring + recalibration triggers — the policy is not set-and-forget.** Emit the signals that say *re-tune the threshold*, and hand the drift-detection math to `/model-drift`:

| Signal | Watch | Recalibration trigger |
|---|---|---|
| Score-distribution shift | Mean/quantiles of `p` on live traffic vs the validation reference (PSI — math owned by `/model-drift`) | PSI > 0.2 → scores may be miscalibrated → re-derive `t*` after re-calibration |
| Production prevalence | Realized positive rate (from delayed labels / audit sample) vs the prevalence `t*` was sized for | Prevalence moves >2× → prior-correct (step 5) and re-check capacity (step 6) |
| Realized confusion costs | Actual $ of FPs/FNs vs the costs assumed in step 3 | Cost ratio changes materially → re-run the cost curve; `t* = C_FP/(C_FP+C_FN)` moves |
| Review-band volume | Cases/day landing in the abstention band vs review capacity | Band overflows capacity for N days → narrow band or add reviewers; never silently drop the overflow into an automated decision |
| Auto-band error rate | Realized error inside auto-approve / auto-reject bands | Auto-band error exceeds its target (e.g. auto-approve precision < 99%) → tighten that cut-point |

   Set a **calendar recalibration floor** (e.g. re-derive every quarter) in addition to trigger-based, so a slow drift that never trips a single trigger still gets caught.

## Output

```
### Threshold Policy: [model / decision name]

**Scores calibrated:** [Yes — ECE < 0.05 per /model-calibration / NO → STOP, calibrate first]
**Decision shape:** [single threshold / three-tier bands / + abstention]
**Production prevalence:** [π_prod] (training prevalence [π_train]; prior-corrected: [Yes/No])

**Costs (business units)**
| | Predicted positive | Predicted negative |
|---|---|---|
| Actual positive | TP: [benefit/cost] | FN: [C_FN] |
| Actual negative | FP: [C_FP] | TN: [benefit/cost] |
Cost ratio C_FN : C_FP = [e.g. 10 : 1]

**Operating point**
- Method: [cost curve / F-beta on PR / Youden's J] — [why, by imbalance]
- Closed form (calibrated): t* = C_FP/(C_FP+C_FN) = [value]
- Tuned on validation, confirmed on test: t = [value]; default-0.5 would have cost [Δ] more
- Imbalance read: positive class [%] → curve used [ROC / PR]

**Tiered bands (if used)**
- t_low = [value]  → auto-reject (FN rate ≤ [target])
- t_high = [value] → auto-approve (precision ≥ [target])
- review band [t_low, t_high): [volume/day] vs review capacity [K/day]

**Abstention / reject-option**
- Confidence rule: abstain where |p − t*| < [δ] or max(p,1−p) < [floor]
- Capacity sizing: band width set to [K/day]; priority order = [highest-cost-at-risk first]
- Abstention rate: [%] (gate: ≤ [max])

**Prevalence-drift handling**
- t* sized for π_prod = [value]; prior-correction formula applied: [Yes/No]
- Capacity assumption breaks if prevalence > [value]

**Monitoring + recalibration triggers**
- [Score-dist PSI > 0.2 → recalibrate then re-derive t* — drift math via /model-drift]
- [Prevalence moves >2× → prior-correct + re-check review capacity]
- [Cost ratio changes → re-run cost curve]
- [Review band overflows N days → narrow band / add reviewers]
- [Calendar floor: re-derive every [quarter]]

**Failure mode to watch:** [the one most likely here — e.g. "scores tuned on SMOTE-balanced validation; will be miscalibrated on 3% prod prevalence until prior-corrected"]
```

## Quality bar
- Never derive a threshold on uncalibrated scores — `t* = C_FP/(C_FP+C_FN)` and any expected-cost minimum are only valid on calibrated probabilities; if scores aren't calibrated, STOP, run `/model-calibration`, then return here to set the operating point.
- Never default to 0.5 — 0.5 is optimal only at equal costs and 50% prevalence; state the cost ratio and derive `t*`, or explain explicitly why 0.5 happens to be right.
- Tune the threshold on validation, confirm on held-out test — picking `t` on the test set leaks and inflates the operating point.
- Always name the prevalence the threshold was sized for, and whether it matches production — a threshold tuned on a re-balanced (SMOTE/weighted) training set is wrong on arrival until prior-corrected; this is the single most common silent failure.
- Read PR not ROC under imbalance — Youden's J on ROC is only valid for balanced, symmetric-cost problems; for rare positives use the cost curve or F-beta on the PR curve.
- Size every abstention/review band against review *capacity*, not just confidence — a band that exceeds throughput overflows into unreviewed automated decisions; track the abstention rate as an acceptance gate (a model that only hits target by abstaining on a third of traffic isn't ready).
- Every threshold policy ships with recalibration triggers — a fixed operating point silently produces costly errors once prevalence or the score distribution drifts; hand the drift-detection math to `/model-drift` but own the trigger thresholds here.

Defers: calibrated-probability production → `/model-calibration` (run it first, then return here); deployment/serving wiring of the chosen thresholds → `/model-deployment`; drift-detection statistics (PSI/KS computation) → `/model-drift`; constrained multi-variable decisions from a prediction → `/decision-optimization`.
