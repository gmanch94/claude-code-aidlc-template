---
name: prompt-review
description: Reviews LLM prompts across 9 dimensions: clarity, injection risk, role/persona, output format, token efficiency, hallucination surface, fallback behavior, PII sensitivity, and versioning. Use when a user shares a system prompt, asks to review or improve a prompt, or when prompt quality issues are suspected.
---

# /prompt-review — Prompt Health Review

## Behavior
1. Ask user to redact real API keys, PII, and proprietary data before sharing
2. Assess across 9 dimensions — flag as [BLOCKER] / [SUGGESTION] / [NITPICK]
3. Surface findings first; suggest rewrites only for BLOCKERs and only on request

## 9 Dimensions

| # | Dimension | BLOCKER condition |
|---|-----------|------------------|
| 1 | **Clarity** | Instruction has two valid contradictory interpretations |
| 2 | **Injection risk** | User input interpolated without trust boundary; no indirect injection guard |
| 3 | **Role & persona** | Persona claims authority it shouldn't have ("licensed professional") |
| 4 | **Output format** | Downstream code parses output but format not constrained in prompt |
| 5 | **Token efficiency** | Instructions repeated more than once (SUGGESTION) |
| 6 | **Hallucination surface** | No "I don't know" instruction on a factual task |
| 7 | **Fallback behavior** | No out-of-scope instruction; model will attempt anything |
| 8 | **PII / sensitivity** | Prompt instructs model to include personal data verbatim in output |
| 9 | **Version & ownership** | No version ID and no owner (LOW — always flag, not a blocker) |

## Output

```
### Prompt Review: [name]
**Overall health:** GREEN / AMBER / RED

| Dimension | Status |
|-----------|--------|
| Clarity | ✓ / ⚠ / ✗ |
| Injection risk | ✓ / ⚠ / ✗ |
| ... | |

#### Blockers
#### Suggestions  
#### Nitpicks
```

## Quality bar
- Never rewrite the full prompt unprompted — surface findings first
- Injection risk must always be assessed — indirect injection is easy to miss
- For template prompts: assess injection risk at every variable substitution point
