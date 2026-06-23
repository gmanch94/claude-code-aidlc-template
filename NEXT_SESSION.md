# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-06-22. **Current branch:** `master`. **Tree:** clean. **HEAD = 2721b08**

---

## State

```
2721b08  Tier-2 skills: vertex-ai, sagemaker, terraform-review, compliance-mapping, dashboard-design (#32)
a3edb60  Holistic review: stale-check + /doc-ci-check + /mcp-design (#31)
cd864f5  feat(skills+prompts): add Databricks + OAuth/OIDC skills, backfill advisor prompt templates [skip ci]
1c32d55  feat(skills+prompts): add 5 Crown OT/industrial skills + prompt templates [skip ci]
fe9a816  feat(docs+hooks+prompts): wire 7 new skills into README/CLAUDE.md + 7 prompt templates + 3 new ML hooks
```

Remote: https://github.com/gmanch94/claude-code-aidlc-template (master, up to date)

---

## What landed since the prior bookmark (cd864f5 → 2721b08)

1. **Holistic review wave** (PR #31): cleanup (NEXT_SESSION + README + CLAUDE.md staleness, 21 missing skill rows in README); `/doc-ci-check` skill + `.github/workflows/doc-ci.yml` (CI gate for count drift, broken links, skill↔prompt↔index parity); `/mcp-design` skill + prompt; 3 CI follow-up commits during the loop
2. **Tier-2 skills wave** (PR #32): 5 new skills with full 5-artifact rule satisfied each
   - `/vertex-ai-design` — GCP Vertex AI footprint
   - `/sagemaker-design` — AWS SageMaker footprint
   - `/terraform-review` — IaC reviewer (Terraform-specific)
   - `/compliance-mapping` — SOC 2 / HIPAA / GDPR / EU AI Act controls → enforcement matrix
   - `/dashboard-design` — BI dashboard spec (Looker/Tableau/Superset/Metabase tool-agnostic)
3. **Independent-reviewer loop applied** to PR #32: 3 rounds of cold-eyes review (domain accuracy + skill consistency lenses), converged on R3, R4 verified ship-quality

---

## Open items

- **Backlog:** Full data engineering project scaffold (separate repo) — opinionated starter with deps, config, tests, CI. Build as its own repo when prioritised.
- **Tier-3 backlog** (deferred from 2026-06-22 holistic review, expansion-only): graph ML, speech/multimodal, geospatial, SRE/SLO. Weak fit to current repo identity per advisor pushback — only build on explicit demand.

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use `git commit -F <file>` with a heredoc-written tempfile instead
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating
- `/doc-ci-check` GH Action runs on every push to master + every PR — keep counts and parity green

---

## Files of note

- `.claude/hooks/` — **13** reference hooks (3 generic: git/secrets/audit + 10 domain: cloud-cost/SQL/ML-leakage/PII/prompt-safety/etc.) + README
- `.claude/skills/` — **132** skills; each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — **143** prompt templates; `README.md` is the index
- `.github/workflows/doc-ci.yml` — doc-CI gate (4 steps: count drift, broken links, skill↔prompt↔CLAUDE↔README↔prompts/README parity, NEXT_SESSION HEAD freshness warning). Mirrors `/doc-ci-check` skill.
- `templates/data-engineering/` — 4 DE script templates
- `templates/skill/` — annotated SKILL-TEMPLATE.md + REFERENCE-TEMPLATE.md
- `templates/security-model/` — SECURITY_MODEL-TEMPLATE.md
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills + stacks; keep in sync. Also lists the exempt-list for the standing 5-artifact rule (mirrored in `.claude/skills/doc-ci-check/SKILL.md` and `.github/workflows/doc-ci.yml`).
- `stacks/` — Python, TypeScript, Go stack add-ons
- `context/` — Claude's persistent memory; `MEMORY.md` is the index
- `decisions/` — 21 ADRs

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.
