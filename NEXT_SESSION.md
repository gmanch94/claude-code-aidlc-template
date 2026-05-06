# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = d9eda2f**

---

## State

```
d9eda2f  Add wave-2 guardrail hooks: infra destroy, SQL safety, unsafe patterns — PR #24
24c51c1  Update NEXT_SESSION.md — HEAD d48db7c, PR #23 merged
d48db7c  Improve CLAUDE.md placeholder framing for cloners — PR #23
21ab565  Update NEXT_SESSION.md — HEAD b3ca777, PR #22 merged
b3ca777  Update README and .gitignore for harness engineering additions — PR #22
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of d48db7c)

---

## What landed in the most recent session

1. **Wave-2 guardrail hooks** (PR #24): Three additional PreToolUse hooks in `.claude/hooks/`
   - `block_infra_destroy.py` — PreToolUse/Bash: blocks terraform destroy, kubectl mass-delete, AWS/GCP/Azure destructive CLI commands. No escape hatch.
   - `check_sql_safety.py` — PreToolUse/Bash+Write|Edit: blocks DROP TABLE without IF EXISTS, TRUNCATE, DELETE FROM without WHERE. Test/seed paths downgrade to warning.
   - `check_unsafe_patterns.py` — PreToolUse/Write|Edit: OWASP A02/A03/A05/A08 + XSS patterns. Per-line `# nosec` opt-out. Test/docs paths downgrade HIGH→WARN.
   - `README.md` — inventory table, wiring snippet, and smoke tests updated for all 6 hooks

---

## Open items

- No open backlog items. Guardrail hook set now complete (6 hooks total: PRs #18, #24).

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master (new rule as of 2026-05-05)
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/hooks/` — 6 reference hooks + README (protocol, wiring snippet, smoke tests)
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
