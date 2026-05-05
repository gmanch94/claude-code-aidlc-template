# ADR-0035: Open-Source — RAG Frameworks

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Retrieval-Augmented Generation pipelines require a principled framework selection for document ingestion, chunking, embedding, retrieval, and re-ranking. Teams building RAG-based products independently choose frameworks, leading to inconsistent retrieval quality, untested chunking strategies, and fragile pipelines that are difficult to evaluate or tune.

## Decision

We adopt a **tiered RAG framework selection** based on production requirements:

- **Production RAG (complex documents, tables, PDFs):** **RAGFlow** — end-to-end RAG engine with deep document understanding, visual pipeline builder, and support for structured table extraction.
- **Flexible modular RAG (general purpose):** **LangChain RAG** — default for pipelines requiring broad loader/splitter/retriever ecosystem and LangGraph integration.
- **Data-centric / structured retrieval:** **LlamaIndex** — preferred when retrieval involves hierarchical indexing, knowledge graphs, or multi-step query decomposition over structured data.
- **Testable enterprise pipelines:** **Haystack RAG** — preferred when pipeline components must be unit-testable, YAML-versioned, and REST API-first.
- **High-recall complex queries:** **RAGatouille (ColBERT)** — plugged into LangChain/LlamaIndex as the retriever when dense embedding retrieval recall is insufficient for nuanced multi-hop queries.

## Rationale

1. **RAGFlow for production document-heavy workloads** — Deep document understanding (PDF layout analysis, table extraction, image captioning) is built-in, not bolted on. Visual pipeline builder accelerates iteration for non-engineering stakeholders. Most RAG frameworks treat PDFs as flat text; RAGFlow preserves structure.
2. **LangChain RAG as the flexible default** — The widest ecosystem of document loaders (200+), text splitters, embedding models, and vector store integrations. New data sources, embedding models, and retrieval strategies can be swapped without changing pipeline structure.
3. **LlamaIndex for structured/hierarchical data** — LlamaIndex's node-based indexing, property graph integration, and multi-step query engines handle structured data (databases, APIs, nested documents) better than LangChain's document-centric model.
4. **RAGatouille for retrieval quality** — ColBERT's late-interaction retrieval (token-level matching) provides superior recall for queries that fail with cosine similarity over dense embeddings. Adds minimal overhead when recall is a critical success metric.
5. **Chunking strategy is pipeline-specific** — No single chunking approach is universally optimal; the framework decision must be accompanied by a chunking ADR supplement defining chunk size, overlap, and splitting strategy per document type.

## Consequences

### Positive
- RAGFlow's visual pipeline builder reduces time-to-working-RAG for document-heavy use cases without requiring ML engineering for initial setup
- LangChain's modular architecture allows independent swapping of loaders, splitters, embeddings, and retrievers — component-level iteration without pipeline rewrites
- ColBERT (RAGatouille) integration is non-invasive — plugs in as a retriever without changing surrounding pipeline architecture

### Negative / Trade-offs
- RAGFlow is a heavier deployment (Docker Compose with Elasticsearch, MinIO) — not appropriate for lightweight or embedded use cases
- Multiple RAG frameworks create a risk of teams mixing LangChain and LlamaIndex in the same project — establish one primary per project in the team ADR supplement
- RAGatouille ColBERT indexes are not compatible with standard vector stores — requires separate index management

### Risks
- [RISK: HIGH] Chunk size and overlap directly impact retrieval quality — wrong defaults cause hallucinations even with correct framework selection; mandate retrieval eval (RAGAS) before production
- [RISK: MED] RAGFlow Elasticsearch dependency adds significant infrastructure overhead — ensure ops team capacity before selecting for production
- [RISK: LOW] LangChain RAG abstractions can obscure retrieval logic — document retrieval chain configuration explicitly in architecture diagrams

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| TxtAI | Good for lightweight/edge; insufficient ecosystem for enterprise RAG requirements; no production-scale vector store support |
| Semantic Kernel RAG | Microsoft-stack oriented; limited Python ecosystem compared to LangChain/LlamaIndex; revisit for .NET teams |
| Custom RAG (no framework) | High build cost; misses battle-tested chunking, retrieval, and re-ranking patterns; only justified for extreme performance requirements |
| DSPy | Strong for optimised prompt pipelines; RAG-specific abstractions less mature than LlamaIndex/LangChain; revisit as DSPy matures |

## Implementation Notes

1. Always implement retrieval evaluation with RAGAS before production: measure `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
2. LangChain RAG: use `RecursiveCharacterTextSplitter` as default; tune `chunk_size` (512–1024) and `chunk_overlap` (10–15%) per document type via eval
3. RAGFlow: deploy via Docker Compose; configure `EMBEDDING_MODEL` and `LLM_API_KEY` in `.env`; use built-in pipeline editor for initial prototype
4. RAGatouille: index with `RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")`; integrate as `retriever = ragatouille_retriever` in LangChain chain
5. LlamaIndex: use `VectorStoreIndex` with `SentenceSplitter`; configure `similarity_top_k` (default 3) and evaluate vs RAGAS metrics
6. Store retrieval configuration (chunk size, overlap, top-k, reranker) in versioned config — changes to retrieval config require re-evaluation

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
