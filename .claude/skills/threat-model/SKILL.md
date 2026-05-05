---
name: threat-model
description: AI-specific threat modeling covering 8 mandatory categories: prompt injection, data poisoning, model extraction, PII leakage, jailbreak, hallucination exploitation, supply chain, and excessive agency. Use when a user describes an AI system architecture, asks about security, or before production deployment of any AI system.
---

# /threat-model — AI System Threat Model

## Behavior
1. Ask if not provided: system name, where untrusted input enters, risk tier (LOW/MED/HIGH), whether agentic, known sensitive data flows
2. Assess all 8 AI-specific threat categories — "not applicable" with reason is acceptable; blank is not
3. Rate each: [RISK: HIGH/MED/LOW]
4. Recommend mitigations; flag which need ADRs
5. HIGH tier → flag that `/red-team` is required before production

## 8 Categories (always cover all)
1. Prompt injection — direct (user input) and indirect (tool output, retrieved content)
2. Data poisoning — training-time and retrieval-time
3. Model extraction / IP theft
4. PII leakage — via prompt, output, or model memorization
5. Jailbreaking / policy bypass
6. Hallucination exploitation — adversarial queries for confident-wrong outputs
7. Supply chain — model provider, embedding API, vector store, plugins
8. Excessive agency — agentic systems taking unintended irreversible actions

## Output
See [REFERENCE.md](REFERENCE.md) for full threat register and output format.

## Quality bar
- Indirect prompt injection assessed separately from direct — different mitigations
- Excessive agency is always [RISK: HIGH] for agentic systems without documented HITL or scope controls
- A HIGH finding without a mitigation is incomplete — ask how the user plans to address it
