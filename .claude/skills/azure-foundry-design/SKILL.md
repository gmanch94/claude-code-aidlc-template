---
name: azure-foundry-design
description: Designs a Microsoft Foundry (formerly Azure AI Foundry) footprint on Azure — surface map, model catalog (1,900+ via Azure OpenAI + partners), Agent Service (GA Mar 16 2026), private networking (BYO VNet), Foundry IQ + Azure AI Search, safety stack (Prompt Shields + Groundedness), cost model (PTU / PAYG / Batch), lock-in posture. Use when scoping a new Foundry deployment, choosing between Foundry and Azure ML for a workload, or auditing an existing footprint. Adjacent to `/bedrock-design` (AWS), `/vertex-ai-design` (GCP), `/sagemaker-design` (AWS classical ML).
---

# /azure-foundry-design — Microsoft Foundry Design

> **Naming note:** Azure AI Foundry was renamed **Microsoft Foundry** at Ignite (Nov 18 2025); January 2026 product terms reflect the change. Doc namespace moved from `/azure/ai-foundry/` to `/azure/foundry/`. Portal exposes both "Foundry (New)" and "Foundry (Classic)" while the migration completes. SDK / REST surfaces still use `azure-ai-projects` package names. This skill uses "Foundry" and notes the legacy "Azure AI Foundry" name where user-facing language matters.

## Role
You are a Microsoft Foundry Platform Architect.

## Behavior
1. Ask if not provided: workload type (chat / RAG / agent / batch-gen / fine-tune), Azure subscription + region constraint, networking posture (public / VNet-isolated / hybrid), Entra ID tenancy, model preference (Azure OpenAI / OSS via Foundry Models / mixed), PTU vs PAYG appetite, compliance constraints
2. Work through the 9 dimensions in order
3. Flag every service choice with a one-line failure mode + cost-class
4. Pin model deployment names + capacity assignment (PTU vs PAYG vs Batch)
5. Recommend ADRs for any load-bearing decision

## 9 Dimensions

**1. Rebrand + surface map.**
- **Microsoft Foundry** = the unified platform for building / running / governing GenAI apps on Azure (rebrand of Azure AI Foundry Nov 18 2025; Jan 2026 product terms reflect).
- **Doc namespace:** `/azure/foundry/` (legacy `/azure/ai-foundry/` redirects).
- **Portal:** Foundry (New) vs Foundry (Classic) — both surfaces live while migration completes.
- **Foundry vs Azure ML decision:**
  - **Foundry** = GenAI / LLM / agents / RAG / multi-model orchestration.
  - **Azure ML** = classical MLOps (training jobs, model registry for non-LLM, AKS endpoints, Designer).
  - Most enterprises run BOTH. Don't try to do classical ML in Foundry; don't try to do GenAI agents in Azure ML.

**2. Model catalog.** Foundry exposes 1,900+ models across vendors and licensing modes.
- **Vendors:** Azure OpenAI (GPT-5 family / GPT-5-nano / o3 / o4-mini / GPT-4.1 / GPT-4o), Anthropic Claude (on Foundry via partnership), Meta Llama, Mistral, DeepSeek, xAI (Grok 4.3+), Cohere, HuggingFace, NVIDIA Nemotron, Fireworks (preview Mar 2026 / GA at Build 2026).
- **Deployment modes:**
  - **Serverless PAYG** — pay per token, no provisioned capacity, regional or Data Zone or Global routing.
  - **Managed compute** — your dedicated GPU cluster; for large / custom models.
  - **Local** — for Foundry-Local (edge / desktop dev).
  - **BYOW (bring-your-own-weights)** — upload + serve.
- **Pricing parity vs vendor direct** — Azure adds **20-40% infra overhead** vs OpenAI direct (managed support, regional residency, Entra integration).

**3. Agent runtime.** Foundry Agent Service is the managed runtime.
- **Foundry Agent Service GA: 2026-03-16.**
- **Wire-compat with OpenAI Responses API** — Agents authored for OpenAI Agents SDK run on Foundry with minimal code change.
- **Thread persistence** — multi-turn state managed by Foundry.
- **Entra RBAC** — agents authorize via Entra identities; tool access scoped via Entra groups.
- **Framework mix on same runtime** — DeepSeek planner + OpenAI generator + LangGraph orchestrator can coexist on one Agent Service instance.
- **Tool ecosystem** — Bing Search, Code Interpreter, File Search, custom OpenAPI tools, MCP servers (via private networking).
- **For non-Foundry agent runtimes** (LangGraph standalone / OpenAI Agents SDK direct) — Foundry Models still works as the model provider; Agent Service is optional.

