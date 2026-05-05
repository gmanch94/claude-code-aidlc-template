# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = 4e8635f**

---

## State

```
4e8635f  Merge pull request #10 — Add platform/strategy skills
7430477  Add platform/strategy skills: /llm-routing, /streaming-pipeline, /build-vs-buy
2e9c01a  Merge pull request #9 — Add AI production skills
2e9c01a  Add AI production skills: /anomaly-detection, /guardrails-design, /multi-agent-design
7fe5ac5  Merge pull request #8 — Add ML domain skills
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 4e8635f)

---

## What landed in the most recent session

1. **AI production skills** (PR #9): `/anomaly-detection`, `/guardrails-design`, `/multi-agent-design` + prompts
2. `/anomaly-detection` — Z-score/IQR/Isolation Forest/LOF/LSTM-AE/CUSUM; no-auto-remove rule; FPR gate
3. `/guardrails-design` — input/output safety layers; threat inventory; 200ms p95 cap; fail-open vs. fail-closed
4. `/multi-agent-design` — LangGraph/CrewAI/AutoGen; agent roster + state schema; max_iterations mandatory
5. **Platform/strategy skills** (PR #10): `/llm-routing`, `/streaming-pipeline`, `/build-vs-buy` + prompts
6. `/llm-routing` — static/cascade/complexity-classifier/semantic; quality-floor gate; escalation rate diagnostic
7. `/streaming-pipeline` — stream vs. batch; Kafka/Flink; watermark → windowing; consumer lag primary health metric
8. `/build-vs-buy` — 5-dimension score; AI tooling matrix; 3-yr TCO with 20% maintenance; exit strategy mandatory

---

## Open items

- [ ] **Backlog skills (deferred):**
  - *ML algorithms:*
    - `/causal-inference` — DiD, propensity score matching, instrumental variables
    - `/survival-analysis` — Kaplan-Meier, Cox PH, survival forests
    - `/computer-vision` — image preprocessing, augmentation, CNN/ViT, mAP/IoU
    - `/online-learning` — streaming ML (River, Vowpal Wabbit)
  - *Data platform:*
    - `/data-mesh` — domain ownership, data products, federated governance
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
