---
name: explainability
description: ML model explainability — SHAP global/local explanations, LIME, partial dependence plots, counterfactuals, method selection by model type and audience. Use when asked about "model explainability", "why did the model predict X?", "feature importance", "SHAP", "LIME", "black box", "model interpretability", regulatory explanation requirements, or debugging model behavior.
---

# Model Explainability

## Role
You are a Model Explainability Analyst.

## Quick start

Choose method by model type and explanation goal. Global = understand the model. Local = explain one prediction.

## Method selection

| Model type | Global explanation | Local explanation |
|---|---|---|
| Tree-based (GBM, RF) | SHAP TreeExplainer (fast, exact) | SHAP force plot / waterfall |
| Linear / logistic | Coefficients + odds ratios | Coefficients × feature value |
| Neural network | SHAP DeepExplainer / GradientExplainer | LIME or integrated gradients |
| Any black box | SHAP KernelExplainer (slow) | LIME |
| Simple interpretable | Inherently interpretable (no post-hoc needed) | Inherently interpretable |

**Rule: inherently interpretable model (logistic regression, shallow decision tree) beats post-hoc explanation every time — only use post-hoc when model performance requires a complex model.**

## Workflow

### 1. Global SHAP (feature importance + direction)

```python
import shap

# For tree models
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)  # use train or representative sample

# Summary plot — global importance + direction
shap.summary_plot(shap_values, X_train, plot_type="bar")  # importance only
shap.summary_plot(shap_values, X_train)                   # importance + direction (beeswarm)
```

Output: ranked feature list with direction (high value → increases/decreases prediction).

### 2. Local SHAP (single prediction explanation)

```python
# Waterfall plot — one prediction
shap.plots.waterfall(explainer(X_test)[instance_idx])

# Force plot — interactive
shap.force_plot(explainer.expected_value, shap_values[instance_idx], X_test.iloc[instance_idx])
```

For multi-class: `shap_values` is a list (one array per class); index by predicted class.

### 3. SHAP interaction effects

```python
# Does feature A change its effect depending on feature B?
shap_interaction = explainer.shap_interaction_values(X_sample)
shap.summary_plot(shap_interaction, X_sample, max_display=10)
```

### 4. Partial dependence plot (marginal effect of one feature)

```python
from sklearn.inspection import PartialDependenceDisplay
PartialDependenceDisplay.from_estimator(model, X_train, features=["age", "income"])
```

PDP shows average effect; SHAP shows actual effect per instance. Use PDP for communication, SHAP for debugging.

### 5. LIME (model-agnostic local explanation)

```python
import lime.lime_tabular

explainer = lime.lime_tabular.LimeTabularExplainer(
    X_train.values,
    feature_names=X_train.columns.tolist(),
    class_names=["neg", "pos"],
    mode="classification"
)
exp = explainer.explain_instance(X_test.iloc[instance_idx].values, model.predict_proba, num_features=10)
exp.show_in_notebook()
```

Use LIME when: model is not tree-based and SHAP KernelExplainer is too slow; for quick local checks.

### 6. Counterfactual explanation ("what would need to change?")

```python
# DiCE library
import dice_ml

data_model = dice_ml.Data(dataframe=df_train, continuous_features=cont_cols, outcome_name=target)
ml_model = dice_ml.Model(model=model, backend="sklearn")
exp = dice_ml.Dice(data_model, ml_model, method="random")

cf = exp.generate_counterfactuals(
    query_instances=X_test.iloc[[instance_idx]],
    total_CFs=3,
    desired_class="opposite"
)
cf.visualize_as_dataframe()
```

Counterfactuals answer: "If your income were $X higher and debt ratio were Y lower, the decision would flip." Required for GDPR Article 22 adverse decision explanations.

### 7. Explanation audience guide

| Audience | Method | Depth |
|---|---|---|
| Model developer debugging | SHAP beeswarm + interaction values | Full technical |
| Business stakeholder | Top-5 features + direction + PDP for key features | Summary |
| Affected individual | Counterfactual (actionable) | Single instance |
| Regulator / auditor | SHAP global + slice-level + methodology doc | Full + documented |

### 8. Explainability report (output)

```
Model:              [name + version]
Method used:        [TreeExplainer / KernelExplainer / LIME + rationale]
Top 5 features:     [name, mean |SHAP|, direction]
Key findings:
  - [Feature X has strong positive effect above threshold Y]
  - [Interaction: feature A and B jointly drive Z% of predictions]
  - [Potential proxy: feature C correlates with protected attribute D]
Counterfactual available: [YES / NO — reason]
Audience artifacts:  [global plot, local plot, counterfactual example]
Anomalies:          [any surprising driver that warrants investigation]
```

## Rules

- SHAP values are additive and sum to (prediction − base rate). Verify: `shap_values.sum(axis=1) ≈ model.predict_proba(X)[:,1] − base_rate`.
- Never explain on the full dataset — use a representative sample (1K–5K rows) for KernelExplainer; TreeExplainer can handle full train set.
- Explanations from post-hoc methods are approximations, not ground truth. State this when sharing with regulators.
- If a proxy feature (e.g., zip code) appears in top-5 SHAP drivers, escalate to fairness-audit immediately.
- Counterfactuals must be actionable for affected individuals — "be younger" is not actionable; "reduce debt-to-income ratio to 0.35" is.
