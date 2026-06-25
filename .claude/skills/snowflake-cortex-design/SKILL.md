---
name: snowflake-cortex-design
description: Designs a Snowflake AI/ML footprint — service split (Cortex AISQL LLM functions / Cortex Analyst text-to-SQL / Cortex Search managed RAG / Cortex Agents / Snowpark ML + Model Registry + Feature Store / SPCS serving), compute model (warehouse vs Cortex serverless vs SPCS compute pool), governance (RBAC / row-access / masking / tags), credit-based cost guardrails, MLOps wiring, deployment pattern (in-warehouse batch vs SPCS real-time), and lock-in posture. Use when scoping a new Snowflake Cortex deployment, choosing between Snowflake AI surfaces for a workload, or auditing an existing footprint. Adjacent to `/bigquery-ml-design` (the warehouse-native ML peer on GCP), `/sagemaker-design` (AWS), `/vertex-ai-design` (GCP), `/bedrock-design` + `/azure-foundry-design` (managed-GenAI siblings), and `/databricks-asset-bundles` (the lakehouse alternative).
---

# /snowflake-cortex-design — Snowflake AI/ML Design

> **Naming + GA snapshot (verified mid-2026 — re-confirm against the live Snowflake docs / release-notes before quoting in deliverables):**
> - **Cortex AISQL** is the SQL-callable LLM-function surface. Current names are `AI_*`-prefixed: `AI_COMPLETE`, `AI_CLASSIFY`, `AI_FILTER`, `AI_AGG`, `AI_SUMMARIZE_AGG`, `AI_EXTRACT`, plus `AI_SIMILARITY` / `EMBED_TEXT_*`. The older `COMPLETE` / `SUMMARIZE` / `TRANSLATE` / `SENTIMENT` / `EXTRACT_ANSWER` functions under the `SNOWFLAKE.CORTEX` schema still work as documented aliases/legacy entry points — prefer the `AI_*` form for new work. Cortex AISQL operators reached **GA Nov 4 2025**; `AI_EXTRACT` GA **Oct 2025**. Verify any specific function's GA before relying on it.
> - **Cortex Analyst** — managed text-to-SQL over a **semantic model / semantic view** (YAML or Snowflake semantic view). Answers business questions over structured tables; default backing LLMs are Snowflake-hosted (Mistral / Meta family) so data stays in the governance boundary.
> - **Cortex Search** — managed hybrid (vector + keyword) retrieval service; handles embedding + indexing + serving with no separate vector DB. Backbone for RAG inside Snowflake.
> - **Cortex Agents** — orchestrated multi-step agentic surface that can call Analyst + Search + tools. Treat as the newest, fastest-moving surface — pin to the documented capability set, don't assume parity with a general agent framework.
> - **Snowpark Container Services (SPCS)** — managed OCI container runtime on Snowflake compute pools. **New GPU instance families went GA May 5 2026** (e.g. `GPU_NV_*` tiers; L40S 48 GB and RTX PRO 6000 Blackwell 96 GB families on AWS, scaling to 8 GPUs). Confirm the exact family name + region availability before sizing.
> - **Model Registry** lives in Snowflake (schema-level `MODEL` objects governed by RBAC) — the Snowflake analog of a UC model registry. **Feature Store** is a Snowpark ML construct over Snowflake tables/dynamic tables.
> - Don't fabricate a Cortex function, model alias, or instance family. If unsure whether a capability is GA in mid-2026, describe the decision shape generically.

## Role
You are a Snowflake AI/ML Platform Architect.

## Behavior
1. Ask if not provided: workload type (analytics-Q&A / RAG / classical-ML / custom-model serving / full lifecycle), team size + Snowflake maturity, expected QPS or batch volume, latency budget, data residency / cloud region (Snowflake runs on AWS / Azure / GCP), existing account + database/schema layout, budget tier
2. Work through the 9 dimensions in order
3. Flag every surface choice with a one-line failure mode + credit/cost class
4. Pin the model lifecycle to the Snowflake **Model Registry** — every SPCS serving job + batch scoring path references a registered model version, not an ad-hoc artifact
5. Recommend ADRs at the end for any load-bearing decision the answers reveal

