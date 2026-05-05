---
name: data-collection-design
description: Design a data collection strategy for an ML task. Use when starting a new ML project, scoping dataset requirements, determining how much data to collect, or planning labeling alongside collection.
---

# Data Collection Design

## Quick start

Tell me: ML task type + current data available + budget/time constraint.

## How much data do you need?

| Task type | Minimum viable | Production ready |
|---|---|---|
| Binary classification, tabular | 1K per class | 10K+ per class |
| Multi-class (≤ 10 classes) | 500 per class | 5K per class |
| Named entity recognition | 1K sentences | 10K+ sentences |
| Text classification | 500 per class | 5K per class |
| Object detection | 500 images per class | 5K+ per class |
| Fine-tuning LLM | 50–200 examples | 1K–10K examples |
| Regression | 1K rows | 10K+ rows |

Rule: these are minimums for a meaningful model. Less → use few-shot prompting or transfer learning instead of training from scratch.

## Collection strategy decision tree

```
Data exists internally?
├── Yes → Audit first: is it labeled? current? representative of prod distribution?
│         Internal data = fastest path; label if needed
└── No  → External sources available?
          ├── Public dataset covers the task → Use it (see /data-sourcing)
          ├── Partial match → Augment with targeted collection
          └── No match → Active collection (crowdsource / scrape / API / synthetic)
```

## Collection methods by data type

| Data type | Collection method | Notes |
|---|---|---|
| Structured / tabular | Internal DB export, public CSV, API pull | Audit schema + freshness before use |
| Text | Web scrape, CommonCrawl, API (Reddit, news), internal logs | License check required |
| Images | Google Open Images, LAION subsets, scrape, internal | Rights clearance; NSFW filter |
| Audio / speech | LibriSpeech, CommonVoice, internal call recordings | PII scrub before use |
| Time series | IoT sensors, logs, financial APIs, synthetic simulation | Validate stationarity |
| Labels | Crowdsource (MTurk, Scale AI), internal SMEs, LLM pre-labeling + review | IAA threshold ≥ 0.6 |

## Representativeness checklist

Before collecting, define the target distribution:
- What time period does the model serve? Collect from same period.
- What geographies / user segments? Stratify collection to match.
- What edge cases must be covered? Budget 10–20% of dataset for hard cases.
- Is the collection environment the same as prod? If not, document the gap.

## Labeling integration

- Define label taxonomy before collection starts — changes mid-collection invalidate prior work
- Budget: ~1–3 min/label for simple tasks; ~5–15 min/label for complex NER/segmentation
- Plan for IAA calibration: 10% overlap between annotators; halt if κ < 0.60
- LLM pre-labeling + human review: 3–5× faster; validate on 10% sample before trusting

## Output format

For each data collection design:
1. Recommended source + collection method
2. Volume target with minimum viable and production-ready thresholds
3. Representativeness gaps to address
4. Labeling plan (who, tool, IAA target)
5. Named failure mode for this collection approach

## Failure modes

- Convenience sampling: collecting what's easy to get ≠ representative; model fails on tail distribution
- Label taxonomy defined after collection: forces re-labeling; budget 2× if this happens
- No IAA check: inconsistent labels degrade model as badly as too few labels
- Ignoring data rights: scraping without license check exposes org to legal risk

Pair with `/annotation-design` for labeling schema, `/data-sourcing` for external dataset evaluation, `/synthetic-data-gen` when real data is scarce.
