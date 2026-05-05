# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = b0c37fe**

---

## State

```
b0c37fe  Merge pull request #7 — Add reinforcement learning skills
595ad32  Add reinforcement learning skills: /bandit-design and /rl-design
63ba9e4  Update NEXT_SESSION.md — HEAD 755dcc8, unsupervised skills PR #6 merged
755dcc8  Merge pull request #6 — Add unsupervised learning skills
63ba9e4  Update NEXT_SESSION.md — HEAD 755dcc8, unsupervised skills PR #6 merged
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of b0c37fe)

---

## What landed in the most recent session

1. **Unsupervised learning** (PR #6): `/clustering`, `/dim-reduction`, `/topic-modeling` + prompts
2. **Reinforcement learning** (PR #7): `/bandit-design`, `/rl-design` + prompts — new "Reinforcement learning" section in all index files
3. `/bandit-design` — epsilon-greedy/UCB/Thompson Sampling/LinUCB; bandit vs A/B gate; delayed reward buffering; offline replay eval
4. `/rl-design` — RL justification gate; MDP spec; DQN/PPO/SAC/TD3/offline RL/RLHF; reward design + Goodhart risk; safety constraints; multi-seed requirement
5. **Coverage now complete**: supervised ✅ unsupervised ✅ reinforcement learning ✅

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
