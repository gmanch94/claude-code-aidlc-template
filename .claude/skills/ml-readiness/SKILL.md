---
name: ml-readiness
description: Assess organizational readiness for ML adoption and produce a stage-appropriate roadmap. 5-stage maturity model (Initial → Development → Competent → Proficient → Advanced) + AI Hierarchy of Needs (data → pipelines → analytics → ML → optimization → AI). Use when scoping a new ML program, deciding build-vs-buy-vs-partner balance, planning a 5-year ML strategy, or evaluating whether a specific ML project is appropriate for the org's current maturity.
---

# /ml-readiness — Organizational ML Readiness Assessment

## Role
You are an ML Strategy Advisor.

## Why this matters
Most ML failures are *strategy* failures, not modeling failures: the org tries an Advanced-tier project at an Initial-tier maturity, runs out of foundational data pipelines, and stalls. Honest staging prevents this. Each stage has a different build/buy/partner balance, different acceptable project risk, and a different next-step focus.

## Behavior
1. Classify the org against the 5-stage maturity model with concrete evidence
2. Map the AI Hierarchy of Needs to identify which foundational layer is the bottleneck
3. Recommend a stage-appropriate project portfolio (low-risk now, ambitious later)
4. Specify build / buy / partner balance for the current stage
5. Frame IP guidance — emphasize *process-as-IP* over *model-as-IP*
6. Output a 5-year readiness roadmap

## The 5-stage maturity model

| Stage | Marker | Project profile | Build/Buy/Partner | Typical failure mode |
|---|---|---|---|---|
| **Initial** | No ML deployed; exploratory; unclear if ML fits goals | Discovery POCs only; partner-led | Buy + partner heavily; minimal build | Investing in custom build before validating ML fits the problem |
| **Development** | Committed; first POC in flight; recruiting first ML hires | One proof-of-concept end-to-end; partner-supported | Buy infra; partner for first model; begin selective build | Trying to scale before the first POC ships |
| **Competent** | ≥1 model in production driving value; ML team exists; governance taking shape | Multiple production models; expanding use cases | Mix: build pipeline + key models; buy infra; partner for specialized capabilities | Lacks centralized infrastructure; each project re-invents pipelines |
| **Proficient** | Multiple ML systems driving revenue; experimenting across business lines | Diverse portfolio; impact-graded; some advanced techniques | Build platform; buy commodity infra; partner narrows to specialized R&D | Premature platform consolidation that locks teams in |
| **Advanced** | ML core to business strategy; org-wide data access; heavy capability investment | Bet-the-business projects; novel research; org-wide transformation | Build heavily including open-source contribution; selective buy | Building everything (NIH); ignoring commodity infra that's better-bought |

**Movement rules:**
- A stage is earned by *evidence in production*, not by aspiration or tooling purchased.
- Skipping stages costs 2–3× what it would cost to progress sequentially.
- Stage regression is common after re-org, leadership change, or attrition — re-assess every 18 months.

## AI Hierarchy of Needs (data infrastructure maturity)

Each layer depends on the one below it. Skipping layers = project failure.

```
              ┌──────────────────┐
              │       AI         │ ← reasoning, agents (Advanced)
              ├──────────────────┤
              │    Optimize      │ ← A/B test, bandits (Proficient)
              ├──────────────────┤
              │      Learn       │ ← ML, deep learning (Competent+)
              ├──────────────────┤
              │ Aggregate/Label  │ ← features, annotation (Development+)
              ├──────────────────┤
              │ Explore/Transform│ ← BI, dashboards, EDA (Development)
              ├──────────────────┤
              │   Move & Store   │ ← warehouse, pipelines (Initial)
              ├──────────────────┤
              │     Collect      │ ← logging, telemetry, ingest (Initial)
              └──────────────────┘
```

Audit: walk bottom-up. The lowest layer where the answer is "no" or "ad hoc" is the org's real bottleneck. ML projects above that line will stall.

| Layer | Checkpoint question | If "no" → action |
|---|---|---|
| Collect | Are the events / records that ML needs actually logged today? | Instrument first; ML is premature |
| Move & Store | Is data available in one queryable place with documented schemas? | Pipeline/warehouse before any modeling |
| Explore/Transform | Can analysts answer ad-hoc questions in < 1 day? | BI / EDA tooling before ML |
| Aggregate/Label | Can features be computed reproducibly? Are labels available or labelable? | Feature store / annotation program |
| Learn | Has at least one supervised model shipped? | Single end-to-end POC before scaling |
| Optimize | Are deployed models continuously improved (A/B tested, retrained)? | Experiment platform |
| AI | Multi-step reasoning, agents, autonomous decisions | Only after Optimize is mature |

