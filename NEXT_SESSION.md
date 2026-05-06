# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = 60d1de3**

---

## State

```
60d1de3  Add data engineering script templates: ETL, validation, split/dedup, schema diff — PR #27
ad269bc  Update NEXT_SESSION.md — HEAD 6496091, PR #26 merged
6496091  Add wave-4 AIDLC guardrail hooks: ML leakage and prompt safety — PR #26
b0e05b7  Update NEXT_SESSION.md — HEAD 64eecbc, PR #25 merged
64eecbc  Add wave-3 guardrail hooks: cloud cost and Python programming gotchas — PR #25
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of d48db7c)

---

## What landed in the most recent session

1. **Data engineering templates** (PR #27): `templates/data-engineering/` with 4 Python script starters
   - `etl_pipeline.py` — extract → validate → transform → load skeleton; structured logging; CLI entry-point
   - `data_validation.py` — schema, null-rate, uniqueness, range, referential checks; `ValidationReport`; raises on CRITICAL
   - `split_dedup.py` — hash-based dedup + stratified train/val/test split + overlap assertion
   - `schema_diff.py` — diffs two DataFrames/schemas; breaking vs non-breaking classification; `--strict` CLI flag
   - `README.md` — template table, design principles, explicit out-of-scope list

---

## Open items

- **Backlog:** Full data engineering project scaffold (separate repo) — opinionated starter with dependencies, config, tests, CI. Broader scope than this template repo; build as its own repo when prioritised.

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master (new rule as of 2026-05-05)
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/hooks/` — 10 reference hooks + README (protocol, wiring snippet, smoke tests)
- `templates/data-engineering/` — 4 DE script templates (ETL, validation, split/dedup, schema diff)
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
