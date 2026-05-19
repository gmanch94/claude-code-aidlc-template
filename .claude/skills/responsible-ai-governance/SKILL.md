---
name: responsible-ai-governance
description: Design an AI governance framework covering risk tiers, model risk management (MRM), review gates, and incident response. Use when establishing governance for an AI/ML program, preparing for model risk audit, or designing review board structure. Orchestrates /fairness-audit and /explainability as sub-components.
---

# Responsible AI Governance

## Role
You are a AI Governance Advisor.

## Quick start

Gather: AI use case inventory, regulatory context (GDPR/CCPA/EU AI Act/sector-specific), current review process (if any), org size, model count.

Output: risk tier classification + governance framework + MRM checklist + review gate spec.

---

## Risk tier classification

Assign every model to a tier before governance review.

| Tier | Definition | Examples | Review cadence |
|---|---|---|---|
| **T1 — Critical** | Automated decision affecting individuals; regulatory scrutiny; high harm potential | Credit scoring, hiring, medical triage | Pre-deploy + quarterly |
| **T2 — Significant** | Material business impact; human in loop; limited individual harm | Fraud detection, churn prediction, pricing | Pre-deploy + semi-annual |
| **T3 — Standard** | Internal tools; reversible decisions; low stakes | Demand forecasting, content tagging | Pre-deploy + annual |
| **T4 — Experimental** | R&D / sandbox; no production traffic | Prototypes, research models | Registration only |

**Escalation rule:** re-classify upward if: model output directly drives an automated action that affects a human, OR regulatory inquiry received, OR fairness disparate impact ratio < 0.80.

---

## Governance framework — 5 pillars

### 1. Inventory & registration
- All models registered in MLflow/Vertex/SageMaker Model Registry before any prod traffic
- Required metadata: risk tier, owner, use case, training data lineage, data sensitivity classification
- Registry review: quarterly inventory audit; deregister unused models

### 2. Pre-deploy review gates

| Gate | T1 | T2 | T3 |
|---|---|---|---|
| Fairness audit (`/fairness-audit`) | Required | Required | Recommended |
| Explainability report (`/explainability`) | Required | Required | Optional |
| Human review of sample outputs | Required (100 cases) | Recommended (25 cases) | Optional |
| Legal/privacy sign-off | Required | If PII | No |
| Model card | Required | Required | Recommended |
| Dual approval (owner + reviewer) | Required | Required | Owner only |

### 3. Monitoring & drift
- Data drift: PSI monitored weekly (T1/T2), monthly (T3) — see `/model-drift`
- Performance: primary metric tracked vs. baseline; alert at > threshold degradation
- Fairness: disparate impact ratio re-measured quarterly (T1), semi-annually (T2)
- Feature quality: freshness + null rate monitored — see `/feature-monitoring`

### 4. Incident response

| Severity | Trigger | Response SLA | Escalation |
|---|---|---|---|
| P1 | Bias/harm complaint; regulatory inquiry | 4h triage, 24h response | CISO + Legal |
| P2 | Performance degradation >20%; fairness threshold breach | 24h triage | ML Lead + Product |
| P3 | Drift alert; data quality issue | 72h triage | ML Lead |

All incidents → post-mortem within 2 weeks → governance register update.

### 5. Audit trail
- Every model version: training run ID, data version, gate results, approvers, deploy timestamp
- Immutable log: no edits; append-only
- Retention: 7 years for T1, 3 years for T2/T3 (adjust for jurisdiction)

---

## Model Risk Management (MRM) checklist

Pre-deploy (T1/T2):
- [ ] Model purpose and intended population documented
- [ ] Out-of-sample validation on held-out data (not CV fold)
- [ ] Stress test on edge cases and adversarial inputs
- [ ] Fairness audit completed (all protected attributes in scope)
- [ ] Explainability report reviewed by business owner
- [ ] Model card reviewed and signed
- [ ] Data lineage traceable to source
- [ ] Challenger model or benchmark identified
- [ ] Rollback plan documented
- [ ] Production monitoring dashboard live before deploy

Post-deploy (T1 quarterly, T2 semi-annual):
- [ ] Drift metrics within bounds
- [ ] Fairness metrics within bounds
- [ ] No unresolved P1/P2 incidents
- [ ] Champion/challenger comparison run
- [ ] Decommissioning criteria reviewed

---

## Intellectual property framing (process-as-IP)

A common mis-framing is to treat *the trained model* as the program's intellectual property. This is brittle and usually wrong:

- A model frozen as IP can't be retrained → goes stale → becomes useless
- The learning algorithm is almost always public-domain math (50+ years of published research)
- The model artifact alone is reproducible by anyone with the data + algorithm

The defensible IP is the **process**:
- Business-problem framing specific to the use case
- Data sourcing, collection mechanisms, consent posture
- Feature-engineering decisions and domain-specific transforms
- Algorithm tweaks and hyperparameter regime
- Evaluation and monitoring methodology
- The *integration* between model output and operational action

**SaaS data-upload clauses** — for every external platform that touches training data, confirm contractually:
1. Who owns the uploaded data?
2. Can the vendor train its own models on your data, or intermingle it with other tenants' data?
3. Who owns derivative models (those trained partially or fully on your data)?
4. What happens to data + models on contract termination?
5. Are model weights or embeddings exportable?

Default vendor contracts often grant the vendor broad rights — review explicitly. Indigenous Data Sovereignty and culturally-sensitive corpora require explicit additional consent posture; data ownership ≠ data sovereignty.

**Joint-project ownership** — academic and partner collaborations need pre-agreement on:
- Right to publish theoretical results (academic partner usually wants this)
- Domain-knowledge attribution
- Whether models trained on partner data can be reused on other projects
- Feature-engineering know-how sharing

**Indigenous Data Sovereignty** — data describing Indigenous peoples, lands, knowledge, or cultural practices is subject to community-level sovereignty rights, not only individual consent. Frameworks: CARE Principles (Collective Benefit, Authority to Control, Responsibility, Ethics); OCAP (Ownership, Control, Access, Possession — First Nations Canada). Flag any in-scope dataset at registration time.

Pair with `/ml-readiness` for the strategic framing, `/build-vs-buy` for component-level decisions.

---

## EU AI Act alignment (high-risk systems)

If T1 system in EU scope:
- Conformity assessment required before market placement
- Technical documentation per Annex IV
- Post-market monitoring plan mandatory
- Human oversight mechanism documented
- Logging: full audit trail of inputs/outputs (6-year retention)

Flag at risk tier classification if: biometric, employment, credit, education, law enforcement use case + EU data subjects.

---

## Review board structure

| Role | Responsibility |
|---|---|
| AI Risk Owner | Final sign-off on T1 pre-deploy |
| ML Lead | Technical gate reviewer |
| Data Privacy Officer | PII/GDPR compliance gate |
| Business Owner | Use case justification + outcome monitoring |
| Legal/Compliance | Regulatory applicability assessment |

Quorum for T1 approval: AI Risk Owner + ML Lead + DPO (minimum 3 of 5).

---

## Output

Deliver:
1. **Risk tier classification** — each model in scope with justification
2. **Governance gap analysis** — current state vs. framework requirements
3. **MRM checklist** — filled per tier
4. **Monitoring plan** — metrics, cadence, alert thresholds
5. **Review board charter** — roles, quorum, escalation paths