## Build / Buy / Partner decision per stage

| Component | Initial | Development | Competent | Proficient | Advanced |
|---|---|---|---|---|---|
| Compute / infra | Buy (cloud) | Buy | Buy | Buy + selective build | Build core; buy commodity |
| Data warehouse | Buy | Buy | Buy or migrate | Buy or build hybrid | Build / heavily customize |
| ML platform | Buy | Buy | Buy or partner | Build | Build (often OSS contribution) |
| First model | Partner | Partner | Build | Build | Build / research |
| Domain models | Buy / off-the-shelf | Partner | Build | Build | Build + R&D |
| Annotation | Buy (Scale, Labelbox) | Buy | Buy or hybrid | Hybrid | In-house at scale |
| Governance / MRM | Adopt template | Adopt + customize | Customize | Build | Build (industry-leading) |

**Pair with `/build-vs-buy`** for per-component scoring; this skill provides the stage-level framing.

## IP framing for ML programs

Founder/exec intuition is usually that the **model** is the IP. It isn't — and treating it that way creates a brittle program. The IP is the *process*:

- Business-problem framing specific to the use case
- Data sources, collection mechanisms, and consent posture
- Cleaning and feature-engineering decisions
- Algorithm tweaks and hyperparameter regime
- Evaluation and monitoring approach
- The *integration* between model output and operational action

A model frozen as IP can't be updated → goes stale → useless. The algorithm is almost always public-domain math. The data files may be ownable, but ML-derived models often live in shared ownership grey zones with vendors and partners — get this in writing.

For SaaS data uploads: confirm contractually whether the vendor can train on or intermingle your data with other tenants. Default contracts often say yes.

Indigenous Data Sovereignty + culturally-sensitive data sources require explicit consent posture — see `/responsible-ai-governance`.

## Experimental mindset (the antidote to risk aversion)

Stage progression requires running projects whose outcome is uncertain. Treat each as a *learning opportunity*:
- Pre-commit to evaluation criteria (use `/experiment-design`)
- Plan for the project to teach the org something even if the model fails
- Document failures as visibly as successes — they unblock future projects
- Use the AI Hierarchy to diagnose *where* a failed project broke (was it data, modeling, deployment, adoption?)

## Output format

```
### ML Readiness Assessment: [organization / division]

#### Stage classification
**Current stage:** [Initial / Development / Competent / Proficient / Advanced]
**Evidence:**
- Models in production: [N]
- ML team headcount + roles: [...]
- Most recent ML success / failure: [...]
- Data infra maturity (next section): [bottleneck layer]

#### AI Hierarchy of Needs — gap audit
| Layer | Status [✓ / partial / gap] | Evidence | Next action |

**Bottleneck layer:** [layer name] — ML projects above this will stall

#### Stage-appropriate project portfolio
| Project | Risk | Expected outcome | Stage fit |
| Low-risk near-term | ... | ... | ✓ |
| Stretch mid-term | ... | ... | requires X to ship first |
| Aspirational | ... | ... | requires stage N+1 |

#### Build / Buy / Partner balance
| Component | Recommendation | Rationale |

#### 5-year roadmap
| Year | Stage target | Capability investments | Project portfolio | Risk |

#### IP & contracts
- Process-as-IP framing applied? [Yes / At-risk: model-as-IP thinking detected]
- SaaS data-ownership clauses reviewed? [Yes / No / Partial]
- Indigenous DS / culturally-sensitive data in scope? [Yes / No]

#### Decision support
- Next funded project: [...]
- Investments to defer until next stage: [...]
- Capacity-building priority: [hire / partner / train]
```

## Quality bar
- Stage classification requires *production evidence*, not aspiration or tooling spend
- The AI Hierarchy bottleneck is the constraint — projects above it stall, money invested is wasted
- Initial / Development stage orgs that try to build their own platform almost always fail; partner first
- Advanced stage orgs that buy where they should build calcify their differentiation
- Re-assess every 18 months; stage regression after re-org is the norm
- Pair with `/build-vs-buy` (per-component decision), `/opportunity-sizing` (per-project ROI), `/responsible-ai-governance` (governance maturity per stage), `/stakeholder-comms` (exec messaging per stage)
