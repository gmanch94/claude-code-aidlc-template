# ADR-0050: Dependency Injection Pattern for ADK Tool Testability

**Date:** 2026-04-29
**Status:** Accepted
**Domain:** [llm] [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ADK tools are plain Python functions. Argus tools call external services — BigQuery, Vertex AI embeddings, Slack — that are unavailable or expensive in unit tests. Without a testability strategy, the entire test suite requires live GCP credentials, incurs API cost, and fails in CI without network access.

Additionally, ADK passes the function's parameter schema to the LLM. Internal clients and state objects must not appear in the schema — the LLM would be prompted to supply them, which it cannot.

## Decision

Use a **hidden dependency injection pattern** via leading-underscore parameters:

1. Each tool function has a public signature (what the LLM sees) and a private implementation (`_func`) that accepts optional `_client`, `_embedding_fn`, `_pending`, or `_poll_interval` override parameters.
2. The public wrapper calls the private implementation with all defaults, hiding DI params from ADK's schema introspection.
3. In tests, the private implementation is called directly with injected fakes/stubs.

```python
# Private implementation — testable
def _find_similar_corrections(
    violation_json: str,
    _client: Any | None = None,       # BigQuery client
    _embedding_fn: EmbedFn | None = None,  # embedding function
) -> str: ...

# Public wrapper — what ADK registers as a tool
def find_similar_corrections(violation_json: str) -> str:
    return _find_similar_corrections(violation_json)
```

For Slack tools, `_pending: dict | None` and `_poll_interval: float | None` are injected to control approval state and polling speed in tests.

All sync tools that call external I/O are wrapped as `async` functions using `asyncio.get_event_loop().run_in_executor(None, ...)` to prevent blocking the ADK event loop.

## Rationale

ADK infers the tool's JSON schema from the public function signature. Parameters starting with `_` are convention-invisible to the LLM schema generation — they are never included in the schema, so the LLM is never asked to supply them. This gives clean separation between what the LLM controls (business parameters) and what the runtime controls (infrastructure clients).

The private-function / public-wrapper split allows tests to call `_func(args, _client=fake_client)` with full control over external dependencies, without mocking module-level globals or patching import paths.

This pattern was validated across all five Argus tools: `bq_vector_search`, `embeddings`, `slack_approval`, `confidence_scorer`, and `catalog_writer`. The 138 unit and integration tests pass without any real GCP or Slack calls.

## Consequences

### Positive
- 138 tests run with no GCP credentials, no Slack token, no network access
- CI runs fast and deterministically — no flakiness from external API rate limits or latency
- LLM schema stays clean — only business parameters visible to the orchestrator
- Async wrapping eliminates Slack "operation timed out" errors under ADK's event loop

### Negative / Trade-offs
- Two functions per tool (private impl + public wrapper) — small boilerplate cost
- Developers must remember to add DI params to the private function, not the public one
- `run_in_executor` wrapping adds complexity; executor thread pool must be sized for concurrent tool calls

### Risks
- [RISK: LOW] ADK schema introspection behavior could change — if ADK starts including `_` params, DI leaks into the LLM schema. Monitor on ADK version upgrades.
- [RISK: LOW] Executor thread leaks if tools are called at very high concurrency — set explicit pool size in production uvicorn config

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| `unittest.mock.patch` on module-level clients | Brittle — depends on import order; global state leaks between tests |
| Pydantic-based tool classes with injected clients | More structure but ADK tools are functions, not classes; wrapping adds friction |
| Real GCP calls in all tests | Expensive, slow, fails in CI without credentials; not viable |
| `pytest-mock` fixture injection | Works but requires test-specific imports scattered across test files; DI params keep injection at the call site |

## Related ADRs

| ADR | Relationship |
|-----|-------------|
| [ADR-0046](ADR-0046-argus-adk-multi-agent-orchestration.md) | All tools tested via this pattern are wired into ADK sub-agents |
| [ADR-0047](ADR-0047-argus-bigquery-vector-search-rag.md) | `_client` DI used in BQ vector search tool |
| [ADR-0049](ADR-0049-argus-slack-human-in-the-loop-approval.md) | `_pending` and `_poll_interval` DI used in Slack approval tools |

## Implementation Notes

1. Convention: all DI params prefixed with `_` in private implementations; public wrapper has zero `_` params
2. `app/tools/embeddings.py` exports `synthetic_embedding` as the test-safe alternative to `generate_embedding`; injected via `_embedding_fn`
3. `app/tools/slack_approval.py`: `_pending` dict injected in tests; `_poll_interval` set to 0.01s to make polling tests fast
4. Async wrapping pattern:
   ```python
   async def post_approval_request(violation_json: str, decision_json: str) -> str:
       loop = asyncio.get_event_loop()
       return await loop.run_in_executor(None, _post_approval_request, violation_json, decision_json)
   ```
5. `app/agents/*.py` — thin `AgentTool` wrappers call `find_similar_corrections` (public), never the private impl
6. All DI-injectable tools documented with `Args:` docstring noting the `_` params and their test purpose
