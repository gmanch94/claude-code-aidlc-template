---
name: ab-test-design
description: A/B test design for ML models — sample size calculation, assignment strategy, guardrail metrics, stopping rules, analysis plan. Use when asked about "A/B test", "experiment design", "canary experiment", "model A vs B in production", "statistical significance", "how long to run the test?", or validating a new model against an existing one in live traffic.
---

# A/B Test Design

## Quick start

Design before launch. Underpowered tests waste weeks; stopping early inflates false positives. Compute N first, then decide duration, then set guardrails.

## Workflow

### 1. Define hypotheses

```
H0: new model ≤ old model on primary metric (no improvement)
H1: new model > old model by at least Δ_min (minimum detectable effect)
```

Δ_min = smallest improvement worth shipping. Tie to business value:
- If 1% lift in conversion = $100K/year, and you need $50K to break even → Δ_min = 0.5%

### 2. Sample size calculation

```python
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()
n_per_group = analysis.solve_power(
    effect_size = delta_min / baseline_std,  # Cohen's d for continuous
    alpha       = 0.05,   # false positive rate (Type I error)
    power       = 0.80,   # 1 − beta; 0.80 = 20% chance of missing real effect
    alternative = "larger"
)

# For binary metrics (conversion rate, click rate):
from statsmodels.stats.proportion import proportion_effectsize, zt_ind_solve_power
es = proportion_effectsize(p1=baseline_rate + delta_min, p2=baseline_rate)
n_per_group = zt_ind_solve_power(effect_size=es, alpha=0.05, power=0.80)
```

Standard defaults: α=0.05, power=0.80. For high-stakes decisions: α=0.01, power=0.90.

Test duration = n_per_group / daily_traffic_per_arm (round up to full weeks to avoid day-of-week bias).

### 3. Assignment strategy

**User-level assignment (default):** hash(user_id + experiment_id) % 100 < treatment_pct

Rules:
- Never assign by request — same user gets inconsistent experiences
- Never re-randomize mid-experiment — invalidates analysis
- Holdout groups must be mutually exclusive (no user in two experiments on same feature)
- Segment by assignment unit, not by observed behavior (no post-hoc "active users only")

**When to use session vs. user assignment:**
- User: when the effect accumulates over time (recommendation, churn, personalization)
- Request/session: only when truly stateless (search ranking, single-query classification)

### 4. Primary + guardrail metrics

**Primary metric:** one metric, directly tied to business KPI. The experiment is a win/loss on this metric.

**Guardrail metrics:** metrics that must NOT regress. Experiment fails if any guardrail is violated even if primary metric improves.

| Example primary | Example guardrails |
|---|---|
| Conversion rate | Page load time, error rate, refund rate |
| Click-through rate | Bounce rate, session length |
| Loan approval rate | Default rate (30-day), fraud rate |
| Churn model recall | Precision (false alarm cost), p99 latency |

### 5. Stopping rules

**Never stop early for positive results** — optional stopping inflates Type I error.

Pre-register stopping rules:
```
Minimum run duration: max(7 days, time to reach N_per_group)
Maximum run duration: 4 weeks (after that, novelty effects / seasonal drift invalidate)
Early stop (negative): stop if guardrail metric degrades > X% for 3 consecutive days
Early stop (safety):   stop immediately if error rate > 1% or p99 > 2× SLA
```

Sequential testing if early stopping for positive is needed: use group sequential design (O'Brien-Fleming bounds) — not ad-hoc peeking.

### 6. Analysis plan

Run analysis only after minimum duration reached and N_per_group accumulated.

```python
from scipy import stats

# Two-sample t-test (continuous metric)
t_stat, p_value = stats.ttest_ind(treatment_values, control_values, alternative="greater")

# Proportions test (binary metric)
from statsmodels.stats.proportion import proportions_ztest
count = [treatment_conversions, control_conversions]
nobs  = [treatment_n, control_n]
z_stat, p_value = proportions_ztest(count, nobs, alternative="larger")

# Effect size + CI
delta = treatment_mean - control_mean
ci_low, ci_high = stats.t.interval(0.95, df=len(treatment)-1,
                                    loc=delta, scale=stats.sem(treatment - control_mean))
```

Minimum bar for shipping: p_value < α AND effect_size > Δ_min AND all guardrails pass.

### 7. A/B test design document (output)

```
Experiment:         [name + model versions]
Hypothesis:         H1: treatment improves [metric] by ≥ [Δ_min]
Primary metric:     [metric + baseline rate + Δ_min]
Guardrail metrics:  [list + threshold per guardrail]
Sample size:        [N per arm, power=0.80, α=0.05]
Expected duration:  [days, based on daily traffic per arm]
Assignment:         [user-level / request-level + hash strategy]
Traffic split:      [50/50 or asymmetric + rationale]
Start date:         [date]
Minimum end date:   [start + duration]
Maximum end date:   [start + 4 weeks]
Early stop triggers:[guardrail thresholds + safety stops]
Analysis date:      [minimum end date]
Decision criteria:  [p < α AND delta > Δ_min AND all guardrails pass]
```

## Rules

- Compute sample size before launch — "we'll run it for 2 weeks" without power calculation is not a design.
- Never peek at results and extend the run to get significance — pre-register the analysis date.
- Interaction effects: if two experiments run simultaneously on overlapping users, results are confounded — use mutual exclusion or factorial design.
- A/B test validates business impact; model offline metrics (AUC, F1) do not replace a production experiment.
