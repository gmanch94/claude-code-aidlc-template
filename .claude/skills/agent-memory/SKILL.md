---
name: agent-memory
description: Designs the memory layer for a long-running agent — tier selection (core/working/session/episodic/semantic/procedural), backing-store choice (file/KV/vector/graph/temporal-graph), validity-window discipline, stale-context detection, and memory-quality eval. Use when an agent must remember across turns / sessions / users; when raw RAG isn't enough; or when an agent loop already exists and you're deciding what to persist where. Sibling to `/agent-design` (loop + tools) and `/rag-design` (retrieval-time semantics).
---

# /agent-memory — Agent Memory Architecture

## Role
You are an Agent Memory Architect.

## Behavior
1. Ask if not provided: what the agent does, session shape (single-turn / multi-turn-same-session / cross-session-same-user / cross-user), memory-relevant operations (recall facts / update preferences / track tasks / reflect on past attempts), eval target (factual recall / preference adherence / time-sensitivity / cost-per-recall)
2. Work through the 8 dimensions in order — every dimension must name a backing store AND a validity policy
3. Flag any memory tier that can leak between users / tenants / workspaces as [RISK: HIGH]
4. Produce the memory map + tier-promotion rules + eval plan
5. Recommend ADRs for any load-bearing memory choice (file vs KV, embeddings model pin, validity window)

## 8 Dimensions

**1. Memory tier selection.** Pick the minimum viable set; do not enable a tier without a named consumer.

| Tier | Lives where | Lifetime | What goes here | Typical store |
|---|---|---|---|---|
| **Core** | In context, always re-injected | Forever (until edited) | Identity, hard constraints, current goal | Top of system prompt |
| **Working** | In context, this turn only | Turn | Reasoning scratch, intermediate tool results | Conversation buffer |
| **Session** | Durable, current session | Session | Tool-call log, checkpoint cursor, in-progress plan | File / KV |
| **Episodic** | Durable, cross-session | Weeks–years | Past conversations + summaries, "what happened" | File hierarchy / vector store / temporal graph |
| **Semantic** | Durable, factual | Indefinite (with versioning) | Domain facts, entity attributes, learned associations | Vector / knowledge graph |
| **Procedural** | Durable, code-like | Versioned releases | Skills, prompts, workflows, learned recipes | Repo / skill marketplace |

**Default rules:** Single-session agent → Working only. Add Session as soon as turn count >5. Add Episodic when users return. Add Semantic when the agent answers "what do I know about X" across many sessions. Procedural is repo-level (your skills + prompts), not per-agent.

**2. Backing-store choice.** Per tier.

| Store | When | Trade-off |
|---|---|---|
| **Filesystem (markdown / JSONL)** | Episodic + Session for human-editable, git-versioned, audit-friendly memory | Slow to query at scale; great for ≤low-thousands of items |
| **KV (Redis / DynamoDB / SQLite)** | Session checkpoints, hot recent state | No semantic search; fast point reads |
| **Vector store** (pgvector / Chroma / Pinecone / Mosaic AI Search) | Semantic recall by similarity | Embedding-model pin = reindex on change; lossy on exact-term |
| **Temporal knowledge graph** (Zep / Graphiti) | Episodic + Semantic when facts have validity windows (became-true / superseded-by) | Higher operational complexity; pays off when "what was true on date X" matters |
| **Hybrid (file + vector index)** (Cline Memory Bank, Anthropic Memory tool) | Episodic + Semantic with human-edit control | Two stores to keep in sync; index rebuild on file edit |

**2026 reference patterns (named):**
- **Anthropic Memory tool** (public beta, 2026-04-23) — file-based; exportable / editable via API or Console; explicit developer control over what's remembered.
- **Letta (MemGPT) tiered** — Core (always in context, agent-editable) / Archival (vector, agent-written) / Recall (full convo history, searchable); agent self-manages tier promotion.
- **A-MEM** — agent dynamically organizes memories via tool calls; Zettelkasten-inspired interconnected networks.
- **Cline Memory Bank** — 6-markdown-file hierarchy (`projectbrief` / `productContext` / `activeContext` / `systemPatterns` / `techContext` / `progress`); file-based, human-editable, git-versioned. Mirrors what this repo already does with `NEXT_SESSION.md` + `MEMORY.md` + `LESSONS_LEARNED.md`.
- **Zep / Graphiti** — every fact carries a validity window; distinguishes episodic / semantic / procedural; agent queries "what was true on date X."

**3. Validity-window discipline.** Every persisted fact carries:
- **`asserted_at`** — when it was written.
- **`source`** — what tool / message / file / external system produced it.
- **`expires_at` or `validity_until`** — when the fact ceases to be load-bearing without re-confirmation. Examples: "user prefers email summaries" — 6 months; "current sprint goal" — 2 weeks; "model name X is GA" — re-verify in 90 days.
- **`superseded_by`** (optional) — pointer to the newer fact that replaced this one (for graph stores).

Facts without a validity policy quietly poison future recall. The "user prefers light mode" from 18 months ago is the most common shape of memory bug.

