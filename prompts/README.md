# prompts/ — System Prompt Templates

Ready-to-use system prompt templates for common AI use cases. Each template includes:
- The system prompt with `{{PLACEHOLDERS}}`
- Placeholder guide
- Usage notes
- Prompt health score across 9 dimensions (run `/prompt-review` to audit after filling)

---

## Templates

| File | Use case | Key placeholders |
|---|---|---|
**Problem framing / EDA:**

| File | Use case | Key placeholders |
|---|---|---|
| [`problem-framing.md`](problem-framing.md) | ML justification, solution type, success metric, non-ML baseline | `BUSINESS_CONTEXT`, `AVAILABLE_DATA`, `CONSTRAINTS` |
| [`eda.md`](eda.md) | Dataset profiling — target, missingness, cardinality, correlations, leakage candidates | `DATASET_CONTEXT`, `TARGET_VARIABLE`, `EDA_GOALS` |

**General / AI:**

| File | Use case | Key placeholders |
|---|---|---|
| [`rag-qa.md`](rag-qa.md) | Grounded Q&A over retrieved documents | `ORGANIZATION_NAME`, `RETRIEVED_CONTEXT`, `SOURCE_IDENTIFIER` |
| [`agentic-assistant.md`](agentic-assistant.md) | Tool-use agent with guardrails | `AGENT_NAME`, `TOOL_LIST`, `OUT_OF_SCOPE_LIST` |
| [`chat-assistant.md`](chat-assistant.md) | General-purpose chat with persona + scope | `ASSISTANT_NAME`, `SCOPE_DESCRIPTION`, `OUT_OF_SCOPE` |
| [`classifier.md`](classifier.md) | Single-label classification → JSON | `LABEL_TAXONOMY`, `FALLBACK_LABEL` |
| [`extractor.md`](extractor.md) | Field extraction from unstructured text → JSON | `JSON_SCHEMA_FIELDS`, `FIELD_DEFINITIONS` |
| [`code-reviewer.md`](code-reviewer.md) | Code review with BLOCKER/SUGGESTION/NITPICK grading | `LANGUAGE_OR_STACK`, `ADDITIONAL_CONSTRAINT` |
| [`summarizer.md`](summarizer.md) | Audience-targeted summarization | `TARGET_AUDIENCE`, `TARGET_LENGTH`, `OUTPUT_FORMAT` |
| [`structured-output.md`](structured-output.md) | NL → strict JSON schema conversion | `JSON_SCHEMA` |

**Data engineering:**

| File | Use case | Key placeholders |
|---|---|---|
| [`nl-to-sql.md`](nl-to-sql.md) | NL → SQL with schema context + safety guardrails | `DIALECT`, `SCHEMA_CONTEXT`, `PARTITION_COLUMN` |
| [`dbt-model-gen.md`](dbt-model-gen.md) | Generate dbt model SQL + schema.yml from spec | `WAREHOUSE`, `UPSTREAM_REFS` |
| [`pipeline-debugger.md`](pipeline-debugger.md) | Systematic pipeline failure / anomaly diagnosis | `PIPELINE_DESCRIPTION`, `STACK_DESCRIPTION` |
| [`data-dict-gen.md`](data-dict-gen.md) | Auto-generate data dictionary from table schema | `OUTPUT_FORMAT`, `AUDIENCE` |
| [`quality-rules-gen.md`](quality-rules-gen.md) | Generate validation rules → dbt tests or SQL checks | `STACK`, `OUTPUT_FORMAT` |
| [`contract-draft.md`](contract-draft.md) | Draft producer/consumer data contract | `OUTPUT_FORMAT`, `SENSITIVITY_NOTE` |

**Data cleansing / normalization:**

| File | Use case | Key placeholders |
|---|---|---|
| [`data-cleanse.md`](data-cleanse.md) | Detection rules + remediation SQL for dirty data | `DIALECT`, `SCHEMA_CONTEXT`, `KNOWN_ISSUES` |
| [`dedup-matcher.md`](dedup-matcher.md) | Blocking strategy, scoring, golden record, merge rules | `ENTITY_TYPE`, `AVAILABLE_FIELDS`, `AUTO_MATCH_THRESHOLD` |
| [`schema-harmonizer.md`](schema-harmonizer.md) | Multi-source canonical mapping + transformation SQL | `SOURCE_SCHEMAS`, `TARGET_WAREHOUSE`, `PRIORITY_SOURCE` |
| [`timeseries-resample.md`](timeseries-resample.md) | Upsample/downsample by metric type + gap handling | `STACK`, `SERIES_CONTEXT`, `SOURCE_FREQUENCY`, `TARGET_FREQUENCY` |
| [`class-balancing.md`](class-balancing.md) | Class imbalance strategy + eval setup + threshold tuning | `DATASET_CONTEXT`, `MODEL_TYPE`, `BUSINESS_OBJECTIVE` |

