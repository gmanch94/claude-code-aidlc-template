# NEXT_SESSION.md

Resume point after `/clear` or a new session. Read this first before any tool calls beyond orientation.

**Last working session:** 2026-06-22. **Current branch:** `chore/research-updates-2026-06-22` (PR #35 open, doc-ci green). **HEAD = a44d1ab**

Once PR #35 merges, refresh this bookmark to the squash-merge SHA on master.

---

## State

```
a44d1ab  fix(ci+docs): finish exempt-list update in doc-ci.yml + doc-ci-check SKILL.md
d76709d  fix(docs): add /rollback-checkpoint to exempt list (3 places per standing rule)
183b933  chore: remove stray '149' file (shell-redirect artifact)
360762f  fix(docs): refresh README inventory counts — 13->15 hooks, 143->149 prompts
c21e14c  chore(gitignore): exclude .claude/checkpoints/ (shadow-Git hook output)
160b358  feat(hooks+skills): 2 new hooks + /rollback-checkpoint skill — shadow-Git checkpoints + session-start staleness check
ab8db12  fix(skills): ENHANCING cluster C — build-vs-buy inference-vendor refresh + fine-tune trio (SFT/DPO/RFT) + review/security-audit/api-audit reasoning-diversity + CLAUDE.md AGENTS.md interop
7ceec1a  fix(skills): ENHANCING cluster B — rag-design managed-cloud matrix + guardrails-design first-party stacks + multi-agent-design framework refresh + model-compression ACBench gate
63d558f  fix(skills): ENHANCING cluster A — cost-optimize multi-vendor caching + agent-design managed runtimes + mcp-design new host targets
dca2c7d  fix(skills): BREAKING drift fixes — Gemini 3.1 Pro GA + RAG-path decision + OpenAI Evals sunset + llm-routing 2026-06 refresh
4132a67  feat(skills): 3 new cloud-LLM platform skills — /bedrock-design + /azure-foundry-design + /openai-platform-design
1f87471  feat(skills): new /plan-mode + /workflow-design skills — Plan-Execute-Verify-Replan + deterministic orchestration
3a3b5a9  feat(skills): new /agent-memory skill — state-across-time layer for long-running agents
a8f8864  fix(skills): research updates batch 1 — cache-TTL + MCP 2026-07 RC + hooks events + sandbox dim + durable session store
c63b48f  fix(skills): drift corrections — Databricks rebrand sweep + MCP auth + Vertex endpoints + SageMaker Studio + Terraform/compliance modernization (#34) [merged to master]
```

Remote: https://github.com/gmanch94/claude-code-aidlc-template

---

## What landed since the prior bookmark (2721b08 → a44d1ab)

1. **PR #34 (`c63b48f`, merged):** drift corrections from the first research wave — Databricks rebrand sweep (DLT→Lakeflow SDP, DABs→Declarative Automation Bundles, Mosaic AI Vector Search→Databricks AI Search), MCP auth corrections (DCR deprecation, RFC 9728/8414-or-OIDC/8707/9207), Vertex AI endpoint taxonomy (4 tiers, PSC), SageMaker (Studio Classic EOL, Amazon SageMaker AI), Terraform (S3 lockfile / HCP Terraform / `action_trigger` / OpenTofu), Compliance (EU AI Act dates + HIPAA NPRM).

2. **PR #35 (this branch, open):** research-wave 2 from 2 parallel deep-research workflows (14 lenses + 14 adversarial-verify passes):
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

- **PR #35 awaiting merge** — squash-merge when ready; will need a bookmark refresh on this file after merge.
- **WAIT items deferred** (research surfaced; need primary-source verify before authoring):
  - `/anthropic-api-design` skill — `POST /v1/skills` Admin endpoint path was unverified in cloud-LLM research (Anthropic doc sidebar references skills-via-API but not at the cited Admin endpoint). Fetch `docs.anthropic.com/en/docs/build-with-claude/skills-guide` to confirm before authoring.
  - `/skills-api-deploy` skill — depends on the above.
  - `/gemini-code-assist-rollout` skill — NO recommendation (out of scope for ML/data/AI engineering focus).
- **Backlog:** Full data engineering project scaffold (separate repo).
- **Tier-3 backlog** (deferred from 2026-06-22 holistic review, expansion-only): graph ML, speech/multimodal, geospatial, SRE/SLO.
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
- **NEW (2026-06-22):** Don't pass commit messages containing `N->M` patterns via `-m "..."` — bash shell-redirects `->NNN` and creates a stray empty file named `NNN`. Use `git commit -F <msgfile>` instead (now covered in LESSONS_LEARNED.md)
- NEXT_SESSION.md is git-tracked at repo root — commit + push it when updating
- `/doc-ci-check` GH Action runs on every push to master + every PR — keep counts and parity green
- When authoring NEW skills, mirror the exempt-list change in 3 places (CLAUDE.md + .claude/skills/doc-ci-check/SKILL.md + .github/workflows/doc-ci.yml) per the "Skill authoring (standing)" rule

---

## Files of note

- `.claude/hooks/` — **15** reference hooks (3 generic: git/secrets/audit + 10 domain: cloud-cost/SQL/ML-leakage/PII/prompt-safety/etc. + 2 optional add-ons: `shadow_git_checkpoint.py` PreToolUse / `staleness_check.py` SessionStart) + README with 2026 event catalog
- `.claude/skills/` — **139** skills; each is a directory with `SKILL.md` (+ optional `REFERENCE.md`)
- `prompts/` — **149** prompt templates; `README.md` is the index
- `.github/workflows/doc-ci.yml` — doc-CI gate (4 steps: count drift, broken links, skill↔prompt↔CLAUDE↔README↔prompts/README parity, NEXT_SESSION HEAD freshness warning). Exempt list mirrors CLAUDE.md L86 + `.claude/skills/doc-ci-check/SKILL.md` L64.
- `templates/data-engineering/` — 4 DE script templates
- `templates/skill/` — annotated SKILL-TEMPLATE.md + REFERENCE-TEMPLATE.md
- `templates/security-model/` — SECURITY_MODEL-TEMPLATE.md
- `README.md` — user-facing skill command table; keep in sync with new skills
- `CLAUDE.md` — automation section lists all skills + stacks; keep in sync. Also lists the exempt-list for the standing 5-artifact rule + AGENTS.md interop pattern.
- `stacks/` — Python, TypeScript, Go stack add-ons
- `context/` — Claude's persistent memory; `MEMORY.md` is the index
- `decisions/` — 21 ADRs
- `scratch/` (gitignored) — 2 active research reports + multiple commit message tempfiles from this session

---

## How to resume

Open this file. Read it. Check `git status` and `git log -5 --oneline`. Confirm tree matches the state above. Then ask the user what they want to work on — don't start anything proactively.

If PR #35 has merged on master:
1. Refresh HEAD on this file to the squash-merge SHA
2. Update commit log snapshot
3. Move "Open items / WAIT" entries (`/anthropic-api-design` + `/skills-api-deploy`) into a new bookmark if they should ship next
