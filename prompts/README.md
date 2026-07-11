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
**Business discovery:**

| File | Use case | Key placeholders |
|---|---|---|
| [`stakeholder-interview.md`](stakeholder-interview.md) | Six-group discovery interview with non-technical stakeholders; Discovery Summary Card | `ORGANIZATION_NAME`, `STAKEHOLDER_ROLE`, `BUSINESS_DOMAIN` |
| [`opportunity-sizing.md`](opportunity-sizing.md) | Status quo cost, AI uplift estimate, build cost, go/no-go recommendation | `BUSINESS_PROBLEM`, `CURRENT_PROCESS`, `ANNUAL_VOLUME` |
| [`kpi-mapping.md`](kpi-mapping.md) | Business objective → KPI → proxy → ML metric chain with failure modes and counter-metric | `BUSINESS_OBJECTIVE`, `CURRENT_KPI_SYSTEM`, `ERROR_TOLERANCE` |
| [`ml-readiness.md`](ml-readiness.md) | 5-stage maturity assessment + AI Hierarchy of Needs + build/buy/partner + 5-year roadmap + process-as-IP | `ORG_CONTEXT`, `ML_FOOTPRINT`, `STRATEGIC_HORIZON` |
| [`stakeholder-comms.md`](stakeholder-comms.md) | Audience map + Rider/Elephant/Path messaging + reporting cadence + failure-comms templates | `PROJECT_CONTEXT`, `STAKEHOLDERS`, `CURRENT_STATE` |
| [`metric-gaming-audit.md`](metric-gaming-audit.md) | Goodhart-resistance audit — proxy scoring, per-actor gaming paths, secondary effects, counter-metrics | `OPTIMIZATION_CONTEXT`, `CANDIDATE_METRICS`, `OPERATING_ENV` |

**Problem framing / EDA:**

| File | Use case | Key placeholders |
|---|---|---|
| [`problem-framing.md`](problem-framing.md) | ML justification, solution type, success metric, non-ML baseline | `BUSINESS_CONTEXT`, `AVAILABLE_DATA`, `CONSTRAINTS` |
| [`eda.md`](eda.md) | Dataset profiling — target, missingness, cardinality, correlations, leakage candidates | `DATASET_CONTEXT`, `TARGET_VARIABLE`, `EDA_GOALS` |
| [`cohort-analysis.md`](cohort-analysis.md) | Cohort segmentation — acquisition/behavioral/attribute cohorts, outcome comparison, retention curves | `ORGANIZATION_NAME`, `DATASET_DESCRIPTION`, `OUTCOME_VARIABLE`, `COHORT_DIMENSIONS` |
| [`time-series-eda.md`](time-series-eda.md) | Time series EDA — stationarity, trend, seasonality, ACF/PACF, structural breaks, anomalies | `ORGANIZATION_NAME`, `SERIES_NAME`, `FREQUENCY`, `MODELING_GOAL` |
| [`feature-correlation.md`](feature-correlation.md) | Feature relationships — correlation by type, VIF, Cramér's V, interaction detection | `ORGANIZATION_NAME`, `FEATURE_LIST`, `TARGET_VARIABLE`, `MODEL_FAMILY` |
| [`hypothesis-test-design.md`](hypothesis-test-design.md) | Statistical test selection for OBSERVATIONAL questions — test by outcome × group × paired × distribution, assumption checks, effect size + a priori power, multiplicity correction, pitfall guards | `ORGANIZATION_NAME`, `QUESTION`, `OUTCOME_TYPE`, `GROUPS`, `PAIRED_OR_INDEPENDENT` |
| [`unstructured-eda.md`](unstructured-eda.md) | Pre-modeling text/image corpus profiling — length/encoding/language, near-dup rate, label coverage, corruption audit, cross-split duplicate leakage; GO/FIX-FIRST verdicts | `ORGANIZATION_NAME`, `MODALITY`, `CORPUS_SIZE`, `TASK`, `SPLITS` |

**Unsupervised learning:**

| File | Use case | Key placeholders |
|---|---|---|
| [`clustering.md`](clustering.md) | Clustering — algorithm selection, k decision, evaluation metrics, stability, cluster profiling | `ORGANIZATION_NAME`, `DATASET_DESCRIPTION`, `K_KNOWN`, `DOWNSTREAM_USE` |
| [`dim-reduction.md`](dim-reduction.md) | Dimensionality reduction — PCA/UMAP/t-SNE selection, variance explained, component count, downstream rules | `ORGANIZATION_NAME`, `FEATURE_COUNT`, `GOAL`, `INFERENCE_REQUIRED` |
| [`topic-modeling.md`](topic-modeling.md) | Topic modeling — LDA/NMF/BERTopic selection, preprocessing, coherence-based k, topic labeling, downstream rules | `ORGANIZATION_NAME`, `CORPUS_DESCRIPTION`, `AVG_DOCUMENT_LENGTH`, `DOWNSTREAM_USE` |

**Reinforcement learning:**

| File | Use case | Key placeholders |
|---|---|---|
| [`bandit-design.md`](bandit-design.md) | Bandit algorithm selection, reward model, exploration params, stopping criteria, offline evaluation | `ORGANIZATION_NAME`, `ARM_COUNT`, `REWARD_TYPE`, `CONTEXT_AVAILABLE`, `REWARD_DELAY` |
| [`rl-design.md`](rl-design.md) | RL justification, MDP spec, algorithm selection, reward design, exploration, safety, evaluation | `ORGANIZATION_NAME`, `PROBLEM_DESCRIPTION`, `ACTION_SPACE_TYPE`, `SIMULATOR_AVAILABLE`, `RLHF_CONTEXT` |

**ML domain skills:**

