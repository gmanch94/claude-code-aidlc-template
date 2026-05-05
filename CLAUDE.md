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

## Working conventions

[Fill in project-specific conventions. Examples:]

- [Naming conventions — files, variables, branches]
- [How tests are run and what "passing" means]
- [Where the source of truth lives for each type of content]
- [PR / commit conventions]
- [Any file that must never be edited directly (generated files, etc.)]

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

[Fill in. Add to this list as you learn what goes wrong. Examples:]

- Don't [X] without explicit instruction
- Don't add [Y] — explicit decision: [reason]
- Don't edit [Z] — it's auto-generated
- Don't push to main directly — branch + PR required

---

## Automation

[Fill in any slash commands, hooks, or scheduled routines.]

**Custom skills** (type in Claude Code prompt — skills live in `.claude/skills/`):

*Problem framing / EDA:*
- `/problem-framing` — ML vs. rules decision; solution type; success metric tied to KPI; non-ML baseline; problem statement card
- `/eda` — dataset profiling (target, missingness, cardinality, correlations, leakage candidates); EDA summary report

*General:*
- `/review` — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format
- `/adr` — draft an Architecture Decision Record
- `/tradeoff` — structured tradeoff analysis for a decision

*Production systems:*
- `/threat-model` — AI-specific threat modeling (8 threat categories + traditional security)
- `/rollout` — phased rollout plan with eval gates and rollback triggers
- `/runbook` — AI incident runbook (8 standard failure scenarios)
- `/pii-scan` — PII exposure audit across the AI data lifecycle
- `/observability` — AI observability stack design (signal layers, metrics, alerts, drift indicators)

*AI / LLM projects:*
- `/eval-design` — LLM evaluation framework (metric taxonomy, test set sizing, drift triggers)
- `/prompt-review` — 9-dimension prompt health score
- `/rag-design` — RAG system design (chunking, embedding, retrieval, reranking, observability)
- `/agent-design` — agentic system design (loop, tool manifest, guardrails, fallbacks)
- `/red-team` — 4-phase AI red team battery (base model → app → infra → operational)
- `/model-card` — model documentation standard (9 sections, governance checklist)
- `/supply-chain-review` — AI model supply chain audit + AI-BOM generation
- `/cost-optimize` — token spend analysis (model tier selection, caching strategy, batch decisions)
- `/feedback-loop` — production feedback loop design (signal collection, annotation, improvement routing)
- `/fine-tune` — fine-tune vs. prompt decision tree (dataset requirements, eval plan, cost-benefit)

*Data engineering:*
- `/pipeline-design` — batch vs. streaming decision, orchestration, idempotency, backfill, SLA
- `/schema-design` — dimensional modeling, SCD types, partitioning, schema evolution policy
- `/data-quality` — validation rules, anomaly detection, quarantine + replay strategy
- `/data-contract` — producer/consumer agreement (schema ownership, SLAs, breaking change policy)
- `/dbt-review` — dbt model review (ref/source, incremental correctness, test coverage)
- `/sql-review` — SQL correctness + performance review (join bugs, partition pruning, anti-patterns)
- `/data-cleanse` — dirty data taxonomy, remediation strategy, audit trail, cleansing order
- `/dedup` — entity resolution (exact/fuzzy decision, blocking, confidence scoring, golden record)
- `/schema-harmonization` — multi-source schema merging (conflict types, canonical design, source priority)
- `/timeseries-resample` — upsample/downsample by metric type, gap handling, temporal alignment
- `/class-balancing` — ML class imbalance (strategy by ratio, SMOTE/weights, eval setup, threshold tuning)
- `/annotation-design` — label taxonomy, decision tree, edge case catalog, calibration process
- `/label-quality` — IAA metrics (κ/α), adjudication workflow, quality thresholds, audit cadence
- `/active-learning` — query strategy by labeled set size, uncertainty/diversity sampling, stopping criteria
- `/split-design` — random/temporal/group split decision, ratios by size, stratification, minimum eval sizes
- `/cross-validation` — k-fold variant selection, time series CV, nested CV for hyperparameter tuning
- `/leakage-audit` — temporal/target/group/preprocessing leakage detection with code fixes

