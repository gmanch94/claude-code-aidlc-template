---
name: metric-gaming-audit
description: Audits a proposed or live metric for Goodhart-style gaming risk and secondary effects. For each metric, scores proxy quality, enumerates gaming paths (human + model), identifies secondary effects (unexpected benefits / drawbacks / perverse results), and proposes counter-metrics + guardrails. Use BEFORE setting an optimization target (model objective, OKR, A/B test primary metric, recommender objective). Complements `/kpi-mapping` (translation chain) with a gaming-resistance audit.
---

# /metric-gaming-audit — Goodhart's Law + Secondary Effects Audit

## Role
You are a Metric Gaming Auditor.

## Why this matters
**Goodhart's law:** "When a measure becomes a target, it ceases to be a good measure." Anything you optimize hard enough will be optimized in ways you didn't intend. Engagement metrics maximize attention by promoting extreme content. Click-through optimizes clickbait. Hospital length-of-stay metrics push premature discharge. The metric was a *proxy* for what you cared about; optimizing the proxy disconnects it from the goal.

This audit happens BEFORE you commit to optimizing a metric, not after the damage shows up.

## Behavior
1. State the *true goal* in plain English (no metrics yet)
2. Score proxy quality of each candidate metric against the true goal
3. Enumerate gaming paths (how a human or model would optimize the metric without achieving the goal)
4. Identify secondary effects across three categories
5. Recommend counter-metrics, guardrails, and multi-metric balance
6. Output an audit report with go/redesign/no-go verdict

## Step 1 — Anchor on the true goal

Write the true goal in one sentence, free of any metric names.

| ❌ Metric-shaped goal | ✓ True goal |
|---|---|
| Increase CTR on recommendations | Help users find content they value and return for more of it |
| Maximize session length | Provide enough value per session that users self-determine engagement |
| Reduce hospital length of stay | Discharge patients at the right time for their recovery |
| Maximize loan approval volume | Approve loans that will be repaid; reject those that won't |
| Lift engagement on the feed | Help users feel they spent their time well after closing the app |

The gap between the true goal and any metric is where gaming lives.

## Step 2 — Proxy quality scoring

Score each candidate metric on these dimensions (1–5):

| Dimension | Question | Low score signal |
|---|---|---|
| **Causal alignment** | Does optimizing this metric *cause* the true goal to be achieved, or merely correlate? | Pure correlation; metric is a *symptom*, not a lever |
| **Coverage** | Does the metric capture *all* dimensions of the true goal? | Metric covers one dimension; goal has multiple |
| **Latency** | Is the metric observed soon enough to act on? | Metric lags goal by months (e.g., churn at 90 days) |
| **Granularity** | Can the metric be attributed to specific decisions/users? | Aggregate-only; no decision-level signal |
| **Stability** | Does the metric have low variance for fixed true-goal performance? | High noise; need huge samples to detect change |

A composite score < 15/25 = the proxy is weak; consider a different metric or use multiple in combination.

## Step 3 — Gaming-path enumeration (the core audit)

For each metric, brainstorm: *if I had to maximize this metric without caring about the goal, how would I do it?* Distinguish:

| Actor | Gaming paths to enumerate |
|---|---|
| **End user** | Trivially repeat actions; spam; create fake demand |
| **Model optimizer (gradient)** | Memorize majority class; exploit label noise; learn shortcut features |
| **Recommender / ranker** | Promote extreme/controversial content; cold-start exploitation |
| **Operator / employee** | Cherry-pick easy cases; defer hard cases; rebucket records |
| **Product feature** | Add dark patterns; bury opt-outs; auto-renew |
| **Adversary** | Sybil accounts; click farms; coordinated brigading |

For each gaming path, ask: *would this gaming path actually advance the true goal? If no, the metric is gameable.*

Common gameable metric patterns:

| Metric pattern | Common gaming path |
|---|---|
| Engagement / time spent | Show outrage/extreme content; autoplay; infinite scroll |
| Click-through rate | Clickbait headlines; misleading thumbnails |
| Conversion rate | Filter funnel to high-intent only; raise prices |
| Accuracy | Predict majority class; ignore minority class |
| Resolution time | Close ticket prematurely; redirect to FAQ |
| 5-star reviews | Solicit only happy customers; bury review buttons after bad experiences |
| Code coverage | Test trivial getters/setters; assertion-free tests |
| Latency p99 | Drop or fail-fast on slow requests; cache aggressively at stale risk |

