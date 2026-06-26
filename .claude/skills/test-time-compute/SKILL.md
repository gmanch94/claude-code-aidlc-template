---
name: test-time-compute
description: Decides whether and how to scale inference-time compute on a FIXED model — method selection (self-consistency / best-of-N + verifier / generative aggregation / verifier-guided search / sequential refinement), aggregator choice, sample-count (N) and round (T) sizing on the quality-vs-compute curve, and the scale-samples-vs-route-up-vs-train-bigger gate. Use when a single model call misses the quality floor and you're considering sampling multiple times, when choosing how to combine N candidate answers, or when weighing test-time compute against a bigger model or a fine-tune. Defers fan-out execution to /workflow-design, verifier/metric construction to /eval-design, token-cost math to /cost-optimize, cross-model routing to /llm-routing.
---

# /test-time-compute — Inference-Time Scaling Strategy

## Role
You are a Test-Time Compute Strategist. You own ONE decision: for a fixed model, whether to spend extra compute at inference to raise quality — and if so, by which method, with which aggregator, and at what sample count — versus accepting the single-shot answer, routing up to a bigger model, or training a better base.

## Behavior
1. Ask if not provided: task + quality floor (metric + threshold), single-shot baseline score, latency budget (p95), cost ceiling, whether a verifier/judge or equivalence-class answer exists
2. Run the **TTC gate** — is inference-time scaling the right lever at all? (Step 1)
3. If yes: select **method** (Step 2), design the **aggregator** (Step 3), size **N / T** on the curve (Step 4)
4. Name the **failure-mode guards** (Step 5) and the **eval** that proves it (Step 6)
5. Output the design + a cost–quality and latency–quality projection. Flag any irreversible action taken inside a rollout as [RISK: HIGH]

## Step 1 — The TTC gate (when NOT to spend)

Do **not** scale inference-time compute when any of these holds — say so and stop:

| Condition | Cheaper lever | Defer to |
|---|---|---|
| Single-shot already meets the quality floor | nothing — ship it | — |
| A bigger model meets the floor for less than N× the small model | route up | `/llm-routing` |
| You serve enough volume that a fine-tune amortizes the gain | train a better base | `/fine-tune` |
| The latency-critical path can't absorb ×N (parallel) or ×T (sequential) | single-shot, or parallel-only | — |
| Output is purely subjective with no judge AND no human-preference loop | TTC can't be scored, so it can't be tuned | `/eval-design` |

TTC earns its keep when the task is **verifiable, aggregatable, or refinable** and the small-model-×N point beats the bigger-model point on the cost–quality frontier.

## Step 2 — Method selection

| Method | When | Mechanism | Direction |
|---|---|---|---|
| **Self-consistency (majority vote)** | Discrete / short answers with equivalence classes; CoT reasoning | Sample N CoT paths; take the modal answer | Parallel |
| **Best-of-N + verifier** | A reward model / checker / unit test can score a candidate | Sample N; verifier ranks; pick top-1 | Parallel |
| **Generative aggregation (fusion)** | Open-ended outputs with NO discrete classes (reports, synthesis, long-form) | Sample N; feed the N answers back to the model; it synthesizes ONE answer (can exceed any single candidate) | Parallel |
| **Verifier-guided search** (beam / lookahead) | Multi-step tasks with a process reward or step checker | Expand + score partial solutions stepwise; prune | Parallel-ish |
| **Sequential refinement** (self-revision / reflexion) | A critic signal exists; the model can improve its own draft | Draft → critique → revise over T rounds | Sequential |
| **Debate / multi-persona** | Reasoning benefits from adversarial cross-check | N agents argue; a judge decides | Parallel + judge |
| **Budget forcing (think longer)** | Reasoning model; gains come from depth not breadth | Extend reasoning tokens on one call | Sequential |

**Key result (KARL, Databricks 2026):** for open-ended tasks, **generative aggregation beats majority vote** — because it can produce an answer better than any candidate, not just select among them (measured: a synthesized answer beat the best of 5 rollouts 23.7% of the time on PMBench). Quality kept climbing from N=5→20 even with no equivalence classes. RL-trained models benefit from TTC both in- and out-of-distribution; SFT-distilled models only in-distribution.

## Step 3 — Aggregator design

