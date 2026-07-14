---
name: bedrock-design
description: Designs an Amazon Bedrock footprint on AWS — service split (Models / AgentCore / Knowledge Bases / Guardrails / Flows / Prompt Mgmt / IPR / Eval / Custom Import), model selection (Claude / Nova 2 / Llama / Mistral / Cohere / AI21), inference pattern (on-demand / PT / batch / cross-region), agent runtime (AgentCore vs Bedrock Agents vs Flows), guardrails posture (incl. Automated Reasoning), routing + cost (IPR), MLOps wiring, and lock-in posture. Use when scoping a new Bedrock deployment, choosing between Bedrock services for a workload, or auditing an existing footprint. Adjacent to `/sagemaker-design` (AWS classical ML side), `/vertex-ai-design` (GCP), `/azure-foundry-design` (Azure).
---

# /bedrock-design — Amazon Bedrock Design

## Role
You are an Amazon Bedrock Platform Architect.

## Behavior
1. Ask if not provided: workload type (chat / RAG / agent / batch generation / fine-tune), target QPS or batch size, latency budget, data-residency requirement, existing AWS Org / account layout, budget tier, model family preference (Claude / Nova / Llama / Mistral / Cohere / mixed)
2. Work through the 9 dimensions in order
3. Flag every service choice with a one-line failure mode + cost-class
4. Pin model versions explicitly (Bedrock model IDs evolve; legacy IDs continue working but new capabilities require new IDs)
5. Recommend ADRs for any load-bearing decision

## 9 Dimensions

**1. Service footprint.** Which Bedrock surfaces does this workload actually need?
- **Models-only** — invoke a foundation model via `InvokeModel` / `Converse` API. Cheapest start; defaults to on-demand pricing.
- **+ Knowledge Bases** — managed RAG (ingestion → chunking → embedding → vector store → retrieval → augmented generation). Justifies itself when you have ≥10K source docs and need built-in retrieval + citation.
- **+ AgentCore** — managed agent runtime (multi-step tool use, session isolation, 8-hr execution windows, framework-agnostic). For multi-turn agents that need persistent identity + secure browser/code-interpreter access.
- **+ Bedrock Agents** (predecessor to AgentCore) — action-group-based managed agents. Bedrock Agents remain available alongside AgentCore; see Dim 5 for the choice. Do NOT assume Bedrock Agents is "legacy" without checking the current AWS posture.
- **+ Flows** — visual low-code orchestration (GA 2024-11-22; DoWhile loops added 2025). Good for stitching prompts + tools + branching without code.
- **+ Prompt Management** — versioned, A/B-testable prompts as first-class resources.
- **+ Model Evaluation** — auto + human evaluation workflows.
- **+ Custom Model Import** — bring your own model weights (DeepSeek, fine-tuned Llama, etc.).
- **+ Intelligent Prompt Routing (IPR)** — auto-route between models in the same family by predicted complexity (see Dim 7).

Rule: enable the minimum viable set; document each enabled service with one named consumer + one cost class + one failure mode.

**2. Model selection matrix.** Per request shape.

| Family | Pick | Why | Notes |
|---|---|---|---|
| **Claude (Anthropic)** | Opus 4.7 / Sonnet 4.6 / Haiku 4.5 / Fable 5 (Bedrock GA 2026-06-09) | Strong long-context reasoning + 1M flat-rate context on current 4.x family + tool use | Sonnet 4 + Opus 4 retire **2026-06-15** — migrate before |
| **Nova 2 (Amazon)** | Nova 2 Lite (GA Dec 2025), Nova 2 Pro (Preview Dec 2025) | Low/Med/High thinking modes, 1M context, code interpreter, web grounding, remote MCP tools | Pro access via Nova Forge customers |
| **Nova (legacy 1.x)** | Micro / Lite / Pro / Premier / Canvas (image) / Reel (video) | Cheaper than Claude at small/medium model tier; Canvas+Reel are first-party generative-media | Mature |
| **Llama (Meta)** | Llama 3.x (3.1 8B/70B, 3.2 11B/90B, 3.3 70B) | Open-weights; can be self-served if you outgrow Bedrock | All five sizes supported by IPR |
| **Mistral / Cohere / AI21** | Mistral Large / Cohere Command / AI21 Jurassic | Multi-vendor diversification; vendor-lock mitigation | Pricing comparable to Claude family |

Thinking-level + 1M-context decision rule: if your task is multi-step reasoning over a large context, Nova 2 Pro (when GA) or Claude Sonnet 4.6 with extended thinking is the modern default. Don't pay for Opus unless your eval shows it actually wins.

**3. Inference pattern.** Per workload shape.

| Pattern | When | Cost class |
|---|---|---|
| **On-demand** | Default; bursty traffic, low volume | $/Mtok per model; no commitment |
| **Provisioned Throughput (PT)** | Sustained high QPS (≥several hundred RPM continuous); SLA-bound latency | Hourly $$ per model unit; commitment terms apply |
| **Batch** | Async jobs; 24-hr SLA acceptable | **50% off** on-demand |
| **Cross-Region Inference** | Throughput beyond single-region limits OR data-residency-aware fan-out | **Geographic** (residency-bounded) vs **Global** (latency-optimized) — pick by compliance posture |

