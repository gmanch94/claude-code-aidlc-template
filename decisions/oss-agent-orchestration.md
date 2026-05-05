# ADR-0034: Open-Source — Agent & Orchestration Frameworks

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** ADR-0001 (LangGraph Multi-Agent Orchestration — superseded by this broader OSS decision)
**Superseded by:** N/A

---

## Context

AI products require orchestration frameworks that manage LLM calls, tool use, memory, and multi-step reasoning loops. The OSS landscape has fragmented into general-purpose chains (LangChain), stateful graph-based agents (LangGraph), RAG-native data frameworks (LlamaIndex), enterprise pipelines (Haystack), and multi-agent collaboration frameworks (CrewAI, AutoGen). Without clear selection criteria, teams mix frameworks arbitrarily, creating integration complexity and inconsistent observability.

## Decision

We adopt a **use-case-driven framework selection** policy:

- **Stateful production agents (primary):** **LangGraph** — graph-based state machines with checkpointing, human-in-the-loop, and explicit branching. Default for any production agentic loop.
- **LLM integration / tooling layer:** **LangChain** — used as the integration and tool ecosystem layer underneath LangGraph; not used standalone for new complex agent projects.
- **RAG-native agents and data pipelines:** **LlamaIndex** — preferred when the agent's primary concern is structured/unstructured data retrieval, multi-modal ingestion, or complex query decomposition.
- **Production NLP pipelines with testability requirements:** **Haystack** — preferred for teams requiring YAML-defined, version-controlled pipeline components with REST API-first architecture.
- **Multi-agent collaboration (experimental):** **CrewAI** for role-based business process workflows; **AutoGen** for research-grade code-writing agent teams. Both require architecture review before production deployment.

## Rationale

1. **LangGraph for production agents** — Explicit state machines prevent the runaway loops and unpredictable branching common in pure ReAct agents. Checkpointing enables resumable agents and human-in-the-loop review gates. First-class support in LangChain's ecosystem means observability (LangSmith / Langfuse) is straightforward.
2. **LangChain as integration layer** — LangChain's value is its tool ecosystem (200+ loaders, vector store integrations, callback system). Using it as a dependency of LangGraph preserves this value without accepting LangChain's complex chain abstractions for orchestration logic.
3. **LlamaIndex for data-centric agents** — LlamaIndex's indexing abstractions (hierarchical, keyword, knowledge graph) are purpose-built for retrieval. When the agent's primary job is data access rather than action execution, LlamaIndex's pipeline is more appropriate than LangGraph's graph model.
4. **Haystack for testable pipelines** — YAML pipeline definitions are version-controllable and diff-friendly. Component isolation enables unit testing of individual pipeline stages — critical for regulated or high-stakes NLP workflows.
5. **Multi-agent frameworks at experimental tier** — CrewAI and AutoGen both lack production-grade observability and reliability guarantees. Use behind feature flags with architecture review; do not use for customer-facing production workloads without a fallback path.

## Consequences

### Positive
- LangGraph's explicit state model eliminates unpredictable agent loops — state transitions are auditable and testable
- Framework selection is deterministic given use case — reduces decision fatigue and inconsistent choices across teams
- LangChain's callback/observability hooks work uniformly across all selected frameworks

### Negative / Trade-offs
- LangGraph adds graph model cognitive overhead — simpler single-step chains are over-engineered with full LangGraph; use LangChain LCEL for those cases
- LlamaIndex and LangChain have overlapping RAG capabilities — teams must resist the temptation to use both in the same project
- Haystack's YAML pipeline model limits dynamic runtime behaviour — not suitable for adaptive or self-modifying agent architectures

### Risks
- [RISK: HIGH] CrewAI and AutoGen multi-agent loops can generate unbounded LLM calls — always enforce `max_iterations` and token budget limits; implement circuit breakers
- [RISK: MED] LangGraph/LangChain release cadence is fast — breaking changes between minor versions; pin versions and run eval suite before upgrades
- [RISK: LOW] Framework lock-in — LangGraph abstractions are non-trivial to migrate away from; document agent state schemas to enable future portability

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Pure ReAct (no framework) | Unpredictable loops, no checkpointing, difficult to add human-in-the-loop; acceptable only for throwaway PoCs |
| Semantic Kernel (.NET/Java) | Relevant for Microsoft-stack enterprise teams; excluded from default OSS selection as Python is primary language; revisit for Java/C# projects |
| Pydantic AI | Emerging framework with strong typing story; insufficient production track record at time of writing; revisit in 6 months |
| OpenAI Agents SDK | Proprietary SDK tightly coupled to OpenAI APIs; contradicts vendor-independence principle |

## Implementation Notes

1. LangGraph: define state as a `TypedDict`; use `StateGraph` with typed node functions; always set `recursion_limit` on `graph.compile()`
2. Enable LangGraph checkpointing via `MemorySaver` (dev) or `PostgresSaver` (production) — store checkpoint backend in config, not code
3. Instrument with Langfuse or Phoenix via LangChain callbacks: `CallbackHandler` wraps all LLM calls automatically
4. CrewAI/AutoGen: wrap in async task with timeout; expose `max_iter` and `max_tokens` as environment-variable-configurable limits
5. LlamaIndex agents: use `FunctionCallingAgentWorker` over `ReActAgent` for tool-calling models; set `verbose=False` in production
6. Document agent state schema in the ADR supplement — state shape is the primary migration artifact if framework changes

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
