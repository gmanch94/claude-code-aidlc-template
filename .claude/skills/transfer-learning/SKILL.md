---
name: transfer-learning
description: Designs a transfer-learning strategy — source task / pre-trained model selection, fine-tuning depth decision (feature extraction vs full fine-tune vs adapter), negative-transfer detection, and evaluation plan. Use when target task has limited labeled data and a related source task / pre-trained model exists. Common in CV (ImageNet/CLIP backbones), NLP (BERT/RoBERTa/LLM), audio (Whisper/wav2vec), and tabular foundation models.
---

# /transfer-learning — Transfer Learning Design

## Role
You are a Transfer Learning Advisor.

## When transfer learning is the right call
- Target task has limited labeled data (< 10k examples for vision; < 1k for NLP classification)
- A pre-trained model or source task exists that's *related* to the target
- Compute budget can't support training from scratch

## When NOT to use transfer learning
- Target task is fundamentally different from any available source (negative transfer risk)
- You have abundant target-domain labeled data AND compute (from-scratch may match transfer)
- Source and target domains differ in input modality with no bridging encoder
- Privacy/licensing forbids pre-trained weights (check model license — many "open" weights are non-commercial)

## Behavior
1. Confirm transfer learning is appropriate (gate above)
2. Categorize the transfer scenario (transductive / inductive / unsupervised)
3. Select source model / task based on relatedness + data + compute
4. Choose adaptation strategy (feature extraction / partial fine-tune / full fine-tune / adapter / LoRA)
5. Define a baseline-comparison evaluation plan including a negative-transfer check
6. Output the design spec

## Transfer scenarios

| Scenario | Source vs target | Example | Typical approach |
|---|---|---|---|
| **Transductive transfer** | Same task, different domain | English sentiment → German sentiment | Domain-adaptive fine-tuning; multilingual model |
| **Inductive transfer** | Different but related tasks, same domain | Pre-trained BERT (MLM) → sentiment classification | Add task head, fine-tune |
| **Unsupervised transfer** | Different task, no labels in source or target | Self-supervised features → downstream classification | Use pre-trained features as input to small classifier |
| **Cross-modal** | Different modality bridged by joint encoder | CLIP (image+text) → zero-shot image classification | Use joint embedding directly |

## Source model selection criteria

| Criterion | Why it matters |
|---|---|
| **Task similarity** | Closer source task ⇒ less fine-tuning ⇒ less target data needed |
| **Domain similarity** | Closer source domain (image style, text genre, audio conditions) ⇒ smaller distribution shift |
| **Model scale** | Larger pre-trained models transfer better in low-data regimes but cost more to fine-tune and serve |
| **License** | Apache-2 / MIT permissive; CC-BY-NC / RAIL non-commercial; some restrict deployment |
| **Domain-specific pre-training available?** | BioBERT, LegalBERT, SciBERT, ClinicalBERT, FinBERT — prefer when domain matches |
| **Recency** | Pre-trained recently enough to know the operational vocabulary / visual concepts |

## Adaptation strategy decision tree

```
Target task labeled examples?
├─ < 100        → Feature extraction (freeze backbone, train classifier head only) OR few-shot prompting (LLM)
├─ 100–1k       → Feature extraction + light fine-tune of top 1–2 layers; or adapter / LoRA
├─ 1k–10k       → Partial fine-tune (unfreeze top 25–50% of layers) with low LR
├─ 10k–100k     → Full fine-tune with low LR; consider warmup; monitor catastrophic forgetting
└─ > 100k       → Full fine-tune OR train from scratch (compare; from-scratch may catch up)
```

## Adaptation strategy comparison