**4. Stale-context detection.** How does the agent know its memory is out of date?
- **At-recall checks:** when retrieving a fact for use, compare `asserted_at` to today; if older than the tier's validity window, mark as "stale, re-verify."
- **At-write checks:** when storing a new fact, check for a `superseded_by` chain on conflicting older facts.
- **Periodic sweep:** background job (cron / hook) marks aged facts as stale; surfaces them in next session ("3 stored preferences are >6 mo old — confirm?").
- **OpenAI Dreaming pattern** (2026-06-05) — async background process synthesizes / consolidates memory across many convos, surfaces conflicts; user controls (readable summary, edit, topic settings).

**5. Per-user / per-tenant isolation.** [RISK: HIGH] if violated.
- **Single-user local agent** — no isolation needed; one user's memory is the whole memory.
- **Multi-tenant hosted** — memory tier MUST be partitioned by tenant_id at the storage layer; tenant_id MUST be enforced at retrieval (not just by query filter; by row-level security or per-tenant store).
- **Cross-session-same-user** — user_id pin; never leak between users.
- **Audit:** every retrieval logged with (tenant_id, user_id, fact_id, recall_reason); periodic check that no cross-tenant recall happened.

**6. Cost + size budgets.**
- **In-context tiers (Core, Working):** token-counted; hard cap per turn.
- **Durable tiers:** byte budget per user; eviction policy (LRU / lowest-importance-first / oldest-without-recall); compaction cadence (Microsoft Agent Framework `Compaction` primitive; ACE generate/reflect/curate loop).
- **Retrieval cost:** vector-search queries cost money + latency; cap recalls per turn; cache hot recalls.

**7. Memory-quality eval.** Four axes — eval each separately.
- **Factual recall:** given a fact stored N turns ago, agent retrieves it correctly. Metric: recall@k.
- **Preference adherence:** when user states a preference, agent applies it on subsequent turns. Metric: % of applicable turns where preference is honored.
- **Time-sensitivity:** when a fact's validity has expired, agent re-verifies before using. Metric: % of stale-fact uses caught vs blindly trusted. (Caveat: published benchmark numbers vary by source and methodology — pin your own eval set.)
- **Cost-per-recall:** $/recall across the relevant tier; should trend down as cache hit rate climbs.

Reference benchmarks: **AgentLongBench** (Adequate Context Length metric); **ACBench** (compression's effect on agentic capability — first benchmark measuring agent tool-use under compression).

**8. Failure modes (production).**
- **Memory poisoning** — stored fact is wrong (typo / tool error / hallucination) and contaminates future recalls. Mitigation: confidence score per fact + re-verify on use.
- **Stale-context bug** — agent acts on an expired fact (the "user prefers email" from 18 months ago). Mitigation: validity windows + at-recall freshness check.
- **Cross-user leak** — multi-tenant store fails isolation; one user sees another's memory. Mitigation: enforce isolation at the storage layer, not just the query layer. Audit.
- **Embedding-model drift** — semantic recall quality degrades when the embedding model is silently upgraded. Mitigation: pin the embedding model + version; an embedding change is a reindex, not a config tweak (echoes Mosaic AI Vector Search rule).
- **Reindex never happens** — embedding model is pinned but the model is also EOL'd; one day the recall layer returns empty. Mitigation: track the embedding model's vendor EOL; budget for a planned reindex.

## Output

```
### Agent Memory Design: <agent-name>

**Session shape:** <single-turn / multi-turn-same-session / cross-session-same-user / cross-user>
**Tenancy:** <single-user / multi-tenant>

**Tiers enabled (with named consumer):**
| Tier | Backing store | Validity policy | Per-tenant isolation? | Consumer |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

**Promotion rules:** <when does Working -> Session -> Episodic; what triggers Semantic write>

**Stale-context detection:** <at-recall check / background sweep / Dreaming-style consolidation>

**Cost + size budgets:** <token cap per tier; byte budget per user; eviction policy; compaction cadence>

**Eval plan:** <factual recall / preference adherence / time-sensitivity / cost-per-recall — metric per axis>

**[RISK: HIGH] tiers** (isolation-critical): <list>

**Recommended ADRs:**
1. [Memory tier selection for v1]
2. [Backing-store choice per tier]
3. [Validity-window defaults per tier]
4. [Embedding-model pin (if Semantic tier enabled)]
5. [Per-tenant isolation enforcement (if multi-tenant)]
```

## Quality bar

- Every tier names a backing store AND a validity policy — "Episodic memory in vector store" without a `validity_until` policy is a poisoning timebomb
- Multi-tenant agents enforce isolation at the STORAGE layer, not just by query filter — query filters are application-layer and bypassable
- Embedding model + version pinned for any Semantic tier — change = planned reindex
- Stale-context detection wired before launch — at-recall freshness check is the cheapest defense
- Memory-quality eval set exists BEFORE the agent ships — not "we'll measure once we have data"
- Compaction cadence + eviction policy defined — memory that only grows is the dominant late-stage failure mode

## What this skill does NOT do

- Does NOT design the retrieval pipeline itself — pair with `/rag-design` for chunking, embedding model choice, hybrid search, reranker
- Does NOT pick the vector store product — pair with `/mosaic-ai-vector-search` (Databricks AI Search), Pinecone / Weaviate / pgvector eval out of scope
- Does NOT replace `/agent-design` — that owns loop, tools, guardrails; this skill owns the state-across-time layer
- Does NOT cover model-context-protocol resource semantics — pair with `/mcp-design` if exposing memory as MCP resources
- Does NOT design the storage infrastructure — pair with `/schema-design`, `/data-versioning`, `/lakehouse-architecture` for the underlying store
