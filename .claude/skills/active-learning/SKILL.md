---
name: active-learning
description: Designs an active learning strategy for annotation budget optimization — query strategy selection, uncertainty sampling, diversity sampling, batch selection, and stopping criteria. Use when annotation budget is limited, when asked which examples to label next, or when a model exists and you want to maximize improvement per annotation dollar.
---

# /active-learning — Active Learning Strategy

## Behavior
1. Confirm prerequisites (a model or heuristic must exist to score unlabeled examples)
2. Apply query strategy decision tree
3. Define batch size and selection method
4. Specify stopping criteria
5. Design the annotation → retrain → re-score loop

## Prerequisites

Active learning requires at least one of:
- A trained model (even a weak baseline) that can score unlabeled examples
- A set of heuristics or rules that can estimate label uncertainty
- An embedding model that can measure similarity / diversity

Without any of these: label a random seed set first (300–500 examples), train a baseline, then start active learning.

## Query strategy decision tree

```
Do you have a trained model?
  No  → Label random seed set (300–500); train baseline; return here
  Yes →
    Is label diversity / coverage a concern? (few labeled examples, unexplored regions)
      Yes → Diversity-first (coreset / clustering) for first 1–2 batches
      No  → Uncertainty-first (most informative examples near decision boundary)
    Ongoing: combine both — uncertainty sampling within diversity-selected clusters
```

## Strategy comparison

| Strategy | How | Best for | Weakness |
|---|---|---|---|
| Least confidence | Label the example the model is least sure about (`max_prob` closest to 1/K) | Binary / multi-class classification | Ignores diversity; can cluster on outliers |
| Margin sampling | Label examples where margin between top-2 predictions is smallest | Multi-class | Same clustering risk |
| Entropy sampling | Label examples with highest prediction entropy | Multi-class with many labels | Computationally equivalent to margin for binary |
| Query by committee | Disagreement between ensemble of models | When ensemble is available | Higher training cost |
| Coreset / diversity | Select examples that best cover the unlabeled space (max-min distance in embedding space) | Early-stage labeling; distribution coverage | Ignores informativeness |
| BADGE | Gradient-based diversity in embedding space | Deep learning; combines uncertainty + diversity | Requires gradient access |
| Hybrid | Cluster unlabeled pool; select most uncertain from each cluster | Production default — best coverage + informativeness | Slightly more complex |

## Batch selection

- **Batch size:** 50–200 examples per cycle (smaller = more retraining overhead; larger = less adaptive)
- **Diversity guard:** deduplicate candidates within each batch using embedding similarity (cosine > 0.95 = remove one)
- **Class balance check:** if selected batch is > 80% one class, add diversity sampling to rebalance

## Stopping criteria

Stop when any of the following:
- Model performance plateaus (< 1% improvement over last 2 cycles on held-out eval set)
- IAA on newly labeled examples drops (labels are getting harder — check guidelines)
- Annotation budget exhausted
- Unlabeled pool falls below 10× batch size

## Output format

```
### Active Learning Design: [task / model]

#### Current state
Labeled: N | Unlabeled pool: N | Model baseline: [metric + score]

#### Recommended strategy
[strategy] — because [rationale]
Batch size: | Cycle frequency: | Retraining trigger:

#### Selection method
[uncertainty / diversity / hybrid — with scoring formula]

#### Stopping criteria
[list with thresholds]

#### Expected efficiency gain
[vs. random labeling — estimate if baseline available]
```

## Quality bar
- Always maintain a held-out random eval set — never sample from it for annotation
- Active learning can create distribution shift in the training set — monitor for this across cycles
- If IAA drops on selected examples, the model is selecting genuinely hard cases — review guidelines, don't just annotate through it
- Pair with `/annotation-design` for guidelines and `/label-quality` for IAA monitoring across cycles
