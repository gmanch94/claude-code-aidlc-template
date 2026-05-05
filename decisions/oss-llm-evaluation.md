# ADR-0037: Open-Source — LLM Evaluation Frameworks

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

LLM-powered features require continuous evaluation to detect hallucinations, measure retrieval quality, and enforce quality gates in CI/CD pipelines. Without a principled evaluation strategy, teams rely on manual spot-checking, miss regressions before production, and lack objective metrics for model upgrade decisions. A canonical evaluation stack prevents duplicate tooling and ensures consistent measurement methodology across teams.

## Decision

We adopt a **layered evaluation strategy**:

- **CI/CD eval gates (unit tests for LLMs):** **DeepEval** — pytest-native framework with 14+ metrics; runs in CI; blocks merges on eval regression.
- **RAG-specific evaluation:** **RAGAS** — purpose-built metrics (faithfulness, answer relevancy, context precision/recall) for retrieval pipeline quality.
- **Model benchmarking / comparative evaluation:** **LM Evaluation Harness** (EleutherAI) — standardised benchmarks (MMLU, HellaSwag, TruthfulQA) for reproducible model comparison at model selection time.
- **Integrated eval + observability:** **Phoenix** (Arize, MIT) — self-hosted tracing with built-in evaluators; used when eval and production observability must share the same platform.
- **Multi-step agent evaluation:** **Opik** (Comet) — purpose-built for evaluating agentic workflows where tool call sequences and intermediate steps matter, not just final output.
- **Experiment tracking + GenAI eval:** **MLflow 3.0** — hallucination detection and LLM-as-a-judge integrated with the experiment tracking and model registry layer already in use.

## Rationale

1. **DeepEval in CI** — Pytest integration means eval runs in existing CI pipelines without new infrastructure. LLM-as-a-judge metrics (G-Eval, hallucination, answer relevancy) are configurable per feature. Eval gates prevent hallucination regressions from reaching production silently.
2. **RAGAS for RAG quality** — RAG pipeline quality cannot be inferred from general LLM metrics alone. RAGAS measures the retrieval-generation interaction: faithfulness (does the answer follow from retrieved context?) and context precision (was retrieved context relevant?). These metrics are not available in general-purpose eval frameworks.
3. **LM Eval Harness at model selection time** — When selecting or upgrading open models (ADR-0032), LM Eval Harness provides reproducible benchmark comparisons. Its 60+ standardised tasks match what model release papers report — results are directly comparable.
4. **Phoenix for integrated eval + trace** — Self-hosted MIT-licensed tool that spans both evaluation and observability. When teams want one platform for tracing production LLM calls and running evaluations against sampled traces, Phoenix eliminates the need for separate Langfuse + eval tooling.
5. **MLflow 3.0 as the evaluation-tracking backbone** — MLflow's eval integration stores eval results alongside experiment runs and model versions. Teams already using MLflow for experiment tracking get LLM evaluation without adding a new platform.

## Consequences

### Positive
- DeepEval CI gates make hallucination regressions visible before production — eval becomes part of the merge process, not an afterthought
- RAGAS gives RAG teams objective retrieval quality metrics — chunk size, top-k, and reranker decisions can be validated empirically, not by intuition
- MLflow 3.0 unifies experiment tracking, model registry, and eval — reduces platform sprawl for teams already in the MLflow ecosystem

### Negative / Trade-offs
- LLM-as-a-judge evaluation (DeepEval, RAGAS) adds LLM inference cost per eval run — budget token costs for eval in CI; use smaller judge models (Phi-4, Mistral) to reduce cost
- LM Eval Harness is a batch benchmarking tool, not a continuous monitoring tool — use only at model selection time, not for production drift detection
- Multiple evaluation tools with overlapping capabilities (Phoenix vs Langfuse, MLflow eval vs DeepEval) require clear team-level decisions on which to use per context

### Risks
- [RISK: HIGH] Eval results are only as good as the test dataset — synthetic test sets can mask real-world failure modes; curate eval sets from production query samples
- [RISK: MED] LLM judge models can disagree with human raters — calibrate judge agreement (Cohen's κ) against human labels before trusting automated eval scores
- [RISK: LOW] MLflow eval API changed significantly in 3.0 — pin MLflow version; test eval pipelines after version upgrades

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| TruLens | Predecessor to Phoenix (Arize acquisition); Phoenix is the maintained successor — no new projects on TruLens |
| Promptfoo | Strong for prompt comparison and red-teaming; less mature for continuous CI eval gates vs DeepEval's pytest integration |
| Giskard | Good for ML fairness and bias testing; less coverage of LLM-specific metrics (hallucination, faithfulness) compared to DeepEval + RAGAS |
| Manual human eval only | Not scalable for CI/CD; acceptable as a supplementary calibration layer but not as the primary eval mechanism |

## Implementation Notes

1. DeepEval: add `@pytest.mark.parametrize` test cases with `assert_test(llm_test_case, [HallucinationMetric(threshold=0.5)])`; run with `deepeval test run` in CI
2. RAGAS: evaluate RAG pipeline with `evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])`; target `faithfulness > 0.85` for production
3. LM Eval Harness: run `lm_eval --model vllm --model_args pretrained=<model> --tasks mmlu,hellaswag --batch_size auto` for model comparison; store results in MLflow
4. Phoenix: deploy via `pip install arize-phoenix; phoenix.launch_app()` or Docker; configure `PHOENIX_PORT` and connect via OpenTelemetry exporter
5. Define eval dataset versioning strategy — store eval sets in `eval/datasets/` with version tags; never mutate existing eval sets (append only)
6. Minimum CI eval gate: DeepEval hallucination + answer relevancy; RAGAS faithfulness for any RAG feature; fail build if metrics drop >10% vs baseline

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
