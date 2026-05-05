---
name: model-card
description: Generates model documentation cards covering intended use, training data, evaluation results, limitations, risks, and governance status. Use when documenting a model for production deployment, compliance review, or handoff to another team.
---

# /model-card — Model Card

## Behavior
1. Ask if not provided: model name/version, use case, training data summary, known limitations, production owner
2. Generate all 9 sections — write "Not yet assessed [TODO]" if data genuinely unavailable; never leave blank
3. Flag governance gaps as [RISK]
4. Recommend storing in `/decisions/` or `/model-cards/`

## 9 Sections
1. **Model overview** — ID, type, framework, hosting, version, last updated
2. **Intended use** — primary use cases, out-of-scope uses (specific), target users, prohibited uses
3. **Training & fine-tuning data** — sources, date range, PII handling, consent status
4. **Evaluation results** — benchmark/eval × score × baseline × date (flag [RISK: HIGH] if missing)
5. **Known limitations & failure modes** — concrete weaknesses, not vague disclaimers
6. **Risks & mitigations** — risk × severity × mitigation in place
7. **Governance** — PII policy, retention, audit logging, HITL, incident response, DPA, AI governance approval
8. **Versioning & change history** — version × date × change summary × approved by
9. **Ownership & contact** — model owner, on-call, user feedback channel

## Quality bar
- No eval results = [RISK: HIGH] — recommend `/eval-design` before deployment
- "Not yet assessed [TODO]" is acceptable; blank fields are not
- Out-of-scope uses must be specific — "not for high-stakes decisions" is not specific enough
- Update on: model version changes, fine-tuning, new failure mode discovery, governance changes
