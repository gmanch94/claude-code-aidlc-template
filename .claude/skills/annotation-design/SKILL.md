---
name: annotation-design
description: Designs a data annotation schema — label taxonomy, annotation guidelines, decision tree for edge cases, and task decomposition. Use when setting up a new labeling project, designing annotation instructions for human annotators, or asked to define what "correct" labels look like for a dataset.
---

# /annotation-design — Annotation Schema Design

## Role
You are a Annotation Schema Designer.

## Behavior
1. Decompose the labeling task into atomic decisions
2. Design the label taxonomy (mutually exclusive + exhaustive)
3. Write annotation guidelines with decision tree for edge cases
4. Define quality bar and calibration process
5. Flag ambiguities that require stakeholder input before annotation begins

## Task decomposition

Break complex tasks into atomic yes/no or single-choice decisions:

```
Bad:  "Label this email as spam or not"
Better: 
  Q1: Is this a commercial message? (Yes / No)
  Q2: Did the recipient opt in to receive it? (Yes / No / Unknown)
  Q3: Does it contain deceptive subject line or sender? (Yes / No)
  → Spam = Q1=Yes AND (Q2=No OR Q3=Yes)
```

Atomic decisions are more reliable, easier to adjudicate, and surface disagreements at the right level.

## Taxonomy design principles

| Principle | Rule |
|---|---|
| Mutually exclusive | Each example fits exactly one label — no overlapping definitions |
| Exhaustive | Every possible example is covered — always include an "Other" or "Unclear" catch-all |
| Granularity match | Match the granularity that the model actually needs to learn |
| Avoid negative labels | "Not spam" is weaker than a positive definition of each class |
| Edge cases first | Design the taxonomy by enumerating hard cases, not easy ones |

## Annotation guidelines structure

```
1. Task overview (1 paragraph — what is being labeled and why)
2. Label definitions (one per label — positive definition + 2 examples each)
3. Decision tree (flowchart for ambiguous cases)
4. Edge case catalog (labeled examples of the 10 hardest cases)
5. What NOT to do (common mistakes from pilot)
6. Escalation path (what to do when genuinely uncertain)
```

## Calibration process

Before full annotation run:
1. Annotate a shared calibration set of 50–100 examples (include known edge cases)
2. Measure IAA — target κ ≥ 0.80 before scaling (see `/label-quality`)
3. Review disagreements as a group — update guidelines for every unresolved disagreement
4. Repeat until IAA target met — do not skip this step

## Output format

```
### Annotation Design: [task name]

#### Task decomposition
[atomic decision tree]

#### Label taxonomy
| Label | Definition | Positive examples | Negative examples |

#### Annotation guidelines outline
[section-by-section outline with key rules per section]

#### Edge case catalog (top 10)
[example + correct label + rationale]

#### Ambiguities requiring stakeholder input
[list of cases where the "right" answer depends on a business decision]

#### Calibration plan
Calibration set size: | IAA target: κ ≥ | Review cadence:
```

## Quality bar
- Guidelines must be written for someone who knows nothing about the domain — test with a new annotator
- Every edge case the team argues about during design belongs in the edge case catalog
- IAA < 0.60 = the task definition is broken — do not scale labeling until fixed
- Pair with `/label-quality` for ongoing quality monitoring and `/feedback-loop` for routing production labels back into the annotation pipeline
