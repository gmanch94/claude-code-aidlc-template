# ADR-0033: Open-Source — LLM Inference & Serving

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Self-hosted LLM workloads require a principled inference serving strategy. Teams face a fragmented landscape of engines with different throughput characteristics, hardware requirements, and operational maturity. Without a canonical selection, projects independently choose serving stacks, leading to inconsistent APIs, duplicated ops work, and missed performance optimisations.

## Decision

We adopt a **tiered serving strategy** based on environment and hardware:

- **Production (NVIDIA GPU cluster):** **vLLM** as the default; **TensorRT-LLM** for peak-throughput NVIDIA-optimised workloads where additional tuning budget exists.
- **High-concurrency structured output / multi-turn:** **SGLang** as the primary alternative to vLLM where RadixAttention KV cache reuse provides measurable gains.
- **Local development / prototyping:** **Ollama** for single-developer environments; **llama.cpp** for CPU-only or quantised edge deployments.
- **Consumer hardware MoE:** **KTransformers** for running 671B MoE models (DeepSeek-V3) on commodity GPU + CPU offload configurations.

All production serving exposes an **OpenAI-compatible REST API** regardless of backend engine.

## Rationale

1. **vLLM as production default** — PagedAttention delivers up to 80% GPU memory reduction vs naive KV cache management; continuous batching maximises GPU utilisation under variable load. Used in production at Meta, LinkedIn, Roblox — battle-tested at scale.
2. **OpenAI-compatible API standardisation** — All selected engines (vLLM, SGLang, Ollama) expose `/v1/chat/completions`. Application code is engine-agnostic; switching engines requires only a base URL change.
3. **SGLang for structured/multi-turn workloads** — RadixAttention enables fine-grained KV cache prefix sharing across requests with common prefixes (system prompts, RAG context). Outperforms vLLM for RAG workloads and agentic loops with shared prefixes.
4. **Ollama for dev parity** — Developers run the same models locally without GPU clusters. One-command model pull, built-in model library, and REST API matching production surface.
5. **KTransformers for MoE on commodity hardware** — 3–28× speedup over naive CPU offloading for DeepSeek-V3 671B. Enables teams to evaluate frontier MoE quality without dedicated multi-GPU nodes.

## Consequences

### Positive
- Production serving API is uniform — downstream clients are engine-agnostic; engine upgrades are transparent
- vLLM's continuous batching and PagedAttention reduce GPU memory cost significantly, lowering infrastructure cost per token
- Local dev (Ollama) mirrors production API surface — no context switching for developers

### Negative / Trade-offs
- vLLM requires NVIDIA CUDA GPU for production deployment — not suitable for CPU-only or AMD GPU without additional configuration
- TensorRT-LLM requires model-specific compilation (engine build step) — higher ops overhead than vLLM's direct weight loading
- KTransformers MoE inference requires 382GB+ system RAM for full DeepSeek-V3 — narrows eligible deployment targets significantly

### Risks
- [RISK: MED] vLLM version upgrades can change KV cache format — test model compatibility before rolling upgrades in production
- [RISK: LOW] Ollama is not production-scale — teams may inadvertently use it for production loads; enforce environment tagging in deployment configs

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Ray Serve + custom model loading | High ops complexity; no PagedAttention or continuous batching out of box; better as deployment wrapper around vLLM |
| Triton Inference Server (NVIDIA) | Requires model conversion to Triton format; higher ops burden than vLLM for LLMs specifically; no native continuous batching |
| HuggingFace TGI | Previously strong competitor; vLLM and SGLang have surpassed TGI on throughput benchmarks; community momentum shifted |
| llama.cpp for production | CPU inference throughput insufficient for multi-user production; acceptable only for edge or single-user workloads |

## Implementation Notes

1. Deploy vLLM via Helm chart or `vllm serve <model> --api-key <key> --port 8000`; set `--max-model-len` based on available GPU VRAM
2. Pin engine versions in `pyproject.toml` / `requirements.txt` — vLLM releases frequently; uncontrolled upgrades risk KV cache incompatibility
3. Configure `--tensor-parallel-size` for multi-GPU deployments; `--pipeline-parallel-size` for multi-node
4. Expose Prometheus metrics via `--enable-metrics`; scrape `/metrics` endpoint for token throughput, queue depth, and GPU utilisation
5. For SGLang: use `python -m sglang.launch_server --model <model> --tp <n>` with `--enable-torch-compile` for additional throughput
6. Ollama: restrict to `localhost` in developer environments; never expose Ollama port externally without auth proxy

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