**4. Private networking.** Foundry's enterprise differentiator vs OpenAI direct.
- **Standard Setup with BYO VNet** (GA) — Foundry resources injected into your VNet; subnet delegation; no public egress.
- **Reach extensions** — private connectivity to MCP servers, Azure AI Search, Fabric data-agents, Storage / Cosmos / SQL — all over private endpoints.
- **Decision rule:** if any data crosses an OpenAI direct boundary today and that's a compliance problem, Foundry + BYO VNet is the path.
- **Cost:** private-endpoint + PrivateLink charges add up — budget for it.

**5. RAG via Foundry IQ + Azure AI Search.**
- **Azure AI Search** (rebrand of Azure Cognitive Search) is the vector + keyword + hybrid (RRF) store; integrated vectorization (skill-based pipelines); GA.
- **Foundry IQ** = orchestration layer over AI Search + connectors (SharePoint / OneDrive / OneLake / Web / Fabric).
- **Agentic retrieval** — LLM-decomposed multi-step queries (vs single-vector lookup); GA.
- **Storage-optimized vector tiers** — recent cost-down for vector-heavy workloads.
- Defer chunking + retrieval-eval depth to **`/rag-design`**; this skill picks the Foundry-side store + pipeline.

**6. Safety stack.**
- **Prompt Shields** (GA) — unified API for direct jailbreak detection + indirect prompt injection detection (e.g. malicious payloads in retrieved docs).
- **Groundedness Detection with auto-correction** — checks if response is grounded in source material; can auto-rewrite ungrounded portions.
- **Content Safety filters** — text + image toxicity / hate / sexual / violence / self-harm severity scoring.
- **Protected Material detection** — flags copyrighted / proprietary content.
- **Stackable** — all filters can run together; can also be invoked outside Foundry on non-Azure models via the standalone Content Safety API.

**7. Cost model.**
- **PAYG (Pay-as-you-go)** — default; per-token billing; Global / Data Zone / Regional routing.
- **PTU (Provisioned Throughput Unit)** — fixed hourly capacity:
  - Starts **~$2,448/month** entry tier (verify against live pricing).
  - **Breakeven** vs PAYG: typically >50% utilization AND >150-200M tokens/mo on GPT-4o.
  - **Annual PTU saves ~35% more** vs monthly commitment.
  - **Non-cancellable** mid-term; commitment risk.
- **Batch API** — 50% off PAYG; 24-hr SLA.
- **Model pricing snapshot (Azure OpenAI):**
  - GPT-5: **$1.25 in / $10.00 out** per Mtok
  - GPT-5-nano: **$0.05 / $0.40**
  - GPT-4.1: 1M context (defer to live pricing for $/Mtok)
  - GPT-4o, o3, o4-mini: defer to live pricing
- Cross-vendor (Anthropic Claude on Foundry, Llama, Mistral, etc.) — vendor sets price; Azure adds infra overhead.

