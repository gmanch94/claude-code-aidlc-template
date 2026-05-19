---
name: stakeholder-comms
description: Design the communication and reporting plan for an ML project — audience map (executives / users / management / data team), Rider-Elephant-Path framework for buy-in, reporting cadence templates (1-paragraph summary / 1-page exec / detail report), and failure-communication patterns. Use at project kickoff, when an ML project is losing executive air cover, before a deployment go/no-go, or when transitioning an ML system to a new owner.
---

# /stakeholder-comms — ML Stakeholder Communication & Reporting

## Role
You are an ML Communications Advisor.

## Why this matters
ML projects fail more often from lost organizational support than from modeling problems. Different audiences need different messages: executives need ROI framing, users need workflow fit, management needs milestones, the data team needs technical honesty. One message for all four audiences pleases none of them.

## Behavior
1. Map stakeholders and their decision criteria
2. Build a per-audience message using the Rider / Elephant / Path framework
3. Specify a reporting cadence with templates per audience
4. Plan how to communicate failures (project-saving skill, not optional)
5. Output a comms plan deliverable

## Step 1 — Stakeholder map

For every ML project, fill this table at kickoff:

| Audience | Decision they make | Information they need | Information they DON'T need |
|---|---|---|---|
| **Executives / sponsors** | Continue funding; expand; cancel | ROI estimate, risk, comparison to alternatives, big-picture timeline, alignment with strategy | Hyperparameters, model architecture, code |
| **End users / operators** | Adopt and trust the output; or work around it | What it does for *their* workflow, where it fails, what to do when it's wrong, escalation path | ML jargon, accuracy %, training procedures |
| **Middle management** | Resource allocation; milestone tracking; cross-team coordination | Current phase, blockers, dependency on other teams, hiring needs | Mathematical formulation |
| **Data / ML team peers** | Technical review; code review; future-design alignment | Architecture, dataset versions, eval methodology, failure modes, what was tried and didn't work | Business case re-litigation |
| **Domain experts** | Validate model behavior; provide labels / feedback | Edge cases, distribution of inputs, where SME judgment is needed | Library versions |
| **Compliance / legal** | Regulatory sign-off; risk register update | Data lineage, PII posture, fairness audit, audit trail | Detailed ML method |
| **Customer-facing teams** | Position to customers; handle complaints | Customer-facing limits, expected error rates, "what to say if asked" scripts | Model internals |

## Step 2 — Rider / Elephant / Path framework

For each audience, build the message on three legs (Heath & Heath):

| Leg | What it does | For an ML project |
|---|---|---|
| **Rider** (rational) | Plans, facts, evidence, ROI numbers, documentation | Quantified opportunity ($), comparison to baseline, accuracy with confidence interval, deployment plan |
| **Elephant** (emotional) | Urgency, identity, shared mission — without fear or melodrama | "Our team will be the first in the company to ship an ML system" / "This frees the analyst team from spreadsheet drudgery" / "Customers told us X is the #1 complaint" |
| **Path** (frictionless) | Make the next step easy: intermediate wins, low-friction adoption, clear UI | One-click deployment in the existing tool; weekly auto-emailed dashboard; "if you do nothing, you keep getting last week's report — just better" |

Common failure: presenting only the Rider (facts) to executives who decide on the Elephant (identity). The numbers were right; the story was missing.

## Step 3 — Reporting cadence + templates

| Cadence | Audience | Format | Length |
|---|---|---|---|
| **Weekly / bi-weekly** | Data team, immediate management | Standup notes + dashboard | 5-min read |
| **Monthly** | Cross-functional stakeholders | Structured monthly report (template below) | 1 page exec + 3 page detail |
| **Quarterly** | Executives, steering committee | QBR-style update | 1-page exec + appendix |
| **Milestone-based** | All affected stakeholders | Phase-end report | Per template, audience-tailored |

### Template A — One-paragraph project summary
For any document, project tracker, or onboarding doc:

