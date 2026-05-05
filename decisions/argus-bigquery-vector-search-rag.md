# ADR-0047: BigQuery Vector Search as Unified RAG and Audit Store

**Date:** 2026-04-29
**Status:** Accepted
**Domain:** [rag] [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

`CorrectionResolverAgent` needs to retrieve past corrections similar to the current violation (RAG), and `FeedbackAgent` needs to write resolved corrections back so future retrievals improve. The system also needs an audit trail of every correction decision.

Options are: a dedicated vector database alongside BigQuery, or using BigQuery's native vector search capability to serve both RAG and structured audit queries from a single store.

The team already has a BigQuery dataset (`argus.correction_history`) provisioned in a dedicated GCP project (set via `GOOGLE_CLOUD_PROJECT`).

## Decision

Use **BigQuery Vector Search (COSINE distance)** over `argus.correction_history` as the sole data store for correction RAG retrieval, audit trail, and feedback loop writes. No separate vector database is deployed.

The embedding model is **Vertex AI `text-embedding-004`** (768 dimensions), with a deterministic LCG synthetic embedding for tests and CI to avoid GCP dependency.

## Rationale

BigQuery Vector Search (GA as of 2026) supports `VECTOR_SEARCH()` SQL function over embedding columns with cosine distance, eliminating the need for a separate vector database. Storing embeddings alongside structured correction metadata in one table means:

- RAG retrieval and audit queries run in the same system, no ETL required
- `approval_rate` and structured fields are immediately available for confidence scoring within the same query
- The feedback loop is a simple BigQuery `INSERT` + embedding column update — no vector DB sync
- Operational complexity reduced: one store to monitor, back up, and access-control

The `FeedbackAgent` re-embeds approved corrections and upserts them, creating a flywheel where the AUTO tier rate improves as correction history grows.

## Consequences

### Positive
- Single store for retrieval, audit, analytics, and feedback — no cross-system sync
- BigQuery AI (BQML) can run root-cause analytics directly on the same table
- No additional vector DB infrastructure, credentials, or network paths
- Synthetic embedding in `embeddings.py` enables full unit test coverage without GCP

### Negative / Trade-offs
- BigQuery Vector Search latency (~1–3s per query) is higher than dedicated vector DBs (Pinecone, Weaviate) at sub-10ms
- Cold-start latency on first query against a new embedding index
- Correction history must reach critical mass (~500+ records) before RAG returns meaningful matches; synthetic seed data required for POC

### Risks
- [RISK: MED] RAG cold-start: early deployments with sparse history will default to FLAG tier frequently. Seed 100+ synthetic corrections at launch.
- [RISK: LOW] BigQuery query cost scales with table size — partition `correction_history` by `event_date` and set scan limits for vector search queries

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Vertex AI Vector Search (Matching Engine) | Additional managed service, separate from audit data, higher ops overhead |
| pgvector (Cloud SQL) | Requires Cloud SQL instance; BigQuery already provisioned and used for analytics |
| Pinecone | External vendor, third GCP service to manage, latency advantage not required at Argus scale |
| In-memory FAISS | No persistence; not suitable for correction history that must survive restarts |

## Related ADRs

| ADR | Relationship |
|-----|-------------|
| [ADR-0046](ADR-0046-argus-adk-multi-agent-orchestration.md) | Orchestration framework that hosts `CorrectionResolverAgent` using this store |
| [ADR-0048](ADR-0048-argus-three-tier-confidence-routing.md) | Confidence score computed from BQ retrieval results drives tier assignment |
| [ADR-0050](ADR-0050-argus-adk-tool-dependency-injection.md) | DI pattern (`_client`) used to test BQ tools without real GCP |

## Implementation Notes

1. Table schema: `correction_history` with `embedding ARRAY<FLOAT64>` column for vector storage
2. Query pattern: `VECTOR_SEARCH(TABLE argus.correction_history, 'embedding', (...), top_k=5, distance_type='COSINE')`
3. Embedding generation: `app/tools/embeddings.py` — `generate_embedding()` for prod, `synthetic_embedding()` for tests
4. DI pattern: `search_similar_corrections(embedding, top_k, client=None)` — pass `bigquery.Client` in tests to avoid real GCP calls
5. Confidence scoring: `Σ(1 - distance_i × approved_i) / k` — computed in `app/tools/confidence_scorer.py` after retrieval
6. Feedback loop: `FeedbackAgent` calls `insert_correction_record()` after every resolved correction; re-embeds if `applied_fix ≠ proposed_fix`