| File | Use case | Key placeholders |
|---|---|---|
| [`time-series-forecasting.md`](time-series-forecasting.md) | Forecasting model selection (ARIMA/ETS/Prophet/TFT/N-BEATS), time series CV, baseline comparison | `ORGANIZATION_NAME`, `SERIES_NAME`, `HORIZON`, `STATIONARITY_VERDICT`, `FORECAST_TYPE` |
| [`recommender-design.md`](recommender-design.md) | Recommendation system design — algorithm, two-stage pipeline, cold-start, offline/online eval | `ORGANIZATION_NAME`, `DOMAIN`, `INTERACTION_TYPE`, `USER_COUNT`, `ITEM_COUNT` |
| [`learning-to-rank.md`](learning-to-rank.md) | Learning-to-rank for query-document search/ads — objective class (pointwise/pairwise/listwise), model family (LambdaMART/cross-encoder), click-bias-corrected judgments (IPW), NDCG/MAP/MRR/ERR, query-level split + interleaving/A-B eval | `ORGANIZATION_NAME`, `DOMAIN`, `LABEL_SOURCE`, `RELEVANCE_GRANULARITY`, `POSITIONS_LOGGED` |
| [`nlp-pipeline.md`](nlp-pipeline.md) | NLP pipeline — preprocessing, embedding selection, task metrics, annotation guidance | `ORGANIZATION_NAME`, `NLP_TASK`, `CORPUS_SIZE`, `DOMAIN`, `LABEL_AVAILABILITY` |
| [`anomaly-detection.md`](anomaly-detection.md) | Anomaly detection — method by data type + label availability, threshold strategy, FPR evaluation, treatment | `ORGANIZATION_NAME`, `DATASET_CONTEXT`, `DATA_TYPE`, `LABEL_AVAILABILITY`, `DETECTION_GOAL` |
| [`predictive-maintenance.md`](predictive-maintenance.md) | PdM framing (anomaly/RUL/classification by failure count), lead-time gate, cost-weighted threshold, alert→work-order policy | `ORGANIZATION_NAME`, `ASSET_FAILURE_MODES`, `FAILURE_HISTORY`, `LEAD_TIME`, `COSTS` |
| [`causal-inference.md`](causal-inference.md) | Causal method by study design, assumption validation, effect estimate + CI | `ORGANIZATION_NAME`, `STUDY_DESIGN`, `TREATMENT_VARIABLE`, `OUTCOME_VARIABLE`, `ATE_OR_ATT_OR_LATE` |
| [`computer-vision.md`](computer-vision.md) | CV architecture by task × dataset size, preprocessing + augmentation, mAP eval | `ORGANIZATION_NAME`, `CV_TASK`, `DATASET_SIZE`, `NUM_CLASSES`, `DEPLOYMENT_CONSTRAINTS` |
| [`survival-analysis.md`](survival-analysis.md) | Method by censoring type (KM/Cox/RSF/AFT), PH validation, C-statistic + calibration | `ORGANIZATION_NAME`, `EVENT_DEFINITION`, `CENSORING_TYPE`, `COVARIATE_DESCRIPTION`, `COMPETING_RISKS` |
| [`online-learning.md`](online-learning.md) | Streaming ML, concept-drift detection, prequential eval, batch-retrain gate | `ORGANIZATION_NAME`, `LEARNING_TASK`, `STREAM_DESCRIPTION`, `DRIFT_PROFILE`, `UPDATE_FREQUENCY` |
| [`graph-ml-design.md`](graph-ml-design.md) | Graph/network ML — GNN-vs-tabular gate, construction, task framing, GNN family + scale strategy, leakage-safe splits for connected data | `ORGANIZATION_NAME`, `SOURCE_DATA_SHAPE`, `PREDICTION_TARGET`, `GRAPH_SCALE`, `INDUCTIVE_OR_TRANSDUCTIVE` |
| [`audio-ml-pipeline.md`](audio-ml-pipeline.md) | Audio/speech ML — task framing, representation (waveform/mel/MFCC) + VAD, pretrained backbone, augmentation, task metrics, leakage gates | `ORGANIZATION_NAME`, `AUDIO_TASK`, `AUDIO_SOURCE`, `SAMPLE_RATE`, `DATA_VOLUME` |
| [`multimodal-design.md`](multimodal-design.md) | Multimodal/VLM — fusion gate, joint-embedding vs generative VLM, model selection, multimodal RAG, cross-modal eval | `ORGANIZATION_NAME`, `MODALITIES`, `TASK`, `QUERY_SHAPE`, `LABEL_AVAILABILITY` |
| [`geospatial-ml.md`](geospatial-ml.md) | Geospatial/spatial ML — CRS discipline, spatial features, task→model, spatial-autocorrelation leakage + spatial CV | `ORGANIZATION_NAME`, `SPATIAL_DATA_TYPE`, `TASK`, `INPUT_CRS`, `EXTENT` |
| [`decision-optimization.md`](decision-optimization.md) | Predict-then-optimize — handoff gate, formulation class (LP/MIP/stochastic/robust), optimizer's-curse remedies, decision-regret eval | `ORGANIZATION_NAME`, `DECISION_DESCRIPTION`, `OBJECTIVE`, `CONSTRAINTS`, `PREDICTION_SOURCE` |

**Industrial / IoT (OT data):**

| File | Use case | Key placeholders |
|---|---|---|
| [`uns-contextualization.md`](uns-contextualization.md) | Unified Namespace hierarchy (ISA-95), asset/digital-twin models, raw-tag → business-concept map, signal governance | `ORGANIZATION_NAME`, `SITE_SCOPE`, `ASSET_CLASSES`, `TAG_INVENTORY`, `BACKBONE` |
| [`industrial-iot-ingestion.md`](industrial-iot-ingestion.md) | OT protocol selection (OPC-UA/MQTT+Sparkplug B/Modbus), edge store-and-forward, OT→IT one-way boundary, volume estimate | `ORGANIZATION_NAME`, `SITE_LINE`, `SOURCES`, `NETWORK`, `BACKBONE` |

**General / AI:**

