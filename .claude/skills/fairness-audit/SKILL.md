---
name: fairness-audit
description: ML fairness audit — demographic parity, equal opportunity, disparate impact ratio, protected-attribute slice analysis, mitigation strategies. Use when asked about "model fairness", "bias audit", "disparate impact", "discrimination", "protected attributes", or before deploying any model that affects people (lending, hiring, healthcare, criminal justice, content moderation).
---

# Fairness Audit

## Role
You are a AI Fairness Auditor.

## Quick start

Identify protected attributes → compute group metrics → check thresholds → select mitigation if needed.

## Workflow

### 1. Identify protected attributes

Legally protected (jurisdiction-dependent): race, sex/gender, age (≥ 40 in US), religion, national origin, disability, pregnancy, marital status.

Proxy risk: zip code, name, school attended, browsing history — can encode protected attributes even if excluded.

**Document which attributes are in the data, which are excluded, and which proxies may exist.**

### 2. Compute group metrics

For each protected attribute group pair (e.g., Group A vs. Group B):

**Classification:**
```python
from sklearn.metrics import confusion_matrix

def group_metrics(y_true, y_pred, y_prob, group_mask):
    tn, fp, fn, tp = confusion_matrix(y_true[group_mask], y_pred[group_mask]).ravel()
    return {
        "positive_rate":    (tp + fp) / len(y_true[group_mask]),
        "tpr":              tp / (tp + fn),   # recall / equal opportunity
        "fpr":              fp / (fp + tn),
        "ppv":              tp / (tp + fp),   # precision
        "auc":              roc_auc_score(y_true[group_mask], y_prob[group_mask])
    }
```

**Regression:** compute mean prediction and RMSE per group.

### 3. Fairness metrics

| Metric | Formula | Threshold | What it checks |
|---|---|---|---|
| Demographic parity difference | P(ŷ=1\|A) − P(ŷ=1\|B) | ≤ 0.05 | Equal positive rate across groups |
| Disparate impact ratio | P(ŷ=1\|B) / P(ŷ=1\|A) | ≥ 0.80 | 80% rule (US EEOC standard) |
| Equal opportunity difference | TPR_A − TPR_B | ≤ 0.05 | Equal benefit for qualified individuals |
| Predictive parity difference | PPV_A − PPV_B | ≤ 0.05 | Equal reliability of positive predictions |
| Calibration difference | ECE_A − ECE_B | ≤ 0.02 | Equal probability accuracy |

**Note: you cannot satisfy all metrics simultaneously (Chouldechova's impossibility theorem) — choose the metric aligned to the harm you most want to avoid.**

### 4. Fairness–accuracy trade-off decision

| Use case | Priority metric | Rationale |
|---|---|---|
| Lending / credit | Equal opportunity | False negatives harm qualified applicants |
| Hiring | Demographic parity | Structural barriers require representation equity |
| Recidivism / bail | Equal FPR | False positives = wrongful detention |
| Healthcare triage | Calibration | Equal reliability matters across groups |
| Content moderation | Equal FPR | False positives = disproportionate suppression |

### 5. Mitigation strategies

**Pre-processing (adjust data):**
- Reweigh training samples (assign higher weight to underrepresented group)
- Resampling to balance group representation
- Remove proxy features (validate with correlation check post-removal)

**In-processing (adjust training):**
- Add fairness constraint to loss function (e.g., adversarial debiasing)
- Use fairness-aware algorithms (FairLearn, AIF360)

**Post-processing (adjust predictions):**
- Threshold shifting per group to equalize TPR or FPR
```python
# Equalize TPR across groups via threshold adjustment
thresholds = {}
for group in groups:
    mask = X_test[protected_col] == group
    thresholds[group] = find_threshold_for_tpr(y_true[mask], y_prob[mask], target_tpr)
```

**Rule: document chosen mitigation + accepted accuracy trade-off. Never silently apply post-processing thresholds in production without disclosure.**

### 6. Fairness audit report (output)

```
Model:              [name + version]
Protected attrs:    [list + proxy risk flags]
Dataset:            [N rows, group sizes + representation %]

Metric summary:
  Demographic parity difference:  [value] [PASS/FAIL vs. 0.05]
  Disparate impact ratio:         [value] [PASS/FAIL vs. 0.80]
  Equal opportunity difference:   [value] [PASS/FAIL vs. 0.05]
  Predictive parity difference:   [value] [PASS/FAIL vs. 0.05]

Worst disparity:    [group pair + metric + magnitude]
Root cause:         [data imbalance / proxy feature / label bias / structural]
Mitigation applied: [none / reweighing / threshold shift + impact on accuracy]
Residual risk:      [what remains after mitigation]
Recommendation:     [GO / NO-GO / CONDITIONAL (with conditions)]
Reviewer:           [name + date]
```

## Rules

- Fairness audit is mandatory before any model that affects access to credit, employment, housing, healthcare, or criminal justice.
- Never remove protected attributes without checking proxies — exclusion alone doesn't remove bias.
- "We didn't measure it" is not the same as "it doesn't exist."
- Fairness metrics on test set only; never tune thresholds to pass on validation.
- Disparate impact ratio < 0.80 → legal risk; flag for legal review regardless of model team decision.
