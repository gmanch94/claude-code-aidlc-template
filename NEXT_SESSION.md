# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = 6aeda01**

---

## State

```
6aeda01  Merge PR #3 — Add sprint workflow + /office-hours skill
1728824  Add sprint workflow + /office-hours skill (assumptions gate)
de1221c  Merge PR #2 — Add /retro skill and prompt template
f97048a  Update NEXT_SESSION.md — master, HEAD 15bd13a
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of beabe68)

---

## What landed in the most recent session

1. **Sprint workflow** — 6-step order added to `CLAUDE.md` (assumptions → plan → implement → review → ship → retro)
2. **`/office-hours` skill** — `.claude/skills/office-hours/SKILL.md`; assumptions gate with six forcing questions and design doc output
3. **`/retro` skill** — `.claude/skills/retro/SKILL.md`; structured retro with LESSONS_LEARNED.md integration
4. **`prompts/retro.md`** — system prompt template for retro facilitator

---

## Open items

- [ ] **Stack add-ons** — `stacks/` currently has Python only; TypeScript/Go stacks could be added
- [ ] **gstack philosophy** — item 5 (specialist personas) not yet brought in

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
