# ADR-0036: Open-Source — Vector Databases

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

RAG and semantic search workloads require vector storage and similarity search. Choosing the wrong vector store creates painful migrations later — scale limits, missing filtering capabilities, hybrid search gaps, or excessive infrastructure overhead for the workload size. A principled selection framework is needed to match workload scale and operational constraints to the right tool.

## Decision

We adopt a **scale and constraint-driven selection matrix**:

- **Rapid prototyping / local dev:** **Chroma** — zero-ops embedded vector store; integrates natively with LangChain and LlamaIndex.
- **Existing Postgres infrastructure:** **pgvector** — pragmatic addition to existing Postgres; avoids new infrastructure for sub-50M vector workloads.
- **Production scale (100M–1B vectors):** **Qdrant** (primary) or **Weaviate** (when hybrid search and multi-tenancy are required).
- **Large-scale distributed (1B+ vectors):** **Milvus** — cloud-native distributed architecture with separated storage and compute.
- **Existing Elasticsearch/OpenSearch estate:** **OpenSearch** with k-NN plugin — avoids introducing a separate vector store for teams already operating ES/OS.

## Rationale

1. **Chroma for dev → Qdrant/Milvus for production** — Chroma's embedded mode eliminates ops overhead during prototyping but has no production clustering. The LangChain/LlamaIndex abstraction layer makes migration to Qdrant or Milvus a configuration change, not a code rewrite — validate this migration path in PoC before committing.
2. **pgvector as the pragmatic default** — For teams operating Postgres (the majority), pgvector avoids new operational surface area. Handles tens of millions of vectors effectively with HNSW indexing. The cost of a separate vector DB is not justified until scale or filtering complexity demands it.
3. **Qdrant for production mid-scale** — Rust-based engine delivers high throughput with low memory footprint. Payload filtering (metadata + vector search in one query) is first-class. gRPC + REST API, strong Kubernetes story, and quantisation support (scalar, product) make it production-ready.
4. **Weaviate when hybrid search is critical** — Built-in BM25 + vector hybrid search without external Elasticsearch dependency. Multi-tenancy is first-class — the right choice for SaaS products serving multiple isolated tenants in one cluster.
5. **Milvus for billion-scale** — Separated storage (S3/MinIO) and compute enables independent scaling of read and write paths. GPU-accelerated indexing available. 35K+ GitHub stars reflects production adoption at scale.

## Consequences

### Positive
- Selection matrix eliminates per-project re-evaluation of vector stores — teams follow scale/constraint criteria, not preferences
- pgvector avoids infrastructure sprawl for the majority of workloads that do not need a dedicated vector DB
- LangChain/LlamaIndex abstraction makes vector store migration low-risk if scale outgrows initial selection

### Negative / Trade-offs
- Chroma is not production-scale — teams must commit to a migration plan to Qdrant/Milvus before production launch
- pgvector performance degrades without careful HNSW index tuning (`m`, `ef_construction`) — untuned pgvector on large datasets can be slower than purpose-built engines
- Milvus deployment complexity (Kubernetes, MinIO, etcd) requires dedicated MLOps capacity; do not select Milvus without ops plan

### Risks
- [RISK: HIGH] Wrong vector store selection is expensive to migrate — validate scale projections before production commit; prefer Qdrant over Chroma as soon as user-facing traffic begins
- [RISK: MED] pgvector HNSW index build is not online — index rebuild required when adding large batches of vectors; plan maintenance windows for bulk ingestion
- [RISK: LOW] Embedding model changes invalidate entire vector store — always store source documents alongside embeddings; version embedding model in metadata

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Pinecone | Managed cloud service; contradicts self-hosted OSS strategy; cost unpredictable at scale; vendor lock-in |
| Redis Vector Search | Redis is a cache-first store; vector search is a secondary capability; operational model mismatched for vector-primary workloads |
| FAISS | Library, not a server — no built-in persistence, no query API, no metadata filtering; appropriate only as an in-process index for batch workloads |
| LanceDB | Strong for local/embedded analytics; less mature for production serving and multi-user access patterns |

## Implementation Notes

1. Always store source text chunks alongside embeddings — use `metadata` field for doc ID, chunk index, source URL, and embedding model version
2. pgvector: create HNSW index with `CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)` — tune based on recall/latency trade-off
3. Qdrant: deploy via Helm chart; enable quantisation (`scalar` for 4× memory reduction); set `hnsw_config.on_disk=true` for collections exceeding GPU VRAM
4. Weaviate: configure `AUTHENTICATION_APIKEY_ENABLED=true` — never expose Weaviate without auth; use `tenant` isolation per customer for SaaS workloads
5. Milvus: deploy `milvus-distributed` on Kubernetes; use `DiskANN` index for datasets that don't fit in memory; configure MinIO for persistent storage
6. Define embedding model in `config/embedding-config.yaml` — changing embedding model requires full re-ingestion; treat as a versioned infrastructure change

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
