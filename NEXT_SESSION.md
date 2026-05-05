# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = afaaf6b**

---

## State

```
afaaf6b  Add Tier 3 AIDLC skills: mlops-cicd, responsible-ai-governance, model-compression, feature-monitoring + .gitattributes
c04edf7  Add Tier 2 MLOps skills + prompts: experiment-tracking, ab-test-design, retraining-strategy, data-versioning
f827014  Add remaining skills and prompts from prior sessions
ff2eb96  Add Tier 1 AIDLC skills + batch prior session skills/prompts
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of afaaf6b)

---

## What landed in the most recent session

1. **Tier 3 AIDLC skills** — `/mlops-cicd`, `/responsible-ai-governance`, `/model-compression`, `/feature-monitoring` + matching prompts
2. **`.gitattributes`** — `* text=auto eol=lf` added; kills CRLF warnings on commit
3. **Index files updated** — `CLAUDE.md`, `README.md`, `prompts/README.md` all reflect 4 new skills

---

## Open items

- [ ] **Tier 3 complete** — all 4 skills built; AIDLC skill library is comprehensive (65+ skills total)
- [ ] **Stack add-ons** — `stacks/` currently has Python only; TypeScript/Go stacks could be added
- [ ] **README audit** — README describes "8 prompt templates" in the summary section (line 34) but there are now 50+ templates; consider updating the count

---

## Things to NOT do without explicit instruction

- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead
- NEXT_SESSION.md is now git-tracked at repo root — commit + push it when updating

---

## Files of note

- `.claude/skills/` — 65+ skills; each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — 50+ prompt templates; `README.md` is the index
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills; keep in sync
- `stacks/python/` — Python stack add-on; `/test-gen`, `/type-fix`, `/deps-audit`
- `.gitattributes` — LF normalization (new this session)

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.