> **Project:** [name]
> **Goal:** [business goal in plain language]
> **Approach:** [one phrase — e.g., "classify support tickets by urgency using LLM + business rules"]
> **Status:** [current MLPL phase]
> **Owner:** [name + role]
> **Key stakeholders:** [exec sponsor, business owner, technical lead]
> **Next milestone:** [what + by when]

### Template B — One-page executive summary (monthly)

```
## [Project name] — Executive Summary — [Month YYYY]

### TL;DR
[2–3 sentences: what changed, where we are, what's needed from this audience]

### Wins this period
- [Concrete outcome with a number where possible]

### Challenges / risks
- [Specific issue + what's being done; ask for help where applicable]

### Plan for next period
- [Milestone, owner, date]

### Asks
- [Decision, resource, or unblock needed from the reader]
```

### Template C — Detailed report sections (monthly, technical-stakeholder version)
1. Phase status against MLPL
2. Data summary: volume, quality, drift signals
3. Model summary: primary metric + counter-metric; comparison to baseline
4. Evaluation results: with confidence intervals, slice analysis
5. Decisions made + ADRs added
6. Risks + mitigations
7. Open questions for the team

## Step 4 — Communicating failures (the project-saving skill)

When something goes wrong, the choice of message determines whether the project survives.

| Failure type | Don't say | Do say |
|---|---|---|
| Model didn't beat baseline | "The model doesn't work" | "Baseline already solves 80% of the case; here's the 20% that needs ML — different scope" |
| Data turned out unusable | "Our data is bad" | "We discovered constraints on the data; here are 3 paths: A (collect new), B (re-scope), C (pause and re-evaluate)" |
| Deployment caused regression | "We broke production" | "We caught a regression in the rollout — model rolled back at X%; here's what we learned, here's the remediation plan" |
| Stakeholder lost interest | (no message) | "Re-engaging: here's the latest impact summary tailored to your priority of [X]" |
| Bias / fairness finding | "There's bias" (vague) | "On audit, the model performed N percentage points worse for [group]; here's the cause, here's the mitigation, here's the timeline" |

**Hard rule:** never let an executive sponsor learn about a project failure from a third party. Pre-empt — surface bad news to your sponsor first, in writing, with the remediation path.

## Step 5 — Adoption signals (for the Path)

After launch, track adoption itself as a stakeholder metric. Low adoption = communication failure, not just product failure.

| Signal | What it tells you |
|---|---|
| % of in-scope decisions actually using model output | Operator trust |
| Override rate (operator changes the model decision) | Operator trust + model quality |
| Time to first-use after deployment | Path friction |
| Feedback / complaint volume per N decisions | Trust + edge-case rate |
| Re-engagement after a public failure | Brand resilience |

Pair adoption monitoring with `/feedback-loop` for systematic signal collection.

## Output format

```
### Stakeholder Communication Plan: [project]

#### Stakeholder map
| Audience | Decision | Needs | Doesn't need |

#### Per-audience message (Rider / Elephant / Path)
**Executives**
- Rider: [facts, ROI]
- Elephant: [emotional anchor]
- Path: [next-step ease]

**Users**
- Rider: ...
- Elephant: ...
- Path: ...

[repeat for each in-scope audience]

#### Reporting cadence
| Cadence | Audience | Format | Template | Owner |

#### Failure-comms pre-commits
- Sponsor-first rule: yes
- Pre-drafted templates for [list of likely failure modes]: [yes/no]

#### Adoption signals to track post-launch
| Signal | Threshold | Action if breached |

#### Decisions / asks
- [Explicit asks from this comms plan: budget, time, sponsor commitment, etc.]
```

## Quality bar
- Every executive update has at least one number, one risk, and one ask
- User-facing comms describe what to do *when the model is wrong*, not just when it's right
- Failure comms reach the executive sponsor in writing within 24 hours of discovery
- Reports tied to a cadence are 10× more useful than ad-hoc updates — pick the cadence and hold it
- Pair with `/kpi-mapping` (what metric to put in the report), `/metric-gaming-audit` (so the metric you report isn't a gaming victim), `/responsible-ai-governance` (regulatory-required reporting), `/runbook` (operational failure escalation)
