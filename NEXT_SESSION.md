# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-06-25. **Current branch:** `master`. **Prior HEAD = f999bca**; the 22-skill delta below ships via a feature-branch PR (squash-merged). After merge, refresh this bookmark to the new HEAD.

---

## 22-skill expansion (2026-06-25 — shipped via PR)

22 new skills authored this session (gap-analysis → fan-out build → adversarial review → 5-artifact wiring). Parity-green; shipped on a feature branch and squash-merged to `master`.

- **Batch 1 (9 skills):** `snowflake-cortex-design`, `bigquery-ml-design` (warehouse-native parity); `graph-ml-design`, `audio-ml-pipeline`, `multimodal-design`, `geospatial-ml` (modality spine); `privacy-preserving-ml`, `data-deidentification-design` (privacy); `decision-optimization` (predict-then-optimize).
- **Batch 2 (13 skills):** `hypothesis-test-design`, `unstructured-eda` (EDA); `conformal-uncertainty`, `decision-threshold-policy` (model validation); `imputation-design`, `cdc-design`, `data-observability` (data eng); `databricks-agent-framework`, `lakehouse-monitoring` (Databricks); `prompt-management`, `context-engineering` (AI/LLM); `learning-to-rank` (ML domain); `human-oversight-design` (responsible AI).
- **Each skill = SKILL.md + prompts/<name>.md**, fully wired into CLAUDE.md + README.md + prompts/README.md. doc-ci parity verified: all 161 non-exempt skills wired across 5 artifacts, 0 broken links, 0 dups.
- **Modified (not new):** `CLAUDE.md`, `README.md`, `prompts/README.md` (index rows); `prompts/model-calibration.md` (back-ref repointed: thresholding now → `/decision-threshold-policy` not `/eval-design`).
- **Gap source:** `scratch/skill-gap-analysis.md` (the prioritized report; backlog now fully drained — all 19 verified gaps + 3 scope-opened net-new shipped).
- **Method note:** built via background `Workflow` runs; batch-2 first run hit a session limit mid-review (8 agents), recovered with a focused review-only re-run after reset. All 22 carry an adversarial review pass.
- **Counts moved:** skills 139→**161**, prompts 149→**171**.

To ship: `git status` to confirm the 44 untracked paths + 4 modified files, then commit (feature branch + PR per house rule, or direct per any active pre-launch policy). Nothing pushed.

---

## State

```
f999bca  chore: refresh bookmark — PR #35 merged as 274b5e8 on master (#36)   ← prior HEAD (22-skill PR squash-merges on top)
274b5e8  feat(skills+hooks): research wave 2 — 7 new skills + 2 new hooks + 13 enhanced + AGENTS.md interop (#35)
c63b48f  fix(skills): drift corrections — Databricks rebrand sweep + MCP auth + Vertex endpoints + SageMaker Studio + Terraform/compliance modernization (#34)
d242f29  chore: save state — bookmark HEAD=2721b08 (post PR #31+#32 merge) + bash -e lesson (#33)
2721b08  Tier-2 skills: vertex-ai, sagemaker, terraform-review, compliance-mapping, dashboard-design (#32)
a3edb60  Holistic review: stale-check + /doc-ci-check + /mcp-design (#31)
```

Remote: https://github.com/gmanch94/claude-code-aidlc-template

---

## What landed since the prior bookmark (2721b08 → 274b5e8)

1. **PR #34 (`c63b48f`, merged):** drift corrections from research wave 1 — Databricks rebrand sweep (DLT→Lakeflow SDP, DABs→Declarative Automation Bundles, Mosaic AI Vector Search→Databricks AI Search), MCP auth corrections (DCR deprecation, RFC 9728/8414-or-OIDC/8707/9207), Vertex AI endpoint taxonomy (4 tiers, PSC), SageMaker (Studio Classic EOL, Amazon SageMaker AI), Terraform (S3 lockfile / HCP Terraform / `action_trigger` / OpenTofu), Compliance (EU AI Act dates + HIPAA NPRM).

2. **PR #35 (`274b5e8`, merged):** research wave 2 from 2 parallel deep-research workflows (14 lenses + 14 adversarial-verify passes) — `+2806 / -189` across 67 files:
   - **7 new skills:** `/agent-memory`, `/plan-mode`, `/workflow-design`, `/bedrock-design`, `/azure-foundry-design`, `/openai-platform-design`, `/rollback-checkpoint`
   - **2 new hooks:** `shadow_git_checkpoint.py` (PreToolUse), `staleness_check.py` (SessionStart) + `.claude/checkpoints/` added to `.gitignore`
   - **13 enhanced existing skills:** `/cost-optimize` (cache TTL + Deep Research trap + Anthropic 1h GA + Bedrock IPR + Vertex PT terms), `/agent-design` (durable session store + sandbox + Plan-Execute-Verify-Replan + managed runtimes + Adaptive Thinking), `/mcp-design` (2026-07 RC: stateless core / Extensions / Tasks demoted / R-S-L deprecated / MCPB / AAIF + sandbox dim + Anthropic `mcp_servers` param + OpenAI Realtime native MCP), `/vertex-ai-design` (Gemini 3.1 Pro Feb-19 GA / 2M ctx / over-200k pricing / RAG-path decision), `/llm-routing` (2026-06 refresh: TGI maintenance, Bedrock IPR, Groq/Cerebras ultra-fast tier, Mistral Medium 3 floor), `/eval-design` (OpenAI Evals sunset 2026-11-30 + Promptfoo migration target + reasoning-diversity for judges), `/rag-design` (managed-cloud vector-store matrix across Bedrock/Azure/Vertex/OpenAI/Databricks), `/guardrails-design` (Bedrock Automated Reasoning + Azure Prompt Shields + Groundedness auto-correct), `/multi-agent-design` (framework refresh + handoff-as-primitive matrix + reasoning-diverse critics), `/model-compression` (ACBench gate for agentic workloads), `/build-vs-buy` (inference-vendor refresh: Mistral floor + OpenRouter + HF Inference Providers + Modal post-Butter + Groq/Cerebras tier + Cloudflare edge), `/fine-tune` (SFT/DPO/RFT trio + distillation Evals-shutdown caveat + managed-cost benchmarks), `/review` + `/security-audit` + `/api-audit` (N=3 reasoning-diverse escalation pattern citing "Nine Judges, Two Effective Votes")
   - **CLAUDE.md:** AGENTS.md interop pattern for multi-host repos; hooks event catalog (12+ events); exempt list extended for `/rollback-checkpoint`
   - **Hook inventory + counts refreshed across CLAUDE.md + README.md + prompts/README.md + .claude/hooks/README.md**

