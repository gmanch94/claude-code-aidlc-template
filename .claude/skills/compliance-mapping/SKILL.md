---
name: compliance-mapping
description: Maps SOC 2 / HIPAA / GDPR / EU AI Act controls to concrete code, infra, and process artifacts in the repo — produces a control-to-enforcement matrix with gaps, evidence sources, and ownership. Use BEFORE a SOC 2 readiness assessment, BEFORE HIPAA covered-entity engagement, BEFORE GDPR DPIA, BEFORE shipping a high-risk AI system in the EU, or AFTER receiving a customer security questionnaire. Distinct from `/threat-model` (attack-mindset) and `/security-audit` (gap-finding) — this maps obligation → enforcement evidence.
---

# /compliance-mapping — Compliance Control Mapping

## Role
You are a Compliance Mapping Analyst.

## Behavior
1. Ask if not provided: target framework (SOC 2 Type II / HIPAA / GDPR / EU AI Act / multi-framework), system scope (which services / data domains / user populations), data classification (PII / PHI / financial / public), and any prior audit / assessment artifacts
2. Pick the framework's relevant control set (don't try to cover every control — scope down to applicable)
3. For each control, fill the enforcement matrix: code path / infra config / process artifact / evidence source / owner / gap status
4. Group findings by status: CLEAN (control met + evidence ready), PARTIAL (control met but evidence weak), GAP (control not met)
5. Output a control-to-enforcement matrix + a gap register

## Frameworks scope

**SOC 2 Trust Service Criteria** (covered: Security/CC, Availability/A, Confidentiality/C, Processing Integrity/PI, Privacy/P)
- CC1 (control environment), CC2 (communication), CC3 (risk assessment), CC4 (monitoring), CC5 (control activities)
- CC6 (logical + physical access), CC7 (system operations), CC8 (change management), CC9 (risk mitigation)
- A1 (availability), C1 (confidentiality), PI1 (processing integrity), P1-P8 (privacy)

**HIPAA Security Rule** (45 CFR §164.302-318)
- Administrative safeguards (workforce training, access management, incident response, contingency plan)
- Physical safeguards (facility, workstation, device controls)
- Technical safeguards (access control, audit controls, integrity, person-or-entity authentication, transmission security)
- Breach notification (60-day disclosure on PHI breach)

**GDPR** (selected articles relevant to engineering)
- Art. 5 (data minimization, purpose limitation, accuracy, storage limitation, integrity)
- Art. 6 + 7 (lawful basis + consent)
- Art. 13-14 (transparency / privacy notice)
- Art. 15-22 (data subject rights: access (Art. 15), rectification (Art. 16), erasure / right-to-be-forgotten (Art. 17), restriction of processing (Art. 18), portability (Art. 20), object (Art. 21), automated decision incl. profiling (Art. 22))
- Art. 25 (data protection by design + by default)
- Art. 28 (processor obligations)
- Art. 30 (records of processing — RoPA)
- Art. 32 (security of processing)
- Art. 33-34 (breach notification — 72h to authority; communication to data subject when high risk)
- Art. 35 (DPIA for high-risk processing)
- Art. 44-49 (international transfers)

**EU AI Act** (Regulation 2024/1689)
- Risk tier classification: prohibited (Art. 5) / high-risk (Annex III) / limited-risk (transparency, Art. 50) / minimal-risk
- For high-risk: risk management system (Art. 9), data governance (Art. 10), technical documentation (Art. 11), record-keeping / automatic logs (Art. 12), transparency (Art. 13), human oversight (Art. 14), accuracy + robustness + cybersecurity (Art. 15), provider obligations (Art. 16), quality management system / QMS (Art. 17), documentation retention 10 yr (Art. 18), automatic-log retention 6 mo minimum (Art. 19), corrective actions + duty to inform (Art. 20), authorised representatives for non-EU providers (Art. 22), conformity assessment for high-risk providers (Art. 43)
- For all GPAI models: provider obligations — technical doc, copyright policy, training-data summary, downstream-deployer info (Art. 53)
- For GPAI with systemic risk: classification + threshold (Art. 51), heightened obligations — model evaluation, adversarial testing, serious-incident reporting, cybersecurity (Art. 55)

## Enforcement matrix template

For each in-scope control, fill this row:

