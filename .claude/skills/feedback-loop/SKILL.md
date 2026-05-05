---
name: feedback-loop
description: Designs the production feedback loop for an AI system — signal collection, human review queue, annotation workflow, and how captured signals feed back into evals and prompt improvement. Use when designing or auditing a deployed AI system's continuous improvement mechanism, or when asked how to collect feedback, set up annotation, or improve a model over time.
---

# /feedback-loop — AI Feedback Loop Design

## Behavior
1. Map current signal sources (explicit, implicit, human review, downstream outcome)
2. Design the collection pipeline
3. Define annotation workflow and quality bar
4. Specify how signals route into evals and prompt iteration
5. Set improvement cycle cadence

## Signal taxonomy

| Signal type | Examples | Collection method | Reliability |
|---|---|---|---|
| Explicit positive | Thumbs up, copy, share | UI event | High |
| Explicit negative | Thumbs down, edit, retry | UI event | High |
| Implicit positive | Session continues, task completes | Behavioral | Medium |
| Implicit negative | Session abandons, fallback triggered | Behavioral | Medium |
| Human review | Annotation, QA pass/fail | Review queue | High |
| Downstream outcome | Task success, conversion, ticket closed | Business metric | Highest |

## Review queue design

Not everything needs human review — sample strategically:

| Sample type | Rate | What it catches |
|---|---|---|
| Random | 1–5% of traffic | Baseline quality distribution |
| Triggered | All refusals + all negative feedback | Known failure modes |
| Adversarial | Red team inputs, edge cases | Safety + robustness gaps |
| Stratified | Proportional across use cases / user types | Coverage of all segments |

**Queue tiers:**
1. **Fast (< 1 day):** Safety incidents, hallucination flags, PII leaks → immediate action
2. **Standard (weekly):** Quality issues, edge cases → prompt iteration backlog
3. **Trend (monthly):** Distribution shift, emerging patterns → eval dataset update

## Annotation schema

```
Input: [production prompt + output]
Fields:
  - Correct? Yes / No / Partial
  - Failure mode: Hallucination | Refusal | Format | Tone | Incomplete | Other
  - Severity: Critical | Major | Minor
  - Gold label: [correct output — use for few-shot / fine-tune]
```

Quality bar: ≥ 2 annotators on Critical/Major items; adjudicate when disagreement > 10%.

## Signal → improvement routing

```
Negative signal → Aggregate weekly → Route by pattern:
  Reproducible in eval? → Add to eval dataset (priority)
  Prompt fixable?       → Prompt iteration (fast path, days)
  Systematic gap?       → Fine-tune candidate (see /fine-tune)
  Data quality issue?   → RAG corpus update (see /rag-design)
```

## Cadence

| Cycle | Frequency | Output |
|---|---|---|
| Live monitoring | Continuous | Alert if thresholds breached (see /observability) |
| Quality review | Weekly | Prompt iteration backlog |
| Eval dataset update | Monthly | New cases from production signals |
| Prompt version review | Monthly or on 5% score drop | Prompt changelog entry |
| Fine-tune assessment | Quarterly | Go/no-go via /fine-tune |

## Output format

```
### Feedback Loop Design: [system]

#### Signal map
[table: signal type → collection method → volume estimate]

#### Review queue spec
[sampling rates + tier definitions + owner per tier]

#### Annotation schema
[fields + severity rubric + inter-annotator agreement target]

#### Improvement routing
[signal type → action → owner → SLA]

#### Cadence
[table: cycle → frequency → owner → output]

#### Gaps
[missing signals, tooling not in place, annotation capacity needed]
```

## Quality bar
- Downstream outcome signals outweigh thumbs — design for both, weight the former
- If no human review capacity: auto-route all negative feedback to eval dataset
- Gold labels from annotation feed directly into the eval dataset — design for this from day one
- PII in feedback logs is a compliance risk — define retention policy for all signal types