| File | Use case | Key placeholders |
|---|---|---|
| [`rag-qa.md`](rag-qa.md) | Grounded Q&A over retrieved documents | `ORGANIZATION_NAME`, `RETRIEVED_CONTEXT`, `SOURCE_IDENTIFIER` |
| [`agentic-assistant.md`](agentic-assistant.md) | Tool-use agent with guardrails | `AGENT_NAME`, `TOOL_LIST`, `OUT_OF_SCOPE_LIST` |
| [`llm-routing.md`](llm-routing.md) | LLM routing — routing strategy, model tier map, fallback chain, quality-floor gate, cost/quality projection | `ORGANIZATION_NAME`, `APPLICATION_DESCRIPTION`, `TASK_TYPES`, `QUALITY_FLOOR`, `COST_CONSTRAINT` |
| [`build-vs-buy.md`](build-vs-buy.md) | Build vs buy — 5-dimension scoring, AI tooling decision matrix, 3-year TCO, vendor alternatives, exit strategy | `ORGANIZATION_NAME`, `COMPONENTS`, `TEAM_SIZE`, `BUDGET_HORIZON`, `CONSTRAINTS` |
| [`prompt-management.md`](prompt-management.md) | PromptOps lifecycle — versioning + registry, env promotion, eval-gated rollout, A/B + canary, regression rollback, change-control governance | `SYSTEM_CONTEXT`, `EVAL_THRESHOLDS`, `GOVERNANCE_CONSTRAINTS` |
| [`context-engineering.md`](context-engineering.md) | Per-turn context-window assembly — budget allocation across sources, position-of-evidence ordering, overflow/compaction, relevance gating, assembly-quality probes | `ORGANIZATION_NAME`, `CALL_NAME`, `SOURCES`, `WINDOW`, `SYMPTOM` |
| [`agent-design.md`](agent-design.md) | Agentic system — stateless loop + durable session store, tool manifest, sandbox + reach, guardrails, HITL, Plan-Execute-Verify-Replan, memory, fallbacks | `ORGANIZATION_NAME`, `GOAL`, `TOOLS`, `SIDE_EFFECTS`, `AUTONOMY` |
| [`agent-memory.md`](agent-memory.md) | Memory architecture — tier selection, backing-store choice, validity windows, stale-context detection, per-tenant isolation, memory-quality eval | `ORGANIZATION_NAME`, `AGENT_NAME`, `SESSION_SHAPE`, `TENANCY`, `MEMORY_OPS`, `EVAL_TARGET` |
| [`plan-mode.md`](plan-mode.md) | Versioned plan artifact at `scratch/PLAN-<task>.md` — subgoal DAG, exit criteria, rollback, cost roll-up, verify gates, Replan procedure | `ORGANIZATION_NAME`, `TASK_SLUG`, `GOAL`, `CONSTRAINTS`, `OUT_OF_SCOPE`, `EXECUTOR` |
| [`workflow-design.md`](workflow-design.md) | Deterministic multi-agent workflow — fan-out shape, phase + grader, adversarial verify N=3, journaling + resume, budget caps, host choice | `ORGANIZATION_NAME`, `WORKFLOW_NAME`, `TASK`, `FAN_OUT_SHAPE`, `QUALITY_BAR`, `EXPECTED_CONCURRENCY`, `BUDGET`, `HOST` |
| [`test-time-compute.md`](test-time-compute.md) | Inference-time scaling on a fixed model — TTC gate (route-up vs scale-samples vs fine-tune), method (self-consistency / best-of-N+verifier / generative aggregation / sequential refinement), aggregator design, N/T sizing on the concave knee, cost/quality + latency/quality projection | `ORGANIZATION_NAME`, `TASK_DESCRIPTION`, `QUALITY_FLOOR`, `BASELINE_SCORE`, `LATENCY_BUDGET`, `COST_CEILING`, `VERIFIER`, `ANSWER_SHAPE` |
| [`agentic-data-curation.md`](agentic-data-curation.md) | Agentic post-training data recipe — build gate (frontier API vs train-your-own), task sourcing (dataset-adaptation / perturb-real-code / seed+skill-taxonomy; diversity-not-count), executable environments + verification (hard test-based vs soft no-tests), teacher rollouts + teacher selection (best ≠ biggest), trajectory filtering (drop timeouts/subagent, keep ≥5-turn) + source mixing (top-4..8), SFT→RL composition | `ORGANIZATION_NAME`, `TARGET_CAPABILITY`, `BASE_MODEL`, `EVAL_STATUS`, `ENV_FEASIBILITY`, `COMPUTE_BUDGET`, `OPEN_WEIGHT_RATIONALE` |
| [`mcp-design.md`](mcp-design.md) | MCP server design — tools/resources/prompts split, transport (stdio vs Streamable HTTP — HTTP+SSE deprecated since spec 2025-03-26), auth (OAuth 2.1+PKCE with RFC 9728/8414-or-OIDC/8707/9207; DCR deprecated → Client ID Metadata Documents) / API key / mTLS, schema discipline, scope boundaries, error contract + idempotency, deferred-tool strategy, host-compat matrix | `ORGANIZATION_NAME`, `SERVER_JOB`, `TARGET_HOSTS`, `CAPABILITIES`, `TRANSPORT`, `AUTH_MODEL`, `SIDE_EFFECT_TOOLS`, `TENANCY` |
| [`multi-agent-design.md`](multi-agent-design.md) | Multi-agent orchestration — pattern selection, framework (LangGraph/CrewAI/AutoGen), agent roster, state schema, failure handling | `ORGANIZATION_NAME`, `SYSTEM_GOAL`, `TOOL_LIST`, `LATENCY_REQUIREMENT`, `FRAMEWORK_PREFERENCE` |
| [`guardrails-design.md`](guardrails-design.md) | LLM input/output safety layers — threat inventory, detection methods, latency budget, FPR targets | `ORGANIZATION_NAME`, `APPLICATION_DESCRIPTION`, `RISK_PROFILE`, `LLM_MODEL`, `LATENCY_BUDGET` |
| [`chat-assistant.md`](chat-assistant.md) | General-purpose chat with persona + scope | `ASSISTANT_NAME`, `SCOPE_DESCRIPTION`, `OUT_OF_SCOPE` |
| [`classifier.md`](classifier.md) | Single-label classification → JSON | `LABEL_TAXONOMY`, `FALLBACK_LABEL` |
| [`extractor.md`](extractor.md) | Field extraction from unstructured text → JSON | `JSON_SCHEMA_FIELDS`, `FIELD_DEFINITIONS` |
| [`code-reviewer.md`](code-reviewer.md) | Code review with BLOCKER/SUGGESTION/NITPICK grading | `LANGUAGE_OR_STACK`, `ADDITIONAL_CONSTRAINT` |
| [`summarizer.md`](summarizer.md) | Audience-targeted summarization | `TARGET_AUDIENCE`, `TARGET_LENGTH`, `OUTPUT_FORMAT` |
| [`structured-output.md`](structured-output.md) | NL → strict JSON schema conversion | `JSON_SCHEMA` |
| [`rag-design.md`](rag-design.md) | Full RAG pipeline — chunking, embedding, retrieval, reranking, grounded generation, observability | `ORGANIZATION_NAME`, `CORPUS`, `USE_CASE`, `SCALE`, `QUALITY_BAR` |
| [`eval-design.md`](eval-design.md) | LLM eval framework — metrics by task, test-set sizing, pass/fail thresholds, drift triggers | `ORGANIZATION_NAME`, `FEATURE`, `TASK_TYPE`, `QUALITY_BAR`, `FAILURE_COST` |
| [`cost-optimize.md`](cost-optimize.md) | LLM token spend — tier selection, prompt caching, batching, budget (distinct from DBU) | `ORGANIZATION_NAME`, `CALL_TYPES`, `MODEL_VOLUME`, `LATENCY`, `QUALITY_FLOOR` |
| [`threat-model.md`](threat-model.md) | AI threat model — injection/jailbreak/poisoning/excessive-agency + traditional, severities | `ORGANIZATION_NAME`, `SYSTEM`, `TRUST_BOUNDARIES`, `MODEL_TOOLS`, `ASSETS` |
| [`red-team.md`](red-team.md) | 5-phase adversarial battery (base/app/infra/operational/user-interaction), findings format | `ORGANIZATION_NAME`, `SYSTEM`, `SURFACES`, `MODEL_TOOLS`, `THREAT_MODEL` |
| [`pii-scan.md`](pii-scan.md) | PII exposure audit across lifecycle (collection→logs→prompts→outputs→third-party), remediations | `ORGANIZATION_NAME`, `SYSTEM`, `PII_CATEGORIES`, `THIRD_PARTIES`, `REGIME` |
| [`dlp-design.md`](dlp-design.md) | DLP system design — classify data → egress surfaces → detection per class → enforcement matrix (class × surface) → policy → response/audit; fingerprints store hashes, warn→block rollout, FP counter-metric | `ORGANIZATION_NAME`, `SYSTEM`, `DATA_CLASSES`, `EGRESS_SURFACES`, `REGIME` |
| [`supply-chain-review.md`](supply-chain-review.md) | AI supply-chain audit + AI-BOM — provenance, license, poisoning, CVE risk per component | `ORGANIZATION_NAME`, `SYSTEM`, `MODELS`, `DATASETS`, `DEPENDENCIES` |
| [`observability.md`](observability.md) | AI observability — signal layers (infra/model/quality/drift/business), alerts, drift indicators | `ORGANIZATION_NAME`, `SYSTEM`, `SLOS`, `QUALITY_SIGNALS`, `CHANNELS` |
| [`runbook.md`](runbook.md) | AI incident runbook — detection/triage/mitigation/rollback per scenario, kill switch | `ORGANIZATION_NAME`, `SYSTEM`, `SCENARIOS`, `MITIGATIONS`, `ESCALATION` |
| [`rollout.md`](rollout.md) | Phased rollout (shadow→canary→limited→GA), eval gates, rollback triggers | `ORGANIZATION_NAME`, `CHANGE`, `RISK`, `TRAFFIC`, `ROLLBACK` |
| [`retro.md`](retro.md) | Engineering retrospective — reviews commits, surfaces lessons, writes LESSONS_LEARNED | `TEAM_OR_PROJECT_NAME`, `COMMIT_RANGE`, `GIT_LOG`, `INCIDENT_NOTES`, `DEVELOPER_NOTES` |

