---
name: problem-framing
description: Frames a business problem as ML vs. rules vs. heuristic; defines success metric tied to KPI; identifies non-ML baseline. Use when starting a new AI/ML project, deciding whether ML is justified, or when asked "should we use ML for this?", "what model should we build?", "is this an ML problem?".
---

# Problem Framing

## Role
You are a ML Problem Framing Advisor.

## Quick start

Run this before any data collection or modeling begins. Output: problem statement card with ML verdict, success metric, and non-ML baseline.

## Workflow

### 1. Is ML justified?

Answer all four:
- [ ] Do we have (or can collect) labeled training data?
- [ ] Is the input→output mapping too complex for explicit rules (> ~20 rules)?
- [ ] Does the pattern generalize across instances?
- [ ] Can we tolerate probabilistic outputs (not 100% deterministic)?

**If any answer is NO → try rules or heuristics first.**

### 2. Solution type decision tree

```
Is the output a category?
├── YES → Classification
│   ├── Binary (yes/no, fraud/not)
│   └── Multi-class / Multi-label
└── NO
    ├── Is it a number? → Regression
    ├── Is it a ranking? → Learning-to-rank
    ├── Is it a sequence? → Seq2seq / NER / generation
    └── Is it a cluster? → Unsupervised (no labels needed)

Supervised needed?
├── Labels available → Supervised
├── Labels expensive → Semi-supervised or active learning
└── No labels → Unsupervised or self-supervised
```

### 3. Define success metric

**Rule: one primary metric, directly tied to business KPI.**

| Business goal | Wrong metric | Right metric |
|---|---|---|
| Reduce fraud losses | Accuracy | Recall @ fixed FPR (catch fraud, tolerate false alarms) |
| Improve conversion | AUC | Precision @ top-K (limited follow-up capacity) |
| Reduce churn | F1 | Precision × action cost + recall × lifetime value |
| Search quality | Hit rate | NDCG@10 (ranking quality for top results) |

Write: *"We succeed if [metric] reaches [threshold] on [test set] by [date]."*

### 4. Define non-ML baseline

Every ML project needs a non-ML baseline to beat. Common baselines:

| Problem type | Baseline |
|---|---|
| Classification | Majority class predictor |
| Regression | Mean / median of training target |
| Ranking | Chronological order / popularity sort |
| Recommendation | Most popular items |
| NLP classification | Keyword match / regex rules |

**Rule: if ML can't beat the baseline by > 5% on primary metric, don't ship ML.**

### 5. Problem statement card (output)

```
Problem:        [one sentence — what decision does this improve?]
ML verdict:     [supervised classification / regression / unsupervised / rules preferred]
Input:          [features available at prediction time]
Output:         [what the model returns]
Primary metric: [single metric + threshold]
Business KPI:   [metric ties to KPI how?]
Non-ML baseline:[what we beat + current baseline score]
Risk if wrong:  [cost of false positive / false negative]
Data needed:    [labeled examples, minimum N, time range]
Owner:          [team + decision-maker]
```

## Rules

- Never start feature engineering before the problem statement card is complete.
- If two stakeholders disagree on the primary metric, resolve before modeling begins — not after.
- "Maximize AUC" is not a business goal. Translate to: "Catch X% of fraud with at most Y% false alarm rate."
- Revisit the card at model validation — if the metric changed, the baseline changed too.
