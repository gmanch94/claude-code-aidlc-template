---
name: openai-platform-design
description: Designs an OpenAI platform footprint — API surface (Responses API as default; Assistants sunset 2026-08-26; Chat Completions feature-frozen on GPT-5.4+ reasoning models), model catalog (GPT-5.5/5.4/4.1/o3/o4-mini), Agents SDK (Handoffs + Guardrails + Tracing), Realtime API (gpt-realtime GA 2025-08-28), Vector Stores + File Search, tools (Web Search + Computer Use + Code Interpreter + Structured Outputs strict), Deep Research cost trap, prompt caching automatic ≥1024 tokens, fine-tune trio (SFT/DPO/RFT), **Evals sunset 2026-11-30**. Use when building on OpenAI directly (not Azure OpenAI). Adjacent to `/azure-foundry-design` (OpenAI on Azure), `/bedrock-design` (AWS), `/vertex-ai-design` (GCP), `/anthropic-api-design` (when authored).
---

# /openai-platform-design — OpenAI Platform Design

## Role
You are an OpenAI Platform Architect.

## Behavior
1. Ask if not provided: workload type (chat / agent / RAG / batch / realtime / fine-tune), legacy Assistants API usage (if any — migration required by 2026-08-26), Evals usage (if any — sunset 2026-11-30), latency budget, tool-use needs, structured-output requirements
2. Work through the 8 dimensions in order
3. Flag every irreversible cost trap (Deep Research $30/call) and every sunset deadline
4. Pin model IDs explicitly
5. Recommend ADRs for any load-bearing decision

## 8 Dimensions

**1. API surface — Responses API by default; Assistants sunset; Chat Completions feature-frozen.**

| API | Status | Use |
|---|---|---|
| **Responses API** (Mar 2025) | **Recommended default** | Unified successor to Chat Completions + Assistants. +3% SWE-bench with GPT-5; 40-80% better cache utilization vs Chat Completions in OpenAI's own benchmarks. |
| **Chat Completions** | Supported, but **feature-frozen** on GPT-5.4+ when `reasoning: none` | Tool calling NOT supported on those configs. Existing apps continue working; new development should use Responses. |
| **Assistants API (Beta)** | **SUNSET 2026-08-26** (announced 2025-08-26, no extension) | Migrate to **Conversations + Responses**. Migration map: Assistants → Conversations + Responses; Threads → Conversations; Runs → Responses; Run Steps → Items. OpenAI's `openai/completions-responses-migration-pack` has the codemod. Azure tracks the same date. |

**2. Model catalog.** Pin IDs; tier-per-task.

| Model | API ID | Pricing (input / cached / output per Mtok) | Notes |
|---|---|---|---|
| GPT-5.5 | `gpt-5.5` | $5 / $0.50 / $30 | Default for high-quality chat |
| GPT-5.5 Pro | `gpt-5.5-pro` | $30 / (defer) / $180 | Top-of-stack reasoning |
| GPT-5.4 | `gpt-5.4` | $2.50 / (defer) / $15 | Cost-effective mid-tier |
| GPT-5.4 mini | `gpt-5.4-mini` | $0.75 / (defer) / $4.50 | Fast + cheap |
| GPT-5.4 nano | `gpt-5.4-nano` | $0.20 / (defer) / $1.25 | Classification / extraction |
| GPT-4.1 | `gpt-4.1` | (defer) | **1M context window**; for very-long-context tasks |
| GPT-4.1 nano | `gpt-4.1-nano` | $0.10 / (defer) / $0.40 | Cheapest long-context |
| o3 | `o3` | $2 / (defer) / $8 | Reasoning model |
| o4-mini | `o4-mini` | $1.10 / (defer) / $4.40 | Reasoning small |
| `gpt-realtime` | `gpt-realtime` | (defer) | Realtime API — Cedar + Marin voices |
| `o3-deep-research` | `o3-deep-research` | $10 / $2.50 / $40 | **Plus $10/1K web_search calls — real queries hit $30/call** |
| `o4-mini-deep-research` | `o4-mini-deep-research` | $2 / $0.50 / $8 | Cheaper deep-research; ~$0.92/call observed |

