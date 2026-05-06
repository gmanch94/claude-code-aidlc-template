# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = d48db7c**

---

## State

```
d48db7c  Improve CLAUDE.md placeholder framing for cloners — PR #23
21ab565  Update NEXT_SESSION.md — HEAD b3ca777, PR #22 merged
b3ca777  Update README and .gitignore for harness engineering additions — PR #22
ada0745  Update NEXT_SESSION.md — HEAD 9e3bb3a, PR #21 merged
9e3bb3a  Fill in scheduled routines placeholder in CLAUDE.md — PR #21
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of d48db7c)

---

## What landed in the most recent session

1. **Reference hooks** (PR #18): Three project-agnostic Python guardrail hooks in `.claude/hooks/` (none wired by default)
   - `block_dangerous_git.py` — PreToolUse/Bash: blocks force-push, reset --hard, --no-verify, etc.
   - `scan_secrets.py` — PreToolUse/Write|Edit: blocks known secret key shapes
   - `audit_log.py` — PostToolUse/*: passive logger to `.claude/logs/audit.jsonl`
   - `README.md` — protocol, wiring snippet, smoke tests, how-to-add guide
2. **Baseline permissions** (PR #19): `settings.json` pre-allows `Read`, `Glob`, `Grep`, and safe git read commands; added `$schema`; CLAUDE.md permissions note added
3. **Skill authoring guide** (PR #20): `templates/skill/SKILL-TEMPLATE.md` (annotated) + `REFERENCE-TEMPLATE.md`; CLAUDE.md repo structure updated
4. **Scheduled routines docs** (PR #21): CLAUDE.md placeholder filled with `/schedule` usage + 3 example patterns
5. **README + .gitignore** (PR #22): README table updated for hooks/permissions/skill template; hooks section rewritten; `.claude/logs/` gitignored
6. **CLAUDE.md placeholder framing** (PR #23): Source of truth marked optional; working conventions intro improved; tone intro clarified; redundant Automation `[Fill in]` line removed; example comment added

---

## Open items

- No open backlog items. Harness engineering sprint complete (PRs #18–21).

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master (new rule as of 2026-05-05)
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/hooks/` — 3 reference hooks + README (protocol, wiring snippet, smoke tests)
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
