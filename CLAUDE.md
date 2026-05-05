# CLAUDE.md

Guidance for Claude Code working in this repo. Auto-loaded at the start of every session.

---

## What this repo is

**[PROJECT NAME]** — [one sentence: what it is, who it's for, what problem it solves].

[Optional: one sentence on what this repo is NOT — helps Claude avoid scope creep.]

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
├── memory/                    ← Claude's persistent project memory
│   └── MEMORY.md              ← Memory index
├── prompts/                   ← System prompt templates (RAG, agent, chat, classifier, etc.)
│   └── README.md              ← Template index + how-to-use guide
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

[Fill in project-specific conventions. Examples:]

- [Naming conventions — files, variables, branches]
- [How tests are run and what "passing" means]
- [Where the source of truth lives for each type of content]
- [PR / commit conventions]
- [Any file that must never be edited directly (generated files, etc.)]

**Confusion Protocol** — when facing an architectural decision or ambiguous requirement, stop and surface the assumption explicitly before proceeding. Never guess on design decisions. Ask one targeted question instead of producing output that may be wrong.

---

## Tone and output constraints

[Fill in. Remove any that don't apply to your project. Examples:]

- No emojis in [artifacts / commits / output] unless explicitly requested
- Numeric where possible — no adjectives doing numeric work ("significant improvement" fails; "42% latency reduction" passes)
- Every recommendation names a failure mode — no universally-best options
- Comments in code: only when the WHY is non-obvious. No "this function does X" comments.
- [Language / framework style guide link if applicable]

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

[Fill in any slash commands, hooks, or scheduled routines.]

**Custom skills** (type in Claude Code prompt — skills live in `.claude/skills/`):

*Business discovery:*
- `/stakeholder-interview` — **Business Discovery Facilitator** — structured six-group discovery interview; Discovery Summary Card output before any ML framing
- `/opportunity-sizing` — **AI Opportunity Analyst** — status quo cost + AI uplift + build cost + go/no-go recommendation
- `/kpi-mapping` — **KPI-to-Metric Mapper** — 4-level chain from business objective to ML metric; translation failure modes + counter-metric

*Problem framing / EDA:*
- `/problem-framing` — **ML Problem Framing Advisor** — ML vs. rules decision; solution type; success metric tied to KPI; non-ML baseline; problem statement card
- `/eda` — **Exploratory Data Analyst** — dataset profiling (target, missingness, cardinality, correlations, leakage candidates); EDA summary report

*General:*
- `/office-hours` — **Assumptions Facilitator** — assumptions gate; six forcing questions + design doc before any implementation
- `/review` — **Code Reviewer** — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format
- `/adr` — **ADR Facilitator** — draft an Architecture Decision Record
- `/tradeoff` — **Tradeoff Analyst** — structured tradeoff analysis for a decision
- `/retro` — **Retrospective Facilitator** — engineering retrospective; reviews recent commits, surfaces lessons, writes to LESSONS_LEARNED.md

*Production systems:*
- `/threat-model` — **AI Threat Modeling Analyst** — AI-specific threat modeling (8 threat categories + traditional security)
- `/rollout` — **Rollout Planner** — phased rollout plan with eval gates and rollback triggers
- `/runbook` — **Incident Runbook Author** — AI incident runbook (8 standard failure scenarios)
- `/pii-scan` — **PII Exposure Auditor** — PII exposure audit across the AI data lifecycle
- `/observability` — **Observability Stack Designer** — AI observability stack design (signal layers, metrics, alerts, drift indicators)

*AI / LLM projects:*
- `/eval-design` — **LLM Evaluation Designer** — LLM evaluation framework (metric taxonomy, test set sizing, drift triggers)
- `/prompt-review` — **Prompt Quality Reviewer** — 9-dimension prompt health score
- `/rag-design` — **RAG System Architect** — RAG system design (chunking, embedding, retrieval, reranking, observability)
- `/agent-design` — **Agentic System Designer** — agentic system design (loop, tool manifest, guardrails, fallbacks)
- `/red-team` — **AI Red Team Lead** — 4-phase AI red team battery (base model → app → infra → operational)
- `/model-card` — **Model Documentation Author** — model documentation standard (9 sections, governance checklist)
- `/supply-chain-review` — **AI Supply Chain Auditor** — AI model supply chain audit + AI-BOM generation
- `/cost-optimize` — **Token Cost Optimizer** — token spend analysis (model tier selection, caching strategy, batch decisions)
- `/feedback-loop` — **Feedback Loop Designer** — production feedback loop design (signal collection, annotation, improvement routing)
- `/fine-tune` — **Fine-Tuning Advisor** — fine-tune vs. prompt decision tree (dataset requirements, eval plan, cost-benefit)

*Data engineering:*
- `/pipeline-design` — **Data Pipeline Architect** — batch vs. streaming decision, orchestration, idempotency, backfill, SLA
- `/schema-design` — **Data Schema Designer** — dimensional modeling, SCD types, partitioning, schema evolution policy
- `/data-quality` — **Data Quality Engineer** — validation rules, anomaly detection, quarantine + replay strategy
- `/data-contract` — **Data Contract Author** — producer/consumer agreement (schema ownership, SLAs, breaking change policy)
- `/dbt-review` — **dbt Model Reviewer** — dbt model review (ref/source, incremental correctness, test coverage)
- `/sql-review` — **SQL Query Reviewer** — SQL correctness + performance review (join bugs, partition pruning, anti-patterns)
- `/data-cleanse` — **Data Cleansing Planner** — dirty data taxonomy, remediation strategy, audit trail, cleansing order
- `/dedup` — **Entity Resolution Specialist** — entity resolution (exact/fuzzy decision, blocking, confidence scoring, golden record)
- `/schema-harmonization` — **Schema Harmonization Architect** — multi-source schema merging (conflict types, canonical design, source priority)
- `/timeseries-resample` — **Time Series Resampling Advisor** — upsample/downsample by metric type, gap handling, temporal alignment
- `/class-balancing` — **Class Imbalance Strategist** — ML class imbalance (strategy by ratio, SMOTE/weights, eval setup, threshold tuning)
- `/annotation-design` — **Annotation Schema Designer** — label taxonomy, decision tree, edge case catalog, calibration process
- `/label-quality` — **Label Quality Assessor** — IAA metrics (κ/α), adjudication workflow, quality thresholds, audit cadence
- `/active-learning` — **Active Learning Strategist** — query strategy by labeled set size, uncertainty/diversity sampling, stopping criteria
- `/split-design` — **Data Split Designer** — random/temporal/group split decision, ratios by size, stratification, minimum eval sizes
- `/cross-validation` — **Cross-Validation Strategist** — k-fold variant selection, time series CV, nested CV for hyperparameter tuning
- `/leakage-audit` — **Data Leakage Auditor** — temporal/target/group/preprocessing leakage detection with code fixes

*ML algorithm selection / tuning:*
- `/algo-select` — **Algorithm Selection Advisor** — algorithm selection by task type + dataset size + constraints; baseline + failure mode per rec
- `/hyperparameter-tuning` — **Hyperparameter Tuning Strategist** — random vs. Bayesian vs. async strategy; search space by algorithm; Optuna code
- `/model-comparison` — **Model Comparison Analyst** — statistical comparison (paired t-test / McNemar / Friedman); practical significance; production verdict

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
- `/inference-service-design` — **Inference Service Designer** — REST/gRPC/batch pattern; latency budget; scaling spec; circuit breaker + safe fallback; observability signals
- `/model-decommissioning` — **Model Decommissioning Planner** — retirement criteria; dependency audit; consumer notification; archive policy; retention schedule

*Responsible AI:*
- `/fairness-audit` — **AI Fairness Auditor** — demographic parity; disparate impact ratio (80% rule); equal opportunity; protected-attribute slices; mitigation strategies
- `/explainability` — **Model Explainability Analyst** — SHAP / LIME / PDP / counterfactuals; global + local; method selection by model type; audience-appropriate output

*MLOps / Lifecycle:*
- `/experiment-tracking` — **Experiment Tracking Designer** — run logging schema; registry promotion criteria; reproducibility checklist; MLflow patterns
- `/ab-test-design` — **A/B Test Designer** — sample size calculation; assignment strategy; guardrail metrics; stopping rules; analysis plan
- `/retraining-strategy` — **Model Retraining Strategist** — drift/calendar/performance triggers; data window design; full vs. incremental; promotion gates
- `/data-versioning` — **Dataset Versioning Specialist** — DVC / time-travel / snapshot approach; dataset registration schema; lineage chain; reproducibility
- `/mlops-cicd` — **MLOps Pipeline Engineer** — ML CI/CD pipeline stages; model quality gates; artifact registration schema; rollback trigger spec; GitHub Actions YAML
- `/responsible-ai-governance` — **AI Governance Advisor** — risk tier classification (T1–T4); 5-pillar governance framework; MRM checklist; EU AI Act flags; review board charter
- `/model-compression` — **Model Compression Specialist** — PTQ / QAT / pruning / distillation / GPTQ selection; code patterns; eval plan on target hardware
- `/feature-monitoring` — **Feature Health Monitor** — freshness SLAs; null rate baselines; schema drift detection; PSI per feature; dashboard spec; anomaly playbook

**Hooks:** [List any hooks in `.claude/hooks/` and what they do.]

**Scheduled routines:** [List any automated agents or cron routines.]
