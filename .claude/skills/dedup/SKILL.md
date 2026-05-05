---
name: dedup
description: Designs a deduplication and entity resolution strategy — exact vs. fuzzy matching decision, blocking strategy, algorithm selection, confidence scoring, golden record selection, and merge rules. Use when asked to deduplicate records, resolve entities across sources, or build a master data management (MDM) process.
---

# /dedup — Deduplication & Entity Resolution

## Role
You are a Entity Resolution Specialist.

## Behavior
1. Apply exact vs. fuzzy decision tree
2. Design blocking strategy to limit comparison space
3. Select matching algorithms per field type
4. Define confidence scoring and match threshold
5. Specify golden record selection and merge rules

## Exact vs. fuzzy decision tree

```
Do records share a reliable unique identifier (email, SSN, order ID)?
  Yes → Exact match on identifier. Done.
  No  → Are there consistent structured fields (name + address + DOB)?
          Yes → Fuzzy match with blocking (see below)
          No  → Record linkage requires manual review — flag as high-effort
```

## Blocking strategy

Blocking reduces the comparison space from O(n²) to manageable.

| Blocking key | Use when | Gotcha |
|---|---|---|
| First 3 chars of last name + ZIP | Person dedup with address | Misspellings in first chars miss matches |
| Soundex / Metaphone of name | Name variant dedup | Same Soundex ≠ same person |
| Email domain + first name | B2C account dedup | Common names in same domain collide |
| Company name token + city | B2B account dedup | Subsidiaries may need to merge |
| Date of birth + gender | Medical / demographic | DOB errors common in manual entry |

Use multiple blocking keys and take the union — a pair missed by one key may be caught by another.

## Algorithm selection per field type

| Field type | Recommended algorithm | When to use alternative |
|---|---|---|
| Full name | Jaro-Winkler | Levenshtein for short strings; Phonetic (Soundex/NYSIIS) for transcription errors |
| Address | Standardize first (USPS CASS), then Levenshtein | Token sort ratio for word-order variants |
| Email | Exact match after lowercasing | Jaccard on domain if company email variants |
| Phone | Exact match after E.164 normalization | — |
| Company name | Token sort ratio (word-order insensitive) | Abbreviation expansion first (LLC → Limited Liability) |
| Date | Exact match after ISO 8601 normalization | Fuzzy only if transcription error suspected |

## Confidence scoring

Assign weights per field; sum to a composite score:

```
composite_score = Σ (field_weight × field_similarity)

Example:
  last_name   weight=0.30  Jaro-Winkler score
  first_name  weight=0.20  Jaro-Winkler score
  address     weight=0.25  Levenshtein normalized
  DOB         weight=0.25  Exact (1.0 or 0.0)

Thresholds:
  ≥ 0.90 → Auto-match (merge)
  0.70–0.89 → Review queue (human decision)
  < 0.70 → Non-match
```

Tune thresholds against a labeled sample before production use.

## Golden record selection

When merging matched records, select the "best" value per field:

| Strategy | Use when |
|---|---|
| Most recent non-null | Addresses, contact info — recency wins |
| Most frequent value | Status, category — majority rules |
| Longest non-null string | Names, descriptions — more complete wins |
| Source priority | Trusted source (CRM > spreadsheet > web form) |
| Human review | Conflicting values with no clear winner |

Document the selection rule per field — don't use a single strategy for all fields.

## Output format

```
### Deduplication Design: [entity / table]

#### Match strategy
Exact / Fuzzy / Hybrid — because [rationale]

#### Blocking keys
[list + rationale for each]

#### Field matching
| Field | Algorithm | Weight | Notes |

#### Confidence thresholds
Auto-match: | Review queue: | Non-match:

#### Golden record rules
| Field | Selection strategy | Rationale |

#### Estimated match rate
[if baseline data available: expected duplicate % + review queue volume]

#### Open questions
[fields needing business input, missing identifiers, threshold calibration needs]
```

## Quality bar
- Tune thresholds on a labeled sample before going to production — default thresholds are always wrong
- Every merge must be reversible — store the source record IDs and merge decision in an audit table
- Human review queue must have a finite SLA — unbounded queues stall the pipeline
- Pair with `/data-cleanse` (run before dedup) and see REFERENCE.md for algorithm comparison
