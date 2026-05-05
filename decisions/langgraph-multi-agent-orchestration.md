# ADR-0001: Use LangGraph for Multi-Agent Orchestration

**Date:** 2026-04-17
**Status:** Superseded
**Domain:** [llm] [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** ADR-0034 (OSS Agent & Orchestration)

---

## Context

We are building a multi-step AI pipeline that requires multiple specialized agents
(retrieval, reasoning, code execution) to collaborate on complex tasks. We need an
orchestration framework that supports stateful, cyclical agent graphs — not just
linear chains.

## Decision

We will use **LangGraph** as the primary orchestration layer for multi-agent workflows,
with LangSmith for observability.

## Rationale

LangGraph's graph-based execution model natively supports cycles, conditional routing,
and shared state — requirements our pipeline has that LangChain's sequential chains
cannot meet without significant workarounds. LangSmith provides trace-level visibility
into agent decisions, which is required by our governance standards.

## Consequences

### Positive
- Native support for cyclical agent graphs and human-in-the-loop checkpoints
- Built-in state management reduces custom plumbing
- LangSmith integration satisfies observability principle from CLAUDE.md

### Negative / Trade-offs
- Tighter coupling to LangChain ecosystem
- Learning curve for engineers unfamiliar with graph-based thinking
- LangGraph API surface is still evolving (v0.2 as of this decision)

### Risks
- [RISK: MED] LangGraph API instability — pin to minor version, review on each upgrade
- [RISK: LOW] Vendor lock-in — abstraction layer recommended at the orchestration boundary

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Raw Python + asyncio | Too much custom plumbing for state, routing, and retries |
| CrewAI | Less flexible graph control; limited enterprise observability |
| AutoGen | Microsoft ecosystem dependency; less Python-native |

## Implementation Notes

1. Pin `langgraph==0.2.x` in `pyproject.toml`
2. All agents must expose a standard `AgentNode` interface
3. LangSmith project created before first deployment
4. Wrap orchestration layer behind an abstract `Orchestrator` protocol for future portability

## Review Checklist

- [x] Aligns with architecture principles in CLAUDE.md
- [x] No undocumented PII exposure
- [x] Observability plan defined (LangSmith)
- [x] Fallback/degradation path exists (single-agent fallback mode)
- [ ] Cost impact estimated — **TODO before Accepted**
- [ ] Reviewed by at least one peer
