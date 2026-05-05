# /threat-model — Reference

## Output Format

### Threat Model: [System Name]
**Date:** [today]
**Risk Tier:** [LOW / MED / HIGH]
**Scope:** [in / out of scope]
**Trust boundary:** [where untrusted input enters]
**Agentic:** [Yes / No]

---

#### Threat Register

| # | Category | Threat | Risk | Mitigation | ADR Needed? |
|---|----------|--------|------|------------|-------------|
| 1 | Prompt injection (direct) | | | | |
| 2 | Prompt injection (indirect) | | | | |
| 3 | Data poisoning | | | | |
| 4 | PII leakage | | | | |
| 5 | Jailbreak / policy bypass | | | | |
| 6 | Hallucination exploitation | | | | |
| 7 | Supply chain | | | | |
| 8 | Excessive agency | | | | |
| 9 | [System-specific] | | | | |

---

#### Open Risks (HIGH only)

| Risk | Blocking Production? | Owner | Due |
|------|---------------------|-------|-----|

---

#### Recommended Next Steps
- [ ] ADRs to create: [list]
- [ ] `/pii-scan` recommended: [Yes / No]
- [ ] `/red-team` required before production: [Yes if HIGH tier]
- [ ] `/supply-chain-review` recommended: [Yes for any system using external models]
