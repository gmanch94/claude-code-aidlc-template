# ADR-0046: Google ADK for Argus Multi-Agent Orchestration

**Date:** 2026-04-29
**Status:** Accepted
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Project Argus requires coordinating five specialized agents — `ItemValidatorAgent`, `CorrectionResolverAgent`, `ApprovalOrchestrator`, `CatalogWriterAgent`, `FeedbackAgent` — in a deterministic pipeline with conditional branching (AUTO / PROPOSE / FLAG tiers). The orchestration framework must support:

- Sub-agent composition with tool-call semantics (agent-as-tool)
- A2A protocol compatibility for future integration with the retailer's agent ecosystem
- Deployment to Gemini Enterprise Agent Platform (Agent Engine)
- Session state management across multi-turn approval workflows

The team is building on Google Cloud (BigQuery, Vertex AI, Gemini) and has an existing ADR (0023) selecting GCP as the primary AI platform.

## Decision

Use **Google Agent Development Kit (ADK)** with `AgentTool` composition for all Argus agent orchestration. The `argus_orchestrator` is an ADK `Agent` that wraps each sub-agent as an `AgentTool`, coordinating the full pipeline via its instruction prompt.

## Rationale

ADK's `AgentTool` pattern allows each sub-agent to expose a clean tool interface to the orchestrator LLM, enabling the orchestrator to reason over pipeline state and route conditionally without custom Python branching logic. This keeps orchestration logic in the LLM instruction layer — auditable, adjustable without code changes.

ADK is the native framework for Agent Engine deployment. Building on it now avoids a framework migration at deploy time and gives access to A2A protocol, Memory Bank, and Agent Registry — all required for Argus v2.

## Consequences

### Positive
- Zero-friction deployment to Agent Engine (same framework, same config)
- A2A compatibility built in — Argus agents are discoverable by other retailer agents
- Sub-agent isolation: each agent has its own model, instruction, and tool scope
- Orchestration logic in instruction prompt — reviewable by non-engineers

### Negative / Trade-offs
- ADK is newer than LangGraph; fewer community examples and debugging tooling
- Orchestrator routing relies on LLM instruction following — not a guaranteed state machine
- `agents-cli playground` does not wire A2A correctly; production testing requires uvicorn + trigger script

### Risks
- [RISK: MED] LLM instruction drift — orchestrator may deviate from routing rules on ambiguous inputs. Mitigate with eval cases covering each tier path.
- [RISK: LOW] ADK API surface still evolving — pin version in `pyproject.toml`, review on each upgrade

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| LangGraph | Better graph control but no native A2A or Agent Engine integration; migration cost at deploy |
| CrewAI | No GCP-native deployment path; weaker tool-call semantics for multi-agent composition |
| Raw Python + asyncio | Full control but too much custom plumbing for state, session, and A2A |
| Vertex AI Reasoning Engine (pre-ADK) | Deprecated path; replaced by ADK + Agent Engine |

## Related ADRs

| ADR | Relationship |
|-----|-------------|
| [ADR-0047](ADR-0047-argus-bigquery-vector-search-rag.md) | RAG store used by `CorrectionResolverAgent` sub-agent |
| [ADR-0048](ADR-0048-argus-three-tier-confidence-routing.md) | Routing logic encoded in orchestrator instruction prompt |
| [ADR-0049](ADR-0049-argus-slack-human-in-the-loop-approval.md) | `ApprovalOrchestrator` sub-agent channel decision |
| [ADR-0050](ADR-0050-argus-adk-tool-dependency-injection.md) | Testability pattern applied to all tools wired into sub-agents |

## Implementation Notes

1. Each sub-agent defined as standalone `Agent` instance; wrapped with `AgentTool` in orchestrator
2. Orchestrator instruction encodes the full routing protocol (STEP 1–4) as a numbered list
3. `InMemorySessionService` for local dev; swap to Agent Engine sessions for prod
4. End-to-end test path: `uvicorn` server + `trigger_flow_a.py` script (not playground)
5. `agents-cli eval run` required before any deploy — covers AUTO, PROPOSE, FLAG, and timeout paths
