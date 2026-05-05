---
name: synthetic-data-gen
description: Generate synthetic training data for ML tasks. Use when real data is scarce, PII prevents use of real data, rare class augmentation is needed, or stress-testing models on edge cases.
---

# Synthetic Data Generation

## When to use synthetic data

| Situation | Approach |
|---|---|
| Real data < minimum viable (see /data-collection-design) | Generate to fill gap; validate distribution match |
| PII prevents using real data | Synthesize from schema + statistics; no real records |
| Class imbalance, minority < 1% | Augment minority only; keep majority real |
| Edge case / adversarial testing | Generate targeted hard examples |
| Pre-labeling for annotation | LLM-generate + human review; never ship unreviewed |

**Never use synthetic data as a drop-in replacement for real data.** Always mix with real data and validate distribution alignment.

## Generation methods by data type

### Tabular

```python
# SDV (Synthetic Data Vault) — preserves correlations
from sdv.single_table import GaussianCopulaSynthesizer
synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit(real_df)
synthetic_df = synthesizer.sample(num_rows=10000)

# CTGAN — better for mixed types + complex distributions
from sdv.single_table import CTGANSynthesizer
synthesizer = CTGANSynthesizer(metadata, epochs=300)
```

Validation: compare column distributions (KS test), correlation matrices, and row-level outlier rates.

### Text

```
LLM-based generation (recommended for labeled text):
  Prompt pattern:
    "Generate {N} examples of {class_label} text for {task_description}.
     Each example should be realistic, diverse, and 1–3 sentences.
     Avoid repeating phrases. Output as JSON array."

  Validation:
    - Run classifier trained on real data — synthetic examples should score ≥ 0.70
    - Check n-gram diversity: if top 10 n-grams repeat across > 20% of examples, prompt is too narrow
    - Human review: spot-check 10% before adding to training set
```

### Images

```
Augmentation (preferred over full synthesis for most tasks):
  from albumentations import Compose, HorizontalFlip, RandomBrightnessContrast, Rotate
  Augmentation is safe to apply at training time; no train/val contamination risk

Diffusion-based synthesis (Stable Diffusion / DALL-E):
  Use only for adding visual diversity, not for creating ground truth labels
  Always validate with a human review step before using as training data
```

### Time series

```python
# TSAugment — noise injection, time warping, scaling
from tsaug import TimeWarp, AddNoise
augmented = (TimeWarp() * 5 + AddNoise(scale=0.01)).augment(X_train)

# Simulation: when you have a domain model (physics, finance)
# Generate from known equations with noise — most controllable approach
```

## Quality gates (required before mixing with real data)

1. **Distribution alignment:** KS test p > 0.05 for numeric columns; chi-squared for categorical
2. **Classifier test:** train binary classifier (real=1, synthetic=0) — AUC < 0.60 = indistinguishable
3. **Downstream model test:** train on real-only vs. real+synthetic; synthetic must not hurt held-out-real performance
4. **Human review:** 10% spot-check for text and image synthesis

## Failure modes

- Replacing real data entirely: synthetic data never captures full real distribution; model underperforms in prod
- Augmenting validation/test sets: contaminates evaluation; synthetic only in training split
- No distribution validation: synthetic may amplify biases or introduce artifacts
- LLM-generated labels shipped without review: LLM hallucinations become training signal

Pair with `/class-balancing` when augmenting minority classes, `/data-collection-design` for overall data strategy, `/annotation-design` when generating pre-labeled examples.
