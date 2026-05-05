---
name: review
description: Code review with BLOCKER/SUGGESTION/NITPICK grading across correctness, security, performance, clarity, and test coverage. Use when reviewing code changes, a file, a diff, or staged changes before merging.
---

# /review — Code Review

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
