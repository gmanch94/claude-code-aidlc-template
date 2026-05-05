# ADR-0045: Retail ML Data Preprocessing Policy

**Status:** Accepted
**Domain:** [mlops] [governance]
**Date:** 2026-04-22

---

## Context

Custom ML models for retail (demand forecasting, markdown optimization, customer segmentation, retail media targeting, fraud detection) depend on a shared set of preprocessing decisions that, if made inconsistently across teams, produce silent failures at production scale:

- **Temporal leakage** — random train/test splits on time-ordered retail data produce inflated offline metrics and production models that degrade on real events (Black Friday, seasonality shifts, promotional cycles)
- **Training data PII gap** — loyalty data cleared for inference-time use is not automatically cleared for ML training under GDPR Art. 6 and CCPA. Teams have historically assumed inference clearance transfers
- **Silent schema drift** — upstream systems (POS, WMS, loyalty platform) change schema without notification; ML pipelines produce corrupted features with no alert
- **Cold-start crashes** — new SKUs, new stores, and new customers appear in production inference that were absent from training data; pipelines with no cold-start handling fail silently or return null predictions
- **[ML_PARTNER] signal misuse** — demand forecast signals from [ML_PARTNER] are frequently used as training labels rather than as input features, introducing a category error that undermines model independence and fallback behavior

This workspace already has governance standards for AI systems (ADR-0043, ADR-0044) and for cloud ML platforms (ADR-0012–0030). This ADR fills the gap: the data preprocessing decisions that sit between raw source data and trained model artifacts.

The `/dataset-readiness` command is the operational tool that audits compliance with this policy before any model training begins.

---

## Decision

### Principle: No Contract, No Training

A dataset may not be used as training data unless a signed data contract exists between the data-producing team and the ML-consuming team. The contract must be active and its schema version must match the consuming pipeline's schema expectations at the time training begins.

This principle is an analog to ADR-0044's "No Provenance, No Prod" for model artifacts — applied to training data.

### 1. Temporal Splitting Policy

**Random train/test splits are prohibited for all retail models with time-series targets.** This applies to: demand forecasting, markdown optimization, CLV, churn prediction, fraud detection, and any other model where the target variable is correlated with time.

Required split structure:

```
[T_start] ──── Training data ──── [T_train_end] │ GAP │ Validation │ GAP │ Test
```

**Mandatory parameters:**

| Model Type | Min Training Window | Validation Gap | Reason for Gap |
|-----------|:-----------------:|:--------------:|----------------|
| Demand / replenishment | 52 weeks | 7 days | Rolling weekly features must not see label-period data |
| Fresh markdown | 26 weeks | 3 days | Intraday rolling features; shorter horizon |
| Customer CLV / churn | 24 months | 14 days | Prediction horizon is 12 months; need separation |
| Retail media audience | 12 months | 30 days | Prediction horizon is 30-day purchase probability |
| Fraud detection | 26 weeks | 7 days | Fraud pattern recency dependency |

The test set must contain at least one major seasonal event (defined as any week where historical demand deviates > 2σ from the annual mean) to ensure the model is validated against realistic variance.

**Enforcement:** The temporal split is a required pipeline step implemented in code and logged in the model registry artifact. A model trained with a random split will not pass registry review.

### 2. Training Data PII Policy

Inference-time PII clearance does not transfer to training data. The following additional steps are required before loyalty data or any dataset containing direct or indirect personal identifiers is used for ML training:

1. **Consent basis confirmed** — legal / privacy team confirms that the data collection consent covers ML model training as an explicit use case. For GDPR: document the applicable Art. 6 basis (or Art. 9 for sensitive categories). For CCPA: confirm the use is within the disclosed purposes.

2. **PII pseudonymization applied before training export** — household IDs must be tokenized using a stable, ML-safe token (not reversible by the ML pipeline). Raw email, name, phone, and address must not appear in any training dataset.

3. **Cross-dataset re-identification risk assessed** — joining two individually low-PII datasets (e.g., POS + web behavioral) can produce a dataset with high re-identification risk. Document and assess before any cross-dataset join in the training pipeline.

4. **Training data retention** — training datasets must not include records outside the data retention policy for the source dataset. Training snapshots are themselves subject to retention limits.

5. **Documented in the AI-BOM** — the training data consent basis, pseudonymization method, and retention limits must be recorded in the model's AI-BOM (per ADR-0044).

> [RISK: HIGH] Use of loyalty data for ML training without confirmed consent basis is a GDPR / CCPA compliance violation regardless of technical feasibility. This is not an ML architecture question — it requires legal sign-off.

### 3. Data Contract Requirements

A data contract (per `data-contract-template.md`) must be:
- Signed by both the data-producing team and the ML-consuming team
- Schema-versioned to a specific version in use by the consuming pipeline
- Containing explicit SLAs for completeness, timeliness, and breaking change notification
- Actively monitored — schema validation at the Bronze ingestion layer must fail fast if the delivered schema deviates from the contract version

**Breaking change protocol:** The producing team must notify the consuming team ≥ [14] calendar days before any breaking change (field removal, rename, type change, new required field). The consuming team must not begin training runs on a new schema version until the pipeline has been updated and tested.

### 4. Cold-Start Strategy is Mandatory

Every ML model that will encounter new entities at inference time must have a documented cold-start strategy. "We will retrain once we have data" is not a strategy — it is a production gap.

Required cold-start strategies per entity type:

| Entity | Minimum Required Strategy |
|--------|--------------------------|
| New SKU | Category-level feature aggregation + product description embedding; fall back to category median for numerical features |
| New Store | Store-format + region averages; cluster to nearest similar store by demographic profile |
| New Customer | Session-level behavioral features (if available) + demographic segment averages; no RFM (requires history) |