## 9 Dimensions

**1. Service split.** Which Snowflake AI surfaces does this workload actually need? Pick the minimum viable set — every surface has a credit-consumption class.

- **Cortex AISQL LLM functions** (`AI_COMPLETE` / `AI_CLASSIFY` / `AI_FILTER` / `AI_AGG` / `AI_SUMMARIZE_AGG` / `AI_EXTRACT`) — SQL-callable inference over columns. Zero infra; pay **per token** consumed (credit-priced per model). Default for "score/classify/summarize a column in a query." Failure mode: a full-table `AI_COMPLETE` over millions of rows silently bills per-token on every row — gate with `WHERE`/`SAMPLE` and a row-count guard before running at scale.
- **Cortex Analyst** — natural-language → SQL over a **semantic model**. Use for business-user self-serve Q&A over governed structured data. Failure mode: answer quality is a function of the semantic-model quality — a thin/ambiguous semantic view produces confidently-wrong SQL. The semantic model IS the work.
- **Cortex Search** — managed RAG retrieval (hybrid vector + keyword). Use for document/knowledge retrieval and as the retrieval leg of a RAG app. Failure mode: index refresh lag + embedding-model pinning — changing the embedding model means a reindex; treat the embedding choice as a one-way door. Defer chunking + retrieval-eval depth to `/rag-design`.
- **Cortex Agents** — multi-step orchestration over Analyst + Search + tools. Use only when a single Analyst/Search call can't answer; newest surface, capability set still moving. Failure mode: agentic loops multiply token spend and latency — cap steps and budget per call.
- **Snowpark ML (modeling API)** — train classical models (sklearn-/xgboost-style) in-warehouse or on SPCS, in Python. Use for tabular ML where the data already lives in Snowflake and you want no egress. Failure mode: a large training run on an undersized warehouse spills to remote storage and silently inflates wall-time + credits — size the warehouse to the data and watch the query profile for spillage, don't just scale up reflexively.
- **Model Registry** — versioned `MODEL` objects governed by RBAC; single source of truth for what's deployable. Every serving + batch path resolves a registered version. Failure mode: serving or scoring a model by hard-coded version instead of an alias defeats the rollback unit — pin consumers to an alias (`prod`/`canary`), never a literal version string.
- **Feature Store** — Snowpark ML feature views over Snowflake tables / dynamic tables; point-in-time-correct features online + offline. Don't enable until ≥2 consumers + a point-in-time requirement (mirrors the Vertex / SageMaker rule). Failure mode: enabling it for a single consumer adds dynamic-table refresh credits + a maintenance surface with no payoff — premature Feature Store is pure cost.
- **SPCS (Snowpark Container Services)** — your container, your code; GPU compute pools for custom/LLM/embedding model hosting. Use when Cortex functions don't cover the model and you need real-time custom serving or GPU inference inside the governance boundary. Failure mode: reaching for SPCS when a Cortex function already covers the task trades a zero-infra managed call for a container + pool you must size, patch, and keep warm — only cross to SPCS at a genuine capability wall.

Rule: don't reach for Snowpark ML + SPCS if Cortex AISQL already covers the task — managed functions beat self-hosted containers on operational cost until you hit a capability wall.