*ML algorithm selection / tuning:*
- `/algo-select` — algorithm selection by task type + dataset size + constraints; baseline + failure mode per rec
- `/hyperparameter-tuning` — random vs. Bayesian vs. async strategy; search space by algorithm; Optuna code
- `/model-comparison` — statistical comparison (paired t-test / McNemar / Friedman); practical significance; production verdict

*Feature engineering:*
- `/feature-engineering` — encoding by cardinality, numeric transforms, date extraction, aggregation features, sklearn Pipeline
- `/feature-selection` — filter → embedded → wrapper; permutation importance over impurity; selection inside CV
- `/feature-store-design` — online/offline architecture, feature definition schema, point-in-time joins, backfill, skew prevention

*Data gathering:*
- `/data-collection-design` — volume targets by task type, collection strategy, representativeness checklist, labeling plan
- `/synthetic-data-gen` — tabular/text/image/time-series synthesis; quality gates; placement rules (train only)
- `/data-sourcing` — public registry search, vendor evaluation checklist, license interpretation guide, per-source verdict

*Data filtering / outlier handling:*
- `/outlier-detection` — Z-score / IQR / Isolation Forest / Mahalanobis / LOF; treatment by situation; audit trail
- `/data-filtering` — domain rules, quality thresholds, relevance scoring, near-dedup; prescribed order; audit report
- `/sparse-class-grouping` — frequency cutoff / hierarchy / embedding clustering / target-rate binning; MI validation; fit-on-train-only

*Model validation:*
- `/model-validation` — 9-gate pre-deploy checklist; CI bootstrap; slice analysis; edge case stress tests; Go/No-Go verdict
- `/model-calibration` — ECE diagnosis; reliability diagram; Platt/isotonic/temperature scaling; AUC-preservation check
- `/model-drift` — data/concept/prediction drift (KS/PSI); severity thresholds; retraining triggers; daily monitoring pipeline

*Model deployment:*
- `/model-deployment` — artifact checklist; shadow→canary→limited→full GA rollout; automated + manual rollback triggers; deployment.yaml
- `/inference-service-design` — REST/gRPC/batch pattern; latency budget; scaling spec; circuit breaker + safe fallback; observability signals
- `/model-decommissioning` — retirement criteria; dependency audit; consumer notification; archive policy; retention schedule

*Responsible AI:*
- `/fairness-audit` — demographic parity; disparate impact ratio (80% rule); equal opportunity; protected-attribute slices; mitigation strategies
- `/explainability` — SHAP / LIME / PDP / counterfactuals; global + local; method selection by model type; audience-appropriate output

*MLOps / Lifecycle:*
- `/experiment-tracking` — run logging schema; registry promotion criteria; reproducibility checklist; MLflow patterns
- `/ab-test-design` — sample size calculation; assignment strategy; guardrail metrics; stopping rules; analysis plan
- `/retraining-strategy` — drift/calendar/performance triggers; data window design; full vs. incremental; promotion gates
- `/data-versioning` — DVC / time-travel / snapshot approach; dataset registration schema; lineage chain; reproducibility
- `/mlops-cicd` — ML CI/CD pipeline stages; model quality gates; artifact registration schema; rollback trigger spec; GitHub Actions YAML
- `/responsible-ai-governance` — risk tier classification (T1–T4); 5-pillar governance framework; MRM checklist; EU AI Act flags; review board charter
- `/model-compression` — PTQ / QAT / pruning / distillation / GPTQ selection; code patterns; eval plan on target hardware
- `/feature-monitoring` — freshness SLAs; null rate baselines; schema drift detection; PSI per feature; dashboard spec; anomaly playbook

**Hooks:** [List any hooks in `.claude/hooks/` and what they do.]

**Scheduled routines:** [List any automated agents or cron routines.]
