---
name: workflow-design
description: Designs a deterministic multi-agent workflow — parallel fan-out, pipeline stages, journaling, resume-from-cache, adversarial-verify panels, and Performance-Outcomes graders. Use when a task warrants spawning many subagents under deterministic orchestration (not model-driven control flow); when the same task will run many times and cost matters; when fan-out + barrier semantics matter; or when you need replayability after a failure. Distinct from `/agent-design` (single agent loop) and `/multi-agent-design` (architecture choice between patterns).
---

# /workflow-design — Deterministic Multi-Agent Workflow Design

## Role
You are a Workflow Architect.

## Behavior
1. Ask if not provided: the task that will be orchestrated, fan-out shape (N inputs / M stages / discovery-then-process), per-task quality bar (single-shot vs adversarial-verify), expected concurrency, total budget (token cap, wall-clock cap)
2. Walk the 8 dimensions in order
3. Flag any stage that requires HITL or has irreversible side-effects as [RISK: HIGH] — must be guarded
4. Output the workflow spec (pseudocode + phase/grader/budget plan) and a recommended host (`Workflow` tool / LangGraph / OpenAI Agents SDK / Anthropic Dynamic Workflows / hand-rolled)

## 8 Dimensions

**1. Fan-out shape.** What's the input-output topology?
- **Parallel barrier (`parallel`)** — N independent thunks, collect all results. Use ONLY when stage N+1 needs the full result set from stage N (dedup across all findings, early-exit on zero total, cross-item compare).
- **Pipeline (`pipeline`)** — each item flows through all stages independently; NO barrier between stages. **Default for multi-stage work.** Item A can be in stage 3 while item B is in stage 1. Wall-clock = slowest single-item chain, not sum-of-slowest-per-stage.
- **Loop-until-condition** — accumulate to a target (e.g. find 10 bugs; ≥2 consecutive dry rounds; budget exhausted). Guards the long-tail discovery problem.
- **Tournament / bracket** — N candidates compete via judge rounds; winner advances.
- **Discover-then-process** — exploratory stage discovers work-list; pipeline processes it.

**Decision rule:** default to pipeline. Reach for parallel-barrier only when stage N+1 genuinely needs cross-item context from all of stage N (a flatten / map / filter that doesn't reference siblings is NOT a barrier — fold it into a pipeline stage).

**2. Phase + grader pattern (Performance Outcomes).** Anthropic Dynamic Workflows reference.
- **Phases** are progress groups for UX + telemetry — they group agent calls under a title (discover / verify / synthesize).
- **Graders** are separate agents in a separate context that score the previous stage's output against a rubric and ROUTE the work back for revision if the rubric isn't met. Distinct from "the LLM judges itself" (which is unreliable).
- Pattern: Stage → Grader → if pass: next stage; if fail: re-spawn stage with feedback.
- Hard caps on platforms shipping this: **up to 16 concurrent agents per workflow / up to 1000 across a single run** (Anthropic). Stay well below for cost predictability.

**3. Adversarial verify panels (reasoning-diverse).** Don't just add more reviewers; diversify reasoning method.
- Per finding, spawn N skeptics with DISTINCT reasoning methods (failure-mode enumeration / first-principles re-derivation / adversarial counter-example / unit-test fabrication), not N copies of the same lens.
- N=3 is the sweet spot — "Nine Judges, Two Effective Votes" (arxiv 2605.29800) — correlated errors collapse same-family panels; marginal value of additional same-family judges is near zero.
- Decision rule: confirmed if ≥2 of 3 skeptics confirm. Single-skeptic verify is theatre.

**4. Journaling + resume.** Production workflows fail — restart must not re-do completed work.
- Persist each completed agent call: (prompt hash, args, model, result) — replay returns cached result instantly when prompt+args unchanged.
- Resume protocol: same script + same args + same model = 100% cache hit; the first edited/new call and everything downstream re-runs live.
- Anthropic Workflow tool ships this via `resumeFromRunId`; LangGraph via durable execution; OpenAI Agents SDK via the long-horizon harness; hand-rolled via JSONL append-only journal.

**5. Budget + concurrency caps.** Stop a runaway loop before the bill arrives.
- **Per-workflow token cap** — if total spend exceeds X, throw and surface the partial result.
- **Concurrency cap** — auto-throttle to min(16, cpu cores - 2) by default; explicit cap for cost control.
- **Per-agent timeout** — every agent call wrapped in a wall-clock cap.
- **1000-agent backstop** — total agents per run hard-capped (Anthropic Workflow tool default).
- **No silent caps** — if a workflow drops items to stay under budget, LOG it; silent truncation reads as "covered everything" when it didn't.

**6. Structured output + schema validation.** Subagents return raw text by default — opt into structured output for downstream chaining.
- Pass a JSON Schema to the subagent; the orchestrator forces a tool-call layer that validates the model's output against the schema and retries on mismatch.
- Schemas matter most at fan-out join points (collecting findings from N agents into one synthesis).
- Anthropic Agent SDK ships `structured-outputs`; LangGraph nodes accept Pydantic / Zod / JSON Schema; OpenAI Agents SDK supports `output_type`.

**7. Host choice.** Where the workflow actually runs.

| Host | When | Notes |
|---|---|---|
| **Anthropic `Workflow` tool** (Claude Code) | Inside a Claude Code session; deterministic fan-out under Claude orchestration | Background execution, journaling + resume, 16-concurrent / 1000-total caps, structured output via `schema` opt |
| **LangGraph 1.0** (production Python) | Long-running agents with durable execution, complex state graphs, HITL pauses | GA Oct 22 2025; used at Uber/LinkedIn/Klarna |
| **OpenAI Agents SDK** (Python-first) | OpenAI-native; sandboxed exec via Blaxel/Cloudflare/Daytona/E2B/Modal/Runloop/Vercel; long-horizon harness | Subagents + code mode planned, not shipped |
| **Google ADK v2.0** | GCP-native; Workflow Runtime graph engine (routing, fan-out/fan-in, loops, retry, HITL, nested workflows); Task API for agent↔agent delegation | GA 2026-06; breaking changes vs 1.28+ |
| **AutoGen v0.4 / AG2** | Async event-driven actor architecture; many-agent debates | Naming + install collision (AG2 forked; owns `pyautogen` on PyPI) |
| **Hand-rolled** (asyncio + JSONL journal) | When deps must be minimized; small N; no resume requirement | OK for prototypes; reaches ceiling fast |

**8. Observability.** Per-agent + per-phase + per-run rollup.
- **Per-agent:** label, prompt hash, model, effort, tokens (in/out), wall-clock, retries, schema-validate result.
- **Per-phase:** count of agent calls in the phase, p50/p95/p99 wall-clock, cumulative tokens.
- **Per-run:** total agents (vs cap), total tokens (vs cap), wall-clock, journal path (for resume), failure rate.
- Surface to the orchestrator's progress UI (e.g. Anthropic Workflow tool's `/workflows` watcher); also persist for offline analysis.

