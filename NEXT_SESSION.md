# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = 7fe5ac5**

---

## State

```
7fe5ac5  Merge pull request #8 — Add ML domain skills
fbcbe87  Add ML domain skills: /time-series-forecasting, /recommender-design, /nlp-pipeline
b0c37fe  Merge pull request #7 — Add reinforcement learning skills
595ad32  Add reinforcement learning skills: /bandit-design and /rl-design
3dbe6e6  Update NEXT_SESSION.md — HEAD b0c37fe, RL skills PR #7 merged
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 7fe5ac5)

---

## What landed in the most recent session

1. **ML domain skills** (PR #8): `/time-series-forecasting`, `/recommender-design`, `/nlp-pipeline` + prompts
2. `/time-series-forecasting` — ARIMA/SARIMA/ETS/Prophet/N-BEATS/TFT; seasonal naive gate (MASE < 1); time series CV only; Ljung-Box residual check
3. `/recommender-design` — ALS/iALS/two-tower/SASRec; two-stage pipeline for >1M items; cold-start mandatory; temporal split only; NDCG@K + Coverage
4. `/nlp-pipeline` — TF-IDF baseline gate; preprocessing decision table; entity-level F1 for NER; ROUGE for summarization; domain-BERT rule

---

## Open items

- [ ] **Backlog skills (deferred):**
  - `/causal-inference` — DiD, propensity score matching, instrumental variables
  - `/survival-analysis` — Kaplan-Meier, Cox PH, survival forests
  - `/computer-vision` — image preprocessing, augmentation, CNN/ViT, mAP/IoU
  - `/online-learning` — streaming ML (River, Vowpal Wabbit)
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