**Cloud ML platforms:**

| File | Use case | Key placeholders |
|---|---|---|
| [`vertex-ai-design.md`](vertex-ai-design.md) | GCP Vertex footprint — service split (Workbench / Pipelines / Training / Endpoints / Feature Store / Garden / Monitoring), compute, MLOps, deployment pattern, cost guardrails, observability, lock-in posture | `ORGANIZATION_NAME`, `WORKLOAD_TYPE`, `QPS_TARGET`, `LATENCY_BUDGET`, `REGION`, `PROJECT_LAYOUT`, `BUDGET`, `DATA_SOURCES`, `COMPLIANCE` |
| [`sagemaker-design.md`](sagemaker-design.md) | AWS SageMaker footprint — service split (Studio / Training / Endpoints / Pipelines / Feature Store / Monitor / Clarify / JumpStart), deployment pattern (real-time / async / serverless / batch / MME), compute, MLOps, cost guardrails, lock-in posture | `ORGANIZATION_NAME`, `WORKLOAD_TYPE`, `TRAFFIC_PROFILE`, `LATENCY_BUDGET`, `PAYLOAD_SIZE`, `REGION`, `ACCOUNT_LAYOUT`, `BUDGET`, `DATA_SOURCES`, `COMPLIANCE` |
| [`bedrock-design.md`](bedrock-design.md) | AWS Bedrock GenAI footprint — service split (Models / AgentCore / Knowledge Bases / Guardrails / Flows / Prompt Mgmt / IPR / Eval / Custom Import), model selection (Claude + Nova 2 + Llama + Mistral + Cohere), inference pattern (on-demand / PT / batch / cross-region), KB vector store, Guardrails (incl. Automated Reasoning), IPR routing, lock-in posture | `ORGANIZATION_NAME`, `WORKLOAD_TYPE`, `QPS_OR_BATCH`, `LATENCY_BUDGET`, `REGION`, `ACCOUNT_LAYOUT`, `BUDGET`, `MODEL_FAMILY`, `COMPLIANCE` |
| [`azure-foundry-design.md`](azure-foundry-design.md) | Microsoft Foundry (formerly Azure AI Foundry) footprint — surface map (Ignite Nov 2025 rebrand), 1,900+ model catalog, Foundry Agent Service GA Mar 16 2026, BYO VNet private networking, Foundry IQ + AI Search agentic retrieval, safety stack (Prompt Shields + Groundedness), PTU vs PAYG vs Batch cost model, lock-in posture | `ORGANIZATION_NAME`, `WORKLOAD_NAME`, `WORKLOAD_TYPE`, `SUB_REGION`, `NETWORKING`, `TENANCY`, `MODEL_PREF`, `PTU_APPETITE`, `COMPLIANCE` |
| [`openai-platform-design.md`](openai-platform-design.md) | OpenAI platform footprint (not Azure OpenAI) — Responses API default, Assistants sunset 2026-08-26, model catalog (GPT-5.x / 4.1 / o3 / o4-mini), Agents SDK, Realtime, Vector Stores, tools (Web Search / CUA / Code Interpreter / Structured Outputs strict), Deep Research cost trap, automatic caching, fine-tune trio (SFT/DPO/RFT), Evals sunset 2026-11-30 | `ORGANIZATION_NAME`, `WORKLOAD_NAME`, `WORKLOAD_TYPE`, `ASSISTANTS_USAGE`, `EVALS_USAGE`, `LATENCY_BUDGET`, `TOOLS`, `STRUCTURED_OUTPUT`, `FINE_TUNE_INTENT`, `COMPLIANCE` |
| [`snowflake-cortex-design.md`](snowflake-cortex-design.md) | Snowflake AI/ML footprint — service split (Cortex AISQL / Analyst / Search / Agents / Snowpark ML + Model Registry + Feature Store / SPCS), compute substrate (warehouse vs Cortex serverless vs SPCS pool), governance, credit-based cost guardrails, in-warehouse-batch vs SPCS-real-time deployment, lock-in posture | `ORGANIZATION_NAME`, `WORKLOAD_NAME`, `WORKLOAD_TYPE`, `DATA_SOURCES`, `BUDGET` |
| [`bigquery-ml-design.md`](bigquery-ml-design.md) | BigQuery ML footprint — BQML-vs-export-to-Vertex gate, model_type selection, Gemini-in-BigQuery + VECTOR_SEARCH, on-demand-vs-slot billing, TRANSFORM-clause skew guard, in-warehouse-vs-Vertex serving | `ORGANIZATION_NAME`, `WORKLOAD_NAME`, `TASK_TYPE`, `DATA_VOLUME`, `COMPUTE_MODEL` |

**Infrastructure as code:**

