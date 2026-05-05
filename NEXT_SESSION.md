# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = df7c9fe**

---

## State

```
df7c9fe  Merge pull request #5 — Add ML lifecycle skills: business discovery, model training, data exploration
f4a3be9  Add data exploration skills: cohort-analysis, time-series-eda, feature-correlation
227862b  Add /experiment-design and /training-infrastructure to fill model development gap
ec9a61c  Add business discovery skills: /stakeholder-interview, /opportunity-sizing, /kpi-mapping
46be42d  Update NEXT_SESSION.md — master, HEAD 4607731, specialist personas landed
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of df7c9fe)

---

## What landed in the most recent session

1. **Business discovery** (3 skills + prompts): `/stakeholder-interview`, `/opportunity-sizing`, `/kpi-mapping` — fills gap upstream of `/problem-framing`
2. **Model development** (2 skills + prompts): `/experiment-design`, `/training-infrastructure` — fills training stage gap (compute selection, distributed strategy, experiment hygiene)
3. **Data exploration** (3 skills + prompts): `/cohort-analysis`, `/time-series-eda`, `/feature-correlation` — expands thin EDA stage
4. All 8 skills indexed in README.md, CLAUDE.md, prompts/README.md

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
