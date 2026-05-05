---
name: pii-scan
description: Audits PII exposure across 10 AI data lifecycle stages (ingest, preprocess, embed, store, retrieve, prompt, generate, log, cache, export) and surfaces governance gaps. Use when a user describes an AI system data flow, asks about privacy or PII handling, or before production deployment of any system handling personal data.
---

# /pii-scan — PII Exposure Audit

## Behavior
0. Ask user to redact real values — replace with `[API_KEY]`, `[USER_EMAIL]`, etc. Need categories and flows, not real data.
1. Extract all data elements mentioned or implied
2. Map each across the 10 AI data lifecycle stages
3. Assign risk level per intersection (HIGH / MED / LOW)
4. Recommend mitigations for all MED and HIGH intersections
5. Surface governance gaps as [RISK]; recommend ADRs for undocumented decisions

## AI Data Lifecycle Stages
Ingest → Preprocess → Embed → Store → Retrieve → Prompt → Generate → Log/Trace → Cache → Export/Downstream

## PII Categories
- Direct identifiers: name, email, phone, SSN, account number
- Quasi-identifiers: DOB, ZIP, job title (linkable in combination)
- Sensitive attributes: health, financial, legal, political, religious
- Behavioral / inferred: usage patterns, LLM-inferred attributes
- Credentials: passwords, API keys, tokens (treat as PII-equivalent)

## Risk levels
- **HIGH** — PII directly exposed with no controls, or controls manual/undocumented
- **MED** — PII present behind a control that could fail or isn't systematically enforced
- **LOW** — PII present but adequately controlled and documented

## Quality bar
- Credentials = PII — don't exclude because "they're not personal data"
- Third-party LLM API receiving user data always requires DPA assessment
- "We don't log PII" is not a control — ask what enforcement mechanism prevents it
- Cross-dataset re-identification risk: two low-PII datasets joined may produce a high-PII result

See [REFERENCE.md](REFERENCE.md) for full output format and governance checklist.
