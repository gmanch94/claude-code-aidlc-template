# claude-code-template

A Claude Code template covering the full AI/ML development lifecycle — from problem framing to production monitoring. 100+ skills, persistent memory, and session continuity out of the box.

---

## The problem

Most projects using Claude Code get less out of it than they could:

| Missing | Effect |
|---|---|
| No `CLAUDE.md` | Claude doesn't know the project's conventions, tone, or what not to do — rediscovers them every session |
| No session bookmark | After `/clear`, Claude re-derives context that was already established. First 10–15 min of every session is orientation |
| No permission allowlist | Every read-only command (`git log`, `gh pr view`, analysis tools) triggers an approval prompt |
| No slash commands | Useful workflows (code review, ADRs, tradeoff analysis) get re-typed from memory or done inconsistently |

This template fixes all four in under 5 minutes of setup.

---

## What's included

| File | What it does |
|---|---|
| `CLAUDE.md` | Auto-loaded every session. Defines project posture, session-start protocol, tone constraints, and things to avoid. Fill in 5 placeholders. |
| `LESSONS_LEARNED.md` | Process lessons that accumulate across sessions. Pre-seeded with 8 generalizable lessons; add project-specific ones as you work. |
| `NEXT_SESSION.md` | Session bookmark — HEAD, branch, what landed, what's open. Claude reads it first after `/clear`. |
| `.claude/settings.json` | Permission allowlist. Pre-populated with `Read`, `Glob`, `Grep`, safe git read commands, and context-mode MCP tools — so common read-only ops never prompt. Add project-specific patterns here; put machine-local ones in `.claude/settings.local.json` (gitignored). |
| `.claude/hooks/` | **15** reference guardrail hooks (none wired by default) — 3 generic (`block_dangerous_git`, `scan_secrets`, `audit_log`) + 10 domain (cloud-cost, SQL safety, ML leakage, PII-in-logs, prompt safety, OWASP patterns, infra-destroy, programming gotchas, test-set balancing, metric guardrails) + 2 optional add-ons (`shadow_git_checkpoint` on `PreToolUse` mutations, `staleness_check` on `SessionStart`). See `.claude/hooks/README.md` for the full inventory + wiring snippet. |
| `.claude/skills/review/SKILL.md` | `/review` — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format. |
| `.claude/skills/adr/SKILL.md` | `/adr` — draft an Architecture Decision Record with full rationale and alternatives. |
| `.claude/skills/tradeoff/SKILL.md` | `/tradeoff` — structured tradeoff analysis: options × pros/cons/failure-mode + recommendation with named constraint. |
| `.claude/skills/security-audit/SKILL.md` | `/security-audit` — deep security audit (CRITICAL→LOW findings with file+line). Stack-aware (Supabase / Firebase / Hasura / FastAPI / Express). |
| `.claude/skills/security-model-init/SKILL.md` | `/security-model-init` — generate `docs/SECURITY_MODEL.md` scaffold for projects with user-facing surfaces. |
| `templates/security-model/SECURITY_MODEL-TEMPLATE.md` | Annotated template for the per-(operation × role × surface) enforcement table; stack-specific scaffolding blocks for Supabase/Firebase/Hasura/FastAPI/Express. |
| `context/MEMORY.md` | Index for Claude's persistent project memory. |
| `prompts/` | **171** system prompt templates across ML, data engineering, LLM, auth, Databricks, cloud ML / GenAI platforms (Bedrock / Azure Foundry / OpenAI / Vertex), agent design (incl. memory + plan-mode + workflow-design), IaC, compliance, BI, and production AI categories. Each has placeholders, usage notes, and a prompt health score. |
| `templates/skill/SKILL-TEMPLATE.md` | Annotated template for authoring new skills. Copy to `.claude/skills/<name>/SKILL.md` and fill in. |
| `.gitignore` | Gitignores `scratch/` (personal workspace), `.claude/settings.local.json`, and `.claude/logs/` (hook audit logs). |
| `operating-philosophy.md` | Portable working philosophy — communication style, context-mode tool hierarchy, advisor protocol, primary-source verification, session management, git hygiene, Karpathy failure modes, design principles. Copy sections into any project's `CLAUDE.md`. |
| `analysis-methodology.md` | Example API audit methodology — 6-phase research approach, advisor feedback rounds, 8 lessons learned, reusable checklist. Reference for similar research/documentation projects. |

---

## Setup (5 minutes)

**1. Create your repo from this template**

Click **Use this template** → **Create a new repository** on GitHub. Or clone and re-init:

```bash
git clone https://github.com/gmanch94/claude-code-template your-project
cd your-project
rm -rf .git && git init && git add . && git commit -m "init from claude-code-template"
```

**2. Fill in `CLAUDE.md`**

Five placeholders to replace:
- `[PROJECT NAME]` — what the repo is
- The one-sentence description
- `[FILENAME]` — your source of truth file
- Working conventions for your stack
- The "things to avoid" list

Start minimal — one or two entries per section. The file compounds over time.

**3. Start your first session**

Open Claude Code in your repo. Claude reads `CLAUDE.md` automatically. It will follow the session-start protocol and ask what you want to work on.

**4. End your first session**

Update `NEXT_SESSION.md` with: current HEAD hash, branch, what landed, what's open. This is the resume point for every future session.

Done. The template is live.

---

## Slash commands

Type these in the Claude Code prompt. Skills live in `.claude/skills/<name>/SKILL.md`. Add your own by creating a new directory with a `SKILL.md` — it becomes `/name` automatically.

**Business discovery:**

| Command | What it does |
|---|---|
| `/stakeholder-interview` | **Business Discovery Facilitator** — structured six-group discovery interview with non-technical stakeholders; outputs a Discovery Summary Card before any ML framing |
| `/opportunity-sizing` | **AI Opportunity Analyst** — status quo cost, AI uplift estimate, build cost, and go/no-go recommendation; validates the initiative is worth building |
| `/kpi-mapping` | **KPI-to-Metric Mapper** — 4-level chain from business objective to ML metric with translation failure modes, Goodhart traps, and counter-metric |
| `/ml-readiness` | **ML Strategy Advisor** — 5-stage maturity assessment (Initial → Development → Competent → Proficient → Advanced) + AI Hierarchy of Needs + build/buy/partner balance per stage + 5-year roadmap + process-as-IP framing |
| `/stakeholder-comms` | **ML Communications Advisor** — audience map (exec/user/mgmt/data team) + Rider/Elephant/Path messaging framework + reporting cadence templates + failure-comms patterns + adoption-signal tracking |
| `/metric-gaming-audit` | **Metric Gaming Auditor** — Goodhart's-law guard before committing to any optimization target; proxy-quality scoring, per-actor gaming-path enumeration, secondary effects (unexpected benefits/drawbacks/perverse results), counter-metric design |

**Problem framing / EDA:**