**Data labeling:**

| File | Use case | Key placeholders |
|---|---|---|
| [`annotation-guidelines.md`](annotation-guidelines.md) | Generate annotation instructions + decision tree + edge case catalog | `TASK_DESCRIPTION`, `LABEL_TAXONOMY`, `ANNOTATOR_AUDIENCE` |
| [`label-qa.md`](label-qa.md) | Review labeled dataset — disagreements, drift, guideline gaps | `TASK_DESCRIPTION`, `LABEL_TAXONOMY`, `IAA_TARGET` |
| [`active-learning-selector.md`](active-learning-selector.md) | Select next annotation batch for maximum model improvement | `LABELED_COUNT`, `MODEL_BASELINE`, `BATCH_SIZE` |

**Data splitting:**

| File | Use case | Key placeholders |
|---|---|---|
| [`split-design.md`](split-design.md) | Train/val/test split strategy + leakage verification | `DATASET_CONTEXT`, `TASK_TYPE`, `CONSTRAINTS` |
| [`cv-design.md`](cv-design.md) | CV variant selection + nested CV configuration | `DATASET_CONTEXT`, `TASK_TYPE`, `COMPUTE_BUDGET` |
| [`leakage-audit.md`](leakage-audit.md) | Audit pipeline for data leakage + code fixes | `PIPELINE_CONTEXT`, `FEATURE_LIST`, `PERFORMANCE_CONCERN` |

**ML algorithm selection / tuning:**

| File | Use case | Key placeholders |
|---|---|---|
| [`algo-select.md`](algo-select.md) | Select algorithm by task type + constraints | `TASK_CONTEXT`, `CONSTRAINTS` |
| [`hyperparameter-tuning.md`](hyperparameter-tuning.md) | Tuning strategy (random / Bayesian) + search space | `ALGORITHM_CONTEXT`, `COMPUTE_BUDGET`, `OPTIMIZATION_METRIC` |
| [`model-comparison.md`](model-comparison.md) | Statistical model comparison + production verdict | `MODELS_TO_COMPARE`, `EVALUATION_METRIC`, `DATASET_CONTEXT` |

**Feature engineering:**

| File | Use case | Key placeholders |
|---|---|---|
| [`feature-engineering.md`](feature-engineering.md) | Encoding, transformation, aggregation + sklearn Pipeline | `DATASET_CONTEXT`, `ALGORITHM_FAMILY`, `TARGET_TYPE` |
| [`feature-selection.md`](feature-selection.md) | Filter / embedded / wrapper selection + importance audit | `DATASET_CONTEXT`, `ALGORITHM_FAMILY`, `SELECTION_GOAL` |
| [`feature-store-design.md`](feature-store-design.md) | Online/offline store design + point-in-time joins + backfill | `USE_CASE_CONTEXT`, `SERVING_REQUIREMENTS`, `STACK` |

**Data gathering:**

| File | Use case | Key placeholders |
|---|---|---|
| [`data-collection-design.md`](data-collection-design.md) | Data volume targets, collection strategy, labeling plan | `TASK_CONTEXT`, `CURRENT_DATA`, `CONSTRAINTS` |
| [`synthetic-data-gen.md`](synthetic-data-gen.md) | Tabular / text / image / time-series synthesis + quality gates | `DATASET_CONTEXT`, `GENERATION_GOAL`, `STACK` |
| [`data-sourcing.md`](data-sourcing.md) | Public dataset search + vendor evaluation + license checklist | `TASK_CONTEXT`, `DATA_REQUIREMENTS`, `COMPLIANCE_CONSTRAINTS` |

**Data filtering / outlier handling:**

| File | Use case | Key placeholders |
|---|---|---|
| [`outlier-detection.md`](outlier-detection.md) | Detect + treat outliers (Z-score / IQR / Isolation Forest / Mahalanobis) | `DATASET_CONTEXT`, `DETECTION_GOAL`, `STACK` |
| [`data-filtering.md`](data-filtering.md) | Remove irrelevant observations by domain rules, quality, relevance, dedup | `DATASET_CONTEXT`, `FILTERING_GOALS`, `STACK` |
| [`sparse-class-grouping.md`](sparse-class-grouping.md) | Collapse rare labels / high-cardinality features into groups | `DATASET_CONTEXT`, `GROUPING_TARGET`, `STACK` |