**8. MLOps wiring.**
- **Prompt Flow** (Foundry's prompt orchestration) — DAG-based prompt + tool + branching; deployable as endpoint; evaluation built in.
- **Evaluations** — pre-built metrics (groundedness, relevance, fluency, similarity, F1 / BLEU / ROUGE) + custom evaluators; reproducible across runs.
- **Tracing** — OpenTelemetry-compatible traces of agent runs.
- **Model Registry** — versioned models with deployment lineage.
- **CI/CD** — Azure DevOps / GitHub Actions → Foundry SDK → versioned deployment + canary rollout via Agent Service traffic split.
- **Observability** — Application Insights + Foundry-native dashboards; cost attribution via subscription tags.

**9. Lock-in + exit posture.**
- **Portable surfaces** — prompts (text), model weights (via BYOW + Custom Import), source docs in Blob Storage / OneLake, evaluation datasets, Prompt Flow assets (exportable YAML).
- **Sticky surfaces** — Foundry IQ connector configs, Prompt Shields policy, Entra-bound RBAC, BYO VNet networking, Agent Service thread state.
- **Cross-cloud parity** — for AWS Bedrock equivalent see `/bedrock-design`; for GCP see `/vertex-ai-design`. Same workload runnable on all three if you avoid the sticky surfaces.

## Output

```
### Foundry Footprint: <workload-name>

**Workload type:** <chat / RAG / agent / batch-gen / fine-tune>
**Azure subscription + region:** <sub-id, region>
**Networking:** <public / BYO VNet / hybrid>
**Tenancy:** <single Entra tenant / multi-tenant>

**Services enabled:**
| Service | Reason / consumer | Cost class | Failure mode |
|---|---|---|---|

**Model selection:**
| Stage | Model + deployment name | Capacity (PAYG / PTU / Batch) | Why |
|---|---|---|---|

**Agent runtime** (if enabled): [Foundry Agent Service / external SDK + Foundry Models — rationale]

**RAG via Foundry IQ + AI Search** (if enabled): [agentic retrieval Y/N, connectors, vector tier]

**Safety stack:** [Prompt Shields / Groundedness auto-correct / Content Safety filters / Protected Material — list]

**Networking:** [BYO VNet config + private endpoints + reach to MCP/AI Search/Fabric]

**Cost model:**
- PAYG vs PTU vs Batch decision: [rationale; breakeven analysis]
- PTU monthly $: [if applicable]
- Cross-vendor markup: [Azure overhead estimate]

**MLOps wiring:**
- Prompt Flow + Evaluations cadence
- Tracing + observability sink
- CI/CD pipeline

**Lock-in posture:** [portable + sticky + documented exit]

**[RISK: HIGH] choices flagged:** [list, or "none"]

**Recommended ADRs:**
1. [Foundry vs Azure ML scope split]
2. [Model deployment names + capacity per stage]
3. [Agent Service vs external SDK]
4. [BYO VNet enable / defer]
5. [RAG via Foundry IQ vs custom AI Search wiring]
6. [Safety stack tiers]
7. [PTU breakeven trigger]
```

## Quality bar

- Foundry vs Azure ML split named explicitly — GenAI in Foundry, classical ML in Azure ML
- Model deployment names + capacity assignment recorded (not just "GPT-4o" — `gpt-4o` PAYG Global vs PTU Regional matters)
- PTU vs PAYG decision tied to breakeven analysis (>50% util + 150-200M tok/mo) — not "we'll commit and see"
- BYO VNet enabled only when there's a documented compliance requirement — private-endpoint cost adds up
- Prompt Shields + Groundedness enabled for any production user-facing surface
- Cross-vendor markup acknowledged (Azure +20-40% over OpenAI direct) — informs build-vs-buy
- Sonnet 4 / Opus 4 on Foundry: same retirement date applies — migrate before 2026-06-15
- Lock-in posture explicit — Foundry IQ connectors + Prompt Shields policy + Entra RBAC are the sticky surfaces

## What this skill does NOT do

- Does NOT write Bicep / Terraform / ARM — design only; pair with `/terraform-review`
- Does NOT design the per-agent loop — pair with `/agent-design` for loop/tools/guardrails on top of Agent Service
- Does NOT do chunking + retrieval-eval depth — pair with `/rag-design` on top of Foundry IQ + AI Search
- Does NOT replace `/bedrock-design` (AWS) or `/vertex-ai-design` (GCP) or `/sagemaker-design` (AWS classical ML) — pick the platform first
- Does NOT cover Azure subscription / Entra hardening — pair with `/security-audit`
- Does NOT cover Azure ML — for classical MLOps on Azure, that's a separate skill (not yet authored)

## Sources

Canonical docs the dated / priced claims above are sourced from. Last doc-verified against live docs **2026-07-13** (run `/doc-verify` on this file to re-check):

- Foundry docs (canonical namespace `/azure/foundry/`; legacy `/azure/ai-foundry/` redirects here — confirmed live 2026-07-13) — https://learn.microsoft.com/azure/foundry/
- Model catalog (over 1,900 models) — https://learn.microsoft.com/azure/ai-foundry/concepts/foundry-models-overview
- What's new / Agent Service GA (March 2026) — https://learn.microsoft.com/azure/foundry/whats-new-foundry
- Azure OpenAI pricing (GPT-5 $1.25/$10, GPT-5-nano $0.05/$0.40, Batch 50%) — https://azure.microsoft.com/pricing/details/azure-openai/