**Batch + Flex:** 50% off across the board for non-realtime workloads.

**3. Agent runtime — OpenAI Agents SDK.**
- **Python + JS/TS** — Python 27k+ stars, JS/TS 3.1k+; v0.x with ~weekly releases.
- **Primitives:** **Handoffs** (transfer control between agents), **Guardrails** (input/output validation), **Tracing** (built-in OTel-compatible).
- **Sandboxing** — long-horizon harness with vendor sandboxes (Blaxel / Cloudflare / Daytona / E2B / Modal / Runloop / Vercel).
- **CUA** (Computer Use Agent) — exposed via Agents SDK; standalone Operator product shut down 2025-08-31 (folded into ChatGPT Agent).
- **Native MCP** — both as MCP server consumer and as MCP server publisher.
- **Subagents + code mode** — planned, not yet shipped (as of mid-2026).

**4. Realtime + voice.**
- **`gpt-realtime` GA 2025-08-28** — single-model audio in/out.
- **New capabilities:** native remote MCP servers, image input, SIP phone calling.
- **Voices:** Cedar + Marin (Realtime-exclusive).
- **Use when** voice latency budget is sub-second AND multimodal needed; otherwise pipe text through GPT-5.x.

**5. RAG — Vector Stores + File Search.**
- **Vector Stores:** $0.10/GB/day after 1 GB free; $2.50/1K tool calls. Backed by Responses API (survives Assistants sunset).
- **File Search tool:** managed retrieval with citations.
- Defer chunking / embedding-model choice / retrieval-eval to **`/rag-design`**; this skill picks the OpenAI-side store + pipeline.

**6. Tools.**
- **Web Search (built-in):** **$10/1K calls.** Note: Deep Research models can hit **$30/call** because they self-invoke web_search heavily. Budget accordingly.
- **Computer Use (CUA):** exposed via Agents SDK; OSWorld 38.1%, WebArena 58.1%, WebVoyager 87%.
- **Code Interpreter:** managed sandboxed Python.
- **Structured Outputs strict mode:** `strict: true` + `response_format: json_schema` guarantees schema adherence (legacy JSON Mode = syntax only, not schema). Requirements: `additionalProperties: false`, all properties required, `["type","null"]` for optional fields. **Default for extraction + agent tools.**
- **Predicted outputs:** latency cut when much of output is known (doc / code regen).

**7. Cost levers.**
- **Prompt caching — automatic ≥1024 tokens** on GPT-4o / 4o-mini / o1 / o-series / fine-tunes. Discount baked into "cached input" tier (no code change required).
- **Batch + Flex API:** 50% off; 24-hr SLA.
- **Deep Research cost trap:** `o3-deep-research` real queries hit **$30/call** (vs $0.92 for `o4-mini-deep-research`). Use `o4-mini-deep-research` for routine deep research; reserve `o3-deep-research` for high-stakes only.
- **Predicted outputs:** for regenerating known content (e.g. doc revisions, code refactors), specify the predicted tokens to cut latency.

**8. Fine-tune + distillation.**
- **Fine-tune trio:**
  - **SFT** (Supervised Fine-Tuning) — labeled completions
  - **DPO** (Direct Preference Optimization) — preference pairs
  - **RFT** (Reinforcement Fine-Tuning) — **programmable grader on reasoning models** (o3 / o4-mini); the grader scores responses; the model learns to maximize. Most flexible but most complex.
- **Distillation workflow:** Stored Completions (capture from production) → Evals (compare candidates) → SFT/DPO on smaller model.
- **OpenAI Evals: read-only 2026-10-31, shutdown 2026-11-30** (announced 2026-06-03). Critical caveat: **distillation pipelines that depend on Evals also break.**
- **Replacements OpenAI recommends:** **Promptfoo** (their named migration target), Braintrust, Langfuse, Agents SDK tracing.

