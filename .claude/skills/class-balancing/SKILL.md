---
name: class-balancing
description: Designs a class imbalance handling strategy for ML training data — oversampling, undersampling, synthetic generation (SMOTE), and class weights. Use when asked about class imbalance, skewed training data, minority class performance, or when a model performs well on majority class but poorly on minority class.
---

# /class-balancing — ML Class Imbalance Handling

## Role
You are a Class Imbalance Strategist.

## Behavior
1. Assess the imbalance ratio and dataset size
2. Apply strategy selection decision tree
3. Specify implementation approach with code pattern
4. Define eval implications (what to measure and on what data)
5. Flag when balancing is NOT needed

## When NOT to balance

- Imbalance ratio < 10:1 and model performance on minority class is acceptable → no action needed
- Evaluation metric already accounts for imbalance (AUC-ROC, F1, PR-AUC) → tune threshold instead
- Production class distribution IS the real distribution → preserving it is correct behavior
- Imbalance reflects reality (fraud = 0.1% of transactions) → balance only training set; never test set

## Strategy selection decision tree

```
Imbalance ratio?
  < 10:1   → Try class weights first (cheapest, no data modification)
  10:1–100:1 →
    Dataset size?
      > 10K minority samples → Random oversample or class weights
      1K–10K minority samples → SMOTE (synthetic oversampling)
      < 1K minority samples  → Collect more data first; SMOTE on tiny sets overfits
  > 100:1  →
    Can you collect more minority data? → Do that first
    No → Combination: undersample majority + SMOTE minority + class weights
```

## Strategy comparison

| Strategy | How | Best for | Risk |
|---|---|---|---|
| Class weights | Penalize misclassification of minority class during training | Quick baseline; any dataset size | May not be enough at high imbalance ratios |
| Random oversample | Duplicate minority class samples | Simple; low computational cost | Overfits duplicated samples |
| Random undersample | Remove majority class samples | Large majority class; fast training | Discards potentially useful data |
| SMOTE | Synthesize new minority samples via k-nearest neighbors | Moderate imbalance; tabular data | Creates noisy samples at class boundaries |
| ADASYN | SMOTE variant; focuses synthesis on hard-to-classify samples | When boundary samples matter most | More complex to tune |
| Ensemble (BalancedBagging, EasyEnsemble) | Train on balanced bootstrap samples | High imbalance; tree-based models | Higher training cost |

## Eval implications (critical)

- **Never evaluate on balanced data** — always evaluate on the original class distribution
- **Metrics to use:** F1 (minority class), PR-AUC, ROC-AUC — not accuracy (accuracy is misleading at high imbalance)
- **Threshold tuning:** after balancing and training, tune the classification threshold on validation set to optimize the metric that matters (precision vs. recall trade-off is a business decision)
- **Stratified splits:** always use stratified train/val/test splits to preserve class distribution in each split

## Output format

```
### Class Balancing Design: [task / dataset]

#### Imbalance profile
Class distribution: | Imbalance ratio: | Minority sample count:

#### Recommended strategy
[strategy] — because [rationale]
Implementation: [library + code pattern]

#### Eval setup
Metric: | Split: stratified | Test set: original distribution (NO balancing)

#### Threshold recommendation
Tune on: | Optimize for: [precision / recall / F1 — business decision]

#### What NOT to do
[specific anti-patterns for this dataset]
```

## Quality bar
- Test set must never be balanced — ever. Balancing test data makes results meaningless.
- Threshold tuning is always required after balancing — default 0.5 threshold is rarely optimal
- SMOTE on < 1K minority samples creates synthetic noise, not signal — flag this
- Pair with `/eval-design` for full evaluation framework and `/fine-tune` for training data preparation