**Model validation:**

| File | Use case | Key placeholders |
|---|---|---|
| [`model-validation.md`](model-validation.md) | Pre-deploy checklist — performance, slices, edge cases, latency, Go/No-Go | `MODEL_CONTEXT`, `PERFORMANCE_BASELINE`, `DEPLOYMENT_CONSTRAINTS` |
| [`model-calibration.md`](model-calibration.md) | Probability calibration — ECE, reliability diagram, Platt/isotonic/temperature | `MODEL_CONTEXT`, `CALIBRATION_GOAL`, `STACK` |
| [`model-drift.md`](model-drift.md) | Production drift detection — data / concept / prediction drift + retraining triggers | `MODEL_CONTEXT`, `MONITORING_CONTEXT`, `STACK` |

**Model deployment:**

| File | Use case | Key placeholders |
|---|---|---|
| [`model-deployment.md`](model-deployment.md) | Artifact packaging, phased rollout (shadow→canary→GA), rollback triggers, deployment.yaml | `MODEL_CONTEXT`, `TARGET_ENVIRONMENT`, `ROLLOUT_CONSTRAINTS` |
| [`inference-service-design.md`](inference-service-design.md) | REST/gRPC/batch pattern, latency budget, scaling, circuit breaker, fallback | `MODEL_CONTEXT`, `TRAFFIC_REQUIREMENTS`, `INFRASTRUCTURE_CONSTRAINTS` |
| [`model-decommissioning.md`](model-decommissioning.md) | Retire a model — retirement criteria, dependency audit, notification, archive policy | `MODEL_CONTEXT`, `SUCCESSOR_CONTEXT`, `CONSTRAINTS` |

**Responsible AI:**

| File | Use case | Key placeholders |
|---|---|---|
| [`fairness-audit.md`](fairness-audit.md) | Bias audit — demographic parity, disparate impact, equal opportunity, mitigation | `MODEL_CONTEXT`, `PROTECTED_ATTRIBUTES`, `REGULATORY_CONTEXT` |
| [`explainability.md`](explainability.md) | SHAP / LIME / counterfactuals — global + local explanations by audience | `MODEL_CONTEXT`, `EXPLANATION_GOALS`, `AUDIENCE` |

**MLOps / Lifecycle:**

| File | Use case | Key placeholders |
|---|---|---|
| [`experiment-tracking.md`](experiment-tracking.md) | Run logging schema, registry promotion criteria, reproducibility checklist | `PROJECT_CONTEXT`, `TRACKING_TOOL`, `REPRODUCIBILITY_REQUIREMENTS` |
| [`ab-test-design.md`](ab-test-design.md) | Sample size, assignment strategy, guardrail metrics, stopping rules, analysis plan | `EXPERIMENT_CONTEXT`, `TRAFFIC_METRICS_CONTEXT`, `BUSINESS_CONSTRAINTS` |
| [`retraining-strategy.md`](retraining-strategy.md) | Trigger types, data window design, full vs. incremental, promotion gates | `MODEL_CONTEXT`, `MONITORING_CONTEXT`, `RETRAINING_CONSTRAINTS` |
| [`data-versioning.md`](data-versioning.md) | Dataset versioning, DVC / time-travel, lineage chain, reproducibility | `DATA_INFRASTRUCTURE_CONTEXT`, `VERSIONING_REQUIREMENTS`, `COMPLIANCE_CONTEXT` |

---

## How to use a template

1. Copy the system prompt block from the template file
2. Fill in all `{{PLACEHOLDERS}}` — the placeholder guide in each file explains each one
3. Run `/prompt-review` to get a 9-dimension health score on your filled prompt
4. Add a version header before shipping to prod: `# System prompt v1.0 — YYYY-MM-DD`
5. Track versions in git — prompt changes are code changes

---

## Common issues across all templates

| Issue | Fix |
|---|---|
| Versioning ❌ on every template | Add `# System prompt v1.0 — YYYY-MM-DD` as first line before prod |
| Injection risk ⚠️ on most templates | Wrap untrusted content in XML tags: `<user_input>...</user_input>` |
| PII exposure ⚠️ on most templates | Define a retention policy for prompt logs before launch |

---

## Adding a new template

1. Copy an existing template as a starting point
2. Fill in: system prompt, placeholders table, usage notes, prompt health table
3. Add a row to this README's table
4. Run `/prompt-review` on the new template before committing