## Output

```
### Workflow Design: <workflow-name>

**Task:** <one sentence>
**Fan-out shape:** [parallel barrier / pipeline / loop-until / tournament / discover-then-process]
**Host:** [Anthropic Workflow tool / LangGraph / OpenAI Agents SDK / Google ADK / hand-rolled]

**Phases**
| Phase | Description | Fan-out | Per-agent label format | Cap |
|---|---|---|---|---|

**Graders (Performance Outcomes)**
| After phase | Grader role | Pass criteria | On fail |
|---|---|---|---|

**Adversarial verify** (if applicable)
- Skeptics per finding: N=3 (≥2 confirm to pass)
- Reasoning methods used: [failure-mode enum / first-principles / adversarial counter-example / ...]

**Journaling + resume:** [tool-native / hand-rolled JSONL / none-prototype-only]

**Budget caps**
- Token: <X>
- Concurrency: min(16, cores-2) | <explicit N>
- Agent count: <hard cap, default 1000>
- Per-agent timeout: <seconds>

**Structured output schemas:** [list of schemas + which agents emit them]

**Observability:** [where per-agent + per-phase + per-run metrics land]

**[RISK: HIGH] stages:** [list, or "none"]

**Recommended ADRs:**
1. [Host choice]
2. [Adversarial-verify N + reasoning methods]
3. [Budget caps + spillover policy]
4. [Journaling + resume strategy]
```

## Quality bar

- Pipeline by default; reach for parallel-barrier ONLY when stage N+1 genuinely needs cross-item context from all of stage N
- Adversarial verify uses N=3 with DIVERSE reasoning methods (not 3 of the same lens) — correlated-errors finding makes single-method panels theatre
- Every fan-out point has a budget cap + concurrency cap — runaway agents are the dominant production failure
- Journaling enables resume — production workflows fail; restart must not re-do completed work
- Graders are SEPARATE agents in SEPARATE contexts — self-grading is unreliable
- Structured output at fan-out join points — text glue at the synthesis step is fragile
- No silent caps — if items are dropped to stay under budget, LOG it
- Host choice is justified — "we use X because we already have it" is fine; "X feels modern" is not

## What this skill does NOT do

- Does NOT replace `/agent-design` — that designs a single agent loop; this designs the orchestrator across many
- Does NOT replace `/multi-agent-design` — that picks the architectural PATTERN (supervisor / hierarchical / debate); this designs the EXECUTION (parallel / pipeline / journaling / verify)
- Does NOT replace `/plan-mode` — that produces the plan artifact; this orchestrates its execution
- Does NOT pick the LLM model — pair with `/llm-routing` for tier selection inside agent calls
- Does NOT design the per-agent prompts — pair with `/prompt-review` for prompt quality
