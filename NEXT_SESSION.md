# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-06. **Current branch:** `master`. **Tree:** clean. **HEAD = 6be74e6**

---

## State

```
6be74e6  Merge pull request #12 — Add 5 deferred skills
74e4d7d  Add 5 deferred skills: causal-inference, survival-analysis, computer-vision, online-learning, data-mesh
b4467c4  Update NEXT_SESSION.md — HEAD b2dc0c4, PR #11 merged
b2dc0c4  Merge pull request #11 — Update repo headline to highlight AIDLC
b7471ab  Update repo headline to highlight AI/ML development lifecycle
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 4e8635f)

---

## What landed in the most recent session

1. **README headline** (PR #11): Updated to lead with AIDLC angle — "full AI/ML development lifecycle, from problem framing to production monitoring"
2. **5 deferred skills** (PR #12): `/causal-inference`, `/survival-analysis`, `/computer-vision`, `/online-learning`, `/data-mesh` — each with SKILL.md + prompt template
3. `/causal-inference` — DiD/PSM/IPW/IV/RDD; estimand-first gate; assumption validation; sensitivity analysis mandatory
4. `/survival-analysis` — KM/Cox PH/RSF/AFT/Fine-Gray; PH assumption test; competing risks; C-stat + calibration
5. `/computer-vision` — CNN/ViT/YOLO/SegFormer by task × dataset size; 3-phase transfer learning; mAP@0.5:0.95
6. `/online-learning` — Hoeffding Tree/HAT/VW; ADWIN drift detection; prequential evaluation; batch-first justification gate
7. `/data-mesh` — domain ownership; data product specs; policy-as-code governance; one-domain-at-a-time migration

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
