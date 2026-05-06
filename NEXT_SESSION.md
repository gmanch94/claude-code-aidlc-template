# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = 0f7978f**

---

## State

```
0f7978f  Add reference hook examples (.claude/hooks/) — PR #18
defa6f7  Update NEXT_SESSION.md — HEAD c26cb40, session end
c26cb40  Update NEXT_SESSION.md — HEAD 4c92d57, staleness sweep complete
4c92d57  Fix stale counts and paths in NEXT_SESSION.md files-of-note section
3d3794e  Merge pull request #17 — Rename memory/ to context/
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 0f7978f)

---

## What landed in the most recent session

1. **Reference hooks** (PR #18): Three project-agnostic Python guardrail hooks in `.claude/hooks/` (none wired by default)
   - `block_dangerous_git.py` — PreToolUse/Bash: blocks force-push, reset --hard, --no-verify, etc.
   - `scan_secrets.py` — PreToolUse/Write|Edit: blocks known secret key shapes
   - `audit_log.py` — PostToolUse/*: passive logger to `.claude/logs/audit.jsonl`
   - `README.md` — protocol, wiring snippet, smoke tests, how-to-add guide
   - CLAUDE.md hooks placeholder replaced with inventory + opt-in note

---

## Open items

Harness engineering gaps (doing one at a time):
- [x] Reference hooks — PR #18
- [ ] Baseline permissions — pre-populate `settings.json` with common safe allowlist
- [ ] SKILL.md authoring guide — local reference for how this repo's skills are structured
- [ ] Scheduled routines — fill CLAUDE.md automation placeholder with example cron pattern

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master (new rule as of 2026-05-05)
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/hooks/` — 3 reference hooks + README (protocol, wiring snippet, smoke tests)
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
