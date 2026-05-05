---
name: sparse-class-grouping
description: Group sparse or rare classes in categorical features or target labels. Use when a class has too few examples to model reliably, encoding high-cardinality categoricals, or collapsing long-tail label distributions.
---

# Sparse Class Grouping

## Role
You are a Sparse Class Grouping Advisor.

## Quick start

Tell me: is this a **target label** (what you're predicting) or a **categorical feature** (an input column)? The treatment differs.

## Sparsity thresholds

| Context | Sparse when |
|---|---|
| Target label (multi-class) | < 50 examples in training set |
| Target label (fine-grained) | < 1% of training set |
| Categorical feature, tree model | < 10 examples per category |
| Categorical feature, linear/neural | < 0.1% frequency |
| Text / NLP label | < 20 labeled examples |

Below threshold = unreliable gradient signal. Model memorizes, doesn't generalize.

## Grouping strategies

### Strategy 1 — Frequency cutoff → "other"
Fastest, least domain knowledge needed.
```python
threshold = 0.01   # 1% of training data
freq = df["category"].value_counts(normalize=True)
rare = freq[freq < threshold].index
df["category_grouped"] = df["category"].where(~df["category"].isin(rare), other="other")
```
When to use: high-cardinality feature with many tail categories that have no interpretable pattern.

### Strategy 2 — Domain hierarchy grouping
Best quality when taxonomy exists.
```python
# Map fine-grained labels to coarser parent class
label_map = {
    "golden_retriever": "dog", "labrador": "dog", "poodle": "dog",
    "siamese": "cat", "persian": "cat",
    "parakeet": "bird",     # sparse — map to parent
    "macaw": "bird",        # sparse — map to parent
}
df["species_grouped"] = df["species"].map(label_map).fillna(df["species"])
```
When to use: labels have a natural hierarchy (product categories, geographic regions, medical codes, job titles).

### Strategy 3 — Embedding-based clustering
For when no taxonomy exists but semantic similarity does.
```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

model = SentenceTransformer("all-MiniLM-L6-v2")
labels = df["category"].unique().tolist()
embeddings = model.encode(labels)

clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.4)
cluster_ids = clustering.fit_predict(embeddings)
label_to_cluster = dict(zip(labels, cluster_ids))
df["category_grouped"] = df["category"].map(label_to_cluster)
```
When to use: free-text categories, job titles, product descriptions — no clean hierarchy.

### Strategy 4 — Target-rate grouping (supervised)
Group by similarity of target rate, not surface label.
```python
# Compute target rate per category, then bin into groups
target_rate = df.groupby("category")["target"].mean()
df["category_target_rate"] = df["category"].map(target_rate)
# Rare categories with similar target rates get binned together
df["category_grouped"] = pd.cut(df["category_target_rate"], bins=5, labels=["G1","G2","G3","G4","G5"])
```
When to use: feature encoding for linear models; groups categories by behavior, not name.
**Must be fit on training data only** — target rate is computed on train, mapped to val/test.

## Target label grouping (special case)

When the sparse class IS the prediction target:

Option A — Merge into nearest parent class (hierarchy)
Option B — Merge into semantically closest class (embedding similarity)
Option C — Flag as "rare" class and treat as binary: `rare_class` vs. `not_rare`
Option D — Collect more data before merging (preferred if feasible)

Document every merge decision: merged class name + reason + count before merge.

## Validation after grouping

```python
# Check: grouped class has sufficient representation
grouped_counts = df["category_grouped"].value_counts()
print(grouped_counts[grouped_counts < 50])   # anything still sparse?

# Check: grouping didn't destroy signal
from sklearn.metrics import mutual_info_score
mi_before = mutual_info_score(df["category"], df["target"])
mi_after  = mutual_info_score(df["category_grouped"], df["target"])
print(f"MI before: {mi_before:.4f}  after: {mi_after:.4f}")
# Acceptable loss: < 10% relative MI drop
```

## Grouping order in pipeline

1. Fit grouping on training data only (frequency counts, target rates, cluster assignments)
2. Apply same mapping to val and test — no re-fitting
3. Handle unseen categories at inference: map to "other" or nearest known group

## Failure modes

- Grouping test set with train statistics: leaks distribution; fit on train, transform all
- "Other" bucket too large (> 20% of data): model learns "other" = catch-all with no signal; reconsider threshold
- Merging classes with very different target rates: destroys discriminative signal — check MI before committing
- No documentation of merge decisions: impossible to audit or reproduce the label schema

Pair with `/class-balancing` if merged groups are still imbalanced, `/feature-engineering` for encoding the grouped column, `/annotation-design` if regrouping target labels that humans labeled.
