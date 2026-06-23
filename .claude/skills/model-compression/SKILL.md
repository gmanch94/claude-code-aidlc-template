---
name: model-compression
description: Select and apply model compression techniques (quantization, pruning, knowledge distillation) for latency reduction or edge deployment. Use when a model is too slow, too large for target hardware, or needs edge/mobile deployment. Outputs technique selection, code pattern, and eval plan.
---

# Model Compression

## Role
You are a Model Compression Specialist.

## Quick start

Gather: current model (framework, architecture, size), latency target (p99 ms), hardware target (GPU/CPU/edge chip), acceptable accuracy drop (%), deployment environment.

Output: technique selection + code pattern + eval plan.

---

## Technique selection

| Situation | Primary technique | Fallback |
|---|---|---|
| PyTorch/TF, GPU serving, < 5% accuracy drop OK | **INT8 quantization** (post-training) | FP16 mixed precision |
| < 2% accuracy drop, can retrain | **Quantization-aware training (QAT)** | PTQ |
| > 50% size reduction needed, can retrain | **Structured pruning** | Distillation |
| Unstructured sparsity (specialized hardware) | **Magnitude pruning** | Distillation |
| Train student from scratch, any framework | **Knowledge distillation** | Distillation + QAT |
| Mobile/edge (Android/iOS) | **TFLite INT8** or **ONNX + ONNX Runtime Mobile** | Distillation → TFLite |
| LLM inference latency | **GPTQ / AWQ (4-bit)** or **llama.cpp gguf** | Speculative decoding |

**Order of preference (least invasive first):** PTQ → FP16 → QAT → pruning → distillation. Stop when target met.

---

## 1. Post-training quantization (PTQ)

No retraining. Run calibration dataset (100–1000 representative samples).

```python
# PyTorch dynamic quantization (CPU, LSTM/Linear layers)
import torch
model_q = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear, torch.nn.LSTM}, dtype=torch.qint8
)

# PyTorch static quantization (CNN, more accurate)
model.eval()
model.qconfig = torch.quantization.get_default_qconfig("fbgemm")  # CPU
# torch.quantization.get_default_qconfig("qnnpack")  # ARM/mobile
torch.quantization.prepare(model, inplace=True)
# Run calibration data through model here
torch.quantization.convert(model, inplace=True)

# ONNX export + quantize
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic("model.onnx", "model_q.onnx", weight_type=QuantType.QInt8)
```

Expected: 2–4× model size reduction, 1.5–3× CPU speedup, <1% accuracy drop (typical).

---

## 2. Quantization-aware training (QAT)

Simulate quantization during training. More accurate than PTQ on image models.

```python
# PyTorch QAT
model.train()
model.qconfig = torch.quantization.get_default_qat_qconfig("fbgemm")
torch.quantization.prepare_qat(model, inplace=True)

# Fine-tune for 5–10% of original training epochs
optimizer = torch.optim.SGD(model.parameters(), lr=1e-4)
for epoch in range(qat_epochs):
    train_one_epoch(model, optimizer, data_loader)

model.eval()
torch.quantization.convert(model, inplace=True)
```

---

## 3. Structured pruning

Remove entire filters/heads; hardware-friendly (dense ops remain dense).

```python
import torch.nn.utils.prune as prune

# Prune 20% of conv layer filters by L1 norm
prune.ln_structured(module, name="weight", amount=0.2, n=1, dim=0)

# Global pruning across layers
parameters_to_prune = [
    (model.conv1, "weight"), (model.conv2, "weight"), (model.fc, "weight")
]
prune.global_unstructured(
    parameters_to_prune, pruning_method=prune.L1Unstructured, amount=0.3
)

# Make permanent, then fine-tune
for module, _ in parameters_to_prune:
    prune.remove(module, "weight")
# Fine-tune 10–20% of original epochs to recover accuracy
```

**Prune iteratively:** 10% → eval → 10% → eval → ... Stop when accuracy drops below threshold.

---

## 4. Knowledge distillation

Train small student to mimic large teacher's soft outputs.

```python
import torch.nn.functional as F

def distillation_loss(student_logits, teacher_logits, labels,
                       temperature=4.0, alpha=0.7):
    # Soft targets from teacher
    soft_loss = F.kl_div(
        F.log_softmax(student_logits / temperature, dim=1),
        F.softmax(teacher_logits / temperature, dim=1),
        reduction="batchmean"
    ) * (temperature ** 2)

    # Hard labels (standard cross-entropy)
    hard_loss = F.cross_entropy(student_logits, labels)

    return alpha * soft_loss + (1 - alpha) * hard_loss
```

- Temperature 2–5 (higher = softer distribution, more transfer)
- Alpha 0.5–0.9 (higher = trust teacher more)
- Student 3–10× smaller than teacher is typical
- Intermediate layer distillation (feature maps) improves results for vision models

---

## 5. LLM-specific compression

| Technique | Tool | Size reduction | Quality impact |
|---|---|---|---|
| GPTQ (4-bit) | `auto-gptq` | 4× | < 1% perplexity increase |
| AWQ (4-bit) | `autoawq` | 4× | Slightly better than GPTQ |
| GGUF (llama.cpp) | `llama.cpp` | 2–8× | Q4_K_M: near-lossless |
| Speculative decoding | vLLM / TGI | 2–3× throughput | No quality loss |

```python
# AWQ quantization
from awq import AutoAWQForCausalLM
model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-3-8b")
quant_config = {"zero_point": True, "q_group_size": 128, "w_bit": 4}
model.quantize(tokenizer, quant_config=quant_config)
model.save_quantized("llama3-8b-awq")
```

---

## Evaluation plan

Run before and after compression:

| Metric | Threshold | Notes |
|---|---|---|
| Primary task metric | < X% drop (set per project) | Non-negotiable gate |
| Latency p99 | Must meet SLA | Test on target hardware |
| Model size (MB) | Document delta | For edge: hard constraint |
| Throughput (req/s) | Document delta | GPU serving |
| Calibration ECE | < 0.05 absolute change | Especially after QAT |
| Fairness metrics | No new disparities introduced | Re-run `/fairness-audit` |
| **Agentic capability** (if model is used by an agent) | < X% drop on tool-use tasks | **ACBench (Agentic Compression Benchmark)** — ICML 2025; 12 tasks × 4 capabilities × 15 models; specifically measures the agentic regressions that LongBench misses. https://github.com/pprp/ACBench |

**Test on target hardware** — GPU latency results don't predict CPU/edge results.

**Agentic-capability gate (new):** if the compressed model will be invoked by an agent (tool calls, multi-step reasoning, planning), classical NLP benchmarks (LongBench, perplexity, downstream task accuracy) under-detect the regression that matters most. Run **ACBench** as the agent-eval gate. Notable findings from the benchmark: 4-bit GPTQ/AWQ and 50% Wanda/SparseGPT pruning often LOSE agentic capability before they lose perplexity/task-accuracy, so PTQ that "looks fine" can still break tool-use chains. Test before shipping into an agent loop.

---

## Output

Deliver:
1. **Technique selection** — chosen approach with rationale + fallback
2. **Code pattern** — ready-to-run compression script for the chosen technique
3. **Eval plan** — before/after metrics checklist on target hardware
4. **Size/latency estimate** — expected reduction with typical range
