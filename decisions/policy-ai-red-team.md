# ADR-0043: AI Red Team Policy

**Status:** Accepted  
**Domain:** [governance]  
**Date:** 2026-04-22

---

## Context

The workspace `/threat-model` command identifies AI-specific risks (prompt injection, data poisoning, excessive agency, supply chain, etc.) but produces no obligation to test against those risks. Without a formal policy, red teaming is ad hoc, inconsistently scoped, and frequently skipped under delivery pressure.

OWASP LLM Top 10 2025 introduced two new categories (LLM07: System Prompt Leakage; LLM08: Vector & Embedding Weaknesses) that are not covered by traditional application security testing. OWASP also released the Top 10 for Agentic Applications (2026) and a Gen AI Red Teaming Guide, establishing community consensus that structured adversarial testing is now a baseline expectation for production AI systems.

MITRE ATLAS v5.1.0 (November 2025) documents 84 techniques across 16 tactics used against AI/ML systems, including a new Command and Control tactic specifically targeting AI agents. This codified threat landscape requires a matching testing obligation.

---

## Decision

All AI features and systems will be classified by risk tier, and red team coverage requirements are determined by that tier. The `/red-team` command is the canonical tool for executing and documenting tests.

### Risk Tier Classification

| Tier | Criteria |
|------|----------|
| **HIGH** | Customer-facing; handles PII or sensitive data; agentic with external tool access; regulated domain (finance, healthcare, legal) |
| **MED** | Internal-facing; handles proprietary data; limited tool access; agentic but sandboxed |
| **LOW** | Internal tooling; no PII; no tool side effects; read-only outputs |

### Mandatory Coverage by Tier

| Phase | Test Scope | HIGH | MED | LOW |
|-------|-----------|------|-----|-----|
| Phase 1 | Base model: alignment, system prompt leakage, information disclosure | Required | Required | Required |
| Phase 2 | Application: injection, guardrail bypass, RAG/vector, output handling | Required | Required | Spot-check |
| Phase 3 | System: supply chain, resource exhaustion, multi-agent trust | Required | Spot-check | — |
| Phase 4 | Operational: social engineering, human-agent interaction, overreliance | Required | — | — |

Agentic systems of any tier must include the OWASP Agentic Top 10 battery regardless of the tier-based scope above.

### When Red Teaming is Mandatory

1. **Before initial production deployment** — all tiers; Phase 1+2 minimum
2. **After a prompt change** — re-run Phase 1+2 for affected categories; all tiers
3. **After a model version change** — full re-run; HIGH and MED tiers
4. **After adding a new tool or plugin** — re-run LLM03 (supply chain) + LLM06 (excessive agency); all tiers
5. **After a security incident or near-miss** — full re-run; all tiers
6. **Scheduled cadence** — HIGH: quarterly | MED: semi-annual | LOW: annual

### Ownership & Process

- **Owner:** The team deploying the AI feature owns red team execution. Security team provides tooling and review for HIGH tier systems.
- **Composition:** Effective red teams require cross-functional input — AI/ML engineers (know the system), security engineers (know the attack patterns), and at least one domain expert for HIGH tier systems.
- **Documentation:** All tests must be documented using the `/red-team` output format. Results are committed to the `/decisions/` directory as an appendix to the relevant system's ADR, or as a standalone findings log.
- **Findings tracking:** Every failed test becomes an open [RISK] with a severity label. HIGH findings block deployment. MED findings require a documented mitigation plan before deployment. LOW findings are advisory.
- **Closure:** A finding is closed when the fix is deployed and the test is re-run and passes.

### Tooling

| Tool | Role |
|------|------|
| `/red-team` (this workspace) | Test plan generation, documentation |
| [promptfoo](https://github.com/promptfoo/promptfoo) | Automated injection + output testing |
| [deepteam](https://github.com/confident-ai/deepteam) | Multi-turn red teaming, jailbreak coverage |
| Manual execution | System prompt leakage, excessive agency, cross-agent injection |

---

## Consequences

**Positive:**
- Structured, repeatable adversarial coverage aligned to OWASP LLM Top 10 2025 and ATLAS v5.1.0
- HIGH findings block deployment — no more "we'll fix it after launch"
- Findings are tracked to closure — not lost in Slack threads

**Negative:**
- Adds pre-deployment effort, especially for HIGH tier systems (Phase 1–4 coverage)
- Teams without a dedicated security function must run their own red team exercises — requires upskilling

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Rely on `/threat-model` alone | Identifies risks but does not verify mitigations are effective |
| Annual penetration test only | Too infrequent; misses prompt, model, and plugin changes between tests |
| Automated scanning only | Automation covers injection patterns well but misses agentic threats, social engineering, and overreliance scenarios |

---

## Related Decisions

- **ADR-0042** — Command Security Policy: red-team tabletop test for `/prompt-review` injection resistance is a recommended task from that ADR
- **ADR-0044** — Model Supply Chain & Provenance Policy: supply-chain findings (LLM03) feed directly into the red-team Phase 3 test battery; supply-chain changes trigger a re-run of LLM03 + LLM06 tests
- **ADR-0012 / ADR-0021 / ADR-0030** — Cloud Governance (Azure / AWS / GCP): content safety and guardrail breach scenarios in `/runbook` should be validated by red-team Phase 2 before go-live

---

## Risks Not Fully Mitigated

- [RISK: MED] Phase 4 (operational layer) tests require live-environment access that may not be available in pre-prod. Mitigation: staging environment must mirror production closely enough to be representative.
- [RISK: LOW] Automated tools (promptfoo, deepteam) generate false negatives for novel jailbreak techniques not in their attack libraries. Mitigation: supplement with manual red team on HIGH tier systems.