| Strategy | What's updated | Compute | Storage | Best for |
|---|---|---|---|---|
| **Feature extraction** | Classifier head only; backbone frozen | Lowest | One head per task; backbone shared | Very small datasets; many downstream tasks |
| **Partial fine-tune** | Top N layers + head | Medium | Full copy per task | Moderate dataset; domain shift |
| **Full fine-tune** | All weights | High | Full copy per task | Large dataset; significant task shift |
| **Adapter / LoRA / prefix-tune** | Small added modules; backbone frozen | Low | Adapter weights only (~1% of model) | Many tasks; serving many models; memory-constrained |
| **Prompting / in-context (LLM)** | Nothing (parameter-free) | Inference only | None | Very few examples; rapid iteration |

## Catastrophic forgetting (full fine-tune risk)

Aggressive fine-tuning can erase general-purpose knowledge. Mitigations:
- Lower learning rate (10x–100x lower than from-scratch training)
- Layer-wise LR decay (lower rates for early layers)
- Warmup + cosine decay schedule
- Mix in some source-task data (replay)
- Use adapter / LoRA instead — they preserve base weights by construction

## Negative transfer — mandatory check

Negative transfer = transfer-learning model performs *worse* than from-scratch baseline. Happens when source and target are insufficiently related. Detection:

| Check | How |
|---|---|
| From-scratch baseline | Train a small model from scratch on the target task; compare to transfer model |
| Frozen-features probe | Linear probe on frozen pre-trained features; if linear probe is near random, source representations don't capture target concepts |
| Layer-wise probe | Probe each layer of the source model; identify which layer (if any) contains useful target features |
| Domain-gap metric | Compute CKA / linear-CKA between source and target intermediate representations |

If negative transfer detected: try a different source model, a less-aggressive adaptation, or accept that from-scratch is the right answer.

## Evaluation plan

| Metric | Why |
|---|---|
| Task-specific metric (F1, mAP, BLEU, etc.) | Primary success criterion |
| Comparison to from-scratch baseline | Confirms transfer is helping, not hurting |
| Comparison to a simpler transfer (smaller source model) | Confirms source-model scale is justified |
| Source-task performance after fine-tune | Detects catastrophic forgetting (if source-task evaluation matters) |
| Per-subgroup performance | Pre-trained models can carry source-domain biases — see `/bias-audit` |

## Output format

```
### Transfer Learning Design: [target task]

#### Scenario
Type: [transductive / inductive / unsupervised / cross-modal]
Source: [pre-trained model name + checkpoint + license]
Target task data: [N labeled examples] | Domain: [domain] | Modality: [modality]

#### Source model selection
| Candidate | Task fit | Domain fit | Scale | License | Pick |
| ... |

#### Adaptation strategy
Strategy: [feature-extract / partial fine-tune / full fine-tune / adapter / LoRA]
Layers unfrozen: [layers]
Learning rate: [value] (vs from-scratch [comparison])
Schedule: [warmup + cosine / constant / etc.]

#### Negative-transfer check
| Check | Result |
| From-scratch baseline | [metric] |
| Linear probe on frozen features | [metric] |
| Verdict | [Transfer beats baseline / inconclusive / negative transfer] |

#### Catastrophic forgetting mitigation (if full fine-tune)
[Strategy chosen]

#### Evaluation plan
Primary metric: | Baselines: | Subgroup analysis: [yes/no — see /bias-audit]

#### Recommendations
- [Start with feature extraction; only unfreeze if performance gap remains]
- [Run negative-transfer check before celebrating fine-tune wins]
- [License review: confirm deployment is permitted]
```

## Quality bar
- A from-scratch baseline is mandatory — without it, you can't tell whether transfer is helping
- License review is part of model selection, not an afterthought — many strong checkpoints forbid commercial use
- Catastrophic forgetting risk increases with LR × unfrozen layers; default to conservative
- Adapter / LoRA should be the default for serving many task-specific models — full fine-tune produces a giant artifact per task
- Pre-trained models inherit source-domain bias — always pair with `/bias-audit` and `/fairness-audit` before deployment
- Pair with `/fine-tune` (training mechanics), `/algo-select` (when transfer is one option among several), `/model-validation` (pre-deploy gates)
