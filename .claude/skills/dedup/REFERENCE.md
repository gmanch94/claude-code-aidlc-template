# /dedup — Reference

## Algorithm comparison

| Algorithm | Best for | Score range | Weakness |
|---|---|---|---|
| Exact match | IDs, emails, phones (after normalization) | 0 or 1 | Any variation = miss |
| Levenshtein distance | Short strings with typos | 0–1 normalized | Sensitive to length; slow on long strings |
| Jaro-Winkler | Person names | 0–1 | Poor on abbreviations; less useful > 15 chars |
| Token sort ratio | Company names, addresses (word order varies) | 0–100 | Misses partial matches |
| Jaccard similarity | Sets of tokens; keyword matching | 0–1 | Doesn't capture ordering |
| Soundex | Phonetic name matching | Match / no-match | Coarse; many false positives |
| NYSIIS | Better phonetic than Soundex for English names | Match / no-match | English-centric |
| Cosine similarity (TF-IDF) | Long text fields, descriptions | 0–1 | Overkill for structured fields |

**Rule of thumb:** Jaro-Winkler for names, token sort ratio for company names and addresses, exact match after normalization for everything else.

## Blocking method comparison

| Method | Comparison reduction | Miss risk | When to use |
|---|---|---|---|
| Sorted neighborhood | High | Medium | Large datasets; sorted on blocking key |
| Standard blocking | Very high | Low-medium | Well-structured data with reliable keys |
| Canopy clustering | High | Low | Approximate nearest neighbors; unlabeled data |
| Q-gram indexing | High | Low | Token-based; handles partial matches well |
| Multiple blocking keys (union) | Moderate | Very low | Production — use 2–3 keys, take union |

## Confidence threshold calibration

Steps to calibrate before production:
1. Label a random sample of 500–1000 record pairs (match / non-match / unsure)
2. Compute composite scores on labeled pairs
3. Plot precision-recall curve at different thresholds
4. Choose auto-match threshold at precision ≥ 0.99 (false merges are expensive)
5. Choose non-match threshold at recall ≥ 0.95 (missed merges create duplicates downstream)
6. Everything between = review queue — size it to your annotation capacity

## Merge audit table pattern

```sql
CREATE TABLE entity_merge_audit (
  merge_id        VARCHAR PRIMARY KEY,
  source_id_1     VARCHAR NOT NULL,
  source_id_2     VARCHAR NOT NULL,
  golden_id       VARCHAR NOT NULL,
  match_type      VARCHAR NOT NULL,  -- 'auto' | 'human_approved' | 'human_rejected'
  confidence      DECIMAL(4,3),
  merged_at       TIMESTAMP NOT NULL,
  merged_by       VARCHAR,           -- system or reviewer ID
  reversible      BOOLEAN DEFAULT TRUE
);
```

Always store both source IDs — enables un-merge if a match is later found to be wrong.

## Common dedup failure modes

| Failure mode | Symptom | Root cause | Fix |
|---|---|---|---|
| Threshold too aggressive | Merging non-matching records | Auto-match threshold too low | Raise threshold; move more to review queue |
| Threshold too loose | Duplicates survive | Auto-match threshold too high | Lower threshold; invest in review capacity |
| Blocking too narrow | Matches missed entirely | Blocking key excludes valid pairs | Add a second blocking key; take union |
| No normalization before match | Low scores on obvious matches | "John Smith" vs "john smith " | Normalize (lowercase, trim) before matching |
| Dedup before cleanse | Dirty data creates false non-matches | Inconsistent formats inflate edit distance | Always cleanse first (see `/data-cleanse`) |
