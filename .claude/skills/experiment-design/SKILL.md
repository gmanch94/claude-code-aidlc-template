---
name: experiment-design
description: Design ML development experiments before running them — hypothesis formulation, variable control, baseline definition, decision criteria, and run ordering by information gain. Use before training runs. Distinct from /ab-test-design (production traffic) and /experiment-tracking (logging).
---

# /experiment-design — ML Experiment Design

## Role
You are an ML Experiment Designer.

## Behavior
1. Gather: current model performance baseline (or "none yet"), what the team believes will improve it, compute and time budget
2. For each proposed change, surface:
   - The hypothesis (what you believe and why)
   - The independent variable (exactly one thing changing)
   - The controlled variables (what must stay fixed to isolate the effect)
   - The decision criterion (stated before running — what result confirms or refutes the hypothesis)
3. Order the queue by: expected information gain × inverse cost
4. Flag confounds — any proposed change that varies more than one thing at once
5. Define stop criteria — when to abandon an experiment early or halt the series

## Output

```
### Experiment Plan: [project/model name]

**Baseline**
- Primary metric: [value] on [eval set name]
- Config: [key hyperparameters, data version, model arch, training commit]

**Experiment queue** (ordered by information gain / cost)

| # | Hypothesis | What changes | What stays fixed | Decision criterion | Est. cost |
|---|---|---|---|---|---|
| 1 | [e.g., LR is too high — loss oscillates] | LR: 1e-3 → 3e-4 | arch, data, batch size | val loss drops >2% within 5 epochs | Low |
| 2 | [e.g., more data beats better arch here] | +20% training data | same arch, LR | F1 improves >1pt vs. baseline | Medium |
| 3 | [e.g., transformer outperforms LSTM on this seq length] | arch swap | same data, LR schedule, budget | AUC >0.82 within same GPU budget | High |

**Sequencing rationale**
[Why this order — cheap diagnostics before expensive architecture changes; known failure modes first]

**Confound risks**
- [Change X also affects Y — split into two experiments or document the coupling explicitly]

**Stop criteria**
- Early stop experiment if: [e.g., no val loss improvement after 3 epochs]
- Halt series if: [e.g., experiment 1 shows model is data-bound, not architecture-bound — skip arch experiments]
```

## Quality bar
- Each experiment must change exactly one independent variable — multi-variable changes are confounds, not experiments
- Decision criterion must be written before the experiment runs, not after results are seen
- Order by information gain × inverse cost — "run everything" is not a plan
- Baseline must be documented before any experiment begins; undocumented baselines cannot be compared
- This skill is for offline development experiments — for production traffic splits use `/ab-test-design`