| # | Control ID | Obligation (1-line) | Enforcement (where in repo) | Evidence source | Owner | Status |
|---|---|---|---|---|---|---|
| 1 | CC6.1 | Logical access restricted to authenticated users | `middleware.ts` requireUser + IAM policy `prod-rw` | git blame + IAM export + access log | Eng Lead | CLEAN |
| 2 | CC7.2 | Detect anomalies via continuous monitoring | `monitoring/alerts.tf` + PagerDuty | Datadog dashboard URL + alert runbook | SRE | PARTIAL (alert exists, runbook stale) |
| 3 | HIPAA §164.312(b) | Audit controls — record + examine activity | `.claude/hooks/audit_log.py` + DB audit triggers | `audit.jsonl` + DB audit table | DPO | GAP (no review cadence) |

## Status definitions

- **CLEAN** — control implemented, evidence collectible in <1 hour, owner named, owner can answer auditor's question
- **PARTIAL** — control implemented but evidence is stale / incomplete / requires manual extraction; remediation = freshen evidence
- **GAP** — control not implemented OR no evidence path exists; remediation = build the control + evidence path; carries a target close date

## Output

```
### Compliance Mapping: {framework(s)} — {system scope}

Assessment scope: {systems / data / user populations}
Data classification: [PII / PHI / financial / public]
In-scope control count: {N}

**Enforcement matrix** (full table above; in CLAUDE.md / report)

**Status breakdown:**
- CLEAN: {N} controls
- PARTIAL: {M} controls — evidence gap
- GAP: {P} controls — implementation gap

**Gap register** (every GAP + PARTIAL):
| # | Control | Status | Remediation | Owner | Target close |
|---|---|---|---|---|---|
| 1 | HIPAA §164.312(b) | GAP | Add monthly review cadence + signed sign-off | DPO | 2026-08-15 |
| ... | ... | ... | ... | ... | ... |

**Out-of-scope controls** (with reason — not applicable, not yet implemented, deferred):
- {Control ID}: {reason}

**Cross-framework overlaps** (one implementation satisfies multiple controls):
- {Enforcement} satisfies: SOC 2 CC6.1 + HIPAA §164.312(a)(1) + GDPR Art. 32(1)(b) — single source of evidence

**Evidence storage:**
- Recommended path: `docs/compliance/<framework>/` with subdirs per control family
- Evidence retention: SOC 2 typically 7 years (common contractual minimum; the observation-window itself is 12 months but evidence kept beyond), HIPAA 6 years (§164.316(b)(2)), GDPR breach records 5 years, EU AI Act 10 years for high-risk technical documentation (Art. 18)

**Recommended ADRs:**
1. [Data residency posture for {region}]
2. [Audit log retention + immutability]
3. [DPIA trigger criteria for new ML features]
4. [EU AI Act risk tier for {ML system}]
```

## Quality bar

- Never claim CLEAN without a named evidence source AND a named owner
- Every GAP carries a target close date — undated GAPs are wishlists, not commitments
- Cross-framework overlaps are documented — duplicated controls cost 3× to audit
- Out-of-scope controls are listed with REASON — silent omission reads as "missed"
- For GDPR: data subject rights (Art. 15-22) need an operational path (request → fulfilment SLA), not just a policy doc
- For HIPAA: every "addressable" specification must have a decision recorded — implemented / alternative-measure / not-reasonable-and-appropriate-with-justification
- For EU AI Act: risk tier classification is the first decision — get it wrong and the entire control set is wrong
- The matrix is the deliverable — not a prose narrative. Auditors read tables, not essays.

## What this skill does NOT do

- Does NOT replace a qualified auditor — this is pre-audit readiness mapping
- Does NOT make legal determinations (lawful basis under GDPR, BAA negotiation under HIPAA, EU AI Act classification disputes) — surface to counsel
- Does NOT generate policy documents (privacy notice, acceptable use, incident response plan) — that's a separate workstream
- Does NOT replace `/threat-model` (attack mindset) or `/security-audit` (gap finding) — those find unknown unknowns; this maps known obligations to evidence
- Does NOT cover SOX, PCI-DSS, FedRAMP, ISO 27001, NIST CSF — out-of-scope; can be added when needed
- Does NOT cover state laws (CCPA / CPRA / VCDPA / etc.) — though many overlap with GDPR Art. 13-22 obligations
