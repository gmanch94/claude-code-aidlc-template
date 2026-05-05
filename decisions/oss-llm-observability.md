# ADR-0038: Open-Source — LLM Observability

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

LLM-powered production systems require observability beyond traditional APM. Teams need to trace multi-step LLM calls, track token costs, detect prompt injection, monitor for drift, and manage prompt versions. Without a principled observability stack, production LLM issues (hallucination spikes, cost blowouts, latency degradation) are identified only after user impact rather than via proactive monitoring.

## Decision

We adopt a **layered LLM observability architecture** built on OpenTelemetry as the instrumentation standard:

- **Instrumentation standard:** **OpenTelemetry (OTel)** — all LLM calls and agent steps emit OTel traces. Vendor lock-in is prevented at the instrumentation layer.
- **Primary LLM tracing platform (self-hosted):** **Langfuse** — production LLM call tracing, prompt management, token cost tracking, A/B prompt experiments. MIT core; self-hostable on Kubernetes.
- **Integrated eval + tracing:** **Phoenix** (Arize, MIT) — used when teams require unified eval and observability without separate platforms (see ADR-0037 cross-reference).
- **Lightweight monitoring (low-ops):** **Langtrace** — for teams wanting quick integration without Langfuse's operational complexity.
- **Data drift and quality monitoring:** **Evidently AI** — 100+ built-in metrics for data drift, model quality, and LLM output monitoring; report generation and alerting.
- **Security-focused observability:** **WhyLabs** — for workloads requiring prompt injection detection, PII leakage monitoring, and privacy-preserving telemetry.

## Rationale

1. **OpenTelemetry as the foundation** — OTel is the vendor-neutral instrumentation standard. Langfuse, Phoenix, and Langtrace all export OTel spans. Instrumenting at the OTel layer means observability backends can be swapped without changing application code.
2. **Langfuse as the production tracing default** — MIT-licensed core with a self-hosted Kubernetes deployment. Covers the full LLM observability lifecycle: tracing → prompt management → cost tracking → A/B experiments → datasets. The most complete self-hosted OSS option with strong community adoption.
3. **Evidently AI for drift and quality** — Traditional model monitoring tools are not LLM-aware; Evidently's LLM-specific metrics (toxicity, sentiment, text length distribution) complement trace-based observability. Decoupled from the serving path — ingests logs, not inline.
4. **WhyLabs for regulated/high-security workloads** — Privacy-preserving statistical profiling without sending raw prompts to a third party. Prompt injection detection and PII leakage alerts address security requirements that Langfuse/Langtrace do not cover.
5. **Phoenix for unified eval + obs** — When a team is already using Phoenix for CI eval (ADR-0037), extending it to production tracing avoids introducing Langfuse as a second platform. Not the default for teams that don't use Phoenix for eval.

## Consequences

### Positive
- OTel instrumentation decouples application code from observability backends — backend can be swapped or multi-homed without code changes
- Langfuse's prompt management + versioning closes the gap between prompt development and production monitoring
- Evidently AI drift reports are standalone HTML/JSON — integrate into existing dashboards without new infrastructure

### Negative / Trade-offs
- Langfuse self-hosted requires Postgres + Redis + object storage — ops overhead is non-trivial; plan infrastructure before selecting for small teams
- Running both Langfuse (tracing) and Evidently (drift) is two systems to operate; accept this complexity or use Phoenix as the unified platform
- WhyLabs statistical profiling has a learning curve for security teams unfamiliar with differential privacy concepts

### Risks
- [RISK: HIGH] Tracing all LLM calls logs prompt content — PII may appear in traces; enforce PII scrubbing at the OTel SDK layer before traces reach Langfuse; see ADR supplement for PII handling
- [RISK: MED] Token cost tracking requires accurate pricing config — pricing changes (provider updates) require manual config updates in Langfuse; automate pricing sync or accept stale cost estimates
- [RISK: LOW] Langtrace is less mature than Langfuse — do not use for regulated workloads requiring audit trail guarantees

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Helicone | Hosted proxy architecture introduces latency in critical path; self-hosted option less mature than Langfuse |
| Datadog LLM Observability | Commercial; per-event pricing at scale is unpredictable; contradicts OSS self-hosted strategy |
| W&B Weave | Strong for ML experiment tracking; LLM tracing is a secondary capability vs Langfuse's primary focus |
| Custom OTel collector + Grafana | Requires significant custom instrumentation for LLM-specific metrics; Langfuse/Phoenix provide this out of box |

## Implementation Notes

1. Instrument with OTel SDK: `from opentelemetry import trace; tracer = trace.get_tracer(__name__)` — wrap LLM calls in spans with `model`, `prompt_tokens`, `completion_tokens` attributes
2. Langfuse: deploy via Helm chart (`langfuse/langfuse`); set `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`; use `langfuse.observe()` decorator for automatic tracing
3. LangChain/LlamaIndex integration: use `CallbackHandler` — `handler = LangfuseCallbackHandler(); chain.invoke(input, config={"callbacks": [handler]})`
4. PII scrubbing: configure OTel `SpanProcessor` to redact PII before export; do not rely on destination-side scrubbing
5. Evidently: ingest LLM logs via `TextEvals` report; run nightly drift reports; alert on `toxicity > 0.05` or response length distribution shift
6. WhyLabs: configure `whylogs` logger with `LangKit` extension for LLM-specific metrics; enable prompt injection detection via `prompt_injection_score`

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