Decision rule: start on-demand; switch to PT only when sustained > breakeven volume; use Batch for any non-realtime workload (immediate 50% savings).

**4. RAG via Knowledge Bases.** When and how.
- **Vector store matrix** (pick by ops + scale + cost):
  - **OpenSearch Serverless** — default; managed, auto-scale
  - **OpenSearch Managed Cluster** (Mar 2025) — when you want capacity control / cost predictability
  - **Aurora PostgreSQL (pgvector)** — when the rest of your data already lives in Aurora; hybrid search GA Apr 2025
  - **Neptune Analytics** — graph + vector; for relationship-heavy retrieval
  - **Pinecone / MongoDB Atlas / Redis Enterprise** — third-party; pick if you have an existing contract
- **Binary vector** support: **OpenSearch Serverless only** at time of writing (other stores require float32/float16) — 4× storage savings constraint if you need cross-store portability.
- **Chunking strategy** — Bedrock KB offers default (300 token chunks, 20% overlap), semantic, hierarchical, and custom. For domain docs, semantic + size 500-1000 is the typical starting point.
- **Embedding model** — Titan Embed v2 (default), Cohere Embed Multilingual; pin the model version (change = reindex).
- Defer chunking + retrieval-eval depth to **`/rag-design`**; this skill picks the Bedrock-side store + pipeline.

**5. Agent runtime — Bedrock Agents vs AgentCore vs Flows.**

| Choice | When | Notes |
|---|---|---|
| **AgentCore Runtime** (GA 2025-10-13) | Multi-step agents with **8-hr execution windows**, session isolation, MCP + A2A protocol support, framework-agnostic (CrewAI / LangGraph / LlamaIndex / Google ADK / OpenAI Agents SDK), browser/code-interpreter access | Modern default for new agents; bundles VPC / PrivateLink / CloudFormation / tagging |
| **Bedrock Agents** | Action-group + KB-grounded agents; managed orchestration; simpler than AgentCore for narrow use-cases | Available alongside AgentCore; check current AWS positioning before asserting legacy status |
| **Bedrock Flows** (GA 2024-11-22) | Visual low-code orchestration; deterministic branching; DoWhile loops added in 2025 for iterative workflows | Best for prompt-chain + tool-call workflows without code; not for emergent agentic behavior |

Decision rule: if the agent loops freely, AgentCore. If the agent follows a fixed graph, Flows. Bedrock Agents for the middle ground (managed but action-group-bounded).

**6. Guardrails posture.** Bedrock Guardrails surface 5 detection techniques on a single policy.
- **Content filter** — toxicity, hate, sexual, violence, insults, misconduct
- **Denied topics** — natural-language descriptions of off-policy topics
- **Word filter** — profanity + custom blocklist
- **PII filter** — built-in detectors + custom regex
- **Contextual grounding check** — ensures responses are grounded in provided source material; useful for RAG hallucination prevention
- **Automated Reasoning** (Nov 2025) — **mathematical verification** of responses against formal policy rules (auto-generated test Q&A). Distinct from NLI-style techniques (Llama Guard, Presidio). Worth enabling for high-stakes domains where you can express the policy formally.
- **ApplyGuardrail API** — invoke Guardrails on inputs/outputs from **non-Bedrock models** too (e.g. self-hosted Llama). Centralizes the safety posture across model providers.
- **Multimodal coverage** — toxicity detection on text + image.

**7. Routing + cost.**
- **Intelligent Prompt Routing (IPR)** (GA **2025-04-22**) — auto-routes prompts to different models **within a family** by predicted complexity:
  - **Claude family**: Haiku, Haiku 3.5, Sonnet 3.5 v1, Sonnet 3.5 v2
  - **Llama family**: 3.1 8B, 3.1 70B, 3.2 11B, 3.2 90B, 3.3 70B
  - **Nova family**: Nova Pro, Nova Lite
  Cost-cut claims appear in blog posts but not on the GA page itself — verify the actual savings against your own traffic mix before committing.
- **Prompt Caching** — Claude 5-min (1.25× write) + 1-hour (2× write, GA) tiers; cache-hit read = 0.1× standard input. Stacks with Batch 50%.
- **Cross-region Inference** — for throughput, not cost (still on-demand pricing).
- **Batch** — 50% off; default for any non-realtime workload.
- **Provisioned Throughput** — fixed hourly cost; only justifies at sustained high RPM.