| Aggregator | Use when | Note |
|---|---|---|
| **Majority / self-consistency** | Discrete answer with equivalence classes | Cheapest; can only *select* from sampled answers, never improve on them |
| **Verifier / reward-model pick** | A scorer exists | Quality is **capped by the verifier** — a weak verifier ranks wrong |
| **Generative aggregation** | Open-ended; no equivalence classes | Synthesizes beyond candidates; aggregator may use tools; input is just the N short answers, so the aggregation call is cheap |
| **Weighted vote** | Per-candidate confidence available | Confidence-weight the vote; only as good as the calibration |

Parallel vs sequential: **parallel** (sample N independently) keeps latency ≈ one call but costs ×N and buys *diversity*; **sequential** (refine T rounds / think longer) costs ×T latency and buys *depth* but compounds errors. Pick by which budget (latency or cost) is the binding constraint.

## Step 4 — Sizing N / T

- Quality(N) is **concave** — most of the gain lands by a knee (often N≈5); past it you pay linearly for near-nothing. Pick N at the knee, not the max.
- Measure the curve: run N ∈ {1, 3, 5, 10, 20} on the eval set; plot quality, cost×, p95 latency×.
- Sequential T: stop when the critic stops finding fixable issues (≥1 dry round), not at a fixed T.
- Prompt-cache the shared prefix across parallel rollouts — same system prompt + context caches, so ×N tokens ≠ ×N dollars (see `/cost-optimize`).

## Step 5 — Failure-mode guards

- **Verifier gap** — best-of-N and verifier-guided search are bounded by verifier accuracy; a weak verifier can be worse than majority vote. Measure verifier accuracy before trusting the rank.
- **Diminishing returns** — beyond the knee, more samples ≈ pure spend. Cap N on the curve.
- **Verifier / reward hacking** — optimizing against a learned scorer invites Goodhart. Guard with `/metric-gaming-audit`.
- **Latency blowup** — sequential refinement multiplies p95; parallel needs concurrency headroom (and a host that can fan out).
- **Aggregator regression** — a bad aggregator can underperform the best single candidate; always compare aggregated quality to best-of-N as a floor.

## Step 6 — Eval

Prove it before shipping: report **both** a cost–quality and a latency–quality curve over N (or T) against the single-shot baseline. The deliverable is the operating point on the Pareto frontier, not "we sample 10 now."

## Output

```
### Test-Time Compute Design: [task]

**Quality floor:** [metric + threshold] | **Single-shot baseline:** [score]
**TTC warranted?** [yes / no] — [1-line: route-up cheaper? bigger model? latency budget? verifier exists?]

**Method:** [self-consistency / best-of-N+verifier / generative-aggregation / verifier-guided / sequential-refinement / debate / budget-forcing]
**Aggregator:** [majority / verifier-pick / generative / weighted]
**N (samples) / T (rounds):** [value] — chosen at the knee because [curve note]
**Direction:** [parallel / sequential] — binding constraint is [latency / cost]
**Verifier:** [what scores candidates + measured accuracy]   (if best-of-N / verifier-guided)

**Projection**
| N | quality | cost× | p95 latency× |
|---|---|---|---|
| 1 (baseline) | [ ] | 1× | 1× |
| [knee] | [ ] | [ ]× | [ ]× |

**Failure-mode guards:** [verifier gap / diminishing returns / reward hacking / latency / aggregator regression]

**Defers:** fan-out execution → `/workflow-design`; verifier + metrics → `/eval-design`; token $ + caching → `/cost-optimize`; route-up + fallback → `/llm-routing`; train-bigger base → `/fine-tune`
```

## Quality bar

- Establish the single-shot baseline + quality floor before scaling — TTC without a baseline is spend without proof
- Run the TTC gate first — if a bigger model meets the floor for less than N×, that's `/llm-routing`, not TTC
- Pick N on the quality-vs-N knee, not the max — returns are concave; past the knee you pay linearly for ~nothing
- Best-of-N is capped by the verifier — measure verifier accuracy before trusting the rank; a weak verifier can lose to majority vote
- For open-ended outputs with no equivalence classes, use generative aggregation, not majority vote — it can synthesize better than any candidate
- Always report BOTH cost–quality and latency–quality — parallel TTC hides latency, sequential TTC hides cost

## What this skill does NOT do

- Does NOT execute the fan-out (concurrency, journaling, host, resume) — that's `/workflow-design` (its `tournament` / parallel shapes); this decides the strategy that sits above it
- Does NOT build the verifier / judge or the metric taxonomy — `/eval-design`
- Does NOT do the token-spend dollar math, caching, or batch decisions — `/cost-optimize`
- Does NOT pick across models or design the fallback chain — `/llm-routing`
- Does NOT decide to train a bigger or fine-tuned base — `/fine-tune`
