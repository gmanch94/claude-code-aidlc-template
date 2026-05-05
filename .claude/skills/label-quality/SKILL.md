---
name: label-quality
description: Designs label quality assurance — inter-annotator agreement metrics, sampling strategy, adjudication workflow, quality thresholds, and audit triggers. Use when measuring labeling quality, investigating disagreements between annotators, auditing an existing labeled dataset, or deciding whether labels are good enough to train on.
---

# /label-quality — Label Quality Assurance

## Behavior
1. Select the right IAA metric for the task type
2. Define sampling strategy for quality checks
3. Specify adjudication workflow for disagreements
4. Set quality thresholds and escalation triggers
5. Design ongoing audit cadence

## IAA metric selection

| Task type | Metric | Interpretation |
|---|---|---|
| Binary classification | Cohen's Kappa (κ) | κ < 0.60 = poor; 0.60–0.80 = moderate; ≥ 0.80 = good; ≥ 0.90 = excellent |
| Multi-class (2+ annotators) | Cohen's Kappa (κ) | Same scale |
| Multi-class (3+ annotators) | Fleiss' Kappa | Generalizes Cohen's to multiple raters |
| Ordinal / rating scale | Krippendorff's Alpha (α) | Handles missing data; α ≥ 0.80 recommended |
| Span / sequence labeling (NER) | Span F1 or token-level F1 | Agreement on both label AND span boundary |
| Ranking / preference | Kendall's Tau | Measures rank correlation between annotators |

## Sampling strategy

Not every example needs double annotation — sample strategically:

| Sample type | Rate | Purpose |
|---|---|---|
| Random spot check | 5–10% of all labels | Baseline quality distribution |
| New annotator ramp | 100% of first 200 examples | Calibration during onboarding |
| Low-confidence model predictions | 100% of bottom 10% confidence | Find systematic errors |
| Class-stratified | Proportional per class | Ensure minority classes are covered |
| Edge case catalog examples | 100% | Verify guidelines are being followed |

## Adjudication workflow

```
Disagreement detected →
  Severity?
    Minor (adjacent labels, boundary case) → Majority vote if ≥ 3 annotators; else senior review
    Major (opposite labels)               → Expert adjudicator required
    Systematic (same annotator wrong repeatedly) → Annotator retraining or removal

Adjudication record:
  - Example ID
  - Annotator labels
  - Final label
  - Adjudicator
  - Rule used or guideline updated
```

Every adjudication that updates a guideline must be propagated back to annotation instructions.

## Quality thresholds

| Metric | Action |
|---|---|
| κ ≥ 0.80 | Production-ready — proceed with single annotation + spot checks |
| κ 0.60–0.79 | Acceptable — increase double-annotation rate to 20%; review edge cases |
| κ 0.40–0.59 | Marginal — pause labeling; review guidelines; re-calibrate |
| κ < 0.40 | Halt — task definition is unclear; redesign with `/annotation-design` |

## Ongoing audit cadence

| Cycle | Frequency | Action |
|---|---|---|
| Spot check | Weekly | Random 5% sample → IAA score → flag if drops > 0.05 |
| Annotator review | Monthly | Per-annotator agreement vs. gold set; flag outliers |
| Dataset audit | Quarterly | Full label distribution check; class drift; systematic error scan |
| Gold set refresh | Quarterly | Add new edge cases discovered in production |

## Output format

```
### Label Quality Report: [dataset / task]

#### IAA scores
| Annotator pair / set | Metric | Score | Status |

#### Disagreement analysis
| Pattern | Count | Root cause | Guideline update needed? |

#### Quality verdict
Overall: Production-ready / Acceptable / Marginal / Halt
Action: [specific next step]

#### Audit schedule
[cadence + owner per cycle]
```

## Quality bar
- IAA below 0.60 means the task definition is broken — do not train on labels with κ < 0.60
- Per-annotator agreement tracking catches individual drift before it contaminates the dataset
- Gold set examples must include the edge cases from the edge case catalog — easy examples don't test anything
- Pair with `/annotation-design` to fix guideline gaps and `/feedback-loop` to route production disagreements back into the quality pipeline