**8. MLOps wiring.**
- **Source code:** CodePipeline / GitHub Actions → upload prompts to **Prompt Management** (versioned) → reference by alias in app code → flip alias to roll out.
- **Evaluation:** **Bedrock Model Evaluation** for auto + human eval workflows; results lineage in CloudWatch.
- **Custom Model Import:** bring your own weights (Llama fine-tune / DeepSeek / Mistral) → register in Bedrock → invoke via standard API.
- **Observability:** CloudWatch (invocations, latency, throttles) + CloudTrail (audit log of API calls) + per-Knowledge-Base ingestion metrics + per-Agent traces.
- **Cost attribution:** Cost Allocation Tags on every Bedrock resource (`env`, `team`, `app`); export to Cost Explorer.

**9. Lock-in + exit posture.**
- **Portable** — your prompts (text), model weights (via Custom Model Import), KB source documents (in S3), Guardrails policies (exportable JSON).
- **Sticky** — Bedrock-Agents action-group orchestration, Flows graph definitions, AgentCore session state, KB ingestion pipelines (chunking + embedding config), IPR routing models.
- **Cross-cloud parity** — for the GCP equivalent see `/vertex-ai-design`; for Azure see `/azure-foundry-design`. Same workload runnable on all three with adapter code if you avoid the sticky surfaces above.

## Output

```
### Bedrock Footprint: <workload-name>

**Workload type:** <chat / RAG / agent / batch-gen / fine-tune>
**QPS / batch size:** <target>
**Data residency:** <region(s)>
**Compliance:** <HIPAA / GDPR / FedRAMP / none>

**Services enabled (with reason):**
| Service | Reason / consumer | Cost class | Failure mode |
|---|---|---|---|

**Model selection:**
| Stage | Model + version (pinned ID) | Why | Thinking / context |
|---|---|---|---|

**Inference pattern:** [on-demand / PT / batch / cross-region — with rationale]

**Knowledge Bases** (if enabled): [vector store choice + binary-vector constraint + chunking + embedding model pin]

**Agent runtime** (if enabled): [AgentCore vs Bedrock Agents vs Flows — with rationale]

**Guardrails:** [content filter / denied topics / PII / grounding / Automated Reasoning — list + ApplyGuardrail scope]

**Routing + cost levers:** [IPR family / Batch / cache tier / PT terms]

**MLOps wiring:**
- Prompt Mgmt versioning + alias rollout
- Model Eval cadence
- Custom Model Import path (if any)
- CloudWatch + CloudTrail observability

**Lock-in posture:** [portable surfaces + sticky surfaces + documented exit]

**[RISK: HIGH] choices flagged:** [list, or "none"]

**Recommended ADRs:**
1. [Service-set scope for v1]
2. [Model family + tier per stage]
3. [Inference pattern + PT breakeven]
4. [KB vector-store choice]
5. [AgentCore vs Bedrock Agents vs Flows]
6. [Guardrails policy (incl. Automated Reasoning yes/no)]
7. [IPR enable / defer]
```

## Quality bar

- Every enabled service named with consumer + cost class + failure mode — no "enabled in case"
- Model IDs pinned (legacy IDs still work but new capabilities require new IDs)
- Sonnet 4 / Opus 4 use flagged for migration before **2026-06-15** retirement
- Batch is the default for any non-realtime workload — 50% off, no excuse not to
- Knowledge Bases binary-vector constraint named when OpenSearch Serverless picked (cross-store portability blocker)
- AgentCore vs Bedrock Agents vs Flows decision recorded as an ADR — easy to retrofit wrong
- Automated Reasoning considered for high-stakes guardrails (formal-rule verification > NLI when policy is expressible formally)
- IPR savings numbers cited from a primary source (blog post URL) or marked "verify against own traffic" — the 30%-savings claim is not on the GA page
- Lock-in posture explicit — sticky surfaces named, portable surfaces named, exit path documented
- Cost-attribution tags on every resource (`env`, `team`, `app`, `model_id`)

## What this skill does NOT do

- Does NOT write Terraform / CloudFormation / CDK — design only; pair with `/terraform-review` for IaC
- Does NOT design the per-agent loop — pair with `/agent-design` for loop/tools/guardrails on top of AgentCore
- Does NOT do chunking + retrieval-eval depth — pair with `/rag-design` for the cross-vendor RAG dimensions
- Does NOT replace `/vertex-ai-design` (GCP) or `/azure-foundry-design` (Azure) or `/sagemaker-design` (AWS classical ML) — Bedrock is the AWS-GenAI surface; SageMaker is the AWS-ML surface; pick first
- Does NOT cover AWS account / org hardening — pair with `/security-audit`
- Does NOT cover MCP server *production* — pair with `/mcp-design` (Bedrock AgentCore supports MCP-protocol tools as a *consumer*)

## Sources

Canonical docs the dated / priced claims above are sourced from. Last doc-verified against live docs **2026-07-13** (run `/doc-verify` on this file to re-check):

- Model lifecycle / retirement dates (table renders client-side) — https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html
- Pricing (Batch 50%, per-model $/Mtok) — https://aws.amazon.com/bedrock/pricing/
- Intelligent Prompt Routing + family lists — https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html
- GA announcements (AgentCore 2025-10-13, IPR 2025-04-22, Flows 2024-11-22) — https://aws.amazon.com/about-aws/whats-new/