| File | Use case | Key placeholders |
|---|---|---|
| [`terraform-review.md`](terraform-review.md) | Terraform code + plan review — state + locking, modules, providers, secrets, blast-radius (`prevent_destroy` / `ignore_changes`), drift, plan-vs-apply CI, destructive-op safety; [BLOCKER] / [SUGGESTION] / [NITPICK] grouped | `ORGANIZATION_NAME`, `ENVIRONMENT`, `PROVIDERS`, `STATE_BACKEND`, `WORKSPACE_STRATEGY`, `CI_SYSTEM`, `INPUT`, `CHANGE_NOTES` |

**Compliance:**

| File | Use case | Key placeholders |
|---|---|---|
| [`compliance-mapping.md`](compliance-mapping.md) | SOC 2 / HIPAA / GDPR / EU AI Act control mapping — enforcement matrix (code path + evidence + owner + CLEAN/PARTIAL/GAP status), gap register, cross-framework overlap | `ORGANIZATION_NAME`, `FRAMEWORKS`, `SYSTEM_SCOPE`, `DATA_CLASSIFICATION`, `REGIONS`, `USER_POPULATIONS`, `STACK_SUMMARY`, `AI_IN_SCOPE` |

**Analytics / BI:**

| File | Use case | Key placeholders |
|---|---|---|
| [`dashboard-design.md`](dashboard-design.md) | BI dashboard spec — single audience + single question, chart selection rubric, refresh + honest SLA, governance (owner / certification / deprecation), performance budget, accessibility | `ORGANIZATION_NAME`, `AUDIENCE`, `QUESTION`, `SOURCE`, `REFRESH_REQUIREMENT`, `UPSTREAM_SLA`, `TOOL`, `DECISIONS`, `SENSITIVE_SEGMENTS` |

**Auth / Identity (OAuth / OIDC):**

| File | Use case | Key placeholders |
|---|---|---|
| [`oauth-flow-design.md`](oauth-flow-design.md) | Grant selection (auth-code+PKCE/client-credentials/device), redirect-URI allowlist, state+PKCE | `ORGANIZATION_NAME`, `CLIENT_TYPE`, `IDP`, `RESOURCE`, `REDIRECT_URIS` |
| [`oidc-integration.md`](oidc-integration.md) | ID-token vs access-token, discovery/JWKS, nonce, claims→user (`sub`), federation, logout | `ORGANIZATION_NAME`, `IDP`, `APP`, `CLAIMS`, `PROVISIONING` |
| [`jwt-validation.md`](jwt-validation.md) | Verifier-pins-alg, JWKS-by-kid, iss/aud/exp/nbf checks, bounded skew, strict-mode lib | `ORGANIZATION_NAME`, `TOKEN_TYPE`, `ISSUER`, `AUDIENCE`, `KEY_SOURCE` |
| [`token-lifecycle.md`](token-lifecycle.md) | No-localStorage/BFF storage, short TTL, refresh rotation + reuse detection, revocation, cookies | `ORGANIZATION_NAME`, `CLIENT_TYPE`, `TOKENS`, `REVOCATION`, `SESSION_MODEL` |
| [`session-management.md`](session-management.md) | Server vs stateless, HttpOnly/Secure/SameSite/__Host- cookies, CSRF token, fixation/timeouts, SLO | `ORGANIZATION_NAME`, `APP`, `SESSION_MODEL`, `AUTH_SURFACE`, `IDP` |
| [`m2m-auth.md`](m2m-auth.md) | Workload-identity/mTLS over secrets, client-credentials + private_key_jwt, one-audience minimal-scope, vault rotation | `ORGANIZATION_NAME`, `CALLER_TARGET`, `RUNTIME`, `AUDIENCE`, `SECRET_STORE` |
| [`scopes-consent-design.md`](scopes-consent-design.md) | resource:action read/write taxonomy, scope+ownership enforcement, legible consent, incremental auth, over-scoping audit | `ORGANIZATION_NAME`, `API`, `CLIENTS`, `SENSITIVE_OPS`, `PARTY` |

**Data engineering:**

| File | Use case | Key placeholders |
|---|---|---|
| [`nl-to-sql.md`](nl-to-sql.md) | NL → SQL with schema context + safety guardrails | `DIALECT`, `SCHEMA_CONTEXT`, `PARTITION_COLUMN` |
| [`streaming-pipeline.md`](streaming-pipeline.md) | Streaming pipeline — stream vs. batch decision, technology selection, windowing, state management, ML feature integration | `ORGANIZATION_NAME`, `PIPELINE_NAME`, `LATENCY_REQUIREMENT`, `THROUGHPUT`, `DELIVERY_SEMANTIC` |
| [`lakehouse-architecture.md`](lakehouse-architecture.md) | Medallion zones (bronze/silver/gold), table format (Iceberg/Delta/Hudi), partitioning, compaction, query engines, lineage | `ORGANIZATION_NAME`, `SCOPE`, `STORAGE`, `WORKLOADS`, `DATA_PROFILE`, `STACK` |
| [`dbt-model-gen.md`](dbt-model-gen.md) | Generate dbt model SQL + schema.yml from spec | `WAREHOUSE`, `UPSTREAM_REFS` |
| [`pipeline-debugger.md`](pipeline-debugger.md) | Systematic pipeline failure / anomaly diagnosis | `PIPELINE_DESCRIPTION`, `STACK_DESCRIPTION` |
| [`data-dict-gen.md`](data-dict-gen.md) | Auto-generate data dictionary from table schema | `OUTPUT_FORMAT`, `AUDIENCE` |
| [`quality-rules-gen.md`](quality-rules-gen.md) | Generate validation rules → dbt tests or SQL checks | `STACK`, `OUTPUT_FORMAT` |
| [`contract-draft.md`](contract-draft.md) | Draft producer/consumer data contract | `OUTPUT_FORMAT`, `SENSITIVITY_NOTE` |
| [`metadata-audit.md`](metadata-audit.md) | 7-dimension column audit (provenance, collection, units, transform, summarization, labels, cadence) + batch effect | `DATASET_CONTEXT`, `METADATA_SOURCES`, `DOWNSTREAM_USE` |
| [`data-alignment.md`](data-alignment.md) | Row-level multi-source consolidation — entity match, timestamp sync, scale harmonization, batch effect | `SOURCES_CONTEXT`, `TARGET_CONTEXT`, `CONSTRAINTS` |
| [`pipeline-design.md`](pipeline-design.md) | Batch vs streaming, orchestration, idempotency, backfill, SLA | `ORGANIZATION_NAME`, `SOURCES_SINKS`, `LATENCY`, `VOLUME`, `FAILURE_TOLERANCE` |
| [`data-mesh.md`](data-mesh.md) | Domain ownership, data-product specs, federated governance, interoperability | `ORGANIZATION_NAME`, `ORG_DESCRIPTION`, `NUM_PRODUCER_TEAMS`, `CURRENT_PLATFORM`, `COMPLIANCE_REQUIREMENTS` |
| [`data-quality.md`](data-quality.md) | Validation rules, anomaly thresholds, quarantine + replay, SLAs (data-layer gate) | `ORGANIZATION_NAME`, `DATASET`, `CONSUMERS`, `FAILURE_MODES`, `VOLUME_FRESHNESS` |
| [`data-contract.md`](data-contract.md) | Producer/consumer contract — schema ownership, SLAs, versioning, breaking-change policy | `ORGANIZATION_NAME`, `FEED`, `PRODUCER`, `CONSUMERS`, `CHANGE_FREQUENCY` |
| [`schema-design.md`](schema-design.md) | Dimensional model, grain, SCD, partitioning, evolution policy | `ORGANIZATION_NAME`, `ENTITIES`, `QUERY_PATTERNS`, `HISTORY_NEEDS`, `SCALE` |
| [`dbt-review.md`](dbt-review.md) | dbt review — ref/source, incremental correctness, test coverage, layering | `ORGANIZATION_NAME`, `MODELS`, `CONVENTIONS`, `MATERIALIZATION` |
| [`sql-review.md`](sql-review.md) | SQL correctness (join fan-out, NULL, grain) + performance (pruning, sargability) | `ORGANIZATION_NAME`, `QUERY`, `DIALECT`, `SCHEMA`, `SCALE` |