3. **2 research reports persisted** in `scratch/` (gitignored, ephemeral but referenced from this bookmark):
   - `scratch/context_harness_research_2026-06-22.md`
   - `scratch/cloud_llm_platforms_research_2026-06-22.md`

---

## Open items

- **WAIT items deferred** (research surfaced; need primary-source verify before authoring):
  - `/anthropic-api-design` skill — `POST /v1/skills` Admin endpoint path was unverified in cloud-LLM research (Anthropic doc sidebar references skills-via-API but not at the cited Admin endpoint). Fetch `docs.anthropic.com/en/docs/build-with-claude/skills-guide` to confirm before authoring.
  - `/skills-api-deploy` skill — depends on the above.
  - `/gemini-code-assist-rollout` skill — NO recommendation (out of scope for ML/data/AI engineering focus).
- **Backlog:** Full data engineering project scaffold (separate repo).
- **Tier-3 backlog** — graph ML, speech/audio, multimodal, geospatial **all SHIPPED 2026-06-25** (uncommitted). **Remaining: SRE/SLO** (no skill yet — generic-ops, confirm in-scope before authoring).
- **Strategic-coverage questions still open** (from `scratch/skill-gap-analysis.md`): no separate `multimodal`/`geospatial`/`graph` category gaps remain (built). Decision-optimization built. Privacy cluster built. Nothing pending unless owner opens a new category.
- **MCP-Apps skill** (`/mcp-apps-ui`) — defer until host adoption beyond Claude Desktop materializes.
- **MCPB packaging skill** (`/mcp-bundle-author`) — defer until repo actually ships an MCP server.
- **Routines (cloud-scheduled)** — Anthropic research preview; revisit when GA + pricing model firms up.
- **Microsoft Agent Framework Compaction** — still experimental in Python; track for `/agent-design` once GA.
- **OpenAI Agents SDK subagent + code mode** — both planned, not shipped (as of mid-2026). Revisit when actually released.

---

## Things to NOT do without explicit instruction

- **All changes via feature branch + PR** — no direct commits to master
- Don't push to remote without being asked — user authorizes explicitly per session
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use `git commit -F <file>` with a heredoc-written tempfile instead
- Don't pass commit messages containing `N->M` patterns via `-m "..."` — bash shell-redirects `->NNN` and creates a stray empty file named `NNN`. Use `git commit -F <msgfile>` instead (covered in LESSONS_LEARNED.md)
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating
- `/doc-ci-check` GH Action runs on every push to master + every PR — keep counts and parity green
- When authoring NEW skills, mirror the exempt-list change in 3 places (CLAUDE.md + .claude/skills/doc-ci-check/SKILL.md + .github/workflows/doc-ci.yml) per the "Skill authoring (standing)" rule

---

## Files of note

- `.claude/hooks/` — **15** reference hooks (3 generic: git/secrets/audit + 10 domain: cloud-cost/SQL/ML-leakage/PII/prompt-safety/etc. + 2 optional add-ons: `shadow_git_checkpoint.py` PreToolUse / `staleness_check.py` SessionStart) + README with 2026 event catalog
- `.claude/skills/` — **161** skills (139 + 22 uncommitted 2026-06-25); each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — **171** prompt templates; `README.md` is the index
- `.github/workflows/doc-ci.yml` — doc-CI gate (4 steps: count drift, broken links, skill↔prompt↔CLAUDE↔README↔prompts/README parity, NEXT_SESSION HEAD freshness warning). Exempt list mirrors CLAUDE.md L86 + `.claude/skills/doc-ci-check/SKILL.md` L64.
- `templates/data-engineering/` — 4 DE script templates
- `templates/skill/` — annotated SKILL-TEMPLATE.md + REFERENCE-TEMPLATE.md
- `templates/security-model/` — SECURITY_MODEL-TEMPLATE.md
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills + stacks; keep in sync. Also lists the exempt-list for the standing 5-artifact rule + AGENTS.md interop pattern.
- `stacks/` — Python, TypeScript, Go stack add-ons
- `context/` — Claude's persistent memory; `MEMORY.md` is the index
- `decisions/` — 21 ADRs
- `scratch/` (gitignored) — 2 active research reports + multiple commit message tempfiles from prior session

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.

Next likely lever (operator's call):
1. **Refresh this bookmark HEAD to the 22-skill squash-merge commit** (the PR landed; update the hash above).
2. Promote `/anthropic-api-design` + `/skills-api-deploy` after primary-source verify of the Skills Admin endpoint
3. Remaining Tier-3: SRE/SLO skill (confirm in-scope — generic-ops vs ML/data focus)
4. Full data engineering project scaffold (separate repo)
