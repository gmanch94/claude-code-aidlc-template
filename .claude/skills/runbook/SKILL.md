---
name: runbook
description: Generates AI incident runbooks with detection signals, triage steps, mitigations, escalation criteria, and post-incident actions for 8 standard AI failure scenarios. Use when preparing a production AI system for launch, setting up on-call procedures, or documenting incident response for an AI feature.
---

# /runbook — AI Incident Runbook

## Behavior
1. Ask if not provided: system name, stack (cloud, model provider, orchestration), known failure modes, on-call, escalation path
2. Generate all 8 standard AI scenarios + any system-specific ones
3. Every scenario: detection → triage → mitigation → escalation → post-incident
4. Flag missing observability that makes detection impossible

## 8 Standard Scenarios

| Scenario | Primary Signal | Typical Cause |
|----------|---------------|--------------|
| Model degradation | Quality score drop, complaint spike | Prompt drift, model version change, data shift |
| Hallucination spike | Faithfulness score drop, error reports | Retrieval failure, prompt regression, context overflow |
| Latency regression | p95/p99 spike | Endpoint overload, retrieval slowdown, network |
| Cost blowout | Token spend > N× baseline | Agent loop, prompt inflation, traffic spike |
| Data pipeline failure | Stale embeddings, retrieval recall drop | ETL failure, schema change, indexing failure |
| Safety / guardrail breach | Toxicity alert, policy violation | Injection, jailbreak, guardrail bypass |
| Model endpoint outage | 5xx rate spike, timeout spike | Provider outage, quota exhaustion, deploy failure |
| Agentic loop runaway | Max iteration alert, cost spike | Termination bug, tool failure loop |

## Observability requirements
Every scenario above requires these signals to be instrumented:
- Quality metric per request
- Token spend per request (hourly alert)
- Latency p50/p95 with alert threshold
- Error rate (5xx, timeouts, model API errors)
- Retrieval recall@k (RAG systems)
- Agent step count with alert (agentic systems)
- Guardrail trigger rate

## Quality bar
- Every scenario needs a detection signal — no signal = no response capability
- Mitigation must be actionable at 3am — no "investigate further" without concrete steps
- Escalation must be time-boxed — "if not resolved in N minutes, escalate"
- Every incident → add regression eval case for the failing query type

See [REFERENCE.md](REFERENCE.md) for scenario template to fill in per system.
