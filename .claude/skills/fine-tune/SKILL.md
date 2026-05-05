---
name: fine-tune
description: Determines whether to fine-tune vs. prompt-engineer, and if fine-tuning is justified, produces dataset requirements, training data format, pre/post eval plan, and cost-benefit analysis. Use when asked whether to fine-tune a model, how to prepare training data, or when a prompt-engineering approach has hit a quality ceiling.
---

# /fine-tune — Fine-Tune vs. Prompt Decision

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
- See REFERENCE.md for training data format, cost estimates, and fine-tune vs. alternatives matrix
