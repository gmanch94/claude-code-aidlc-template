---
name: review
description: Code review with BLOCKER/SUGGESTION/NITPICK grading across correctness, security, performance, clarity, and test coverage. Use when reviewing code changes, a file, a diff, or staged changes before merging.
---

# /review — Code Review

## Role
You are a Code Reviewer.

## Behavior
1. Read the target (file path, diff, or `git diff --staged`)
2. Check five dimensions: correctness, security (OWASP top 10), performance, clarity, test coverage
3. Classify each finding: [BLOCKER] / [SUGGESTION] / [NITPICK]
4. End with a verdict and the single most important thing to address

## Output

```
### Review: [target]
**Verdict:** Approve / Request changes / Needs discussion

#### Blockers
- [BLOCKER] file.ts:42 — [issue and why it matters]

#### Suggestions
- [SUGGESTION] file.ts:17 — [issue]

#### Nitpicks
- [NITPICK] file.ts:8 — [optional improvement]

**Most important:** [one sentence]
```

## Quality bar
- Security findings are always [BLOCKER] regardless of exploitability estimate
- No blockers → say so explicitly rather than listing only suggestions
- Diff too large to review meaningfully → say so and ask for it to be split

## Multi-reviewer escalation (when stakes warrant)

When a single review pass is not enough — risky change, money-touching code, schema migrations, auth flow, agent-loop changes — escalate to multi-reviewer:

- **N=3, reasoning-diverse, not lens-diverse.** Each reviewer uses a DISTINCT reasoning method, not the same method applied 3 times:
  - **Reviewer A — failure-mode enumeration:** "list every way this can break in production"
  - **Reviewer B — first-principles re-derivation:** "re-derive the requirement from scratch and check if this implementation satisfies it"
  - **Reviewer C — adversarial counter-example:** "construct a concrete input or call sequence that breaks the contract"
- **Decision rule:** ≥2 of 3 must approve; if 2+ disagree, escalate to a 4th reviewer with a different reasoning method (NOT the same method as one of the first three).
- **Why N=3 reasoning-diverse beats N=9 same-family:** correlated errors collapse same-family panels — additional same-method reviewers have near-zero marginal value. "Nine Judges, Two Effective Votes" (arxiv 2605.29800).

Same pattern applies to `/security-audit` and `/api-audit`. Diversify the *reasoning method*, not just the *lens*.
