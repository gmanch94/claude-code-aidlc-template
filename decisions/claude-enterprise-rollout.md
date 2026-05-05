# ADR-0031: Claude Enterprise Rollout Strategy

**Status:** Proposed  
**Domain:** `[llm]` `[governance]`  
**Date:** 2026-04-19  
**Author:** AI Architect

---

## Context

The enterprise is adopting Claude (Anthropic) as the primary LLM across multiple cross-functional use cases: developer productivity (Claude Code), internal knowledge Q&A (RAG over internal docs), and workflow automation. Starting with a single-team pilot (~10–50 users) to validate quality, cost model, and governance posture before scaling.

Risk tier is **MED**: internal users, some sensitive data (code, internal docs), meaningful productivity impact if quality is poor or service degrades.

A structured phased rollout is required to:
1. Validate output quality without user-facing risk (shadow mode)
2. Catch production-specific issues before wide exposure (canary)
3. Validate cost model before committing to enterprise licensing
4. Satisfy governance requirements (audit trail, PII handling, AUP)

---

## Decision

Adopt a **5-phase phased rollout** for Claude enterprise deployment, starting with a single-team pilot:

**Shadow → Internal Dogfood → Canary → Limited GA (Pilot) → Full GA**

Full rollout plan: `/context/claude-rollout-plan.md`

Phase transitions require explicit approver sign-off (Engineering Lead / CISO) with numeric gate criteria met.

---

## Consequences

**Positive:**
- Catches quality, cost, and compliance issues before wide user impact
- Builds internal confidence and evidence base for Full GA business case
- Governance artifacts (model card, PII scan, runbook) produced as byproduct
- Rollback path defined and tested at every phase

**Negative:**
- Shadow + dogfood phases add 4 weeks before any user value is delivered
- Feature flag and traffic-split infrastructure required upfront
- Eval framework must be defined before Phase 1 — adds planning overhead

**Risks:**
- [RISK] Pilot cohort is unrepresentative — cross-functional use cases may behave differently at scale
- [RISK] Cost model validated at pilot scale may not hold at enterprise scale (token usage patterns differ)
- [RISK] Prompt/model version pinning adds operational overhead if Anthropic releases breaking changes

---

## Alternatives Considered

### 1. Big-bang rollout (direct to all users)
Rejected. MED risk tier requires phased validation. No rollback path; compliance exposure if PII handling is misconfigured.

### 2. Canary-only (skip shadow + dogfood)
Rejected. Cross-functional use cases have heterogeneous quality profiles — shadow mode needed to baseline each task type before user exposure.

### 3. Department-level pilot (500+ users from the start)
Rejected. Blast radius too large for first deployment. Single-team pilot limits incident scope and simplifies governance review.

---

## Follow-on ADRs

| ADR | Decision Needed |
|-----|----------------|
| ADR-0032 | Feature flag / traffic split mechanism |
| ADR-0033 | PII handling and data classification for Claude inputs/outputs |
