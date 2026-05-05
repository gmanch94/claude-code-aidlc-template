---
name: model-calibration
description: Check and fix probability calibration for ML classifiers. Use when predicted probabilities are used for ranking, thresholding, or downstream decisions — not just hard class labels.
---

# Model Calibration

## Role
You are a Model Calibration Specialist.

## When calibration matters

Calibration is required when:
- Probabilities drive a business decision (risk score, pricing, ranking)
- A threshold other than 0.5 is used
- Probabilities are combined across models
- Confidence is displayed to end users

Calibration is NOT required when:
- Only the predicted class (argmax) is used
- AUC / ranking quality is the only metric that matters

## What is calibration?

A well-calibrated model: among all predictions of 0.70, ~70% should actually be positive.

```python
# Reliability diagram (calibration curve)
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

fraction_pos, mean_pred = calibration_curve(y_test, y_prob, n_bins=10)
plt.plot(mean_pred, fraction_pos, "s-", label="model")
plt.plot([0,1], [0,1], "k--", label="perfect")
plt.xlabel("Mean predicted probability")
plt.ylabel("Fraction of positives")
```

## Expected Calibration Error (ECE)

```python
def expected_calibration_error(y_true, y_prob, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i+1])
        if mask.sum() == 0:
            continue
        acc = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += mask.sum() / len(y_true) * abs(acc - conf)
    return ece

ece = expected_calibration_error(y_test, y_prob)
print(f"ECE: {ece:.4f}")
# ECE < 0.05 = well-calibrated; > 0.10 = recalibrate
```

## Calibration check by model type

| Model | Typical calibration | Action |
|---|---|---|
| Logistic regression | Usually well-calibrated | Verify; rarely needs fix |
| Random forest | Overconfident (probabilities near 0/1) | Calibrate |
| Gradient boosting (XGBoost/LGB) | Overconfident | Calibrate |
| SVM | Poorly calibrated | Always calibrate |
| Neural net (with softmax) | Often overconfident | Check; calibrate if ECE > 0.05 |
| Naive Bayes | Underconfident | Calibrate |

## Calibration methods

```python
from sklearn.calibration import CalibratedClassifierCV

# Platt scaling — sigmoid fit; good for small calibration sets
calibrated = CalibratedClassifierCV(base_model, method="sigmoid", cv="prefit")
calibrated.fit(X_cal, y_cal)   # dedicated calibration set (10–20% of train)

# Isotonic regression — non-parametric; needs larger calibration set (> 1K)
calibrated = CalibratedClassifierCV(base_model, method="isotonic", cv="prefit")
calibrated.fit(X_cal, y_cal)
```

**Rule:** calibration set must be separate from both training and test sets. Fit calibrator on cal set; evaluate on test set. Never calibrate on test.

```
Data split for calibration:
  60% train → fit base model
  20% cal   → fit calibrator (Platt or isotonic)
  20% test  → evaluate calibrated model
```

## Post-calibration validation

```python
ece_before = expected_calibration_error(y_test, y_prob_raw)
ece_after  = expected_calibration_error(y_test, y_prob_calibrated)
print(f"ECE before: {ece_before:.4f}  after: {ece_after:.4f}")

# Also check: AUC should not drop significantly (calibration shouldn't hurt ranking)
auc_before = roc_auc_score(y_test, y_prob_raw)
auc_after  = roc_auc_score(y_test, y_prob_calibrated)
print(f"AUC before: {auc_before:.4f}  after: {auc_after:.4f}")
# Acceptable AUC drop from calibration: < 0.005
```

## Temperature scaling (neural nets)

```python
# Post-hoc calibration without retraining — scales logits by learned temperature T
# T > 1 = soften probabilities (reduce overconfidence)
# T < 1 = sharpen probabilities
# Fit T on validation set by minimizing NLL
```

## Failure modes

- Calibrating on the test set: data leakage; use a dedicated calibration set
- Using isotonic regression on small calibration sets (< 500): overfits; use Platt scaling
- Calibrating without checking AUC: calibration can hurt ranking quality if done wrong
- Skipping calibration for threshold-based decisions: wrong threshold → wrong business outcome

Pair with `/model-validation` for the full pre-deploy checklist and `/eval-design` for threshold optimization.
