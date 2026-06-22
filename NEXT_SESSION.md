# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-06-22. **Current branch:** `master`. **Tree:** clean. **HEAD = cd864f5**

---

## State

```
cd864f5  feat(skills+prompts): add Databricks + OAuth/OIDC skills, backfill advisor prompt templates [skip ci]
1c32d55  feat(skills+prompts): add 5 Crown OT/industrial skills + prompt templates [skip ci]
fe9a816  feat(docs+hooks+prompts): wire 7 new skills into README/CLAUDE.md + 7 prompt templates + 3 new ML hooks
87751fc  feat(skills): add 7 skills + enhance 5 from Data-for-ML and Optimizing-ML-Performance courses — PR #30
0c99e27  docs: lesson — PR descriptions are ephemeral; operator actions belong in a file — PR #29
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date)

---

## What landed since the prior bookmark (60d1de3 → cd864f5)

1. **Security pair** (PR #28): `/security-audit` + `/security-model-init` skills + `templates/security-model/SECURITY_MODEL-TEMPLATE.md`
2. **PR-description lesson** (PR #29): operator actions belong in a file, not a PR body — added to LESSONS_LEARNED.md
3. **Data-for-ML / Optimizing-ML wave** (PR #30): 7 new skills + 5 enhancements
4. **7-skill wire-up** (fe9a816): 7 prompt templates + 3 new ML guardrail hooks; extended `check_ml_leakage`
5. **Crown OT/industrial** (1c32d55): 5 skills covering UNS, IIoT ingestion, predictive maintenance, edge ML, lakehouse
6. **Databricks + OAuth/OIDC** (cd864f5): 8 Databricks skills + 7 auth skills + matching prompts

---

## Open items

- **Backlog:** Full data engineering project scaffold (separate repo) — opinionated starter with deps, config, tests, CI. Build as its own repo when prioritised.
- **Backlog tier-2 skills** (from 2026-06-22 holistic review): `/vertex-ai-design`, `/sagemaker-design`, `/terraform-review`, `/compliance-mapping`, `/dashboard-design`. Adjacent extensions; pick when needed.

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/hooks/` — **13** reference hooks (3 generic: git/secrets/audit + 10 domain: cloud-cost/SQL/ML-leakage/PII/prompt-safety/etc.) + README (protocol, wiring snippet, smoke tests)
- `templates/data-engineering/` — 4 DE script templates (ETL, validation, split/dedup, schema diff)
- `templates/skill/` — annotated SKILL-TEMPLATE.md + REFERENCE-TEMPLATE.md
- `templates/security-model/` — SECURITY_MODEL-TEMPLATE.md (stack-specific scaffolding)
- `.claude/skills/` — **125** skills; each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — **137** prompt templates; `README.md` is the index
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills + stacks; keep in sync
- `stacks/` — Python, TypeScript, Go stack add-ons; each has `/test-gen`, `/type-fix`, `/deps-audit`
- `context/` — Claude's persistent memory; `MEMORY.md` is the index
- `.gitattributes` — LF normalization
- `decisions/` — 21 ADRs (OSS, policy, Argus, general); no sequence numbers
- `templates/adr/ADR-TEMPLATE.md` — ADR template
- `.github/workflows/doc-ci.yml` — doc-CI gate: count drift + relative-link validity + skill↔prompt parity (added 2026-06-22)

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.
