# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = beabe68**

---

## State

```
beabe68  Add general ADRs: LangGraph orchestration + Claude enterprise rollout
ac2a9b2  Add Argus ADRs from ai-enablement-ws
5530cad  Add OSS + policy ADRs and ADR template from ai-enablement-ws
76018ed  Add branch+PR workflow rule to CLAUDE.md and NEXT_SESSION.md
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of beabe68)

---

## What landed in the most recent session

1. **ADRs added** — 21 ADRs copied from `ai-enablement-ws` into `decisions/`: OSS (0032–0041), Policy (0042–0045), Argus (0046–0050), General (0001, 0031)
2. **Renamed** — sequence number prefix stripped (e.g. `ADR-0032-oss-llm-selection.md` → `oss-llm-selection.md`); policy files prefixed with `policy-`
3. **ADR template** — copied to `templates/adr/ADR-TEMPLATE.md`
4. **Memory** — PowerShell command length feedback saved to `memory/feedback_powershell_length.md`

---

## Open items

- [ ] **Tier 3 complete** — all 4 skills built; AIDLC skill library is comprehensive (65+ skills total)
- [ ] **Stack add-ons** — `stacks/` currently has Python only; TypeScript/Go stacks could be added
- [ ] **README audit** — README describes "8 prompt templates" in the summary section (line 34) but there are now 50+ templates; consider updating the count

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
