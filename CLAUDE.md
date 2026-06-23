# CLAUDE.md

Guidance for Claude Code working in this repo. Auto-loaded at the start of every session.

---

## What this repo is

**[PROJECT NAME]** — [one sentence: what it is, who it's for, what problem it solves].

[Optional: one sentence on what this repo is NOT — helps Claude avoid scope creep.]

<!-- Example: **Retail Pricing Engine** — ML service that updates product prices daily using demand signals; serves the merchandising team. Not a general pricing framework — single-tenant, single-SKU-hierarchy only. -->

---

## Session-start protocol

Before any tool calls beyond basic orientation:

1. Read [`NEXT_SESSION.md`](NEXT_SESSION.md) — resume bookmark: HEAD, branch, what landed last session, open items, things NOT to do without explicit instruction
2. Read [`LESSONS_LEARNED.md`](LESSONS_LEARNED.md) — process lessons from prior sessions; re-reading prevents repeat mistakes
3. Read this file — repo posture and constraints
4. `git status` + `git log --oneline -5` — confirm state matches the bookmark
5. Only then ask the user what they want to work on — do not start anything proactively

---

## Source of truth

[Optional — delete this section if your project has no single canonical reference file.]

**[FILENAME]** is the canonical source for [what it defines — e.g., schema, feature list, API spec, pricing].

The `[Used in / Referenced by]` column (or equivalent) maps each row to downstream files that need follow-up edits.

**Never** edit a derived file without updating the source of truth in the same change.

---

## Repo structure

```
[PROJECT NAME]/
├── CLAUDE.md                  ← This file
├── LESSONS_LEARNED.md         ← Process lessons (re-read each session)
├── scratch/                   ← Gitignored; NEXT_SESSION.md and personal workspace
├── context/                   ← Claude's persistent project memory
│   └── MEMORY.md              ← Memory index
├── prompts/                   ← System prompt templates (RAG, agent, chat, classifier, etc.)
│   └── README.md              ← Template index + how-to-use guide
├── templates/
│   ├── adr/ADR-TEMPLATE.md    ← ADR template (used by /adr skill)
│   └── skill/                 ← Skill authoring guide
│       ├── SKILL-TEMPLATE.md  ← Annotated template — copy to .claude/skills/<name>/SKILL.md
│       └── REFERENCE-TEMPLATE.md ← Optional reference doc template
└── [your project files here]
```

---

## Sprint workflow

For any non-trivial task, follow this order:

1. **Assumptions** — run `/office-hours` to surface unstated assumptions and produce a design doc before writing code
2. **Plan** — agree on approach; use `/tradeoff` if options need evaluating, `/adr` if a decision needs recording
3. **Implement** — build against the design doc; invoke Confusion Protocol if new ambiguity surfaces
4. **Review** — run `/review` before opening a PR
5. **Ship** — feature branch + PR; no direct commits to master
6. **Retro** — run `/retro` at end of session or sprint; write new lessons to LESSONS_LEARNED.md

Skip steps only with explicit agreement — not because the task feels small.

---

## Working conventions

[Fill in: start with 3–5 entries. Remove examples you don't use. Add more as conventions crystallize across sessions.]

- [Naming conventions — files, variables, branches]
- [How tests are run and what "passing" means for this project]
- [PR / commit conventions — branch naming, squash vs. merge, etc.]
- [Any file that must never be edited directly (generated files, lockfiles, etc.)]
- [Stack-specific: language version, formatter, linter commands]
- **Skill authoring (standing):** whenever a new skill is added under `.claude/skills/`, ALWAYS also (1) add a corresponding prompt template in `prompts/<name>.md` and (2) wire the skill into the CLAUDE.md Automation index (and the `prompts/README.md` index). A skill is not "done" until both exist. **Exempt from the prompt-template requirement:** workflow / facilitator / agent-spawning skills that *are* the prompt or spawn a subagent rather than parameterize an LLM system prompt — `adr`, `office-hours`, `retro`, `review`, `tradeoff`, `prompt-review`, `api-audit`, `security-audit`, `security-model-init`, `doc-ci-check`. These still get a CLAUDE.md index entry but no `prompts/<name>.md`. A stale-check should not re-flag them. The same list is mirrored in `.claude/skills/doc-ci-check/SKILL.md` and `.github/workflows/doc-ci.yml` — keep all three in sync.

**Confusion Protocol** — when facing an architectural decision or ambiguous requirement, stop and surface the assumption explicitly before proceeding. Never guess on design decisions. Ask one targeted question instead of producing output that may be wrong.

**AGENTS.md interop (multi-host repos)** — if this repo will be used with Codex / Cursor / Gemini CLI / Aider alongside Claude Code, keep the project rules in a single source-of-truth `AGENTS.md` at the repo root and have `CLAUDE.md` IMPORT it via `@AGENTS.md` (or a symlink). Claude Code as of mid-2026 does NOT read `AGENTS.md` directly, so the import is required; the other tools read `AGENTS.md` natively. This pattern keeps a single rules file usable across hosts without duplication. If the template is Claude-Code-only, ignore this — `CLAUDE.md` alone suffices.

---

## Tone and output constraints

[Fill in: keep only what applies; delete the rest. These become hard constraints Claude follows without being reminded.]

- No emojis in [artifacts / commits / output] unless explicitly requested
- Numeric where possible — no adjectives doing numeric work ("significant improvement" fails; "42% latency reduction" passes)
- Every recommendation names a failure mode — no universally-best options
- Comments in code: only when the WHY is non-obvious. No "this function does X" comments.
- [Language / framework style guide link if applicable]

---

## Security primer

When this project grows a user-facing surface (auth, DB, API, file uploads, public reads):

1. **Commit #2 of that growth:** run `/security-model-init` to scaffold `docs/SECURITY_MODEL.md`. Don't write the next code change until §4's enforcement table has no empty cells (or the empty cells are tracked in §6 with target close dates).
2. **Before any multi-PR sprint touching DB/auth:** run `/security-audit`. Triage CRITICAL/HIGH must be fixed before sprint starts.
3. **Before production deploy:** run `/security-audit` again. Pre-launch gating, not post-launch reactive.

Universal mental model — **the API endpoint you wrote is one path to the data; auto-generated REST/GraphQL endpoints, mobile SDK queries, public file URLs are others.** Every invariant the API enforces must independently exist at the data layer (RLS / Firestore Rules / Hasura permissions / DB triggers / column-level REVOKE / service-role-only writes). "I check it in the action" is decorative if `curl` against the auto-surface bypasses it.

Full protocol: see `operating-philosophy.md` § Security thinking. Pre-merge independent reviewer policy applies to every PR touching auth flow, RLS / authorization rules, DB triggers/functions, payment state, or any "safety property" comment.

---

## Things to avoid

- Don't commit directly to `master` — all changes via feature branch + PR
- Don't push to remote without explicit user instruction
- Don't use long PowerShell here-strings for commit messages — hits 948-byte parse limit; use inline `-m "..."` instead

**Four failure modes to guard against (Karpathy):**
- **Wrong assumptions** — don't guess at intent; surface the assumption and ask
- **Overcomplexity** — don't add abstraction, generalization, or flexibility the task doesn't require
- **Orthogonal edits** — don't touch code outside the stated task scope; no drive-by cleanup
- **Imperative over declarative** — prefer describing the desired outcome over prescribing steps

---

## Automation

**Custom skills** (type in Claude Code prompt — skills live in `.claude/skills/`):

*Business discovery:*
- `/stakeholder-interview` — **Business Discovery Facilitator** — structured six-group discovery interview; Discovery Summary Card output before any ML framing
- `/ml-readiness` — **ML Strategy Advisor** — 5-stage maturity (Initial → Development → Competent → Proficient → Advanced) + AI Hierarchy of Needs (Collect → Move/Store → Explore → Aggregate/Label → Learn → Optimize → AI); build/buy/partner balance per stage; process-as-IP framing; 5-year roadmap
- `/stakeholder-comms` — **ML Communications Advisor** — audience map (exec / user / mgmt / data team); Rider/Elephant/Path framework; reporting cadence templates (1-para / 1-page exec / detailed); failure-comms patterns; adoption-signal tracking
- `/opportunity-sizing` — **AI Opportunity Analyst** — status quo cost + AI uplift + build cost + go/no-go recommendation
- `/kpi-mapping` — **KPI-to-Metric Mapper** — 4-level chain from business objective to ML metric; translation failure modes + counter-metric
- `/metric-gaming-audit` — **Metric Gaming Auditor** — Goodhart's law guard; proxy-quality scoring; per-actor gaming-path enumeration; secondary effects (unexpected benefits/drawbacks/perverse results); counter-metric + multi-metric balance; run BEFORE committing to any optimization target

*Problem framing / EDA:*
- `/problem-framing` — **ML Problem Framing Advisor** — ML vs. rules decision; solution type; success metric tied to KPI; non-ML baseline; problem statement card
- `/eda` — **Exploratory Data Analyst** — dataset profiling (target, missingness, cardinality, correlations, leakage candidates); EDA summary report
- `/cohort-analysis` — **Cohort Analysis Specialist** — segment by acquisition/behavioral/attribute cohorts; outcome comparison with significance tests, retention curves, distribution shifts
- `/time-series-eda` — **Time Series Data Analyst** — stationarity (ADF+KPSS), trend (Mann-Kendall), seasonality (STL), ACF/PACF, structural breaks, anomaly detection
- `/feature-correlation` — **Feature Relationship Analyst** — Pearson/Spearman/MI by variable type, VIF multicollinearity, Cramér's V for categoricals, interaction candidate detection

*Unsupervised learning:*
- `/clustering` — **Clustering Advisor** — algorithm selection (k-means/DBSCAN/GMM/hierarchical); k decision (elbow+silhouette); stability testing; cluster profiling
- `/dim-reduction` — **Dimensionality Reduction Advisor** — PCA/UMAP/t-SNE by goal; variance explained; component count; t-SNE visualization-only rule enforced
- `/topic-modeling` — **Topic Modeling Advisor** — LDA/NMF/BERTopic selection; preprocessing pipeline; coherence-based k decision; topic labeling; downstream feature rules

*Reinforcement learning:*
- `/bandit-design` — **Bandit Strategy Designer** — epsilon-greedy/UCB/Thompson Sampling/LinUCB; reward model; exploration parameters; stopping criteria; bandit vs A/B test decision
- `/rl-design` — **RL System Designer** — RL justification gate; MDP specification; DQN/PPO/SAC/TD3/offline RL/RLHF selection; reward design pitfalls; safety constraints; multi-seed evaluation

*ML domain skills:*
- `/time-series-forecasting` — **Time Series Forecasting Advisor** — ARIMA/SARIMA order from ACF/PACF; ETS; Prophet; N-BEATS/TFT; time series CV; seasonal naive baseline gate
- `/recommender-design` — **Recommender System Designer** — CF/content-based/two-tower/sequential; two-stage pipeline; cold-start strategy; temporal split evaluation; exploration integration
- `/nlp-pipeline` — **NLP Pipeline Designer** — preprocessing decisions; TF-IDF/BERT/SBERT/LLM selection by task; entity-level F1/ROUGE/BERTScore; TF-IDF baseline gate
- `/anomaly-detection` — **Anomaly Detection Specialist** — method by data type + label availability (Z-score/IQR/Isolation Forest/LOF/LSTM-AE/CUSUM); threshold strategy; FPR evaluation; treatment decision
- `/causal-inference` — **Causal Inference Advisor** — method selection (DiD/PSM/IPW/IV/RDD); assumption validation; effect estimate with 95% CI; sensitivity analysis; estimand stated before method
- `/survival-analysis` — **Survival Analysis Advisor** — method by censoring type (KM/Cox PH/RSF/AFT/Fine-Gray); PH assumption validation; survival curves + log-rank; C-statistic + calibration
- `/computer-vision` — **Computer Vision Advisor** — architecture by task × dataset size (CNN/ViT/YOLO/SegFormer); preprocessing + augmentation; mAP@0.5:0.95; 3-phase transfer learning
- `/online-learning` — **Online Learning Advisor** — streaming ML (Hoeffding Tree/HAT/VW); concept drift detection (ADWIN/EDDM); prequential evaluation; batch retrain recommended when viable
- `/predictive-maintenance` — **Predictive Maintenance Advisor** — frames anomaly vs RUL vs failure-classification by failure-event count; lead-time gate (horizon = parts + scheduling + repair); cost-weighted threshold; leakage-audited features; alert→work-order policy

*Industrial / IoT (OT data):*
- `/uns-contextualization` — **Unified Namespace Architect** — ISA-95 namespace hierarchy; asset/digital-twin models (class once, instance per unit); raw-tag → business-concept map stored as versioned data; non-destructive (`_raw` preserved); per-signal owner/unit/freshness SLA
- `/industrial-iot-ingestion` — **Industrial IoT Ingestion Architect** — OT protocol selection (OPC-UA/MQTT+Sparkplug B/Modbus); edge gateway store-and-forward (no-loss on outage); source/edge event-time stamping; OT→IT one-way boundary (no control path); deadband volume control

*General:*
- `/office-hours` — **Assumptions Facilitator** — assumptions gate; six forcing questions + design doc before any implementation
- `/review` — **Code Reviewer** — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format
- `/adr` — **ADR Facilitator** — draft an Architecture Decision Record
- `/tradeoff` — **Tradeoff Analyst** — structured tradeoff analysis for a decision
- `/retro` — **Retrospective Facilitator** — engineering retrospective; reviews recent commits, surfaces lessons, writes to LESSONS_LEARNED.md
- `/security-model-init` — **Security Model Scaffolder** — generates `docs/SECURITY_MODEL.md` with stack-specific scaffolding (Supabase/Firebase/Hasura/FastAPI/Express). Run as commit #2 on any new project that has auth/DB/API surfaces.
- `/security-audit` — **Security Researcher** — deep audit of the codebase from an attacker's perspective. CRITICAL→LOW findings with file+line citations. Use BEFORE multi-PR sprints touching DB/auth, BEFORE production deploy, AFTER major feature sweeps.
- `/doc-ci-check` — **Doc-CI Gate** — count drift + broken-link + skill↔prompt↔CLAUDE↔README↔prompts/README parity + NEXT_SESSION HEAD freshness. Severity-grouped report. Run BEFORE shipping any docs commit and AFTER adding a skill/prompt/hook. Pair with `.github/workflows/doc-ci.yml` for CI enforcement.

*Research and analysis:*
- `/api-audit` — **API Ecosystem Analyst** — structured API portfolio audit (6-phase: discovery → inventory → shortcomings → recommendations → executive summary → options analysis); enforces primary-source verification, cross-file consistency, and advisor review gates

*Production systems:*
- `/threat-model` — **AI Threat Modeling Analyst** — AI-specific threat modeling (8 threat categories + traditional security)
- `/rollout` — **Rollout Planner** — phased rollout plan with eval gates and rollback triggers
- `/runbook` — **Incident Runbook Author** — AI incident runbook (8 standard failure scenarios)
- `/pii-scan` — **PII Exposure Auditor** — PII exposure audit across the AI data lifecycle
- `/observability` — **Observability Stack Designer** — AI observability stack design (signal layers, metrics, alerts, drift indicators)

*Auth / Identity (OAuth / OIDC):*
- `/oauth-flow-design` — **OAuth 2.x Flow Architect** — grant selection by client (auth-code+PKCE / client-credentials / device); redirect-URI exact-match allowlist; state + PKCE; implicit/password rejected
- `/oidc-integration` — **OIDC Integration Architect** — ID-token vs access-token; discovery + JWKS; nonce; claims→user via `sub`(+`iss`) not email; IdP federation; RP-initiated + back-channel logout
- `/jwt-validation` — **JWT Validation Engineer** — verifier-pins-alg (reject `none`, RS↔HS confusion); JWKS-by-`kid`; `iss`/`aud`/`exp`/`nbf` checks; bounded skew; strict-mode lib (most auth CVEs live here)
- `/token-lifecycle` — **Token Lifecycle Engineer** — no-localStorage/BFF storage; short access TTL; refresh rotation + reuse detection → family revoke; introspection/deny-list; secure-cookie attrs
- `/session-management` — **Session Management Engineer** — server-side vs stateless; HttpOnly+Secure+SameSite+__Host- cookies; CSRF token beyond SameSite; id-regen on login; idle+absolute timeout; logout + SLO
- `/m2m-auth` — **M2M Auth Engineer** — workload-identity/mTLS over static secrets; client-credentials + `private_key_jwt`; one-audience minimal-scope tokens; per-service credential; vault + rotation
- `/scopes-consent-design` — **Scopes & Consent Designer** — `resource:action` read/write-split taxonomy (no `full_access`); scope + per-resource ownership/RBAC; legible consent; incremental auth; over-scoping audit

*AI / LLM projects:*
- `/eval-design` — **LLM Evaluation Designer** — LLM evaluation framework (metric taxonomy, test set sizing, drift triggers)
- `/prompt-review` — **Prompt Quality Reviewer** — 9-dimension prompt health score
- `/rag-design` — **RAG System Architect** — RAG system design (chunking, embedding, retrieval, reranking, observability)
- `/agent-design` — **Agentic System Designer** — agentic system design (stateless loop + durable session store convergence, tool manifest, sandbox + reach, guardrails, Plan-Execute-Verify-Replan, fallbacks)
- `/agent-memory` — **Agent Memory Architect** — memory layer for long-running agents: tier selection (core/working/session/episodic/semantic/procedural), backing-store choice (file/KV/vector/graph/temporal-graph), validity-window discipline (asserted_at + expires_at + superseded_by), stale-context detection, per-tenant isolation at storage layer, memory-quality eval (factual recall / preference adherence / time-sensitivity / cost-per-recall). Sibling to `/agent-design` (loop+tools) and `/rag-design` (retrieval-time semantics)
- `/plan-mode` — **Plan-Mode Author** — produces versioned executable plan artifact at scratch/PLAN-<task>.md; subgoal DAG with depends_on + parallel_with; per-subgoal observable exit criterion + rollback (or [RISK: HIGH] flag); cost roll-up vs envelope; interleaved verify gates; Replan triggers + Reflexion-style lessons. Sits between `/office-hours` (assumptions) and implementation
- `/workflow-design` — **Workflow Architect** — deterministic multi-agent workflow design: fan-out shape (parallel barrier / pipeline / loop-until / tournament), phase + grader (Performance Outcomes) pattern, adversarial-verify N=3 with diverse reasoning methods, journaling + resume, budget + concurrency caps (default 16-concurrent / 1000-per-run), structured output schemas, host choice (Anthropic Workflow tool / LangGraph 1.0 / OpenAI Agents SDK / Google ADK / hand-rolled), observability. Distinct from `/multi-agent-design` (architectural pattern) and `/agent-design` (single loop)
- `/mcp-design` — **MCP Server Designer** — MCP server design: tool/resource/prompt manifests; transport (stdio vs Streamable HTTP — note HTTP+SSE deprecated since spec 2025-03-26); auth (OAuth 2.1+PKCE with RFC 9728 PRM + RFC 8414/OIDC discovery + RFC 8707 resource indicators + RFC 9207 `iss` validation; DCR / RFC 7591 deprecated, prefer OAuth Client ID Metadata Documents); schema discipline; scope boundaries; error contract + idempotency; deferred-tool strategy; host-compatibility matrix; observability + audit log. Producer side (complements `/agent-design`)
- `/multi-agent-design` — **Multi-Agent System Designer** — orchestration pattern + framework (LangGraph/CrewAI/AutoGen); agent roster; state schema; failure handling; max_iterations gate
- `/guardrails-design` — **Guardrails System Designer** — input/output safety layers; threat inventory; detection per threat (Llama Guard/Presidio/NLI); latency budget; FPR targets; fail-open vs. fail-closed
- `/red-team` — **AI Red Team Lead** — 5-phase AI red team battery (base model → app → infra → operational → user-interaction adversarial)
- `/model-card` — **Model Documentation Author** — model documentation standard (9 sections, governance checklist)
- `/supply-chain-review` — **AI Supply Chain Auditor** — AI model supply chain audit + AI-BOM generation
- `/cost-optimize` — **Token Cost Optimizer** — token spend analysis (model tier selection, caching strategy, batch decisions)
- `/feedback-loop` — **Feedback Loop Designer** — production feedback loop design (signal collection, annotation, improvement routing)
- `/fine-tune` — **Fine-Tuning Advisor** — fine-tune vs. prompt decision tree (dataset requirements, eval plan, cost-benefit)
- `/llm-routing` — **LLM Router** — routing strategy (static/cascade/complexity-classifier/semantic); model tier map; fallback chain; quality-floor gate; cost/quality projection
- `/build-vs-buy` — **Build vs Buy Advisor** — 5-dimension scoring; AI tooling decision matrix; 3-year TCO; vendor alternatives; exit strategy per component

*Cloud ML platforms:*
- `/vertex-ai-design` — **Vertex AI Platform Architect** — GCP Vertex footprint: service split (Workbench/Pipelines/Training/Endpoints/Feature Store/Model Garden/Monitoring); compute selection; MLOps wiring; deployment pattern (online/batch/streaming); cost guardrails; observability; lock-in posture. Adjacent to `/sagemaker-design` (AWS) + `/databricks-asset-bundles` (Databricks)
- `/sagemaker-design` — **SageMaker Platform Architect** — AWS SageMaker footprint: service split (Studio/Training/Endpoints/Pipelines/Feature Store/Monitor/Clarify/JumpStart); deployment pattern (real-time/async/serverless/batch/MME/MCE); compute; MLOps; cost guardrails; observability; lock-in posture
- `/bedrock-design` — **Amazon Bedrock Architect** — AWS Bedrock GenAI footprint: service split (Models / AgentCore (GA 2025-10-13) / Knowledge Bases / Guardrails / Flows / Prompt Mgmt / IPR / Eval / Custom Import); model selection (Claude 4.x + Fable 5 + Nova 2 + Llama + Mistral + Cohere; Sonnet 4/Opus 4 retire 2026-06-15); inference pattern (on-demand / PT / batch / cross-region); KB vector-store matrix (OpenSearch / Aurora / Neptune / Pinecone / MongoDB / Redis; binary-vector OpenSearch-only); Guardrails (incl. Automated Reasoning Nov 2025); IPR intra-family routing (GA 2025-04-22). Distinct from `/sagemaker-design` (AWS classical ML); adjacent to `/vertex-ai-design` (GCP) + `/azure-foundry-design` (Azure)
- `/azure-foundry-design` — **Microsoft Foundry Architect (formerly Azure AI Foundry)** — Azure GenAI footprint: surface map (rebrand Ignite Nov 2025; `/azure/foundry/`), 1,900+ model catalog (Azure OpenAI GPT-5 family + Anthropic Claude + Llama + Mistral + DeepSeek + xAI + Cohere + Fireworks); Foundry Agent Service (GA 2026-03-16, Responses-API wire-compat); BYO VNet private networking GA; Foundry IQ + Azure AI Search agentic retrieval; safety stack (Prompt Shields + Groundedness auto-correct + Content Safety + Protected Material); cost model (PTU breakeven >50% util + 150-200M tok/mo on GPT-4o; PAYG / Batch 50%; Azure +20-40% over OpenAI direct). Distinct from Azure ML (classical MLOps); adjacent to `/bedrock-design` (AWS) + `/vertex-ai-design` (GCP)
- `/openai-platform-design` — **OpenAI Platform Architect** — direct OpenAI footprint (not Azure OpenAI): API surface (Responses API default; **Assistants API sunset 2026-08-26**; Chat Completions feature-frozen on GPT-5.4+ reasoning); model catalog (GPT-5.5/5.5 Pro/5.4/5.4 mini/5.4 nano/GPT-4.1 (1M ctx)/4.1 nano/o3/o4-mini); Agents SDK (Handoffs + Guardrails + Tracing; vendor sandboxes Blaxel/Cloudflare/Daytona/E2B/Modal/Runloop/Vercel); Realtime API (`gpt-realtime` GA 2025-08-28; Cedar+Marin voices; native MCP + image + SIP); Vector Stores + File Search; tools (Web Search $10/1K + Computer Use + Code Interpreter + Structured Outputs strict); **Deep Research cost trap ($30/call on o3-deep-research)**; prompt caching automatic ≥1024 tokens; Batch+Flex 50%; fine-tune trio (SFT/DPO/RFT); **OpenAI Evals read-only 2026-10-31 / shutdown 2026-11-30** — replace with Promptfoo/Braintrust/Langfuse/Agents-SDK tracing

*Infrastructure as code:*
- `/terraform-review` — **Terraform Reviewer** — IaC review across 9 dimensions: state backend + locking; module structure; variable/output discipline; provider versioning; secrets handling; blast-radius gates (`prevent_destroy`/`ignore_changes`); drift detection; plan-vs-apply CI pattern; destructive-op safety. [BLOCKER]/[SUGGESTION]/[NITPICK] grouped findings. Use BEFORE `terraform apply` in any shared-state env

*Compliance:*
- `/compliance-mapping` — **Compliance Mapping Analyst** — SOC 2 / HIPAA / GDPR / EU AI Act controls → enforcement matrix (code path + evidence source + owner + CLEAN/PARTIAL/GAP status); gap register with target close dates; cross-framework overlap detection. Use BEFORE SOC 2 readiness, HIPAA engagement, GDPR DPIA, high-risk EU AI Act ship

*Analytics / BI:*
- `/dashboard-design` — **BI Dashboard Designer** — audience-first scoping (exec/analyst/operator/external — ONE per dashboard); one-question-per-dashboard rule; chart selection rubric by question shape; refresh cadence + honest SLA; governance (owner/certification/deprecation); performance budget + accessibility. Tool-agnostic (Looker/Tableau/Superset/Metabase/Power BI). Distinct from `/observability` and `/feature-monitoring`

*Data engineering:*
- `/pipeline-design` — **Data Pipeline Architect** — batch vs. streaming decision, orchestration, idempotency, backfill, SLA
- `/data-mesh` — **Data Mesh Architect** — domain ownership boundaries; data product specs (SLA/schema/access/quality contract); federated governance (policy-as-code); platform stack; one-domain migration
- `/streaming-pipeline` — **Streaming Pipeline Architect** — stream vs. batch vs. hybrid; Kafka/Flink/Spark Streaming selection; windowing; state management; ML feature pipeline integration; consumer lag monitoring
- `/lakehouse-architecture` — **Lakehouse Architect** — medallion bronze/silver/gold zones; open table format (Iceberg/Delta/Hudi); partitioning by dominant query filter; compaction + snapshot expiry for OT/IoT scale; query-engine choice; lineage + time-travel reproducibility
- `/schema-design` — **Data Schema Designer** — dimensional modeling, SCD types, partitioning, schema evolution policy
- `/data-quality` — **Data Quality Engineer** — validation rules, anomaly detection, quarantine + replay strategy
- `/data-contract` — **Data Contract Author** — producer/consumer agreement (schema ownership, SLAs, breaking change policy)
- `/dbt-review` — **dbt Model Reviewer** — dbt model review (ref/source, incremental correctness, test coverage)
- `/sql-review` — **SQL Query Reviewer** — SQL correctness + performance review (join bugs, partition pruning, anti-patterns)
- `/data-cleanse` — **Data Cleansing Planner** — dirty data taxonomy (incl. batch effect, sparse classes, metadata-flagged anomalies), remediation strategy, audit trail, cleansing order
- `/dedup` — **Entity Resolution Specialist** — entity resolution (exact/fuzzy decision, blocking, confidence scoring, golden record)
- `/schema-harmonization` — **Schema Harmonization Architect** — multi-source schema merging (conflict types, canonical design, source priority)
- `/data-alignment` — **Data Alignment Architect** — row-level multi-source consolidation (entity match, timestamp sync, scale/encoding harmonization, batch effect detection + mitigation); distinct from schema-harmonization (schema-level)
- `/metadata-audit` — **Metadata Auditor** — 7-dimension column audit (provenance, collection, units, transformation, summarization, labeling, cadence); batch effect detection; gap register with severity
- `/timeseries-resample` — **Time Series Resampling Advisor** — upsample/downsample by metric type, gap handling, temporal alignment
- `/class-balancing` — **Class Imbalance Strategist** — ML class imbalance (strategy by ratio, SMOTE/weights, eval setup, threshold tuning)
- `/annotation-design` — **Annotation Schema Designer** — label taxonomy, decision tree, edge case catalog, calibration process
- `/label-quality` — **Label Quality Assessor** — IAA metrics (κ/α), adjudication workflow, quality thresholds, audit cadence
- `/active-learning` — **Active Learning Strategist** — query strategy by labeled set size, uncertainty/diversity sampling, stopping criteria
- `/split-design` — **Data Split Designer** — random/temporal/group split decision, ratios by size, stratification, minimum eval sizes
- `/cross-validation` — **Cross-Validation Strategist** — k-fold variant selection, time series CV, nested CV for hyperparameter tuning
- `/leakage-audit` — **Data Leakage Auditor** — temporal/target/group/preprocessing/operational-availability leakage detection with code fixes; production-readiness checks

*Databricks integration:*
- `/unity-catalog-governance` — **Unity Catalog Governance Architect** — catalog/schema/table namespace; group-based least-privilege grants; **ABAC + governed tags (preferred)** over row filters / column masks / dynamic views in UC (never BI); lineage for pre-change impact; system-table audit; per-catalog storage credentials
- `/databricks-asset-bundles` — **Declarative Automation Bundles Engineer (formerly DABs)** — jobs/pipelines/models/dashboards as code in databricks.yml; per-target (dev/staging/prod) overrides; service-principal run-as; build-once promote-many; validate gate in CI
- `/delta-live-tables` — **Lakeflow SDP Designer (formerly DLT)** — declarative medallion pipelines; streaming table vs materialized view per layer; expectations (warn/drop/fail) as code; APPLY CHANGES for CDC/SCD; triggered vs continuous
- `/databricks-jobs-orchestration` — **Lakeflow Jobs Orchestrator (formerly Workflows)** — multi-task DAG; job-cluster/serverless (never all-purpose for prod); bounded retries + timeouts + on-failure alert; idempotent tasks for repair runs
- `/spark-performance-tuning` — **Spark Performance Engineer** — Spark-UI-evidence-first diagnosis (skew/shuffle/spill/small files/join); AQE + broadcast + clustering fixes; Photon (stateless streaming only) compute-last; query+layout before compute
- `/dbu-cost-optimization` — **Databricks Cost Engineer** — system.billing attribution first (via `billing_origin_product` enum); jobs vs all-purpose; serverless/Photon/spot; forced auto-termination; cluster-policy guardrails (distinct from `/cost-optimize` LLM tokens)
- `/databricks-model-serving` — **Model Serving Engineer** — UC-registered model → endpoint; serve-by-alias rollout/rollback; scale-to-zero vs warm; traffic-split canary; inference tables → drift monitoring
- `/mosaic-ai-vector-search` — **Databricks AI Search Engineer (formerly Mosaic AI Vector Search)** — Databricks-native RAG retrieval; Delta Sync index (CDF on); pinned embedding model (change = reindex); hybrid search + UC ACLs; recall@k/MRR eval (chunking → `/rag-design`)
- `/auto-loader-ingestion` — **Auto Loader Ingestion Engineer** — incremental cloudFiles → Delta bronze; **file events (managed `useManagedFileEvents`) preferred** over legacy `useNotifications`; directory listing only for small backfills; `_rescued_data` kept; dedicated checkpoint exactly-once; schema evolution

*ML algorithm selection / tuning:*
- `/experiment-design` — **ML Experiment Designer** — hypothesis formulation, one-variable control, pre-stated decision criteria, ordered run queue
- `/training-infrastructure` — **Training Infrastructure Designer** — compute selection, distributed training strategy (DDP/FSDP), orchestration, cost estimate
- `/algo-select` — **Algorithm Selection Advisor** — algorithm selection by task type + dataset size + constraints; baseline + failure mode per rec
- `/hyperparameter-tuning` — **Hyperparameter Tuning Strategist** — random vs. Bayesian vs. async strategy; search space by algorithm; Optuna code
- `/model-comparison` — **Model Comparison Analyst** — statistical comparison (paired t-test / McNemar / Friedman); practical significance; production verdict
- `/transfer-learning` — **Transfer Learning Advisor** — source model/task selection; adaptation strategy (feature extract / partial / full / adapter / LoRA); negative-transfer check; catastrophic-forgetting mitigation

*Feature engineering:*
- `/feature-engineering` — **Feature Engineering Advisor** — encoding by cardinality, numeric transforms, date extraction, aggregation features, sklearn Pipeline
- `/feature-selection` — **Feature Selection Advisor** — filter → embedded → wrapper; permutation importance over impurity; selection inside CV
- `/feature-store-design` — **Feature Store Architect** — online/offline architecture, feature definition schema, point-in-time joins, backfill, skew prevention

*Data gathering:*
- `/data-collection-design` — **Data Collection Planner** — volume targets by task type, collection strategy, representativeness checklist, labeling plan
- `/synthetic-data-gen` — **Synthetic Data Generation Specialist** — tabular/text/image/time-series synthesis; quality gates; placement rules (train only)
- `/data-sourcing` — **Data Sourcing Analyst** — public registry search, vendor evaluation checklist, license interpretation guide, per-source verdict

*Data filtering / outlier handling:*
- `/outlier-detection` — **Outlier Detection Specialist** — Z-score / IQR / Isolation Forest / Mahalanobis / LOF; treatment by situation; audit trail
- `/data-filtering` — **Data Filtering Planner** — domain rules, quality thresholds, relevance scoring, near-dedup; prescribed order; audit report
- `/sparse-class-grouping` — **Sparse Class Grouping Advisor** — frequency cutoff / hierarchy / embedding clustering / target-rate binning; MI validation; fit-on-train-only

*Model validation:*
- `/model-validation` — **Model Validation Engineer** — 9-gate pre-deploy checklist; CI bootstrap; slice analysis; edge case stress tests; Go/No-Go verdict
- `/model-calibration` — **Model Calibration Specialist** — ECE diagnosis; reliability diagram; Platt/isotonic/temperature scaling; AUC-preservation check
- `/model-drift` — **Model Drift Monitor** — data/concept/prediction drift (KS/PSI); severity thresholds; retraining triggers; daily monitoring pipeline

*Model deployment:*
- `/model-deployment` — **Model Deployment Engineer** — artifact checklist; shadow→canary→limited→full GA rollout; automated + manual rollback triggers; deployment.yaml
- `/inference-service-design` — **Inference Service Designer** — REST/gRPC/batch + edge/IoT/on-device pattern; latency budget; scaling spec; circuit breaker + safe fallback; OTA rollout for edge; observability signals
- `/edge-ml-deployment` — **Edge ML Deployment Engineer** — edge-vs-cloud gate; per-stage latency budget; on-device-validated compressed model; signed atomic OTA + offline rollback; fail-safe fallback; OT advises-not-actuates boundary; offline-tolerant observability
- `/model-decommissioning` — **Model Decommissioning Planner** — retirement criteria; dependency audit; consumer notification; archive policy; retention schedule

*Responsible AI:*
- `/bias-audit` — **Training Data Bias Auditor** — 6 bias classes (sample selection / demographic / geographic / temporal / labeler / survivorship); training-data representativeness vs operational env; run BEFORE training (vs `/fairness-audit` AFTER)
- `/fairness-audit` — **AI Fairness Auditor** — demographic parity; disparate impact ratio (80% rule); equal opportunity; protected-attribute slices; mitigation strategies
- `/explainability` — **Model Explainability Analyst** — SHAP / LIME / PDP / counterfactuals; global + local; method selection by model type; audience-appropriate output

*MLOps / Lifecycle:*
- `/experiment-tracking` — **Experiment Tracking Designer** — run logging schema; registry promotion criteria; reproducibility checklist; MLflow patterns
- `/ab-test-design` — **A/B Test Designer** — sample size calculation; assignment strategy; guardrail metrics; stopping rules; analysis plan
- `/retraining-strategy` — **Model Retraining Strategist** — drift/calendar/performance triggers; data window design; full vs. incremental; promotion gates
- `/data-versioning` — **Dataset Versioning Specialist** — DVC / time-travel / snapshot approach; dataset registration schema; lineage chain; reproducibility
- `/mlops-cicd` — **MLOps Pipeline Engineer** — ML CI/CD pipeline stages; model quality gates; artifact registration schema; rollback trigger spec; GitHub Actions YAML
- `/responsible-ai-governance` — **AI Governance Advisor** — risk tier classification (T1–T4); 5-pillar governance framework; MRM checklist; EU AI Act flags; IP framing (process-as-IP, SaaS clauses, Indigenous Data Sovereignty / CARE / OCAP); review board charter
- `/model-compression` — **Model Compression Specialist** — PTQ / QAT / pruning / distillation / GPTQ selection; code patterns; eval plan on target hardware
- `/feature-monitoring` — **Feature Health Monitor** — freshness SLAs; null rate baselines; schema drift detection; PSI per feature; dashboard spec; anomaly playbook

**Stack add-ons** (language-specific skills in `stacks/`):

| Stack | Commands | How to adopt |
|---|---|---|
| `stacks/python/` | `/test-gen`, `/type-fix`, `/deps-audit` | `cp -r stacks/python/skills/* .claude/skills/` + merge settings-snippet.json + paste claude-md-addendum.md |
| `stacks/typescript/` | `/test-gen`, `/type-fix`, `/deps-audit` | `cp -r stacks/typescript/skills/* .claude/skills/` + merge settings-snippet.json + paste claude-md-addendum.md |
| `stacks/go/` | `/test-gen`, `/type-fix`, `/deps-audit` | `cp -r stacks/go/skills/* .claude/skills/` + merge settings-snippet.json + paste claude-md-addendum.md |

**Permissions:** `.claude/settings.json` pre-allows safe read-only operations (`Read`, `Glob`, `Grep`, git read commands) so they never prompt. Destructive tools (`Write`, `Edit`, `Bash` broadly) are intentionally omitted — add them to `settings.local.json` (gitignored) for your own machine, or use the `update-config` skill.

**Hooks:** See `.claude/hooks/README.md` for protocol, wiring snippet, smoke tests, the full inventory, and the **2026 event catalog** (Claude Code now exposes 12+ lifecycle events — `SessionStart` / `UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `PostToolUseFailure` / `PostToolBatch` / `Stop` / `StopFailure` / `SubagentStop` / `TaskCreated` / `TaskCompleted` / `TeammateIdle` / `WorktreeCreate` / `WorktreeRemove` / `CwdChanged` / `SessionEnd` / `PreCompact`; `PostToolUse` ships `duration_ms` + can mutate output via `hookSpecificOutput.updatedToolOutput`). **13 reference hooks ship** (none wired by default) — 3 generic + 10 domain guardrails; the bundled set targets only `PreToolUse`/`PostToolUse`. Authoring new hooks against the broader event surface (e.g. `UserPromptSubmit` prompt-time gates, `Stop` uncommitted-changes refusal, `SessionStart` staleness check, `SessionEnd` audit-log finalize) is on the backlog:

*Generic (3):*
- `block_dangerous_git.py` (PreToolUse/Bash) — blocks force-push, `reset --hard`, `--no-verify`, and other destructive git ops
- `scan_secrets.py` (PreToolUse/Write|Edit) — blocks files containing AWS/GitHub/Slack/OpenAI/Anthropic/Google/Stripe key shapes
- `audit_log.py` (PostToolUse/*) — passive; appends every tool call to `.claude/logs/audit.jsonl`

*Domain guardrails (10):*
- `block_infra_destroy.py` — blocks `terraform destroy`, `kubectl delete --all`, mass cloud-resource deletes (no escape hatch)
- `check_sql_safety.py` — blocks unguarded `DROP/TRUNCATE/DELETE`
- `check_unsafe_patterns.py` — flags OWASP A02/A03/A05/A08 + XSS patterns
- `check_cloud_cost.py` — warns on expensive EC2/RDS/EKS classes, `deletion_protection=false`, `publicly_accessible=true`
- `check_programming_gotchas.py` — blocks Python mutable defaults, bare `except:`, `== None`
- `check_ml_leakage.py` — blocks `fit_transform(X_test)`; warns on missing `random_state`, preprocessing-order leakage, operational-availability features
- `block_test_set_balancing.py` — blocks SMOTE / `fit_resample` on `X_test` / `X_val`
- `check_metric_guardrail.py` — Goodhart's-law check on eval/experiment configs without counter-metric
- `check_pii_in_logs.py` — warns when log calls reference PII-shaped vars
- `check_prompt_safety.py` — warns on prompt-injection risk (f-string with user vars) + hardcoded model paths

**Scheduled routines:** None configured by default. Use `/schedule` to create recurring remote agents. Each routine runs on a cron schedule and can invoke any skill or task.

Common patterns to adapt:
- **Weekly retro** — "Every Friday at 4pm, run `/retro`, summarize recent commits, and append new lessons to `LESSONS_LEARNED.md`"
- **Staleness check** — "Every Monday, check if `NEXT_SESSION.md` HEAD is more than 7 days old and notify me"
- **Dependency audit** — "Weekly: scan for outdated packages and open a GitHub issue if any are found"

To create one: type `/schedule` and describe the routine in plain English. To list or remove: `/schedule` → manage existing routines.