**2. Compute model.** Three distinct compute substrates — pick per stage; mixing them up is the most common cost mistake.
- **Virtual warehouses** (XS → 6XL) — for SQL, Snowpark DataFrame work, batch `AI_*` scoring, in-warehouse training on tabular data. Bill **per-second while running** at a size-doubling credit rate (XS = 1 credit/hr … each size up doubles). **Auto-suspend** (default 600 s; set 60 s for spiky workloads) and auto-resume are the primary cost lever. Failure mode: an oversized warehouse left at `AUTO_SUSPEND` too high burns credits between queries.
- **Cortex serverless** — AISQL functions, Analyst, Search run on Snowflake-managed serverless compute; **no warehouse to size**, billed per-token (LLM) or per-query/credit (Search/Analyst). Failure mode: serverless feels "free" because there's no warehouse — but per-token spend on a large batch is unbounded without a guard.
- **SPCS compute pools** — node pools (CPU `CPU_X64_*` / GPU `GPU_NV_*` families) that back container services. Bill **per node-second while the pool has nodes**, independent of warehouse credits. Auto-suspend on the pool (`AUTO_SUSPEND_SECS`) + `MIN_NODES`/`MAX_NODES` control floor cost. Failure mode: a GPU pool with `MIN_NODES ≥ 1` left running overnight is the most expensive idle resource in the account.
- Warehouse **sizing rule:** start one size down from your instinct, measure query queuing, scale up only if queued; use **multi-cluster** (scale-out) for concurrency, **bigger size** (scale-up) for single heavy queries — not both reflexively.

**3. Governance.** Snowflake's data-layer controls — the invariant is that AI surfaces inherit the same RBAC + masking, so a Cortex function can't read a column the calling role can't.
- **RBAC** — role hierarchy; grant `USAGE` on Cortex / SPCS at the role level, not to `PUBLIC`. The Model Registry `MODEL` object is RBAC-governed like any schema object.
- **Row-access policies** — per-row filtering; a `AI_COMPLETE` over a table sees only rows the role's policy admits.
- **Dynamic data masking + tag-based masking** — column-level masking; PII columns stay masked when piped into a Cortex function unless the role is unmasked. Prefer **tag-based masking** (attach a `governance` tag → policy applies everywhere the tag is) over per-column policies at scale.
- **Object tagging** — tag databases/schemas/warehouses with `env` / `team` / `cost_center` / `data_classification`; drives both masking policy and credit attribution.
- Failure mode: enabling a Cortex feature with a role that has broad `SELECT` bypasses the intended masking — audit the **calling role's** grants, not just the policy existence. (Mirror the universal rule: the SQL function is one path to the data; the data-layer policy must hold on every path.)

**4. Cost guardrails.** Everything is **credits**; the surfaces bill differently.
- **Per-token (Cortex LLM/AISQL)** — model-priced credits per 1M tokens; large models cost multiples of small. Pick the smallest model that passes eval; gate full-table scans with a row-count check.
- **Per-second (warehouses + SPCS pools)** — auto-suspend is the lever. Warehouse `AUTO_SUSPEND = 60`; SPCS pool `AUTO_SUSPEND_SECS` short; never leave a GPU pool warm without a named latency reason.
- **Resource monitors** — set on warehouses to **suspend at a credit quota** (suspend-immediate vs suspend-after-running); the hard backstop against a runaway loop. Set per-env (dev tighter than prod).
- **Budgets / spending limits** — account- or object-level credit budget alerts; pair with resource monitors (alerts ≠ enforcement).
- **Attribution** — `SNOWFLAKE.ACCOUNT_USAGE` views (`METERING_HISTORY`, `CORTEX_FUNCTIONS_USAGE_HISTORY`, warehouse/credit views) + object tags for per-team/per-model chargeback. Without tags the usage views aren't sliceable.
- Failure mode: relying on a budget **alert** as a control — alerts notify, **resource monitors** (and pool/warehouse auto-suspend) actually stop spend.

**5. Deployment pattern.** Match the request shape.
- **In-warehouse batch scoring** — `AI_*` functions or a Snowpark ML model called inside a SQL/Snowpark job; no idle cost beyond the warehouse run; ideal for "score this table nightly." Schedule via **Tasks** (cron / DAG) or **Dynamic Tables** (declarative refresh).
- **SPCS real-time service** — container exposes a service function / REST endpoint; warm pool gives low latency, costs per node-second; for sub-second custom-model inference inside the boundary.
- **Streaming-ish** — Snowpipe / Snowpipe Streaming lands data → a Task or Dynamic Table runs `AI_*`/model scoring on arrival; the model is a downstream call, not an inline stream operator.
- **Provider app / data-share** — package a model behind a Native App for cross-account consumption (advanced; document lock-in).
- Decision rule: default to in-warehouse batch; reach for SPCS real-time only when there's a documented sub-second latency budget that a scheduled Task can't meet.

