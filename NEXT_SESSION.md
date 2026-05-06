# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = 026b459**

---

## State

```
026b459  Merge pull request #13 — Add TypeScript and Go stacks
61f8162  Add TypeScript and Go stacks: test-gen, type-fix, deps-audit + settings + addenda
a3e532c  Update NEXT_SESSION.md — HEAD 6be74e6, PR #12 merged
6be74e6  Merge pull request #12 — Add 5 deferred skills
74e4d7d  Add 5 deferred skills: causal-inference, survival-analysis, computer-vision, online-learning, data-mesh
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 4e8635f)

---

## What landed in the most recent session

1. **README headline** (PR #11): Updated to lead with AIDLC angle
2. **5 deferred skills** (PR #12): `/causal-inference`, `/survival-analysis`, `/computer-vision`, `/online-learning`, `/data-mesh` — each with SKILL.md + prompt template
3. **TypeScript stack** (PR #13): `/test-gen` (Vitest/Jest), `/type-fix` (tsc/eslint), `/deps-audit` (npm/pnpm audit) + settings-snippet + CLAUDE.md addendum
4. **Go stack** (PR #13): `/test-gen` (table-driven), `/type-fix` (go build/vet/staticcheck), `/deps-audit` (govulncheck) + settings-snippet + CLAUDE.md addendum

---

## Open items

- No open backlog items.

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master (new rule as of 2026-05-05)
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/skills/` — 65+ skills; each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — 50+ prompt templates; `README.md` is the index
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills; keep in sync
- `stacks/python/` — Python stack add-on; `/test-gen`, `/type-fix`, `/deps-audit`
- `.gitattributes` — LF normalization
- `decisions/` — 21 ADRs (OSS, policy, Argus, general); no sequence numbers
- `templates/adr/ADR-TEMPLATE.md` — ADR template

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.
