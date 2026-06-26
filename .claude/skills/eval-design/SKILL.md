---
name: eval-design
description: Designs LLM evaluation frameworks with metric selection by task type, test set sizing, pass/fail thresholds, and drift triggers. Use when setting up evals for an LLM feature, before first production deployment, or when asked how to measure AI quality.
---

# /eval-design — LLM Evaluation Framework

## Role
You are a LLM Evaluation Designer.

## Behavior
1. Ask if not provided: feature name, model, use case, latency budget, pre-launch only or ongoing
2. Select metrics by task type (see below)
3. Define test set with minimum sizes and ground truth sources
4. Set thresholds, cadence, and drift triggers

## Metric taxonomy

| Task type | Primary metrics | Safety metrics |
|-----------|----------------|----------------|
| Q&A / RAG | Faithfulness, Answer relevance, Context recall | Hallucination rate, Refusal rate |
| Summarization | ROUGE-L, BERTScore, Factual consistency | PII leakage rate |
| Classification | Accuracy, F1, Confusion matrix | Bias across demographic slices |
| Code generation | Pass@k, Syntax error rate, Test pass rate | Injection / unsafe code detection |
| Agentic / tool use | Task completion rate, Step efficiency, Tool-call accuracy | Scope creep, unintended action rate |
| Open-ended | LLM-as-judge (1–5), Coherence, Tone | Toxicity, Jailbreak susceptibility |

**Query-regime coverage (Q&A / RAG / agentic-search evals):** the eval set must span the heterogeneous query regimes your users actually hit — constraint-driven entity lookup, cross-document synthesis, tabular / numeric reasoning, exhaustive retrieval (recall-bound), procedural how-to, fact aggregation. A model tuned for one regime is not competent on the others; a single-regime eval set hides the gap and overstates readiness. (KARLBench six-regime finding, arXiv:2603.05218, Databricks 2026.)

**Benchmark hygiene (static / public benchmarks):** before trusting a static benchmark as a blocking gate, audit it for three recurring defect classes — **specification–verification mismatch** (the grader passes/fails answers the task spec doesn't), **resource mismatch** (tasks assume tools / data / compute the harness doesn't actually provide), and **benchmark drift** (the benchmark or its dependencies changed under you). Re-baseline on every version bump: one benchmark point-release moved frontier agents by up to ~12pp, so scores are not comparable across versions — never mix results from two benchmark versions in one table. (Terminal-Bench 2.1 audit, as reported in OpenThoughts-Agent, arXiv:2606.24855.)

## Test set minimums (rule of thumb)

| Type | Min | Blocking? |
|------|-----|-----------|
| Regression | 30–50 | Yes — block on > 5% drop |
| Format compliance | 50–100 | Yes — any failure |
| Tool-call accuracy | 50–150 | Yes — per-tool threshold |
| Grounding / hallucination | 50–200 | Yes — per-task threshold |
| Adversarial | 30–100 | Advisory; refresh quarterly |
| Cost-per-task | 100+ (from production) | Alert on > 20% regression |
| Latency p50/p95 | 30–50 | Alert on > 20% regression |

## Eval tooling note (2026-06)

> **OpenAI Evals sunset — read-only 2026-10-31, shutdown 2026-11-30** (announced 2026-06-03). If your evals or distillation pipelines depend on the `openai.evals` API, migrate before Oct 31. OpenAI's own named migration target is **Promptfoo**; other replacements: **Braintrust**, **Langfuse**, **OpenAI Agents SDK tracing** (for run-level capture).

Distillation pipelines (Stored Completions → Evals → SFT/DPO on smaller model) also break when Evals is gone — plan the replacement for the eval stage AND the distillation stage in the same migration.

Cross-vendor eval tooling that survives this sunset:
- **Promptfoo** — OpenAI's own named migration target; open-source; YAML-configurable
- **Braintrust** — commercial; integrates with most LLM providers
- **Langfuse** — open-source; trace + eval combined
- **LangSmith** (LangChain) — commercial; tight LangChain integration
- **Arize Phoenix** — open-source; observability + eval
- **Inspect AI** (Anthropic) — research-grade; agentic-task focus
- **OpenAI Agents SDK tracing** — for run-level capture inside the Agents SDK loop

## Human preference eval (blind side-by-side)

When automated metrics + LLM-as-judge can't separate two candidates (open-ended generation, deep-research reports, agent traces), collect human preferences:

- **Blind side-by-side:** show both outputs; **hide model identity AND citations until a vote is recorded**, and **randomize left/right position**. Hiding identity kills model-awareness bias; randomizing position kills position bias — both are large, documented confounds in human preference voting.
- **Aggregate:** win-rate or Elo over enough pairings to separate; capture a free-text failure note per vote; keep a shareable link to each pairing for team review.
- **Defers:** statistical significance of the win-rate → `/model-comparison`; trace triage + failure-note routing → `/feedback-loop`; inter-annotator agreement → `/label-quality`; live-traffic sizing → `/ab-test-design`.

(Pattern: LMArena-style blind arena; KARL eval harness, arXiv:2603.05218, Databricks 2026.)

## Quality bar
- No LLM system goes to Week 1 without 30-row regression + 50-row format eval minimum
- LLM-as-judge requires calibration against human judgments before use as blocking gate
- "We'll add evals later" = [RISK: HIGH] — no pre-launch baseline means no regression signal
- Golden set used for prompt tuning is no longer a golden set — maintain strict separation
- Adversarial sets decay — refresh quarterly
- **Don't build new pipelines on OpenAI Evals** (sunset 2026-11-30) — pick a survivor from the tooling note above
- For multi-judge agreement on the same eval row, **diversify reasoning method** (failure-mode enumeration / first-principles re-derivation / adversarial counter-example), not just lens — same-family panels collapse on correlated errors ("Nine Judges, Two Effective Votes," arxiv 2605.29800). N=3 reasoning-diverse beats N=9 same-family.