**6. MLOps wiring.** What touches what.
- **Source code:** Python / Snowpark in Git → push container image to the account's private **OCI image repository** (for SPCS) → register the model in **Model Registry** with a version + alias.
- **Triggers:** **Tasks** (cron / task-graph), **Dynamic Tables** (declarative dependency refresh), **Streams** (CDC) feeding a Task, or external CI (GitHub Actions / Snowflake CLI / **Snowpark Container Services jobs**) calling `EXECUTE TASK` / deploying a service.
- **CI/CD:** model promotion gated by an evaluation Task — `evaluate → compare-vs-baseline → set-registry-alias` — a deterministic flow, not a console click.
- **Rollback:** flip the **Model Registry alias** (`prod` → prior version); the SPCS service / batch job resolves the alias on next invocation. Keep the prior container image so a service redeploy is one command.
- Failure mode: a promotion gate that's a console click instead of a deterministic Task (`evaluate → compare-vs-baseline → set-alias`) drifts between environments and can't be audited — and a long-running SPCS service that caches the resolved version won't pick up an alias flip until it's restarted, so confirm the consumer re-resolves on next invocation, not just on restart.

**7. Feature Store decision.** Do you actually need it?
- Yes when: ≥2 services consume the same features; point-in-time correctness across training/serving matters; features are computed at >1 cadence.
- No when: features are baked into the training table and never re-served; serving features come straight from the request payload or a single SQL view.
- Cost note: feature views run on warehouse compute (or dynamic-table refresh credits) — don't materialize an entity/feature view until a consumer exists.

