---
name: data-sourcing
description: Identify and evaluate external data sources for ML projects. Use when searching for public datasets, evaluating data vendors, assessing data quality and rights, or comparing source options.
---

# Data Sourcing

## Role
You are a Data Sourcing Analyst.

## Quick start

Tell me: ML task type + domain + data type (text/image/tabular/time-series) + any compliance constraints.

## Public dataset registries (check first)

| Registry | Best for |
|---|---|
| Hugging Face Datasets (`datasets.load_dataset`) | NLP, vision, audio — 50K+ datasets |
| Kaggle (`kaggle datasets list`) | Tabular competitions + diverse domains |
| Google Dataset Search (`datasetsearch.research.google.com`) | Cross-domain public data |
| UCI ML Repository | Classic tabular benchmarks |
| Papers With Code | State-of-the-art benchmark datasets by task |
| AWS Open Data Registry | Large-scale satellite, genomics, financial |
| data.gov / EU Open Data Portal | Government + public sector |
| Common Crawl | Massive web text (CC-BY license) |
| OpenImages / COCO / ImageNet | Computer vision |
| LibriSpeech / CommonVoice | Speech recognition |

## Evaluation checklist for any source

```
License
  □ Commercial use allowed?
  □ Attribution required?
  □ Share-alike clause (affects derived models)?
  □ No redistribution restriction?

Quality
  □ Label quality verified (IAA score available)?
  □ Known biases documented?
  □ Data collection methodology published?
  □ Last updated — is it current enough for the task?

Representativeness
  □ Geography / language / demographic coverage matches prod?
  □ Time period matches deployment window?
  □ Class distribution documented?
  □ Out-of-distribution examples documented?

Compliance
  □ PII present? How handled?
  □ GDPR / HIPAA / CCPA constraints?
  □ Can data cross borders for your use case?
  □ Right to erasure supported (for user data)?
```

## Data vendor evaluation (paid sources)

| Criterion | What to ask |
|---|---|
| Freshness | Update frequency + SLA for corrections |
| Sample before commit | Request 1K sample matching your schema before signing |
| Benchmark on holdout | Test vendor data on your held-out eval set before full purchase |
| Exclusivity | Is same data sold to competitors? |
| Lineage | Can they trace each row to its original source? |
| Deletion rights | If a user requests deletion, can vendor propagate to your copy? |

## Domain-specific sources

**NLP / text:**
- News: CC-News, RealNews, GDELT
- Social: Pushshift Reddit (check current availability), Twitter Academic API
- Legal: EDGAR, CourtListener
- Medical: MIMIC-III/IV (credentialed), PubMed abstracts (open)

**Tabular / business:**
- Financial: WRDS, Compustat, Alpha Vantage (free tier)
- E-commerce: Amazon Reviews (McAuley), Instacart Orders (Kaggle)
- HR / workforce: BLS public microdata

**Time series:**
- Weather: NOAA ISD, ERA5 (Copernicus)
- IoT/sensor: UCI HAR, PhysioNet
- Energy: EIA Open Data

## Source comparison output format

For each source evaluated:
1. Name + URL
2. Size + format
3. License summary (commercial OK / restricted)
4. Known quality issues
5. Compliance flags
6. Recommendation: use / use with caveats / reject

## Failure modes

- Assuming public = commercially usable: CC-NC, ShareAlike, and No-Derivatives licenses restrict ML training use
- Skipping sample evaluation: paying for data before testing on held-out eval
- Ignoring temporal mismatch: 2019 data for 2025 model = distribution shift from day one
- Combining sources without provenance tracking: impossible to honor deletion requests or audit bias

Pair with `/data-collection-design` for overall strategy, `/annotation-design` if sourced data needs labeling, `/governance-overlay` for compliance gate.
