# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = b2dc0c4**

---

## State

```
b2dc0c4  Merge pull request #11 — Update repo headline to highlight AIDLC
b7471ab  Update repo headline to highlight AI/ML development lifecycle
d4de3e6  Update NEXT_SESSION.md — HEAD 4e8635f, PRs #9 and #10 merged
4e8635f  Merge pull request #10 — Add platform/strategy skills
7430477  Add platform/strategy skills: /llm-routing, /streaming-pipeline, /build-vs-buy
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 4e8635f)

---

## What landed in the most recent session

1. **README headline** (PR #11): Updated to lead with AIDLC angle — "full AI/ML development lifecycle, from problem framing to production monitoring"

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
