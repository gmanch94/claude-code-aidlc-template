# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = 64eecbc**

---

## State

```
64eecbc  Add wave-3 guardrail hooks: cloud cost and Python programming gotchas — PR #25
638b844  Update NEXT_SESSION.md — HEAD d9eda2f, PR #24 merged
d9eda2f  Add wave-2 guardrail hooks: infra destroy, SQL safety, unsafe patterns — PR #24
24c51c1  Update NEXT_SESSION.md — HEAD d48db7c, PR #23 merged
d48db7c  Improve CLAUDE.md placeholder framing for cloners — PR #23
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of d48db7c)

---

## What landed in the most recent session

1. **Wave-3 guardrail hooks** (PR #25): Two additional PreToolUse hooks in `.claude/hooks/`
   - `check_cloud_cost.py` — PreToolUse/Write|Edit: warns on expensive EC2/EKS families (p4d, p3dn, x1e, u-*tb1), high-cost RDS classes, `deletion_protection = false`, `publicly_accessible = true`. Warn-only; `# cost-ok` opt-out.
   - `check_programming_gotchas.py` — PreToolUse/Write|Edit: blocks Python mutable default args, bare `except:`, `== None` comparison. `.py` only; test paths downgrade to warning; `# nosec` opt-out.
   - `README.md` — inventory, wiring snippet, and smoke tests updated for all 8 hooks

---

## Open items

- No open backlog items. Guardrail hook set now at 8 hooks (PRs #18, #24, #25).

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master (new rule as of 2026-05-05)
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/hooks/` — 8 reference hooks + README (protocol, wiring snippet, smoke tests)
- `templates/skill/` — annotated SKILL-TEMPLATE.md + REFERENCE-TEMPLATE.md
- `.claude/skills/` — 70+ skills; each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — 59 prompt templates; `README.md` is the index
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills + stacks; keep in sync
- `stacks/` — Python, TypeScript, Go stack add-ons; each has `/test-gen`, `/type-fix`, `/deps-audit`
- `context/` — Claude's persistent memory; `MEMORY.md` is the index
- `.gitattributes` — LF normalization
- `decisions/` — 21 ADRs (OSS, policy, Argus, general); no sequence numbers
- `templates/adr/ADR-TEMPLATE.md` — ADR template

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.