**Databricks integration:**

| File | Use case | Key placeholders |
|---|---|---|
| [`unity-catalog-governance.md`](unity-catalog-governance.md) | UC namespace, group-based grants, ABAC + governed tags (preferred) over row filters / column masks / dynamic views, lineage, system-table audit | `ORGANIZATION_NAME`, `SCOPE`, `GROUPS`, `SENSITIVE_DATA`, `STORAGE` |
| [`databricks-asset-bundles.md`](databricks-asset-bundles.md) | Declarative Automation Bundles (formerly DABs) — resources as code (databricks.yml), per-target envs, service-principal run-as, build-once promote-many, validate gate | `ORGANIZATION_NAME`, `RESOURCES`, `TARGETS`, `SERVICE_PRINCIPALS`, `CI_SYSTEM` |
| [`delta-live-tables.md`](delta-live-tables.md) | Lakeflow Spark Declarative Pipelines (SDP — formerly DLT) — streaming vs materialized, expectations, APPLY CHANGES CDC, triggered vs continuous | `ORGANIZATION_NAME`, `SOURCES`, `TARGET_TABLES`, `LATENCY`, `UC_TARGET` |
| [`databricks-jobs-orchestration.md`](databricks-jobs-orchestration.md) | Lakeflow Jobs (formerly Workflows) DAG, job-cluster/serverless, retries+timeouts+alerts, idempotent repair runs | `ORGANIZATION_NAME`, `TASKS`, `TRIGGER`, `COMPUTE`, `SLA` |
| [`spark-performance-tuning.md`](spark-performance-tuning.md) | Spark-UI-first diagnosis (skew/shuffle/spill/small files/join), AQE+broadcast+clustering fixes, Photon (stateless streaming only) compute last | `ORGANIZATION_NAME`, `JOB`, `SYMPTOM`, `EVIDENCE`, `DATA_SCALE` |
| [`dbu-cost-optimization.md`](dbu-cost-optimization.md) | system.billing attribution (via `billing_origin_product` enum), jobs vs all-purpose, serverless/Photon/spot, auto-termination, cluster-policy guardrails | `ORGANIZATION_NAME`, `ATTRIBUTION`, `WORKLOADS`, `SLAS`, `COMPUTE_SETUP` |
| [`databricks-model-serving.md`](databricks-model-serving.md) | UC model → endpoint, serve-by-alias rollout, scale-to-zero vs warm, traffic-split canary, inference tables | `ORGANIZATION_NAME`, `UC_MODEL`, `ALIAS`, `ENDPOINT_TYPE`, `TRAFFIC`, `LATENCY_SLA` |
| [`mosaic-ai-vector-search.md`](mosaic-ai-vector-search.md) | Databricks AI Search (formerly Mosaic AI Vector Search) — Delta Sync index, pinned embeddings, hybrid search + UC ACLs, recall@k eval | `ORGANIZATION_NAME`, `SOURCE`, `EMBEDDING`, `FILTERS`, `QUALITY_TARGET` |
| [`auto-loader-ingestion.md`](auto-loader-ingestion.md) | Incremental cloudFiles → Delta bronze, file events (managed `useManagedFileEvents`) preferred, `_rescued_data`, dedicated-checkpoint exactly-once | `ORGANIZATION_NAME`, `LANDING_ZONE`, `FORMAT_VOLUME`, `SCHEMA_STABILITY`, `LATENCY` |
| [`databricks-agent-framework.md`](databricks-agent-framework.md) | Mosaic AI Agent Framework — MLflow ChatAgent/ResponsesAgent contract, Tracing/autolog, Agent Evaluation judge harness (`mlflow.genai.evaluate`), UC-function tools, register to UC | `ORGANIZATION_NAME`, `AGENT_TASK`, `TOOLS`, `UC_TARGET`, `GROUND_TRUTH` |
| [`lakehouse-monitoring.md`](lakehouse-monitoring.md) | Databricks data-profiling monitor over a Delta/inference table — profile type (Snapshot/TimeSeries/InferenceLog), baseline, slices, `_profile_metrics`/`_drift_metrics`, inference→drift-alert loop | `ORGANIZATION_NAME`, `TABLE`, `TABLE_KIND`, `PROBLEM_TYPE`, `BASELINE` |

**Data cleansing / normalization:**

| File | Use case | Key placeholders |
|---|---|---|
| [`data-cleanse.md`](data-cleanse.md) | Detection rules + remediation SQL for dirty data | `DIALECT`, `SCHEMA_CONTEXT`, `KNOWN_ISSUES` |
| [`dedup-matcher.md`](dedup-matcher.md) | Blocking strategy, scoring, golden record, merge rules | `ENTITY_TYPE`, `AVAILABLE_FIELDS`, `AUTO_MATCH_THRESHOLD` |
| [`schema-harmonizer.md`](schema-harmonizer.md) | Multi-source canonical mapping + transformation SQL | `SOURCE_SCHEMAS`, `TARGET_WAREHOUSE`, `PRIORITY_SOURCE` |
| [`timeseries-resample.md`](timeseries-resample.md) | Upsample/downsample by metric type + gap handling | `STACK`, `SERIES_CONTEXT`, `SOURCE_FREQUENCY`, `TARGET_FREQUENCY` |
| [`class-balancing.md`](class-balancing.md) | Class imbalance strategy + eval setup + threshold tuning | `DATASET_CONTEXT`, `MODEL_TYPE`, `BUSINESS_OBJECTIVE` |
| [`schema-harmonization.md`](schema-harmonization.md) | Schema-level merge — conflict types, canonical design, source priority (vs row-level data-alignment) | `ORGANIZATION_NAME`, `SOURCES`, `TARGET_USE`, `CONFLICTS` |
| [`dedup.md`](dedup.md) | Entity resolution — exact/fuzzy, blocking, scoring, golden record, merge rules | `ORGANIZATION_NAME`, `RECORDS`, `ATTRIBUTES`, `PURPOSE`, `SCALE` |

