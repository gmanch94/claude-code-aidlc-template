# ADR-0032: Open-Source — LLM Selection & Model Tiers

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Self-hosted AI workloads require a principled model selection policy that balances capability, licensing, inference cost, and operational footprint. Without a clear tier structure, teams independently evaluate and deploy models, leading to fragmented infrastructure, inconsistent quality, and unmanaged compliance risk from non-permissive licenses.

## Decision

We adopt a **three-tier open model strategy**:

- **Tier 1 — Production default:** Llama 3.3 70B and Mistral Small 3 24B cover the majority of instruction-following, RAG, and agentic workloads with Apache 2.0 or community licenses suitable for commercial use.
- **Tier 2 — High-throughput MoE:** DeepSeek-V3 671B (MIT) and Mixtral 8x22B (Apache 2.0) for workloads where throughput-per-token-dollar matters more than memory footprint.
- **Tier 3 — Edge / constrained compute:** Phi-4 14B (MIT) and Gemma 3 1B–27B for on-device, latency-sensitive, or cost-constrained scenarios.

Model selection must be approved at the architecture level for Tier 2+ due to infrastructure requirements.

## Rationale

1. **License clarity first** — MIT and Apache 2.0 models are safe for commercial self-hosted use without legal review. Llama Community License and Gemma Terms of Use require review before commercial deployment; this is enforced at the ADR gate.
2. **Llama 3.3 70B as Tier 1 anchor** — Strong reasoning, 128K context, broad community support, and extensive inference engine optimisation (vLLM, SGLang, TensorRT-LLM). Covers ~80% of production use cases.
3. **MoE for throughput** — DeepSeek-V3's 37B active parameters from a 671B parameter MoE delivers frontier quality at tolerable inference cost. MIT license removes legal friction.
4. **Phi-4 / Gemma 3 for edge** — Sub-14B models with strong reasoning at small scale for local serving, developer laptops (via Ollama/llama.cpp), or embedded inference.

## Consequences

### Positive
- Consistent license and compliance posture across teams — no surprise non-commercial-only models in production
- Infrastructure planning simplified: Tier 1 fits on 2× A100 80GB; Tier 2 MoE requires node-level planning with KTransformers or multi-GPU
- MoE selection unlocks frontier quality without paying frontier cloud inference prices

### Negative / Trade-offs
- Llama Community License requires Meta's usage policy review — teams must document use case before deploying 70B+ Llama models commercially
- MoE (DeepSeek-V3) requires significant RAM (382GB+ for CPU offload with KTransformers) — limits deployment environments
- Open models lag frontier proprietary models on instruction following for complex reasoning; evaluate per use case

### Risks
- [RISK: MED] Model weights from HuggingFace Hub may be tampered — verify SHA checksums against official model cards before production deployment
- [RISK: LOW] Rapid open model releases may make tier assignments stale within 6 months — quarterly model tier review required

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Single model for all workloads | No single OSS model optimally covers edge, production, and high-throughput simultaneously; creates unnecessary compute waste |
| Qwen 2.5 as Tier 1 | Strong multilingual and coding capability but primarily optimised for Chinese-language enterprise use cases; Llama 3.3 is better default for English-primary workloads |
| Command R+ (CC-BY-NC) | Non-commercial license prohibits production use without Cohere agreement; excluded from default tiers |
| Proprietary models only | Eliminates cost arbitrage, data residency flexibility, and vendor independence — contradicts platform strategy |

## Implementation Notes

1. Store model tier assignments in `config/model-registry.yaml` — include model ID, HuggingFace repo, SHA checksum, license, and approved use cases
2. Pull models via `huggingface-cli download` with `--include "*.safetensors"` — always verify against published SHA
3. Llama 3.3 70B: request Meta access at [meta.ai/llama-downloads](https://llama.meta.com/llama-downloads/); document use case in ADR supplement
4. For MoE (DeepSeek-V3): validate available RAM before deployment; use KTransformers for commodity hardware, vLLM multi-GPU for production cluster
5. Define model upgrade SLA: Tier 1 upgrades go through architecture review; Tier 3 can be updated by ML eng with PR approval only

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
