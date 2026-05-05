# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-05-05. **Current branch:** `master`. **Tree:** clean. **HEAD = 755dcc8**

---

## State

```
755dcc8  Merge pull request #6 — Add unsupervised learning skills
a7e93fe  Add /topic-modeling skill (LDA/NMF/BERTopic)
1143be2  Add unsupervised skills: /clustering and /dim-reduction
4b74217  Update NEXT_SESSION.md — HEAD df7c9fe, ML lifecycle skills PR #5 merged
df7c9fe  Merge pull request #5 — Add ML lifecycle skills: business discovery, model training, data exploration
```

Remote: https://github.com/gmanch94/claude-code-template (master, up to date as of 755dcc8)

---

## What landed in the most recent session

1. **Unsupervised learning** (3 skills + prompts): `/clustering`, `/dim-reduction`, `/topic-modeling` — new "Unsupervised learning" section in all index files
2. `/clustering` — k-means/DBSCAN/GMM/hierarchical; elbow+silhouette k decision; stability (ARI); cluster profiling
3. `/dim-reduction` — PCA/UMAP/t-SNE by goal; variance explained; t-SNE visualization-only rule; leakage guard
4. `/topic-modeling` — LDA/NMF/BERTopic; coherence-based k; preprocessing pipeline; topic labeling; BERTopic −1 handling
5. **Open question**: RL coverage — deferred, to revisit with user

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