**Data labeling:**

| File | Use case | Key placeholders |
|---|---|---|
| [`annotation-guidelines.md`](annotation-guidelines.md) | Generate annotation instructions + decision tree + edge case catalog | `TASK_DESCRIPTION`, `LABEL_TAXONOMY`, `ANNOTATOR_AUDIENCE` |
| [`label-qa.md`](label-qa.md) | Review labeled dataset — disagreements, drift, guideline gaps | `TASK_DESCRIPTION`, `LABEL_TAXONOMY`, `IAA_TARGET` |
| [`active-learning-selector.md`](active-learning-selector.md) | Select next annotation batch for maximum model improvement | `LABELED_COUNT`, `MODEL_BASELINE`, `BATCH_SIZE` |
| [`annotation-design.md`](annotation-design.md) | Label taxonomy, guidelines, edge-case decision tree, task decomposition | `ORGANIZATION_NAME`, `TASK`, `LABELS`, `ANNOTATORS`, `AMBIGUITIES` |
| [`label-quality.md`](label-quality.md) | IAA metrics (κ/α/ICC/F1), adjudication workflow, thresholds, audit cadence | `ORGANIZATION_NAME`, `TASK`, `ANNOTATORS`, `AGREEMENT` |
| [`active-learning.md`](active-learning.md) | Query strategy by labeled-set size, uncertainty+diversity, batch selection, stopping rule | `ORGANIZATION_NAME`, `LABELED`, `POOL`, `MODEL_TASK`, `BUDGET` |

**Data splitting:**

| File | Use case | Key placeholders |
|---|---|---|
| [`split-design.md`](split-design.md) | Train/val/test split strategy + leakage verification | `DATASET_CONTEXT`, `TASK_TYPE`, `CONSTRAINTS` |
| [`cv-design.md`](cv-design.md) | CV variant selection + nested CV configuration | `DATASET_CONTEXT`, `TASK_TYPE`, `COMPUTE_BUDGET` |
| [`leakage-audit.md`](leakage-audit.md) | Audit pipeline for data leakage + code fixes | `PIPELINE_CONTEXT`, `FEATURE_LIST`, `PERFORMANCE_CONCERN` |
| [`cdc-design.md`](cdc-design.md) | CDC capture-side — mechanism (log/query/trigger), snapshot→incremental cutover (no gap/dupe), delete/tombstone handling, DDL propagation, idempotent dedup into sink | `ORGANIZATION_NAME`, `SOURCE_ENGINE`, `TABLES`, `SINK`, `DELETES_MATTER` |
| [`data-observability.md`](data-observability.md) | Estate-wide run-time data observability — five pillars as auto-baselined monitors, column-level lineage for root-cause, incident lifecycle, build-vs-buy axes | `ORGANIZATION_NAME`, `ESTATE`, `CONSUMERS`, `LINEAGE_STATE`, `GAPS` |
| [`cross-validation.md`](cross-validation.md) | CV variant by structure (time/group/imbalance), leakage guards, nested CV, reporting | `ORGANIZATION_NAME`, `SIZE`, `STRUCTURE`, `TASK_METRIC`, `TUNING` |

**ML algorithm selection / tuning:**

| File | Use case | Key placeholders |
|---|---|---|
| [`algo-select.md`](algo-select.md) | Select algorithm by task type + constraints | `TASK_CONTEXT`, `CONSTRAINTS` |
| [`experiment-design.md`](experiment-design.md) | ML experiment queue — hypotheses, one-variable control, decision criteria, ordered by information gain | `PROJECT_NAME`, `BASELINE_METRIC`, `IMPROVEMENT_HYPOTHESES` |
| [`training-infrastructure.md`](training-infrastructure.md) | Compute selection, distributed training strategy, orchestration, cost estimate | `MODEL_TYPE`, `PARAMETER_COUNT`, `DATASET_SIZE`, `COST_BUDGET` |
| [`hyperparameter-tuning.md`](hyperparameter-tuning.md) | Tuning strategy (random / Bayesian) + search space | `ALGORITHM_CONTEXT`, `COMPUTE_BUDGET`, `OPTIMIZATION_METRIC` |
| [`model-comparison.md`](model-comparison.md) | Statistical model comparison + production verdict | `MODELS_TO_COMPARE`, `EVALUATION_METRIC`, `DATASET_CONTEXT` |
| [`transfer-learning.md`](transfer-learning.md) | Source-model selection, adaptation strategy (feature-extract / partial / full / adapter / LoRA), negative-transfer check, catastrophic-forgetting mitigation | `TARGET_TASK_CONTEXT`, `SOURCE_CANDIDATES`, `CONSTRAINTS` |

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
| [`imputation-design.md`](imputation-design.md) | Missing-value strategy — MCAR/MAR/MNAR diagnosis, method selection (deletion/mean/KNN/MICE/model/time-aware), missingness-indicator, fit-on-train-only, distortion check | `DATASET_CONTEXT`, `MISSINGNESS_SUMMARY`, `DOWNSTREAM_MODEL` |

**Model validation:**

| File | Use case | Key placeholders |
|---|---|---|
| [`model-validation.md`](model-validation.md) | Pre-deploy checklist — performance, slices, edge cases, latency, Go/No-Go | `MODEL_CONTEXT`, `PERFORMANCE_BASELINE`, `DEPLOYMENT_CONSTRAINTS` |
| [`model-calibration.md`](model-calibration.md) | Probability calibration — ECE, reliability diagram, Platt/isotonic/temperature | `MODEL_CONTEXT`, `CALIBRATION_GOAL`, `STACK` |
| [`model-drift.md`](model-drift.md) | Production drift detection — data / concept / prediction drift + retraining triggers | `MODEL_CONTEXT`, `MONITORING_CONTEXT`, `STACK` |
| [`conformal-uncertainty.md`](conformal-uncertainty.md) | Distribution-free UQ via split conformal — prediction sets (classification) + intervals (regression) with coverage guarantee, nonconformity score, calibration-set sizing, adaptive variants, coverage-loss-under-shift monitor | `MODEL_CONTEXT`, `COVERAGE_REQUIREMENT`, `DATA_SHIFT_CONTEXT` |
| [`decision-threshold-policy.md`](decision-threshold-policy.md) | Score→decision — cost-optimal operating point (not 0.5), ROC-vs-PR by imbalance, prevalence-drift handling, multi-tier bands, abstention/reject-option sized to review capacity | `MODEL_CONTEXT`, `DECISION_COSTS`, `OPERATIONAL_CONSTRAINTS` |