The cold-start strategy must be documented in the model card and tested on held-out new entities before production deployment.

### 5. [ML_PARTNER] Signal Policy

[ML_PARTNER] demand forecasts are input features, not training labels. Using them as labels:
- Creates a dependency where [RETAILER]'s model is only as good as [ML_PARTNER]'s model
- Breaks the fallback path — if [ML_PARTNER] is unavailable, the model has no label to compare against
- Prevents model improvement beyond [ML_PARTNER]'s signal quality

**[ML_PARTNER] signals must be treated as:** enrichment features with a staleness indicator (`mlpartner_signal_age_hours`) and an availability flag (`mlpartner_signal_available`). The model must be trained on data where the [ML_PARTNER] signal is occasionally absent, so it degrades gracefully.

### 6. Feature Naming and Registration

All features used in production models must follow the naming convention defined in `feature-engineering-playbook.md` and be registered in the feature store with full lineage to their source dataset (DS-XX reference). Unregistered features cannot be used in production models.

### 7. Golden Dataset Standard

Every production model must have a designated golden dataset — a versioned, held-out dataset that is never used for training or hyperparameter tuning, and is used exclusively for:
- Pre-production final evaluation gate
- Regression testing after model updates
- Monitoring for concept drift (compare production predictions against golden dataset ground truth)

Golden dataset minimum requirements per use case archetype:

| Use Case | Minimum Golden Dataset Size | Minimum Coverage |
|----------|:--------------------------:|-----------------|
| Demand forecasting | 8 weeks of item × store × day rows | All store formats; all categories; at least 1 major seasonal event |
| Fresh markdown | 4 weeks of markdown events | All fresh categories; at least one weekend |
| Customer segmentation | 10,000 households | Balanced across segments; includes new members |
| Retail media audience | 10,000 household × category pairs | Balanced purchase / no-purchase; multiple categories |
| Fraud detection | 5,000 events; ≥ 2% fraud rate | Includes known fraud patterns; recent cohort |

---

## Consequences

**Positive:**
- Temporal split policy eliminates the most common cause of offline-to-online metric gap in retail ML
- "No Contract, No Training" creates upstream accountability and prevents silent model breakage from schema changes
- Training data PII policy closes the governance gap between inference-cleared and training-cleared data
- Cold-start requirement prevents production null-prediction failures on new SKU launches, new store openings, and new customer enrollment periods
- Golden dataset standard makes regression testing systematic rather than ad hoc

**Negative:**
- Data contract negotiation adds lead time before training can begin — teams must plan for 2–4 weeks of contract setup before a new dataset can be used
- PII consent verification for training may reveal that some legacy loyalty data lacks the required consent basis, requiring re-consent or data deletion before use
- Feature store registration adds overhead for rapid-iteration research phases — teams may push back on registration requirement for experimental models (mitigation: create a "research" tier with lighter requirements, but production models always require full registration)

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Allow random splits for non-time-series features | Retail targets are almost always time-correlated. Teams cannot reliably determine which features are "safe" for random splits; blanket policy removes the judgment call. |
| Infer consent basis from existing privacy policy | Existing privacy policies rarely enumerate ML model training explicitly. Legal confirmation is required — inference is not acceptable given regulatory risk. |
| Data contracts optional for internal datasets | Internal datasets change silently too. ADR-0044 established this for model artifacts; the same logic applies to training data. |
| Cold-start handled post-launch | New SKU launches and new store openings are predictable events. Post-launch hot-fixes are disruptive and delay value. Mandatory pre-launch cold-start design is lower total cost. |

---

## Implementation Notes

1. The `/dataset-readiness` command in this workspace audits compliance with this policy before training begins — run it for every new model and for every major model retraining
2. Add schema validation at the Bronze ingest layer for each data contract — fail fast on schema deviation
3. Add a temporal split enforcement step to the training pipeline DAG — output a log artifact recording the exact cutoff dates and window sizes used
4. Register the training data consent basis in the AI-BOM field `training_data_consent_basis` — this field is required from ADR-0044
5. Golden datasets are versioned artifacts in the model registry — committed alongside the model they evaluate

---

## Related Decisions

- **ADR-0043** — AI Red Team Policy: Phase 4 operational testing requires a staging environment that mirrors production data pipeline behavior; the preprocessing pipeline design here is what must be replicated in staging
- **ADR-0044** — Model Supply Chain & Provenance Policy: training data is a supply chain component; the AI-BOM must include training dataset name, version, hash, consent basis, and PII handling method — all defined by this ADR's requirements
- **ADR-0039** — OSS MLOps Workflow Orchestration: the preprocessing pipeline DAGs defined here are implemented using the orchestration tool chosen in that ADR
- **ADR-0034 / ADR-0035** — Agent and RAG frameworks: the golden dataset standard here applies equally to RAG evaluation datasets (which are a form of preprocessing output)

---

## Risks Not Fully Mitigated

- [RISK: HIGH] Legacy loyalty data collected before ML training was an enumerated use case may require re-consent or exclusion from training sets. This is a programme-level risk requiring legal and CRM team involvement before any loyalty-based model enters training.
- [RISK: MED] Data contracts require sustained organizational commitment from data-producing teams who are not directly incentivized to maintain them. Mitigation: AI Platform Team owns the schema validation tooling and automated breach detection; data producers get paged when their pipeline breaks downstream ML.
- [RISK: LOW] The mandatory seasonal event in the test set may be unavailable for models trained very early in the programme (before a full seasonal cycle has passed). Mitigation: document the gap in the model card and schedule a retraining gate after the first seasonal event is observed in production.
