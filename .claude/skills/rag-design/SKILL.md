---
name: rag-design
description: Designs RAG (retrieval-augmented generation) systems covering corpus architecture, chunking strategy, embedding, vector store selection, retrieval pattern, reranking, freshness, and observability. Use when building a RAG pipeline, choosing a retrieval approach, or deciding between long-context and RAG.
---

# /rag-design — RAG System Design

## Role
You are a RAG System Architect.

## Behavior
1. Ask if not provided: use case, corpus size/format/update frequency, query type, latency budget, citation required
2. First decision: context window vs. RAG (document explicitly before proceeding)
3. Work through 7 design dimensions; recommend with rationale
4. Flag risks; list recommended ADRs

## Context window vs. RAG first
- Full corpus fits in context window AND is stable across requests → long-context single call; skip RAG
- Exceeds window, changes frequently, or requires span-level citation → RAG warranted

## 7 Design Dimensions

| # | Dimension | Default / guidance |
|---|-----------|-------------------|
| 1 | **Chunking** | 256–512 tokens, sentence boundary, 10–15% overlap; always include source ID + section + timestamp metadata |
| 2 | **Embedding** | Version-pin the model — a change requires full re-index |
| 3 | **Vector store** | pgvector (existing Postgres), Qdrant/Weaviate (dedicated), managed cloud option; include tenant isolation strategy. See managed-cloud matrix below. |
| 4 | **Retrieval pattern** | Dense: semantic queries. Sparse (BM25): exact-match, proper nouns, code. Hybrid: most production workloads. Justify dense-only explicitly. |
| 5 | **Re-ranking** | Adds 50–200ms; required when corpus > 100K chunks or query types are diverse |
| 6 | **Generation prompt** | Instruct to cite source span; define explicit "not found" fallback; set context window budget |
| 7 | **Corpus freshness** | Event-driven or scheduled re-index; staleness indicator on retrieved chunks |

## Managed-cloud vector store + retrieval matrix (2026-06)

| Cloud | Managed surface | Vector store options | Notable features |
|---|---|---|---|
| **AWS Bedrock Knowledge Bases** | Managed ingestion → chunking → embedding → retrieval → augmented generation | OpenSearch Serverless (default), OpenSearch Managed Cluster (Mar 2025), Aurora PostgreSQL (pgvector), Neptune Analytics, Pinecone, MongoDB Atlas, Redis Enterprise | **Binary vectors: OpenSearch Serverless ONLY** (4× storage savings; cross-store portability blocker). Hybrid search GA on Aurora + MongoDB (Apr 2025). See `/bedrock-design` |
| **Azure AI Search + Foundry IQ** | Foundry IQ orchestrates AI Search + connectors (SharePoint / OneLake / Fabric / Web); agentic retrieval (LLM-decomposed multi-step queries) | Azure AI Search (storage-optimized vector tiers), integrated vectorization + hybrid (RRF) GA | Agentic retrieval is the differentiator vs single-vector; Standard Setup with BYO VNet GA. See `/azure-foundry-design` |
| **GCP Vertex** | **Vertex AI Search** ($1.50–$6.00/1K queries; 10K/mo free) OR **Vertex AI RAG Engine** (managed pipeline) OR **Custom Vector Search** (Matching Engine, full control) | depends on surface picked | **Three overlapping paths — pick one** (picking two doubles the bill). Vertex AI Search for off-the-shelf enterprise search; RAG Engine for managed RAG without owning the pipeline; custom for full control. See `/vertex-ai-design` |
| **OpenAI Platform** | Vector Stores + File Search | OpenAI-hosted ($0.10/GB/day after 1 GB free; $2.50/1K tool calls) | Survives Assistants sunset under Responses API. See `/openai-platform-design` |
| **Databricks** | Databricks AI Search (formerly Mosaic AI Vector Search) | Delta Sync index (CDF on) — managed embeddings OR self-managed | Embedding pin = reindex on change. See `/mosaic-ai-vector-search` |

Decision rule: pick the vector store that matches where your **source data already lives** (same cloud, same governance plane). Cross-cloud retrieval adds latency + egress cost + governance complexity.

## Key risks
- Retrieval miss → tune top-k, add hybrid, improve chunking
- Retrieval-count saturation → too many chunks per call floods the context window and answer quality plateaus, then degrades — more retrieval is not free. For agentic multi-step search, ~40 docs/call is past the knee: a single retrieval crowds out the room left for reasoning. Cap top-k and leave headroom for multi-step reasoning; cross-ref `/context-engineering` for per-source budget. (KARL search-environment ablation, Databricks 2026.)
- Stale index → freshness indicator + re-index cadence
- Cross-tenant leak → namespace/filter isolation per tenant
- Embedding drift → version-pin; re-index on model change

## Quality bar
- Context window vs. RAG decision must be documented
- "Not found" fallback is mandatory
- Chunk metadata (source ID, timestamp) is not optional — citation and freshness filtering require it
- Latency budget allocated across all stages before choosing retrieval and reranking options