**8. Observability.**
- **Cortex usage:** `CORTEX_FUNCTIONS_USAGE_HISTORY` / query history for per-function token spend, model, latency, and error rate.
- **SPCS:** service logs + compute-pool metrics (node count, GPU/CPU utilization) via the event table / `SYSTEM$` functions.
- **Pipelines:** Task / Dynamic Table run history (status, duration, failure) via `TASK_HISTORY` + the event table; route to alerts.
- **Model quality / drift:** Snowflake ML monitoring (model monitor over inference logs) for drift / performance over time; for LLM-output quality define an eval set and score it on a schedule (Snowflake doesn't auto-grade generation quality). Failure mode: assuming a Cortex/LLM surface is self-monitoring — generation quality silently degrades with no signal unless you stand up a scheduled eval set; usage views show spend and latency, not correctness.
- Alerts: per-token spend over $X/day, warehouse/pool credit over budget, Task failure, p99 latency breach on an SPCS service, drift over threshold.

**9. Lock-in posture.**
- **Snowflake-native (heavy lock-in):** Cortex AISQL / Analyst / Search / Agents (no portable equivalent — the SQL surface IS Snowflake), semantic models, Model Registry aliases, Tasks / Dynamic Tables / Streams orchestration. Document a migration path BEFORE making these load-bearing for a regulated or exit-sensitive workload.
- **Portable (modest lock-in):** Snowpark ML models (standard sklearn/xgboost/PyTorch artifacts — the model file is portable), SPCS containers (OCI images run anywhere), data in open formats (Iceberg tables on your cloud storage).
- **Portable choice:** train a standard artifact via Snowpark ML, register it, serve on SPCS from an OCI image — the same artifact + image can run on SageMaker / Vertex / Databricks Model Serving with an adapter. The Cortex *functions* don't port; a self-hosted model on SPCS does.

## Output

```
### Snowflake AI Footprint: {workload-name}

**Workload type:** [analytics-Q&A / RAG / classical-ML / custom-model serving / full lifecycle]
**QPS / batch target:** [N real-time / batch only / streaming-on-arrival]
**Cloud + region:** [AWS / Azure / GCP region]

**Surfaces enabled (with reason):**
- [Cortex AISQL / Cortex Analyst / Cortex Search / Cortex Agents / Snowpark ML / Model Registry / Feature Store / SPCS — pick subset]

**Compute model per stage:**
- Scoring/training: [warehouse size + auto-suspend / Cortex serverless per-token / SPCS pool family + min/max nodes]
- Serving: [in-warehouse Task / SPCS service + pool + warm-vs-suspend posture]
- Concurrency: [multi-cluster? scale-up vs scale-out]

**Deployment pattern:** [in-warehouse batch (Task / Dynamic Table) / SPCS real-time / streaming-on-arrival — with rationale]

**Governance:**
- RBAC: [roles granted USAGE on which surfaces]
- Row-access / masking: [policies + tag-based masking on PII columns]
- Calling-role audit: [what the Cortex-calling role can SELECT]

**Cost guardrails:**
- Per-token gate: [row-count guard + model tier]
- Auto-suspend: [warehouse N s / SPCS pool N s]
- Resource monitor: [credit quota + suspend action per env]
- Attribution: [object tags + ACCOUNT_USAGE views]

**MLOps wiring:**
- Source → OCI image / Model Registry → Alias chain
- Trigger: [Task / Dynamic Table / Stream / external CI]
- Promotion gate + rollback (alias flip) RTO

**Feature Store:** [enabled? feature views? consumers]

**Observability:** [usage history views, SPCS pool metrics, Task history, drift/eval signal, alerts]

**Lock-in posture:** [Snowflake-native (Cortex) + portable (Snowpark ML artifact / SPCS image / Iceberg) + documented exit]

**[RISK: HIGH] choices flagged:** [list, or "none"]

**Recommended ADRs:**
1. [Cortex managed function vs self-hosted SPCS model for {task}]
2. [Cortex Analyst semantic-model ownership + quality gate]
3. [Compute substrate per stage (warehouse vs serverless vs SPCS pool)]
4. [Feature Store enable / defer]
5. [Resource-monitor credit quota + suspend action per environment]
```

## Quality bar

- Every enabled surface has one named consumer + one credit/cost class + one failure mode — no "enabled in case"
- Per-token Cortex calls over a table ALWAYS carry a row-count / `SAMPLE` guard — an ungated full-table `AI_COMPLETE` is an unbounded bill
- A budget **alert** is not a control — pair every spend ceiling with a **resource monitor** (warehouses) or **auto-suspend** (warehouses + SPCS pools) that actually stops compute
- Audit the **calling role's** grants, not just policy existence — a Cortex function inherits the role's SELECT; broad grants bypass masking on a different path
- Feature Store is OFF by default; only enable with ≥2 consumers AND a point-in-time requirement
- Model Registry alias is the rollback unit — never roll back by redeploying an old artifact by hand
- GPU SPCS pools NEVER left warm without a documented sub-second latency budget; default `AUTO_SUSPEND_SECS` short and `MIN_NODES = 0` for non-prod
- Cost-attribution object tags on every database/warehouse/pool: `env`, `team`, `cost_center`, `model_id` — `ACCOUNT_USAGE` chargeback is unusable without them
- Document the lock-in posture explicitly — the Cortex functions don't port; a Snowpark ML artifact on an SPCS image does

## What this skill does NOT do

- Does NOT write Terraform / Snowflake CLI / SQL DDL — design only; pair with `/terraform-review` for the IaC side
- Does NOT choose the ML algorithm — pair with `/algo-select` upstream
- Does NOT design the RAG chunking / retrieval-eval in depth — pair with `/rag-design` for Cortex Search retrieval semantics (Databricks analog: `/mosaic-ai-vector-search`)
- Does NOT replace `/bigquery-ml-design` (warehouse-native ML peer on GCP) / `/sagemaker-design` (AWS) / `/vertex-ai-design` (GCP) / `/bedrock-design` + `/azure-foundry-design` (managed GenAI) / `/databricks-asset-bundles` (lakehouse) — pick the platform first, then this skill scopes the Snowflake side
- Does NOT cover Snowflake account-level security hardening in depth — pair with `/security-audit` for the RBAC / network-policy pass
