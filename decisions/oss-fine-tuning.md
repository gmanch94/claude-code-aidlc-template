# ADR-0040: Open-Source — Fine-Tuning

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [llm]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Production AI products sometimes require fine-tuned models for domain adaptation, task-specific behaviour, or cost reduction (smaller fine-tuned model vs larger general model). The fine-tuning tooling landscape spans full fine-tuning, parameter-efficient fine-tuning (PEFT), RLHF/preference optimisation, and hardware-optimised kernels. Without a canonical tooling stack, teams independently assemble fine-tuning pipelines with inconsistent quality, reproducibility, and GPU cost.

## Decision

We adopt a **purpose-driven fine-tuning toolkit**:

- **Standard PEFT (LoRA, QLoRA, DoRA):** **Hugging Face PEFT** — industry-standard library; integrates with Transformers, Accelerate, and TRL; the default entry point for all PEFT fine-tuning.
- **RLHF and preference optimisation (DPO, PPO, GRPO):** **TRL** (Hugging Face) — full RLHF and preference optimisation pipeline; works with PEFT and Accelerate; the default for instruction tuning and alignment work.
- **GPU-efficient fine-tuning (cost reduction):** **Unsloth** — 2× faster training, 60% less VRAM via optimised LoRA/QLoRA kernels; drop-in replacement for HF Transformers; use when GPU cost or VRAM is a constraint.
- **Config-driven fine-tuning (reproducibility):** **Axolotl** — YAML-defined fine-tuning recipes for SFT, LoRA, QLoRA, RLHF; strong community model-specific recipes; use when reproducibility and config-as-code are the primary concerns.

Fine-tuning is a **last resort** after prompt engineering, RAG, and few-shot approaches have been evaluated and found insufficient. Every fine-tuning project requires a documented eval baseline before training begins.

## Rationale

1. **HF PEFT as the canonical PEFT library** — PEFT (LoRA, QLoRA, DoRA, IA³) is the industry standard. The library is maintained by Hugging Face, integrates with the full HF ecosystem, and has the largest community of model-specific configurations. Starting here avoids fragmentation.
2. **TRL for alignment work** — TRL implements SFT, DPO, PPO, and GRPO with a consistent API. DPO (Direct Preference Optimisation) is significantly cheaper than PPO for preference alignment and is the default alignment technique unless online RL is specifically required.
3. **Unsloth for GPU cost reduction** — When fine-tuning on consumer GPUs (24GB VRAM) or reducing cloud GPU spend is a requirement, Unsloth's optimised CUDA kernels deliver 2× throughput improvement and 60% VRAM reduction vs baseline HF Transformers. It is a drop-in replacement — no workflow changes required.
4. **Axolotl for config-as-code** — YAML-defined fine-tuning configurations are version-controllable, diffable, and reproducible. Community recipes for common model/task combinations (Llama-3 SFT, Mistral LoRA) reduce setup time. The right choice when the fine-tuning config must be auditable and reproducible across runs.
5. **Fine-tuning as a last resort** — Fine-tuning introduces model maintenance burden (re-tuning on base model updates, eval regression risk, dataset governance). Prompt engineering + RAG resolves most domain adaptation needs at lower cost and with simpler rollback paths. Document the rationale for fine-tuning over alternatives before beginning.

## Consequences

### Positive
- HF PEFT + TRL covers the majority of fine-tuning scenarios with a consistent API and strong community support
- Unsloth reduces GPU cost enough to make fine-tuning feasible on smaller GPU instances — LoRA/QLoRA on a single A100 rather than multi-GPU
- Axolotl YAML configs stored in version control provide full reproducibility — re-running a config produces the same model

### Negative / Trade-offs
- Fine-tuned models require ongoing maintenance — every base model update requires re-evaluation of fine-tuned behaviour; factor maintenance cost into the build decision
- Axolotl's YAML abstraction hides training loop details — debugging unusual training dynamics requires understanding the underlying HF Transformers code
- Unsloth supports a limited set of models (Llama, Mistral, Qwen family) — verify model support before committing to Unsloth for a new model architecture

### Risks
- [RISK: HIGH] Fine-tuning on biased or PII-containing datasets bakes the data problems into model weights permanently — mandatory data audit (see `/pii-scan`) before fine-tuning begins
- [RISK: MED] LoRA rank and alpha hyperparameters significantly affect output quality — run hyperparameter sweep (Optuna/MLflow) before committing to production training config
- [RISK: LOW] Unsloth quantised training can introduce subtle numerical differences vs full-precision training — validate final model output quality with eval suite before production deployment

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Full fine-tuning (no PEFT) | 10–100× more GPU memory and compute vs LoRA; rarely justified for instruction tuning tasks; consider only for domain-specific pretraining |
| LM Studio (GUI) | Acceptable for developer experimentation; not suitable for reproducible, auditable production fine-tuning pipelines |
| OpenAI fine-tuning API | Proprietary; contradicts self-hosted strategy; no access to model weights; vendor lock-in |
| Ludwig | ML framework with fine-tuning support; less LLM-specific optimisation than HF ecosystem; larger learning curve for teams already on HF Transformers |

## Implementation Notes

1. Always establish an eval baseline before fine-tuning: run DeepEval or RAGAS on the base model to set the quality floor
2. HF PEFT LoRA config: `LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05, bias="none")`; adjust `r` based on task complexity
3. TRL SFT: `SFTTrainer(model, args=SFTConfig(output_dir=...), train_dataset=..., peft_config=lora_config)` — always use `peft_config` for efficient training
4. Unsloth: `from unsloth import FastLanguageModel; model, tokenizer = FastLanguageModel.from_pretrained(model_name, load_in_4bit=True)` — 4-bit QLoRA by default
5. Axolotl: define config in `config.yaml`; run with `accelerate launch -m axolotl.cli.train config.yaml`; store config in `fine-tuning/configs/` under version control
6. Log fine-tuning runs to MLflow: `mlflow.log_params(lora_config)`, `mlflow.log_metrics({"train_loss": ..., "eval_loss": ...})`; register final adapter in model registry

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
