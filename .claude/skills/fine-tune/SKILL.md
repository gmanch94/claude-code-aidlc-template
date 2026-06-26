---
name: fine-tune
description: Determines whether to fine-tune vs. prompt-engineer, and if fine-tuning is justified, produces dataset requirements, training data format, pre/post eval plan, and cost-benefit analysis. Use when asked whether to fine-tune a model, how to prepare training data, or when a prompt-engineering approach has hit a quality ceiling.
---

# /fine-tune — Fine-Tune vs. Prompt Decision

## Role
You are a Fine-Tuning Advisor.

## Behavior
1. Apply the fine-tune vs. prompt decision tree
2. If fine-tuning justified: specify dataset requirements
3. Define pre/post eval plan
4. Estimate cost-benefit
5. Output go/no-go recommendation with rationale

## Decision tree

```
Can few-shot examples in the prompt achieve target quality?
  Yes → Prompt engineer first. Fine-tune adds cost + maintenance overhead.
  No  → Is the gap in knowledge (facts) or behavior (style/format/task)?
          Knowledge gap → RAG or grounding, not fine-tune (see /rag-design)
          Behavior gap  → How many consistent gold examples exist?
                            < 100  → Collect more data; prompt engineer meanwhile
                            100–1K → Fine-tune candidate (validate with eval first)
                            > 1K   → Fine-tune justified
```

## When NOT to fine-tune

| Situation | Better alternative |
|---|---|
| Model lacks recent facts | RAG + grounding |
| Single use case, few examples | Few-shot prompting |
| Reducing hallucinations | Grounding + retrieval |
| Cost reduction is the only goal | Tier down to Haiku/Sonnet (see /cost-optimize) |
| No eval exists yet | Build eval first — can't measure improvement otherwise |

## Fine-tune approach selection (2026 menu)

| Approach | When | Notes |
|---|---|---|
| **SFT (Supervised Fine-Tuning)** | Labeled completions exist (≥100 high-quality examples); style / format / task adherence is the gap | Cheapest; default starting point. Available on OpenAI, Anthropic, Together, Modal, SageMaker, Bedrock Custom Model Import, Vertex |
| **DPO (Direct Preference Optimization)** | Preference pairs exist (chosen vs rejected response); behavior should be steered without explicit "right answer" | Newer; lower data requirement than RLHF; available on OpenAI, Together, custom (TRL library) |
| **RFT (Reinforcement Fine-Tuning)** | Reasoning models (o3 / o4-mini); programmable grader scores responses and model learns to maximize | **OpenAI-specific** (RFT for o-series reasoning models); most flexible but most complex. See `/openai-platform-design` |
| **GRPO / online RL (RLVR)** | A verifiable or rubric-scored reward exists; reasoning / agentic tasks; you want OOD generalization, not just imitation of gold completions | Group-relative policy optimization — the open-weights RL path (DeepSeek, GLM). More compute + infra than SFT/DPO. **Off-policy variants (e.g. OAPL) tolerate trainer↔inference-engine skew without GRPO stabilization heuristics.** Reward design + RL mechanics defer to `/rl-design`; reward-gaming guard to `/metric-gaming-audit` |

## Distillation workflow

```
Stored Completions (capture from production)
    →
Evals (compare candidate small models against teacher)
    →
SFT or DPO on smaller model
    →
Deploy distilled model at lower cost / latency
```

**Caveat (2026):** OpenAI's distillation workflow tightly couples Stored Completions → **Evals** → fine-tune. **OpenAI Evals: read-only 2026-10-31, shutdown 2026-11-30.** Distillation pipelines that depend on Evals also break. Plan replacement for BOTH the eval stage AND the distillation stage in the same migration. Replacements: **Promptfoo** (OpenAI's own named target), Braintrust, Langfuse, Agents SDK tracing — see `/eval-design`.

**OOD-generalization caveat:** when out-of-distribution generalization matters, prefer **one multi-task fine-tune over a stack of per-task experts you then distill**. Distillation teaches the model to imitate task-specific expert behavior — it scales within the training distribution but does not generalize beyond it; multi-task RL develops more general capability (KARL / OAPL multi-task-RL-vs-multi-expert-distillation finding, Databricks 2026). Balance training tokens roughly equally across tasks.

## Managed fine-tune cost benchmarks (2026)

| Provider | Approach | Cost floor |
|---|---|---|
| **Together AI** | LoRA on Llama 70B | **$14 per M training tokens**; hosted at base-model pricing |
| **Modal** | Self-managed GPU + bring-your-own-script | Hourly GPU rental; bVisor sandbox isolation (post-Butter acquisition Apr 2026) |
| **SageMaker** | Managed training jobs + Custom Model Import | Per-hour ml instance; managed-spot reduces 50-70% |
| **OpenAI fine-tune** | SFT / DPO / RFT on GPT family | Per-token training + per-token inference uplift |
| **Bedrock Custom Model Import** | Upload your own weights (incl. fine-tuned Llama / Mistral / DeepSeek) | Per-second invocation at standard Bedrock pricing |
| **Vertex AI** | Managed fine-tune on Gemini family + AutoML | Per-token training |

## Dataset requirements

| Dimension | Minimum | Target |
|---|---|---|
| Total examples | 100 | 500–1K+ |
| Format consistency | Required | Required |
| Annotator agreement (on Critical) | ≥ 2 reviewers | ≥ 2 + adjudication |
| Distribution coverage | All use case variants | Stratified sampling |
| Negative examples | Optional | 10–20% of set |
| Held-out eval set | 10% isolated before training | 15–20% |

## Pre/post eval plan

1. **Baseline eval** — run current prompt on held-out set; record scores
2. **Fine-tune** — train on curated dataset (held-out set never included)
3. **Post eval** — same eval on fine-tuned model; compare to baseline
4. **Regression check** — test on out-of-distribution inputs (fine-tune narrows behavior)
5. **Gate** — require > X% improvement on target metric; no regression > Y% on adjacent tasks

## Output format

```
### Fine-Tune Assessment: [task / model]

#### Decision
Go / No-Go / Defer — [specific reason]

#### If Go:
Dataset requirements
| Dimension | Minimum | Target | Current state |

Pre/post eval plan
[metrics, thresholds, regression checks]

Cost-benefit
| Item | Estimate |
| Dataset curation | N hrs × $rate |
| Training cost | $X |
| Ongoing inference delta | ±$Y/mo |
| Break-even | Z months |

#### If No-Go:
Alternative: [prompt engineering / RAG / model tier / data collection]
Revisit when: [condition that changes this decision]
```

## Quality bar
- Build the eval before collecting training data — measure first, then improve
- Fine-tune narrows generalization — always regression-test out-of-distribution inputs
- Dataset curation is the bottleneck, not compute — budget more time for data than training
- Gold labels from the annotation pipeline (see /feedback-loop) are the best training data source
- **Pick SFT / DPO / RFT explicitly** — defaulting to SFT when DPO or RFT would fit is the most common silent mistake in 2026 fine-tune projects
- **If your distillation workflow uses OpenAI Evals**, plan the replacement before 2026-11-30 — Evals shutdown breaks the pipeline at the eval stage
- See REFERENCE.md for training data format, cost estimates, and fine-tune vs. alternatives matrix
