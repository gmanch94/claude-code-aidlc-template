# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = 15bd13a**

---

## State

```
e905c4c  Add Confusion Protocol + Karpathy failure modes to CLAUDE.md
a011259  Fix README: update prompt count to 54, fix commands→skills paths
beabe68  Add general ADRs: LangGraph orchestration + Claude enterprise rollout
ac2a9b2  Add Argus ADRs from ai-enablement-ws
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of beabe68)

---

## What landed in the most recent session

1. **README audit** — prompt count corrected (8→54); `.claude/commands/` paths fixed to `.claude/skills/<name>/SKILL.md`
2. **CLAUDE.md** — added Confusion Protocol (halt on ambiguous decisions, ask instead of guessing) and Karpathy's four failure modes (wrong assumptions, overcomplexity, orthogonal edits, imperative over declarative)
3. Both changes on branch `fix/readme-audit` — PR not yet opened

---

## Open items

- [ ] **Open PR** — `fix/readme-audit` branch has 2 commits; open PR to merge into master
- [ ] **Stack add-ons** — `stacks/` currently has Python only; TypeScript/Go stacks could be added
- [ ] **gstack philosophy** — items 2 (sprint order), 4 (`/retro` skill), 5 (specialist personas) not yet brought in

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
