# Skill: /review — Code Review

## Trigger
User runs `/review` followed by a file path, diff, PR description, or "staged changes."

## Behavior
1. Read the target (file, diff, or `git diff --staged` output)
2. Check across five dimensions:
   - **Correctness** — logic errors, off-by-one, null handling, race conditions
   - **Security** — OWASP top 10: injection, XSS, auth bypass, insecure deserialization, secrets in code
   - **Performance** — N+1 queries, unnecessary allocations, blocking I/O in hot paths
   - **Clarity** — naming, function length, dead code, comments that explain what instead of why
   - **Test coverage** — missing cases, over-mocked tests that can't catch real failures
3. Classify each finding: [BLOCKER] / [SUGGESTION] / [NITPICK]
4. End with a verdict and one sentence on the most important thing to address

## Output format

### Review: [target]

**Verdict:** Approve / Request changes / Needs discussion

#### Blockers (must fix before merge)
- [BLOCKER] `file.ts:42` — [description and why it matters]

#### Suggestions (worth fixing, not blocking)
- [SUGGESTION] `file.ts:17` — [description]

#### Nitpicks (optional, low stakes)
- [NITPICK] `file.ts:8` — [description]

**Most important:** [one sentence on what to address first if time is limited]

## Quality bar
- A security finding is always [BLOCKER] regardless of exploitability estimate — don't downgrade it
- "Works on my machine" is not a mitigation for a race condition — flag it
- If there are no blockers, say so explicitly rather than listing only suggestions
- If the diff is too large to review meaningfully, say so and ask for it to be split
