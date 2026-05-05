# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = 4607731**

---

## State

```
4607731  Merge pull request #4 — Add specialist personas to all 67 skills
c025b9d  Add specialist personas to all 66 skills (SKILL.md + README + CLAUDE.md)
7e4d67c  Update NEXT_SESSION.md — master, HEAD 6aeda01, session close
6aeda01  Merge pull request #3 — Add sprint workflow + /office-hours skill
1728824  Add sprint workflow + /office-hours skill (assumptions gate)
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 4607731)

---

## What landed in the most recent session

1. **Specialist personas** — all 67 SKILL.md files now have `## Role` with a task-anchored functional title
2. **README + CLAUDE.md** — every skill entry prefixed with `**Persona** —` for AIDLC mindset reinforcement
3. Role names are durable (task-domain, not job-title): ADR Facilitator, RAG System Architect, Data Leakage Auditor, etc.

---

## Open items

- [ ] **Stack add-ons** — `stacks/` currently has Python only; TypeScript/Go stacks could be added

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