**Model deployment:**

| File | Use case | Key placeholders |
|---|---|---|
| [`model-deployment.md`](model-deployment.md) | Artifact packaging, phased rollout (shadow→canary→GA), rollback triggers, deployment.yaml | `MODEL_CONTEXT`, `TARGET_ENVIRONMENT`, `ROLLOUT_CONSTRAINTS` |
| [`edge-ml-deployment.md`](edge-ml-deployment.md) | Edge-vs-cloud gate, per-stage latency budget, signed atomic OTA + offline rollback, fail-safe fallback, OT advises-not-actuates | `ORGANIZATION_NAME`, `MODEL_USE_CASE`, `LATENCY_BUDGET`, `TARGET_HARDWARE`, `SAFETY_CLASS` |
| [`inference-service-design.md`](inference-service-design.md) | REST/gRPC/batch pattern, latency budget, scaling, circuit breaker, fallback | `MODEL_CONTEXT`, `TRAFFIC_REQUIREMENTS`, `INFRASTRUCTURE_CONSTRAINTS` |
| [`model-decommissioning.md`](model-decommissioning.md) | Retire a model — retirement criteria, dependency audit, notification, archive policy | `MODEL_CONTEXT`, `SUCCESSOR_CONTEXT`, `CONSTRAINTS` |

**Responsible AI:**

| File | Use case | Key placeholders |
|---|---|---|
| [`bias-audit.md`](bias-audit.md) | Training-data bias audit (6 classes: sample-selection, demographic, geographic, temporal, labeler, survivorship); run BEFORE training | `OPERATIONAL_ENV`, `TRAINING_DATA_CONTEXT`, `LABELING_CONTEXT` |
| [`fairness-audit.md`](fairness-audit.md) | Model-output fairness audit — demographic parity, disparate impact, equal opportunity, mitigation | `MODEL_CONTEXT`, `PROTECTED_ATTRIBUTES`, `REGULATORY_CONTEXT` |
| [`explainability.md`](explainability.md) | SHAP / LIME / counterfactuals — global + local explanations by audience | `MODEL_CONTEXT`, `EXPLANATION_GOALS`, `AUDIENCE` |
| [`privacy-preserving-ml.md`](privacy-preserving-ml.md) | PPML mechanism — DP/DP-SGD/FL/anonymization per data flow, epsilon budget, inference-threat→defense map, privacy-utility tradeoff, residual-risk register | `SYSTEM_CONTEXT`, `DATA_FLOWS`, `ADVERSARY_MODEL`, `OBLIGATION_AND_UTILITY` |
| [`data-deidentification-design.md`](data-deidentification-design.md) | De-identification treatment — per-field technique selection, direct-vs-quasi-identifier classification, re-id risk scoring, utility-vs-privacy matrix + release verdict | `ORGANIZATION_NAME`, `FIELDS`, `RELEASE_CONTEXT`, `DOWNSTREAM_TASK`, `REGIME` |
| [`human-oversight-design.md`](human-oversight-design.md) | In-path human-oversight loop for non-agentic ML — escalation routing + queue sizing (Little's Law), override/appeal/contest flow, automation-bias mitigation, oversight metrics keyed to risk tier | `ORGANIZATION_NAME`, `SYSTEM`, `RISK_TIER`, `ARRIVAL_RATE`, `APPEAL_REQUIRED` |

**MLOps / Lifecycle:**

| File | Use case | Key placeholders |
|---|---|---|
| [`experiment-tracking.md`](experiment-tracking.md) | Run logging schema, registry promotion criteria, reproducibility checklist | `PROJECT_CONTEXT`, `TRACKING_TOOL`, `REPRODUCIBILITY_REQUIREMENTS` |
| [`ab-test-design.md`](ab-test-design.md) | Sample size, assignment strategy, guardrail metrics, stopping rules, analysis plan | `EXPERIMENT_CONTEXT`, `TRAFFIC_METRICS_CONTEXT`, `BUSINESS_CONSTRAINTS` |
| [`retraining-strategy.md`](retraining-strategy.md) | Trigger types, data window design, full vs. incremental, promotion gates | `MODEL_CONTEXT`, `MONITORING_CONTEXT`, `RETRAINING_CONSTRAINTS` |
| [`data-versioning.md`](data-versioning.md) | Dataset versioning, DVC / time-travel, lineage chain, reproducibility | `DATA_INFRASTRUCTURE_CONTEXT`, `VERSIONING_REQUIREMENTS`, `COMPLIANCE_CONTEXT` |
| [`mlops-cicd.md`](mlops-cicd.md) | ML CI/CD pipeline stages, quality gates, artifact schema, rollback spec | `MODEL_FRAMEWORK_AND_STORE`, `TARGET_ENVIRONMENT`, `CI_PLATFORM` |
| [`responsible-ai-governance.md`](responsible-ai-governance.md) | AI governance framework — risk tiers, MRM checklist, review gates, EU AI Act | `USE_CASE_INVENTORY`, `REGULATORY_CONTEXT`, `ORG_CONTEXT` |
| [`model-compression.md`](model-compression.md) | Compression technique selection + code + eval plan on target hardware | `MODEL_CONTEXT`, `LATENCY_TARGET`, `TARGET_HARDWARE` |
| [`feature-monitoring.md`](feature-monitoring.md) | Feature health monitoring — freshness, null rate, schema drift, PSI, alerts | `FEATURE_LIST`, `SERVING_STACK`, `IMPORTANCE_RANKING` |
| [`fine-tune.md`](fine-tune.md) | Fine-tune vs prompt/RAG decision, dataset requirements, method, eval plan, cost-benefit | `ORGANIZATION_NAME`, `TASK`, `GAP`, `DATA`, `CONSTRAINTS` |
| [`model-card.md`](model-card.md) | 9-section model card + governance checklist (intended use, limits, fairness) | `ORGANIZATION_NAME`, `MODEL`, `INTENDED_USE`, `TRAINING_DATA`, `EVAL_RESULTS` |
| [`feedback-loop.md`](feedback-loop.md) | Production feedback — signal collection, annotation routing, improvement flow | `ORGANIZATION_NAME`, `SYSTEM`, `SIGNALS`, `LEVERS`, `VOLUME` |

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
