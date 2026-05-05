# ADR-0041: Open-Source — SDKs & Integration Libraries

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

LLM application development requires a set of foundational libraries for model loading, provider abstraction, structured output extraction, and distributed training. Without canonical library selections, teams accumulate incompatible dependencies, duplicate provider-specific integration code, and produce LLM outputs with unpredictable formats. This ADR covers the integration and SDK layer that sits below orchestration frameworks (ADR-0034) and above inference engines (ADR-0033).

## Decision

We adopt the following **canonical integration library stack**:

- **Model loading, inference, fine-tuning:** **Hugging Face Transformers** — the standard entry point for all open models; 200K+ models; integrates with all MLOps tools.
- **Model versioning and sharing:** **Hugging Face Hub** — versioned model and dataset registry; team model sharing and weight distribution.
- **Distributed training scale-out:** **Accelerate** — minimal code changes to scale fine-tuning from single GPU to multi-GPU or multi-node.
- **Multi-provider LLM abstraction:** **LiteLLM** — unified OpenAI-compatible API proxy across 100+ providers; cost tracking, fallbacks, and model routing.
- **Structured LLM outputs (Pydantic):** **Instructor** — type-safe JSON extraction from any LLM via Pydantic; primary tool for reliable structured output in Python.
- **Constrained generation (open models):** **Outlines** — constrained decoding (JSON schema, regex, grammar) for open models running locally; guarantees valid structured output without post-processing.

## Rationale

1. **HF Transformers as the model loading standard** — All major open models (Llama, Mistral, Qwen, Phi) publish HuggingFace-compatible weights. Transformers provides a consistent `AutoModelForCausalLM` / `AutoTokenizer` interface regardless of model architecture. Centralises model loading patterns across the team.
2. **LiteLLM for provider abstraction** — When workloads span self-hosted open models and cloud providers (Anthropic, OpenAI, Bedrock), LiteLLM normalises all providers to the OpenAI chat completions format. A model switch requires one configuration change; application code is unchanged. Cost tracking and fallback routing are built in.
3. **Instructor for structured outputs (API-based LLMs)** — Instructor's Pydantic integration provides type-safe structured extraction from any LLM. Automatic retry with validation feedback reduces hallucination rate on structured tasks. Works with any OpenAI-compatible API — including LiteLLM-proxied providers.
4. **Outlines for constrained generation (open models)** — For open models served locally (vLLM, SGLang, Ollama), Outlines enforces valid output at the token generation level via constrained decoding. Unlike post-processing validation, constrained decoding guarantees the output matches the schema — zero invalid JSON.
5. **Accelerate for distributed training** — Accelerate's `Accelerator` class handles distributed training configuration (DDP, FSDP, DeepSpeed) without requiring model code changes. Teams scale from laptop to multi-node cluster by changing the `accelerate config`, not the training code.

## Consequences

### Positive
- LiteLLM abstraction makes provider switching a config change — A/B testing between open models and cloud models requires no code changes
- Instructor + Pydantic structured extraction eliminates brittle JSON parsing — validation errors are surfaced and retried automatically, not silently producing invalid data downstream
- Outlines constrained decoding on open models eliminates the "invalid JSON in production" failure class entirely

### Negative / Trade-offs
- LiteLLM proxy adds a network hop for every LLM call — in latency-sensitive paths, route directly to provider; use LiteLLM as a sidecar proxy, not a remote service
- Instructor retry logic can multiply LLM call costs for complex schemas — set `max_retries=2` and monitor retry rate; simplify schemas if retry rate is high
- Outlines constrained decoding is not compatible with all vLLM/SGLang configurations — verify engine support for guided generation (`--guided-decoding-backend`) before relying on Outlines in production

### Risks
- [RISK: MED] HF Transformers model loading reads full weights into CPU memory before GPU transfer — for large models (70B+), ensure sufficient system RAM; use `device_map="auto"` and `load_in_8bit` for memory-constrained environments
- [RISK: MED] LiteLLM version updates can change provider routing behaviour — pin version; test failover routing after upgrades
- [RISK: LOW] HF Hub model downloads are cached to `~/.cache/huggingface/hub` by default — set `HF_HOME` to a dedicated storage path in production environments to avoid disk pressure

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| OpenAI Python SDK directly | Proprietary; no abstraction over open models; creates coupling to OpenAI API format in application code |
| Marvin | Structured output extraction alternative; smaller ecosystem than Instructor; less Pydantic-native |
| Guidance (Microsoft) | Constrained generation library; less active community than Outlines; Outlines has broader model coverage |
| DeepSpeed directly | Distributed training with more control than Accelerate; higher complexity; Accelerate provides sufficient abstraction for most fine-tuning scenarios |

## Implementation Notes

1. HF Transformers: use `AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.bfloat16)` for production loading; never load in `float32` for 7B+ models
2. HF Hub: authenticate with `huggingface-cli login`; use `snapshot_download(repo_id, local_dir=...)` for controlled model caching in production environments
3. LiteLLM proxy: deploy as sidecar with `litellm --config config.yaml`; configure model routing, fallbacks, and cost limits in `config.yaml`; expose on `localhost:4000` to application
4. Instructor: `import instructor; client = instructor.from_openai(openai.OpenAI(base_url="http://localhost:4000"))` — works with any OpenAI-compatible endpoint including LiteLLM
5. Outlines: `import outlines; model = outlines.models.vllm("model-id"); generator = outlines.generate.json(model, MyPydanticSchema)` — use with vLLM backend for production
6. Accelerate: run `accelerate config` to set up distributed training config; replace `model.to(device)` with `accelerator.prepare(model, optimizer, dataloader)`

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