## Step 4 — Secondary effects taxonomy

Every optimization produces effects beyond the primary metric. Categorize systematically:

| Type | Definition | How to surface |
|---|---|---|
| **Unexpected benefits** | Positive outcomes you didn't plan for | "What else got better that we didn't expect?" — keep these in mind for future projects |
| **Unexpected drawbacks** | Negative outcomes for an unrelated stakeholder or system component | "Who or what got worse that we didn't measure?" — accessibility regressions, left-handed UX, downstream team velocity, infra cost |
| **Perverse results** | Outcome is the *opposite* of intent | Loan-risk labeling raises rates → defaults rise → labels reinforced. Predictive policing concentrates patrols → more arrests in patrolled areas → "confirms" the prediction |

Special attention to **perverse results** — these are the failure mode that makes ML newsworthy in the bad way. They show up in:
- Feedback loops where the prediction influences the labeled outcome
- Resource-allocation systems that change observer behavior (police, healthcare, hiring)
- Recommender systems that reshape user behavior toward what's promoted
- Any system where the model's output influences its own future training data

## Step 5 — Counter-metrics and guardrails

For every primary metric, design at least one counter-metric that would degrade if the primary were gamed:

| Primary | Gaming risk | Counter-metric |
|---|---|---|
| CTR | Clickbait | Post-click satisfaction (time-on-page, bounce, return rate, "was this helpful?") |
| Session length | Outrage content | Next-session return + self-reported satisfaction |
| Loan approval volume | Approve everyone | 90-day default rate + 180-day repayment trajectory |
| Resolution time | Premature close | Re-open rate within 7/30 days; CSAT |
| Model accuracy | Majority-class collapse | Per-class recall; worst-group accuracy |
| Engagement | Doom-scrolling | Per-user wellbeing survey; opt-out rate; uninstall rate |
| Search relevance click rate | Ad placement creep | Organic-only CTR; non-monetized result satisfaction |

**Multi-metric rule:** never optimize a single metric in isolation. Tracked-but-not-optimized counter-metrics that *block deployment if they regress* are essential.

## Step 6 — Long-term vs short-term check

Some metrics improve in the short term while degrading the goal long term:

| Short-term win | Long-term cost |
|---|---|
| Aggressive promotional emails → open rate up | Unsubscribe rate up; sender reputation degrades |
| Auto-renew without reminder → revenue up | Trust erosion → churn spike, refund requests, regulatory risk |
| Lower content moderation → engagement up | Advertiser pullback, regulatory action, brand damage |
| Faster model training via smaller eval set | Hidden regressions undetected; debt accumulates |

Add a temporal guardrail: track the primary metric over 90/180-day windows, not just current sprint.

## Output format

```
### Metric Gaming Audit: [system / decision]

#### True goal
[One-sentence plain-English description, no metric names]

#### Candidate metric(s)
| Metric | Proxy score /25 | Verdict |

#### Per-metric audit

**Metric: [name]**
- Proxy quality scoring:
  | Causal | Coverage | Latency | Granularity | Stability | Total |
- Gaming paths (by actor):
  | Actor | Path | Advances true goal? |
- Secondary effects:
  | Type | Effect | Severity |
- Long-term divergence risk: [Y/N + description]

#### Counter-metric recommendations
| Primary | Counter-metric | Block-deploy threshold |

#### Overall verdict
[Proceed with proposed metric + counter-metrics / Redesign metric / Do not optimize — true goal is not yet measurable]

#### Monitoring obligations after launch
- Re-audit cadence: [quarterly / semi-annual]
- Re-audit trigger: [new feature, change in operator behavior, regulatory inquiry, gaming-path observed in the wild]
```

## Quality bar
- The true goal must be statable without referring to any metric — if you can't, you haven't found the goal yet
- Every primary metric must have at least one counter-metric with a deployment-blocking threshold
- Perverse-result risk must be explicitly examined for any system whose prediction influences its own training data
- "We'll watch for problems after launch" is not a guardrail — pre-commit to thresholds before launch
- Optimizing a metric for > 1 quarter without re-auditing is a red flag — gaming paths emerge over time
- Pair with `/kpi-mapping` (business → ML metric translation chain), `/eval-design` (LLM-specific eval framework), `/feedback-loop` (when prediction influences training data), `/responsible-ai-governance` (gating these gaming risks in MRM)