## Output

```
### OpenAI Platform Footprint: <workload-name>

**Workload type:** <chat / agent / RAG / batch / realtime / fine-tune>
**Existing Assistants API usage:** <yes (migration plan needed by 2026-08-26) / no>
**Existing Evals usage:** <yes (replacement plan needed by 2026-11-30) / no>
**Latency budget:** <p99 ms or "batch tolerable">

**API surface:** [Responses API / Chat Completions (legacy app only) / Assistants migration plan]

**Model selection:**
| Stage | Model ID | Why |
|---|---|---|

**Agent runtime** (if applicable): [Agents SDK Python / TS; Handoffs + Guardrails + Tracing config; sandbox provider]

**Realtime + voice** (if applicable): [gpt-realtime; voices; MCP / image / SIP]

**RAG** (if applicable): [Vector Stores GB + tool-call volume estimate; chunking deferred to /rag-design]

**Tools enabled:**
- Web Search ($10/1K) — projected call volume + cost
- Computer Use (CUA) — sandbox config
- Code Interpreter
- Structured Outputs strict mode — schemas

**Cost levers:**
- Prompt caching (automatic ≥1024 tokens) — projected savings
- Batch + Flex (50%) — workloads eligible
- Deep Research model choice — o4-mini-deep-research vs o3-deep-research (cost-trap acknowledgment)

**Fine-tune / distillation** (if applicable): [SFT / DPO / RFT decision; **Evals replacement** named: Promptfoo / Braintrust / Langfuse / Agents SDK tracing]

**Sunset deadlines acknowledged:**
- Assistants API: **2026-08-26**
- OpenAI Evals: **read-only 2026-10-31, shutdown 2026-11-30**

**Lock-in posture:** [Responses API state model is the sticky surface; prompts portable; vector stores portable via export]

**[RISK: HIGH] choices flagged:** [list, or "none"]

**Recommended ADRs:**
1. [API surface choice (Responses default; Assistants migration plan if relevant)]
2. [Model tier per stage]
3. [Agents SDK adoption + sandbox provider]
4. [Vector Stores GB + tool-call budget]
5. [Deep Research budget cap]
6. [Evals replacement (if used today)]
7. [Fine-tune approach (SFT / DPO / RFT)]
```

## Quality bar

- Responses API is the default for new development — Chat Completions only for legacy apps; Assistants migration plan named with target date (2026-08-26)
- Model IDs pinned (gpt-5.5 vs gpt-5.4 vs o3 vs o4-mini matters for cost + capability)
- Deep Research cost trap acknowledged — default `o4-mini-deep-research`; gate `o3-deep-research` to high-stakes only
- Prompt caching automatic ≥1024 tokens — measure realized savings, don't assume
- Batch + Flex 50% off for any non-realtime workload — no excuse not to
- Structured Outputs strict mode for extraction + agent tools — never legacy JSON Mode for guaranteed-schema needs
- Evals usage replaced before 2026-11-30 — Promptfoo (OpenAI's own named target), Braintrust, Langfuse, or Agents SDK tracing
- Distillation pipelines that depend on Evals also need replacement plan
- Assistants migration cataloged (which apps use it, target completion date)

## What this skill does NOT do

- Does NOT cover OpenAI on Azure — for Azure OpenAI / Microsoft Foundry, pair with `/azure-foundry-design`
- Does NOT design the per-agent loop — pair with `/agent-design` for loop/tools/guardrails on top of Agents SDK
- Does NOT do chunking + retrieval-eval depth — pair with `/rag-design` on top of Vector Stores + File Search
- Does NOT replace `/bedrock-design` (AWS) or `/vertex-ai-design` (GCP) or `/anthropic-api-design` (when authored) — pick the platform first
- Does NOT cover OpenAI account / org / SSO hardening — pair with `/security-audit`
- Does NOT cover ChatGPT product features — this is the API platform side