| Command | What it does |
|---|---|
| `/problem-framing` | **ML Problem Framing Advisor** — ML vs. rules decision, solution type, success metric tied to KPI, non-ML baseline, problem statement card |
| `/eda` | **Exploratory Data Analyst** — Dataset profiling — target distribution, missingness, cardinality, correlations, leakage candidates, EDA summary report |
| `/cohort-analysis` | **Cohort Analysis Specialist** — segment by acquisition/behavioral/attribute cohorts; outcome comparison with significance tests, retention curves, distribution shifts |
| `/time-series-eda` | **Time Series Data Analyst** — stationarity (ADF+KPSS), trend (Mann-Kendall), seasonality (STL), ACF/PACF, structural breaks, anomaly detection |
| `/feature-correlation` | **Feature Relationship Analyst** — Pearson/Spearman/MI by variable type, VIF multicollinearity, Cramér's V for categoricals, interaction candidate detection |
| `/hypothesis-test-design` | **Hypothesis Test Designer** — picks the right test for an OBSERVATIONAL question (outcome × group-count × paired × distribution), assumption checks with a named fallback per failure, effect size + a priori power (bans post-hoc power), multiplicity correction (Holm/Bonferroni/BH-FDR), and the four pitfall guards (p-hacking, Simpson's, pseudo-replication, p≠effect). Defers interventional→`/experiment-design`, A/B→`/ab-test-design`, model-vs-model→`/model-comparison` |
| `/unstructured-eda` | **Unstructured Corpus EDA (Text + Image)** — pre-modeling profiling of a raw text/image corpus: length/encoding/language mix, near-dup rate, label coverage, vocab/OOV, PII flag (text); resolution/channel/corruption audit, class balance, EXIF/batch confounds (image); cross-split duplicate leakage as the top finding. Defers tabular→`/eda`, temporal→`/time-series-eda`, dedup mechanics→`/dedup`, PII detail→`/pii-scan` |

**Unsupervised learning:**

| Command | What it does |
|---|---|
| `/clustering` | **Clustering Advisor** — algorithm selection (k-means/DBSCAN/GMM/hierarchical), k decision (elbow+silhouette), stability testing, cluster profiling |
| `/dim-reduction` | **Dimensionality Reduction Advisor** — PCA/UMAP/t-SNE selection by goal, variance explained, component count, downstream use rules (t-SNE visualization-only enforced) |
| `/topic-modeling` | **Topic Modeling Advisor** — LDA/NMF/BERTopic selection, preprocessing pipeline, coherence-based k decision, topic labeling, downstream feature rules |

**Reinforcement learning:**

| Command | What it does |
|---|---|
| `/bandit-design` | **Bandit Strategy Designer** — epsilon-greedy/UCB/Thompson Sampling/LinUCB selection, reward model, exploration parameters, stopping criteria, offline evaluation; bandit vs A/B test decision |
| `/rl-design` | **RL System Designer** — RL justification gate, MDP specification, algorithm selection (DQN/PPO/SAC/TD3/offline RL/RLHF), reward design, exploration strategy, safety constraints, multi-seed evaluation |

**ML domain skills:**

| Command | What it does |
|---|---|
| `/time-series-forecasting` | **Time Series Forecasting Advisor** — ARIMA/SARIMA order from ACF/PACF, ETS, Prophet, N-BEATS/TFT, ML with lag features, time series CV, seasonal naive baseline gate |
| `/recommender-design` | **Recommender System Designer** — CF/content-based/two-tower/sequential selection, two-stage pipeline, cold-start strategy, temporal split evaluation, exploration-exploitation integration |
| `/learning-to-rank` | **Learning-to-Rank Designer** — query-document ranking for search/ads/document retrieval; objective class (pointwise/pairwise/listwise); model family (LambdaMART via LightGBM/XGBoost rank objectives, cross-encoder, learned-sparse); click-bias judgment construction (click models + IPW / counterfactual LTR); NDCG/MAP/MRR/ERR; query-level split + interleaving→A/B eval. Defers user-item personalization to `/recommender-design`, A/B mechanics to `/ab-test-design` |
| `/nlp-pipeline` | **NLP Pipeline Designer** — preprocessing decisions, TF-IDF/BERT/SBERT/LLM embedding selection by task, task-specific metrics (entity-level F1/ROUGE/BERTScore), TF-IDF baseline gate |
| `/anomaly-detection` | **Anomaly Detection Specialist** — method selection by data type and label availability (Z-score/IQR/Isolation Forest/LOF/LSTM-AE/CUSUM), threshold strategy, FPR evaluation, treatment decision |
| `/causal-inference` | **Causal Inference Advisor** — method selection (DiD/PSM/IPW/IV/RDD), assumption validation, effect estimate with 95% CI, sensitivity analysis; estimand stated before method |
| `/survival-analysis` | **Survival Analysis Advisor** — method by censoring type (KM/Cox PH/RSF/AFT/Fine-Gray), PH assumption validation, survival curves with log-rank test, C-statistic + calibration |
| `/computer-vision` | **Computer Vision Advisor** — architecture by task × dataset size (CNN/ViT/YOLO/SegFormer), preprocessing + augmentation pipeline, mAP@0.5:0.95 evaluation, 3-phase transfer learning |
| `/online-learning` | **Online Learning Advisor** — streaming ML method (Hoeffding Tree/HAT/VW), concept drift detection (ADWIN/EDDM), prequential evaluation; batch retrain recommended when viable |
| `/graph-ml-design` | **Graph ML Designer** — GNN-vs-tabular gate; graph construction (node/edge, homo/heterogeneous, static/temporal); task framing (node/link/graph); GNN family (GCN/GraphSAGE/GAT/GIN/R-GCN/TGN/TGAT) by task × scale × inductive; scale strategy (full-batch/neighbor/Cluster-GCN/GraphSAINT); owns leakage-safe splits for connected data |
| `/audio-ml-pipeline` | **Audio ML Pipeline Designer** — task framing (ASR/TTS/speaker-ID/SED/KWS/diarization/audio-anomaly), representation (waveform/log-mel/MFCC) + sample-rate + VAD, pretrained backbone (Whisper/wav2vec2/HuBERT/AST/pyannote), augmentation, task metrics (WER/DER/event-F1/EER/MOS), speaker-level split |
| `/multimodal-design` | **Multimodal System Designer** — fusion gate (multimodal vs two single-modality), fusion strategy (joint-embedding vs generative VLM), model selection (CLIP/SigLIP, frontier+open VLMs, LayoutLM/Donut docs), multimodal RAG, cross-modal eval + failure modes (modality collapse / missing-modality / OCR bottleneck) |
| `/geospatial-ml` | **Geospatial ML Advisor** — spatial data type (point/polygon/raster/trajectory/network), CRS + projection discipline, spatial features (distance/spatial-join/H3/KDE/spatial-lag), task→model (kriging/RF+spatial/GWR/Getis-Ord), owns spatial-autocorrelation leakage + spatial-block CV |
| `/decision-optimization` | **Decision-Layer Designer** — predict-then-optimize: prediction→optimizer handoff gate, formulation (LP/MIP/CP-SAT/stochastic/robust/simulation), the optimizer's-curse failure mode + uncertainty-aware remedies, pure-OR check, decision-regret evaluation. Single-shot — distinct from `/bandit-design` + `/rl-design` |

**Industrial / IoT (OT data):**

| Command | What it does |
|---|---|
| `/uns-contextualization` | **Unified Namespace Architect** — ISA-95 namespace hierarchy; asset/digital-twin models (class once, instance per unit); raw-tag → business-concept map stored as versioned data; non-destructive (`_raw` preserved); per-signal owner/unit/freshness SLA |
| `/industrial-iot-ingestion` | **Industrial IoT Ingestion Architect** — OT protocol selection (OPC-UA / MQTT+Sparkplug B / Modbus); edge gateway store-and-forward (no-loss on outage); source/edge event-time stamping; OT→IT one-way boundary (no control path); deadband volume control |
| `/predictive-maintenance` | **Predictive Maintenance Advisor** — frames anomaly vs RUL vs failure-classification by failure-event count; lead-time gate (horizon = parts + scheduling + repair); cost-weighted threshold; leakage-audited features; alert→work-order policy |

**General (any project):**

| Command | What it does |
|---|---|
| `/office-hours` | **Assumptions Facilitator** — assumptions gate, six forcing questions that surface unstated assumptions and produce a design doc before any code is written |
| `/review` | **Code Reviewer** — [BLOCKER] / [SUGGESTION] / [NITPICK] grading across correctness, security, performance, clarity, test coverage |
| `/adr` | **ADR Facilitator** — Draft an Architecture Decision Record with context, rationale, alternatives, consequences, and risks |
| `/tradeoff` | **Tradeoff Analyst** — Options × pros/cons/failure-mode table + recommendation with named constraint |
| `/security-audit` | **Security Researcher** — Deep audit from attacker's perspective; stack-aware (Supabase/Firebase/Hasura/FastAPI/Express); CRITICAL→LOW findings with file+line. Use BEFORE multi-PR sprints touching DB/auth, BEFORE production deploy |
| `/security-model-init` | **Security Model Scaffolder** — generates `docs/SECURITY_MODEL.md` with stack-specific scaffolding. Run as commit #2 on any new project that has auth/DB/API surfaces |
| `/doc-ci-check` | **Doc-CI Gate** — count drift + broken-link + skill↔prompt↔CLAUDE↔README↔prompts/README parity + NEXT_SESSION HEAD freshness. Severity-grouped report. Use BEFORE shipping any docs commit. Pair with `.github/workflows/doc-ci.yml` |
| `/retro` | **Retrospective Facilitator** — Engineering retrospective — shipped summary, went well/wrong, one process change, writes new entries to LESSONS_LEARNED.md |

**Research and analysis:**

| Command | What it does |
|---|---|
| `/api-audit` | **API Ecosystem Analyst** — structured 6-phase API portfolio audit (discovery → inventory → shortcomings → recommendations → executive summary → options analysis); enforces primary-source verification, cross-file consistency, and advisor review gates |

**Production systems:**

| Command | What it does |
|---|---|
| `/threat-model` | **AI Threat Modeling Analyst** — AI-specific threat model — 8 mandatory threat categories (injection, poisoning, PII leakage, jailbreak, supply chain, excessive agency, etc.) |
| `/rollout` | **Rollout Planner** — Phased rollout plan — Shadow → Internal → Canary → Limited GA → Full GA, with eval gates and rollback triggers at each boundary |
| `/runbook` | **Incident Runbook Author** — AI incident runbook — 8 standard failure scenarios (degradation, hallucination spike, cost blowout, agentic loop runaway, etc.) with detection/triage/mitigation/escalation |
| `/pii-scan` | **PII Exposure Auditor** — PII exposure audit — maps data elements across 10 AI lifecycle stages; surfaces governance gaps; recommends ADRs |
| `/observability` | **Observability Stack Designer** — AI observability stack design — 5 signal layers, required metrics + alert thresholds, drift indicators, dashboard spec |

**Auth / Identity (OAuth / OIDC):**

| Command | What it does |
|---|---|
| `/oauth-flow-design` | **OAuth 2.x Flow Architect** — grant selection by client type (auth-code + PKCE / client-credentials / device); redirect-URI exact-match allowlist; `state` + PKCE; implicit/password rejected |
| `/oidc-integration` | **OIDC Integration Architect** — ID-token vs access-token; discovery + JWKS; `nonce`; claims→user via `sub` (+`iss`) not email; IdP federation; RP-initiated + back-channel logout |
| `/jwt-validation` | **JWT Validation Engineer** — verifier-pins-alg (reject `none`, RS↔HS confusion); JWKS-by-`kid`; `iss`/`aud`/`exp`/`nbf` checks; bounded skew; strict-mode lib (most auth CVEs live here) |
| `/token-lifecycle` | **Token Lifecycle Engineer** — no-localStorage / BFF storage; short access TTL; refresh rotation + reuse detection → family revoke; introspection / deny-list; secure-cookie attrs |
| `/session-management` | **Session Management Engineer** — server-side vs stateless; `HttpOnly`+`Secure`+`SameSite`+`__Host-` cookies; CSRF token beyond SameSite; id-regen on login; idle + absolute timeout; logout + SLO |
| `/m2m-auth` | **M2M Auth Engineer** — workload-identity / mTLS over static secrets; client-credentials + `private_key_jwt`; one-audience minimal-scope tokens; per-service credential; vault + rotation |
| `/scopes-consent-design` | **Scopes & Consent Designer** — `resource:action` read/write-split taxonomy (no `full_access`); scope + per-resource ownership / RBAC; legible consent; incremental auth; over-scoping audit |

**AI / LLM projects:**

| Command | What it does |
|---|---|
| `/eval-design` | **LLM Evaluation Designer** — LLM eval framework — metric taxonomy by task type, test set minimums, pass/fail thresholds, drift triggers |
| `/prompt-review` | **Prompt Quality Reviewer** — 9-dimension prompt health score — clarity, injection risk, role/persona, output format, token efficiency, hallucination surface, fallback, PII, versioning |
| `/rag-design` | **RAG System Architect** — context window vs. RAG decision, chunking, embedding, vector store, retrieval pattern, reranking, freshness, observability |
| `/agent-design` | **Agentic System Designer** — Agentic system design — stateless loop + durable session store, tool manifest, sandbox + reach, guardrails, HITL, Plan-Execute-Verify-Replan, fallback paths, observability |
| `/agent-memory` | **Agent Memory Architect** — tier selection (core/working/session/episodic/semantic/procedural), backing-store choice (file/KV/vector/graph/temporal-graph), validity windows, stale-context detection, per-tenant isolation, memory-quality eval |
| `/plan-mode` | **Plan-Mode Author** — versioned plan artifact at `scratch/PLAN-<task>.md`; subgoal DAG with depends_on + parallel_with; per-subgoal exit criterion + rollback (or [RISK: HIGH]); cost roll-up vs envelope; verify gates; Replan triggers |
| `/workflow-design` | **Workflow Architect** — deterministic multi-agent orchestration: fan-out (parallel / pipeline / loop-until / tournament), phase + Performance-Outcomes grader, N=3 reasoning-diverse adversarial verify, journaling + resume, budget caps (16-concurrent / 1000-per-run), host choice (Workflow tool / LangGraph / OpenAI Agents SDK / Google ADK / hand-rolled) |
| `/rollback-checkpoint` | **Rollback Operator** — rolls the working tree back to a snapshot taken by `shadow_git_checkpoint.py`; list / diff / partial-restore / full-restore (DESTRUCTIVE) / take-new-checkpoint workflow; never touches the project's own `.git`. Pair with the shadow-git-checkpoint hook. Distinct from `git revert` |
| `/mcp-design` | **MCP Server Designer** — MCP server design — tool/resource/prompt manifests; transport (stdio vs Streamable HTTP — note HTTP+SSE deprecated since spec 2025-03-26); auth (OAuth 2.1+PKCE with RFC 9728 PRM + RFC 8414/OIDC discovery + RFC 8707 resource indicators + RFC 9207 `iss` validation; DCR / RFC 7591 deprecated, prefer OAuth Client ID Metadata Documents); schema discipline; scope boundaries; error contract + idempotency; deferred-tool strategy; host-compatibility matrix; observability + audit log. Producer side (complements `/agent-design`) |
| `/multi-agent-design` | **Multi-Agent System Designer** — orchestration pattern (sequential/parallel/hierarchical/debate), framework selection (LangGraph/CrewAI/AutoGen), agent roster, state schema, failure handling, max_iterations gate |
| `/guardrails-design` | **Guardrails System Designer** — input/output safety layers, threat inventory, detection method per threat (Llama Guard/Presidio/NLI), latency budget, FPR targets, fail-open vs. fail-closed policy |
| `/red-team` | **AI Red Team Lead** — 5-phase AI red team battery — base model, application, infrastructure, operational, user-interaction adversarial (misinterpreted ambient input, spoofed biometrics, frustrated-user exploit, overreliance); phases scaled to risk tier |
| `/model-card` | **Model Documentation Author** — Model documentation — 9 sections: overview, intended use, training data, evals, limitations, risks, governance, versioning, ownership |
| `/supply-chain-review` | **AI Supply Chain Auditor** — AI supply chain audit — 6 layers (foundation model, training data, embedding, frameworks, plugins, AI-BOM) with production gate checklist |
| `/cost-optimize` | **Token Cost Optimizer** — Token spend analysis — model tier decision tree (Opus/Sonnet/Haiku), prompt caching strategy, batch vs. real-time, token budget sizing |
| `/feedback-loop` | **Feedback Loop Designer** — Production feedback loop design — signal taxonomy, review queue sampling, annotation workflow, signal → eval routing, improvement cadence |
| `/fine-tune` | **Fine-Tuning Advisor** — Fine-tune vs. prompt-engineer decision tree — dataset requirements, pre/post eval plan, cost-benefit analysis, training data format |
| `/llm-routing` | **LLM Router** — routing strategy (static/cascade/complexity-classifier/semantic), model tier map, fallback chain, quality-floor gate, cost/quality projection |
| `/build-vs-buy` | **Build vs Buy Advisor** — 5-dimension scoring (cost/control/speed/risk/capability), AI tooling decision matrix, 3-year TCO, vendor alternatives, exit strategy |
| `/prompt-management` | **PromptOps Lifecycle Engineer** — prompt-artifact CD pipeline: versioning + registry, build-once-promote-many env promotion, eval-gated promotion (consumes `/eval-design` thresholds), canary vs in-prod A/B, automated+manual rollback to last-good, change-control governance + audit. Defers eval metrics→`/eval-design`, one-time scoring→`/prompt-review`, model-object lifecycle→`/experiment-tracking` + `/model-deployment` |
| `/context-engineering` | **Context Assembly Architect** — per-turn context-window assembly: budget allocation across system + tool defs + memory + chunks + history, position-of-evidence ordering (lost-in-the-middle + cache-stable prefix), overflow/compaction (truncate/summarize/evict), relevance gating + dedup, assembly-quality probes. Owns request-construction glue; defers retrieval→`/rag-design`, memory tiers→`/agent-memory`, cost math→`/cost-optimize` |

**Cloud ML platforms:**

| Command | What it does |
|---|---|
| `/vertex-ai-design` | **Vertex AI Platform Architect** — GCP Vertex footprint: service split (Workbench / Pipelines / Training / Endpoints / Feature Store / Model Garden / Monitoring); compute selection; MLOps wiring; deployment pattern (online / batch / streaming); cost guardrails; observability; lock-in posture. Adjacent to `/sagemaker-design` (AWS) + `/databricks-asset-bundles` (Databricks) |
| `/sagemaker-design` | **SageMaker Platform Architect** — AWS SageMaker footprint: service split (Studio / Training / Endpoints / Pipelines / Feature Store / Monitor / Clarify / JumpStart); deployment pattern (real-time / async / serverless / batch / MME / MCE); compute; MLOps; cost guardrails; observability; lock-in posture |
| `/bedrock-design` | **Amazon Bedrock Architect** — AWS Bedrock GenAI footprint: service split (Models / AgentCore (GA 2025-10-13) / Knowledge Bases / Guardrails / Flows / Prompt Mgmt / IPR / Eval / Custom Import); model selection (Claude 4.x + Fable 5 + Nova 2 + Llama + Mistral + Cohere; **Sonnet 4 / Opus 4 retire 2026-06-15**); inference pattern (on-demand / PT / batch / cross-region); KB vector-store matrix (OpenSearch / Aurora / Neptune / Pinecone / MongoDB / Redis; binary-vector OpenSearch-only); Guardrails (incl. **Automated Reasoning** Nov 2025); IPR intra-family routing (GA 2025-04-22). Distinct from `/sagemaker-design` (AWS classical ML); adjacent to `/vertex-ai-design` (GCP) + `/azure-foundry-design` (Azure) |
| `/azure-foundry-design` | **Microsoft Foundry Architect (formerly Azure AI Foundry)** — Azure GenAI footprint: surface map (rebrand Ignite Nov 2025; `/azure/foundry/`), 1,900+ model catalog (Azure OpenAI GPT-5 family + Anthropic Claude + Llama + Mistral + DeepSeek + xAI + Cohere + Fireworks); **Foundry Agent Service (GA 2026-03-16, Responses-API wire-compat)**; BYO VNet private networking GA; Foundry IQ + Azure AI Search agentic retrieval; safety stack (**Prompt Shields** + Groundedness auto-correct + Content Safety + Protected Material); cost model (PTU breakeven >50% util + 150-200M tok/mo on GPT-4o; PAYG / Batch 50%; Azure +20-40% over OpenAI direct). Distinct from Azure ML (classical MLOps); adjacent to `/bedrock-design` (AWS) + `/vertex-ai-design` (GCP) |
| `/openai-platform-design` | **OpenAI Platform Architect** — direct OpenAI footprint (not Azure OpenAI): API surface (Responses API default; **Assistants API sunset 2026-08-26**; Chat Completions feature-frozen on GPT-5.4+ reasoning); model catalog (GPT-5.5/5.5 Pro/5.4/5.4 mini/5.4 nano/GPT-4.1 (1M ctx)/4.1 nano/o3/o4-mini); Agents SDK (Handoffs + Guardrails + Tracing; vendor sandboxes Blaxel/Cloudflare/Daytona/E2B/Modal/Runloop/Vercel); Realtime API (`gpt-realtime` GA 2025-08-28; Cedar+Marin voices; native MCP + image + SIP); Vector Stores + File Search; tools (Web Search $10/1K + Computer Use + Code Interpreter + Structured Outputs strict); **Deep Research cost trap ($30/call on o3-deep-research)**; prompt caching automatic ≥1024 tokens; Batch+Flex 50%; fine-tune trio (SFT/DPO/RFT); **OpenAI Evals read-only 2026-10-31 / shutdown 2026-11-30** — replace with Promptfoo/Braintrust/Langfuse/Agents-SDK tracing |
| `/snowflake-cortex-design` | **Snowflake AI/ML Platform Architect** — Snowflake AI footprint: service split (Cortex AISQL / Analyst / Search / Agents / Snowpark ML + Model Registry + Feature Store / SPCS), compute substrate (warehouse vs Cortex serverless vs SPCS pool), governance, credit-based cost guardrails, batch-vs-real-time deployment, lock-in. Warehouse-native peer to `/bigquery-ml-design` |
| `/bigquery-ml-design` | **BigQuery ML (BQML) Platform Architect** — warehouse-native SQL-driven ML: BQML-vs-export-to-Vertex gate, model_type selection, Gemini-in-BigQuery (ML.GENERATE_* / VECTOR_SEARCH / remote models), on-demand-vs-slot billing, TRANSFORM-clause skew guard, batch-vs-Vertex-endpoint serving. Adjacent to `/vertex-ai-design` + `/snowflake-cortex-design` |

**Infrastructure as code:**

| Command | What it does |
|---|---|
| `/terraform-review` | **Terraform Reviewer** — IaC review across 9 dimensions: state backend + locking; module structure; variable / output discipline; provider versioning; secrets handling; blast-radius gates (`prevent_destroy` / `ignore_changes`); drift detection; plan-vs-apply CI pattern; destructive-op safety. [BLOCKER] / [SUGGESTION] / [NITPICK] grouped findings. Use BEFORE `terraform apply` in any shared-state env |

**Compliance:**

| Command | What it does |
|---|---|
| `/compliance-mapping` | **Compliance Mapping Analyst** — SOC 2 / HIPAA / GDPR / EU AI Act controls → enforcement matrix (code path + evidence source + owner + CLEAN / PARTIAL / GAP status); gap register with target close dates; cross-framework overlap detection. Use BEFORE SOC 2 readiness, HIPAA engagement, GDPR DPIA, high-risk EU AI Act ship |

**Analytics / BI:**

| Command | What it does |
|---|---|
| `/dashboard-design` | **BI Dashboard Designer** — audience-first scoping (exec / analyst / operator / external — ONE per dashboard); one-question-per-dashboard rule; chart selection rubric by question shape; refresh cadence + honest SLA; governance (owner / certification / deprecation); performance budget + accessibility. Tool-agnostic (Looker / Tableau / Superset / Metabase / Power BI). Distinct from `/observability` and `/feature-monitoring` |

**Data engineering:**

| Command | What it does |
|---|---|
| `/pipeline-design` | **Data Pipeline Architect** — batch vs. streaming decision, orchestration, idempotency, backfill strategy, error handling, SLA |
| `/data-mesh` | **Data Mesh Architect** — domain ownership boundaries, data product specs (SLA/schema/access/quality contract), federated governance (policy-as-code), platform stack, one-domain-at-a-time migration |
| `/streaming-pipeline` | **Streaming Pipeline Architect** — stream vs. batch vs. hybrid decision, Kafka/Flink/Spark Streaming technology selection, windowing, state management, ML feature pipeline integration, consumer lag monitoring |
| `/schema-design` | **Data Schema Designer** — Data modeling — dimensional vs. 3NF vs. OBT decision, SCD types, partitioning strategy, schema evolution policy |
| `/data-quality` | **Data Quality Engineer** — Quality gate design — validation rules by dimension, anomaly detection thresholds, quarantine + replay strategy, SLAs |
| `/data-contract` | **Data Contract Author** — Producer/consumer data contract — schema ownership, SLAs, versioning, breaking change policy, enforcement |
| `/dbt-review` | **dbt Model Reviewer** — dbt model review — naming, ref/source usage, incremental correctness, test coverage, documentation |
| `/sql-review` | **SQL Query Reviewer** — SQL query review — join correctness, fanout bugs, partition pruning, performance anti-patterns, readability |
| `/data-cleanse` | **Data Cleansing Planner** — Data cleansing workflow — dirty data taxonomy (incl. batch effect, sparse classes, metadata-flagged anomalies), detection rules, remediation strategy, audit trail, cleansing order |
| `/dedup` | **Entity Resolution Specialist** — Deduplication & entity resolution — exact vs. fuzzy decision, blocking strategy, algorithm selection, confidence scoring, golden record, merge rules |
| `/schema-harmonization` | **Schema Harmonization Architect** — Multi-source schema merging — conflict taxonomy, canonical schema design, type/semantic/enum resolution, source priority policy |
| `/data-alignment` | **Data Alignment Architect** — Row-level multi-source consolidation — entity matching, timestamp synchronization (as-of joins, window aggregation), scale/encoding harmonization, batch effect detection + mitigation; complements `/schema-harmonization` (schema-level) |
| `/metadata-audit` | **Metadata Auditor** — 7-dimension column audit (provenance, collection method, units, transformation history, summarization rule, labeling process, update cadence); batch effect detection; gap register with severity |
| `/timeseries-resample` | **Time Series Resampling Advisor** — Time series resampling — upsample (interpolation by metric type) vs. downsample (aggregation), gap handling, temporal alignment |
| `/class-balancing` | **Class Imbalance Strategist** — ML class imbalance handling — strategy by imbalance ratio, SMOTE/oversample/weights, eval setup, threshold tuning |
| `/annotation-design` | **Annotation Schema Designer** — Annotation schema design — label taxonomy, decision tree, edge case catalog, calibration process |
| `/label-quality` | **Label Quality Assessor** — Label quality assurance — IAA metrics (κ/α), sampling strategy, adjudication workflow, quality thresholds |
| `/active-learning` | **Active Learning Strategist** — Active learning strategy — query strategy by labeled set size, uncertainty/diversity sampling, stopping criteria |
| `/split-design` | **Data Split Designer** — Train/val/test split — random/temporal/group decision, ratios by dataset size, stratification, minimum eval sizes |
| `/cross-validation` | **Cross-Validation Strategist** — CV strategy — k-fold variant selection, time series CV, group k-fold, nested CV for hyperparameter tuning |
| `/leakage-audit` | **Data Leakage Auditor** — Data leakage detection — temporal, target, group, preprocessing-order, and operational-availability leakage (production-readiness check) with code fixes |
| `/cdc-design` | **Change-Data-Capture Architect** — capture-side of an OLTP→lake/warehouse CDC pipeline: mechanism (log-based/query-based/trigger-based), snapshot→incremental cutover with no-gap/no-dupe boundary, delete/tombstone handling, DDL propagation, idempotent dedup contract into the sink. Defers stream topology→`/streaming-pipeline`, sink MERGE/SCD→`/delta-live-tables`, batch-vs-stream→`/pipeline-design` |
| `/data-observability` | **Data Observability Architect** — run-time, estate-wide observability over tables nobody wrote rules for: five pillars (freshness/volume/schema/distribution/lineage) as auto-baselined monitors with min-history-before-alerting, column-level lineage as the root-cause primitive, incident lifecycle (detect→triage→route→SLA), metadata anomaly signals, build-vs-buy axes. Defers per-pipeline gates→`/data-quality`, ML-feature health→`/feature-monitoring`, Databricks config→`/lakehouse-monitoring` |
| `/lakehouse-architecture` | **Lakehouse Architect** — medallion bronze/silver/gold zones; open table format (Iceberg/Delta/Hudi); partitioning by dominant query filter; compaction + snapshot expiry for OT/IoT scale; query-engine choice; lineage + time-travel reproducibility |

**Databricks integration:**

| Command | What it does |
|---|---|
| `/unity-catalog-governance` | **Unity Catalog Governance Architect** — catalog/schema/table namespace; group-based least-privilege grants; **ABAC + governed tags (preferred)** over row filters / column masks / dynamic views in UC (never BI); lineage for pre-change impact; system-table audit; per-catalog storage credentials |
| `/databricks-asset-bundles` | **Declarative Automation Bundles Engineer (formerly DABs)** — jobs / pipelines / models / dashboards as code in `databricks.yml`; per-target (dev/staging/prod) overrides; service-principal run-as; build-once promote-many; `validate` gate in CI |
| `/delta-live-tables` | **Lakeflow SDP Designer (formerly DLT)** — declarative medallion pipelines; streaming table vs materialized view per layer; expectations (warn/drop/fail) as code; `APPLY CHANGES` for CDC/SCD; triggered vs continuous |
| `/databricks-jobs-orchestration` | **Lakeflow Jobs Orchestrator (formerly Workflows)** — multi-task DAG; job-cluster / serverless (never all-purpose for prod); bounded retries + timeouts + on-failure alert; idempotent tasks for repair runs |
| `/spark-performance-tuning` | **Spark Performance Engineer** — Spark-UI-evidence-first diagnosis (skew/shuffle/spill/small files/join); AQE + broadcast + clustering fixes; Photon (stateless streaming only) compute-last; query+layout before compute |
| `/dbu-cost-optimization` | **Databricks Cost Engineer** — `system.billing` attribution first (via `billing_origin_product` enum); jobs vs all-purpose; serverless / Photon / spot; forced auto-termination; cluster-policy guardrails (distinct from `/cost-optimize` LLM tokens) |
| `/databricks-model-serving` | **Model Serving Engineer** — UC-registered model → endpoint; serve-by-alias rollout/rollback; scale-to-zero vs warm; traffic-split canary; inference tables → drift monitoring |
| `/mosaic-ai-vector-search` | **Databricks AI Search Engineer (formerly Mosaic AI Vector Search)** — Databricks-native RAG retrieval; Delta Sync index (CDF on); pinned embedding model (change = reindex); hybrid search + UC ACLs; recall@k / MRR eval (chunking → `/rag-design`) |
| `/auto-loader-ingestion` | **Auto Loader Ingestion Engineer** — incremental `cloudFiles` → Delta bronze; **file events (managed `useManagedFileEvents`) preferred** over legacy `useNotifications`; directory listing only for small backfills; `_rescued_data` kept; dedicated checkpoint exactly-once; schema evolution |
| `/databricks-agent-framework` | **Mosaic AI Agent Framework Engineer** — authors a GenAI agent against the MLflow `ChatAgent`/`ResponsesAgent` contract (models-from-code logging), instruments MLflow Tracing/autolog, gates promotion with the Agent Evaluation judge harness (`mlflow.genai.evaluate` + deterministic `@scorer`), binds Unity Catalog functions as governed tools, registers to UC. Defers serving→`/databricks-model-serving`, retrieval→`/mosaic-ai-vector-search`, loop/guardrails→`/agent-design` |
| `/lakehouse-monitoring` | **Databricks Data-Profiling Monitor Engineer (formerly Lakehouse Monitoring)** — configures a UC Data Quality Monitoring profile over a Delta/inference table: profile type (Snapshot/TimeSeries/InferenceLog), baseline strategy + stale-baseline guard, slices/granularities/custom metrics, auto `_profile_metrics`/`_drift_metrics` tables, refresh cadence, debounced SQL-alert + dashboard, inference→drift-alert loop. Owns PRODUCT config; defers drift math→`/model-drift` + `/feature-monitoring`, estate-wide→`/data-observability` |

**ML algorithm selection / tuning:**

| Command | What it does |
|---|---|
| `/algo-select` | **Algorithm Selection Advisor** — Algorithm selection — task type × dataset size × constraint decision tree; baseline + failure mode per recommendation |
| `/experiment-design` | **ML Experiment Designer** — hypothesis formulation, one-variable-per-experiment discipline, decision criteria before running, ordered queue by information gain / cost |
| `/training-infrastructure` | **Training Infrastructure Designer** — compute selection (CPU/GPU/TPU/cloud), distributed training strategy (DDP/FSDP/model-parallel), orchestration, checkpointing, cost estimate |
| `/hyperparameter-tuning` | **Hyperparameter Tuning Strategist** — Tuning strategy — random vs. Bayesian vs. async; search space by algorithm; complete Optuna/sklearn code |
| `/model-comparison` | **Model Comparison Analyst** — Statistical model comparison — test selection, effect size, practical significance threshold, production verdict |
| `/transfer-learning` | **Transfer Learning Advisor** — Source model/task selection, adaptation strategy (feature-extract / partial / full / adapter / LoRA), negative-transfer check, catastrophic-forgetting mitigation, evaluation plan including from-scratch baseline |

**Feature engineering:**

| Command | What it does |
|---|---|
| `/feature-engineering` | **Feature Engineering Advisor** — Encoding (categorical cardinality rules), numeric transforms, date extraction, aggregation features, sklearn Pipeline |
| `/feature-selection` | **Feature Selection Advisor** — Filter (variance, correlation, MI) → embedded (LASSO, permutation importance) → wrapper (RFECV); selection inside CV |
| `/feature-store-design` | **Feature Store Architect** — Online/offline store architecture, feature definition schema, point-in-time correct joins, backfill strategy, skew prevention |

**Data gathering:**

| Command | What it does |
|---|---|
| `/data-collection-design` | **Data Collection Planner** — Data volume targets by task type, collection strategy decision tree, representativeness checklist, labeling plan |
| `/synthetic-data-gen` | **Synthetic Data Generation Specialist** — Synthesis by data type (tabular/text/image/time-series), quality gates, synthetic-to-real ratio, placement rules |
| `/data-sourcing` | **Data Sourcing Analyst** — Public registry search, vendor evaluation checklist, license interpretation guide, per-source verdict |

**Data filtering / outlier handling:**

| Command | What it does |
|---|---|
| `/outlier-detection` | **Outlier Detection Specialist** — Method selection (Z-score / IQR / Isolation Forest / Mahalanobis / LOF), treatment by situation, outlier report, audit trail |
| `/data-filtering` | **Data Filtering Planner** — Domain rule filters, quality/completeness thresholds, relevance scoring, near-dedup — prescribed order + audit report |
| `/sparse-class-grouping` | **Sparse Class Grouping Advisor** — Collapse rare classes — frequency cutoff, domain hierarchy, embedding clustering, target-rate binning; MI validation |
| `/imputation-design` | **Imputation Strategist** — missingness-mechanism diagnosis (MCAR/MAR/MNAR via Little's test + missingness-AUC probe), method selection (deletion / mean-median-mode / KNN / MICE / model-based / domain / time-aware) by rate × mechanism, missingness-indicator decision, fit-on-train-only mechanics, post-imputation distortion check. Defers temporal gap-fill→`/timeseries-resample`, leakage audit→`/leakage-audit` |

**Model validation:**

| Command | What it does |
|---|---|
| `/model-validation` | **Model Validation Engineer** — Pre-deploy checklist (9 gates), CI bootstrap, slice analysis, edge case stress tests, latency gate, Go/No-Go verdict |
| `/model-calibration` | **Model Calibration Specialist** — ECE diagnosis, reliability diagram, Platt/isotonic/temperature scaling, AUC-preservation check |
| `/model-drift` | **Model Drift Monitor** — Data/concept/prediction drift detection (KS/PSI), severity levels, retraining triggers, daily monitoring pipeline |
| `/conformal-uncertainty` | **Conformal Uncertainty Quantification Designer** — distribution-free UQ via split conformal: prediction SETS (classification) + INTERVALS (regression) with a finite-sample coverage guarantee at 1−alpha; nonconformity score choice (LAC/APS/RAPS, CQR), calibration-set sizing, adaptive variants (Mondrian/weighted/EnbPI/ACI), coverage-loss-under-shift failure mode + rolling-coverage monitor. Distinct from `/model-calibration`; pairs with `/decision-threshold-policy` |
| `/decision-threshold-policy` | **Decision Threshold Designer** — turns calibrated scores into decisions: cost-optimal operating point (`t* = C_FP/(C_FP+C_FN)`, not 0.5), ROC-vs-PR choice by imbalance (Youden's J / F-beta / cost curve), prevalence-drift handling, multi-tier auto-approve/review/auto-reject bands, abstention/reject-option sized against review capacity. Defers calibrated probabilities→`/model-calibration`, deployment→`/model-deployment`, drift math→`/model-drift` |

**Model deployment:**

| Command | What it does |
|---|---|
| `/model-deployment` | **Model Deployment Engineer** — Artifact packaging checklist, phased rollout (shadow→canary→limited→full GA), automated + manual rollback triggers, deployment.yaml |
| `/inference-service-design` | **Inference Service Designer** — Serving pattern decision (REST/gRPC/batch + edge/IoT/on-device), latency budget breakdown, scaling spec, circuit breaker + safe fallback, OTA rollout for edge, observability signals |
| `/edge-ml-deployment` | **Edge ML Deployment Engineer** — edge-vs-cloud gate; per-stage latency budget; on-device-validated compressed model; signed atomic OTA + offline rollback; fail-safe fallback; OT advises-not-actuates boundary; offline-tolerant observability |
| `/model-decommissioning` | **Model Decommissioning Planner** — Retire a model — retirement criteria, dependency audit, consumer notification, archive policy, retention schedule |

**Responsible AI:**

| Command | What it does |
|---|---|
| `/bias-audit` | **Training Data Bias Auditor** — Training-data representativeness vs operational environment; 6 bias classes (sample selection, demographic, geographic, temporal, labeler, survivorship); run BEFORE training. Complements `/fairness-audit` which checks model outputs AFTER training |
| `/fairness-audit` | **AI Fairness Auditor** — Demographic parity, disparate impact ratio (80% rule), equal opportunity, protected-attribute slice analysis, mitigation strategies |
| `/explainability` | **Model Explainability Analyst** — SHAP / LIME / PDP / counterfactuals — global + local explanations, method selection by model type, audience-appropriate output |
| `/privacy-preserving-ml` | **PPML Mechanism Advisor** — the HOW of privacy at train/inference time: per-data-flow mechanism (DP/DP-SGD/PATE, federated learning + secure aggregation, k-anon·l-diversity·t-closeness), epsilon budget pinned before training, inference-threat→defense map (membership inference / model inversion / extraction), residual-risk register. NIST AI RMF "Privacy-Enhanced" trait |
| `/data-deidentification-design` | **Data De-identification Designer** — per-field treatment (suppression/masking/tokenization/pseudonymization/hashing/generalization/k-anon·l-div·t-closeness/DP/FPE), direct-vs-quasi-identifier classification, re-id risk scoring, utility-vs-privacy matrix + release verdict. Design-side complement to `/pii-scan` |
| `/human-oversight-design` | **Human Oversight Designer** — in-decision-path human-review loop for non-agentic ML: escalation routing + queue topology, reviewer-queue sizing/SLA (Little's Law), reviewer-override + subject appeal/contest flow (GDPR Art. 22 / EU AI Act Art. 14), automation-bias mitigation (anti-rubber-stamp), oversight metrics where HIGH reviewer–model agreement is a RED FLAG. Defers governance→`/responsible-ai-governance`, case-selection band→`/decision-threshold-policy`, QA sampling→`/feedback-loop` |

**MLOps / Lifecycle:**

| Command | What it does |
|---|---|
| `/experiment-tracking` | **Experiment Tracking Designer** — Run logging schema (params, metrics, artifacts, env), registry promotion criteria, reproducibility checklist |
| `/ab-test-design` | **A/B Test Designer** — Sample size calculation, assignment strategy, guardrail metrics, stopping rules, analysis plan + decision criteria |
| `/retraining-strategy` | **Model Retraining Strategist** — Trigger types (drift/calendar/performance), data window design, full vs. incremental, validation gates before promotion |
| `/data-versioning` | **Dataset Versioning Specialist** — Dataset versioning approach (DVC/time-travel/snapshot), registration schema, lineage chain, reproducibility checklist |
| `/mlops-cicd` | **MLOps Pipeline Engineer** — ML CI/CD pipeline stages, model quality gates (performance/fairness/latency), artifact registration schema, rollback triggers, GitHub Actions YAML |
| `/responsible-ai-governance` | **AI Governance Advisor** — Risk tier classification (T1–T4), 5-pillar governance framework, MRM checklist, pre-deploy gate matrix, EU AI Act flags, IP framing (process-as-IP, SaaS data-upload clauses, Indigenous Data Sovereignty / CARE / OCAP) |
| `/model-compression` | **Model Compression Specialist** — Compression technique selection (PTQ/QAT/pruning/distillation/GPTQ), ready-to-run code, eval plan on target hardware |
| `/feature-monitoring` | **Feature Health Monitor** — Production feature health — freshness SLAs, null rate baselines, schema drift, PSI per feature, dashboard spec, anomaly playbook |

---

## Stack add-ons

The base template is stack-agnostic. The [`stacks/`](stacks/) directory has drop-in additions for specific languages.

**Available stacks:**

| Stack | Commands added | What it includes |
|---|---|---|
| [`stacks/python/`](stacks/python/) | `/test-gen`, `/type-fix`, `/deps-audit` | pytest test generation, mypy/pyright error fixes, dependency CVE + outdated audit, ruff/mypy allowlist entries, Python CLAUDE.md block |
| [`stacks/typescript/`](stacks/typescript/) | `/test-gen`, `/type-fix`, `/deps-audit` | Vitest/Jest test generation, tsc/eslint error fixes, npm/pnpm audit, tsc/eslint/vitest allowlist entries, TypeScript CLAUDE.md block |
| [`stacks/go/`](stacks/go/) | `/test-gen`, `/type-fix`, `/deps-audit` | Table-driven test generation, go build/vet/staticcheck fixes, govulncheck audit, go allowlist entries, Go CLAUDE.md block |

**To adopt a stack (3 steps):**
```bash
# 1. Copy skills — replace <stack> with python, typescript, or go
cp -r stacks/<stack>/skills/* .claude/skills/

# 2. Merge settings — add entries from stacks/<stack>/settings-snippet.json into .claude/settings.json
# 3. Paste stacks/<stack>/claude-md-addendum.md into your CLAUDE.md
```

See [`stacks/README.md`](stacks/README.md) for how to add a new stack.

---

## Optional: context-mode MCP (for large codebases)

The `.claude/settings.json` pre-allowlists five context-mode tools. These are no-ops until you install the MCP server — safe to ignore if your codebase is small.

**What it does:** Runs shell commands and indexes their output into a sandboxed full-text search database. Instead of `cat bigfile.log` flooding your context window with 2,000 lines, `ctx_batch_execute` indexes the output and you query what you need. Prevents context exhaustion on large repos, long build logs, and multi-file analysis.

**When you need it:** When you hit context limits mid-task — build logs, dependency graphs, large refactors, or any codebase where multiple files need to be understood together.

**Install:**

```bash
# Requires Node.js 18+
npm install -g @anthropic-ai/context-mode
```

Then add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "context-mode": {
      "command": "context-mode",
      "args": ["serve"]
    }
  }
}
```

Restart Claude Code. The `ctx_*` tools in `.claude/settings.json` are already allowlisted — no further config needed.

> **Without context-mode:** Everything works. The allowlist entries are inert. Skip this section entirely for projects where context limits aren't a problem.

---

## Customizing the permission allowlist

`.claude/settings.json` controls which commands auto-approve without a prompt. Add patterns you use frequently that are read-only (no side effects, no state mutation):

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run typecheck)",
      "Bash(pytest --co -q *)",
      "Bash(gh pr view *)"
    ]
  }
}
```

Rules:
- Use `Bash(command *)` for prefix matching (space before `*` is required)
- Use `Bash(exact command)` for a single fixed invocation
- Never wildcard interpreters (`python3 *`, `node *`) — those allow arbitrary code execution
- `git`, `gh`, `ls`, `cat`, `grep`, `find` are auto-allowed by Claude Code — no entry needed

---

## How the session protocol works

Every session, Claude reads `CLAUDE.md` and follows:

```
NEXT_SESSION.md  →  LESSONS_LEARNED.md  →  CLAUDE.md  →  git status + log
                                                                          ↓
                                                              Ask what to work on
```

At the end of each session, you (or Claude) update `NEXT_SESSION.md` with HEAD, what landed, and what's open. The next session picks up exactly where the last one left off — no re-orientation.

`scratch/` is gitignored, so NEXT_SESSION.md stays local. If you work across machines, copy it manually or move it to a committed location.

---

## What to add over time

**More slash commands.** Every repeated workflow is a candidate:
- `/changelog` — draft a changelog entry from recent commits
- `/test-plan` — generate a test plan for a feature
- `/standup` — summarize yesterday's commits as a standup update

**More LESSONS_LEARNED entries.** Every time something goes wrong or unusually right, add a one-liner with a **Why:** line. The file compounds — after 10 sessions it's the most valuable thing in the repo.

**Hooks.** **13** reference hooks ship with the template in `.claude/hooks/`. None are wired by default — paste the snippet from `.claude/hooks/README.md` into your `settings.json` to enable any of them.

*Generic (3):*
- `block_dangerous_git.py` — PreToolUse/Bash: blocks force-push, `reset --hard`, `--no-verify`, and other destructive git operations
- `scan_secrets.py` — PreToolUse/Write|Edit: blocks AWS/GitHub/Slack/OpenAI/Anthropic/Google/Stripe key shapes before they land on disk
- `audit_log.py` — PostToolUse/*: passive; appends every tool call to `.claude/logs/audit.jsonl`

*Domain guardrails (10):*
- `block_infra_destroy.py`, `check_sql_safety.py`, `check_unsafe_patterns.py`, `check_cloud_cost.py`, `check_programming_gotchas.py`, `check_ml_leakage.py`, `block_test_set_balancing.py`, `check_metric_guardrail.py`, `check_pii_in_logs.py`, `check_prompt_safety.py` — see `.claude/hooks/README.md` for the full inventory + behaviour table.

To write your own, copy `templates/skill/SKILL-TEMPLATE.md` as a model for structure, then see `.claude/hooks/README.md` for the protocol (stdin format, exit codes, smoke tests).

---

## License

[Choose your license — MIT, Apache 2.0, CC-BY, etc.]
