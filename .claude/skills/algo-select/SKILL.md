---
name: algo-select
description: Select the right ML algorithm for a task. Use when choosing between algorithms, asking "which model should I use", or starting a new ML project with unknown algorithm.
---

# Algorithm Selection

## Quick start

Tell me: task type + dataset size + constraints (latency, interpretability, training time).

## Decision tree

```
What is the task?
├── Classification
│   ├── Tabular data
│   │   ├── < 1K rows           → Logistic regression or SVM
│   │   ├── 1K–100K rows        → Gradient boosting (XGBoost/LightGBM) — default choice
│   │   └── > 100K rows         → LightGBM or neural net if structured patterns complex
│   ├── Text                    → Fine-tuned transformer (BERT family) or TF-IDF + LR baseline
│   └── Image                   → CNN (ResNet/EfficientNet) or fine-tune vision transformer
├── Regression
│   ├── Tabular                 → Gradient boosting first; linear regression if interpretability required
│   ├── Time series             → ARIMA/SARIMA for univariate; LightGBM with lag features for multivariate
│   └── Spatial                 → Kriging or GNN
├── Clustering
│   ├── Known k                 → K-means (fast, scalable)
│   ├── Unknown k               → HDBSCAN (handles noise, variable density)
│   └── High-dim text/embed     → HDBSCAN on UMAP-reduced embeddings
├── Anomaly detection
│   ├── Labeled                 → Gradient boosting on imbalanced data (see /class-balancing)
│   └── Unlabeled               → Isolation Forest or Autoencoder
└── Ranking / recommendation
    ├── Collaborative filtering → Matrix factorization (ALS) or LightFM
    └── Learning-to-rank        → LambdaMART (LightGBM ranker)
```

## Constraint modifiers

| Constraint | Adjustment |
|---|---|
| Must explain prediction | Linear model or tree + SHAP; avoid neural nets |
| Latency < 10ms | Logistic regression or small tree; no ensemble |
| No GPU | Avoid deep learning; use gradient boosting |
| Streaming / online learning | SGD classifier, Vowpal Wabbit, River |
| Few labeled examples | Few-shot with fine-tuned LLM; semi-supervised |

## Baseline rule

Always build a trivial baseline first (majority class, mean predictor). Gradient boosting beats it 80% of the time on tabular data without feature engineering.

## Failure modes

- Choosing neural net for tabular data: gradient boosting usually wins with far less effort
- Choosing complex model before establishing baseline: no reference point for improvement
- Ignoring inference cost: training accuracy ≠ production viability

## Output format

For each recommendation:
1. Primary algorithm + library
2. Hyperparameters to tune first (top 3)
3. Named failure mode for this choice
4. Baseline to beat

Pair with `/hyperparameter-tuning` after selection and `/model-comparison` when evaluating alternatives.
