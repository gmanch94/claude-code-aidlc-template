# claude-code-template

A GitHub template repo for Claude Code projects. Pre-wires the four things that determine whether Claude Code is genuinely useful on a project — or just occasionally helpful.

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
| `.claude/settings.json` | Permission allowlist. Pre-populated with context-mode MCP tools (see below). Add project-specific read-only patterns here. |
| `.claude/commands/review.md` | `/review` — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format. |
| `.claude/commands/adr.md` | `/adr` — draft an Architecture Decision Record with full rationale and alternatives. |
| `.claude/commands/tradeoff.md` | `/tradeoff` — structured tradeoff analysis: options × pros/cons/failure-mode + recommendation with named constraint. |
| `memory/MEMORY.md` | Index for Claude's persistent project memory. |
| `prompts/` | 8 system prompt templates — RAG Q&A, agent, chat, classifier, extractor, code reviewer, summarizer, structured output. Each has placeholders, usage notes, and a prompt health score. |
| `.gitignore` | Gitignores `scratch/` (personal workspace) and `.claude/settings.local.json`. |

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

**Problem framing / EDA:**

| Command | What it does |
|---|---|
| `/problem-framing` | ML vs. rules decision, solution type, success metric tied to KPI, non-ML baseline, problem statement card |
| `/eda` | Dataset profiling — target distribution, missingness, cardinality, correlations, leakage candidates, EDA summary report |

**General (any project):**

| Command | What it does |
|---|---|
| `/review` | Code review — [BLOCKER] / [SUGGESTION] / [NITPICK] grading across correctness, security, performance, clarity, test coverage |
| `/adr` | Draft an Architecture Decision Record with context, rationale, alternatives, consequences, and risks |
| `/tradeoff` | Options × pros/cons/failure-mode table + recommendation with named constraint |

**Production systems:**

| Command | What it does |
|---|---|
| `/threat-model` | AI-specific threat model — 8 mandatory threat categories (injection, poisoning, PII leakage, jailbreak, supply chain, excessive agency, etc.) |
| `/rollout` | Phased rollout plan — Shadow → Internal → Canary → Limited GA → Full GA, with eval gates and rollback triggers at each boundary |
| `/runbook` | AI incident runbook — 8 standard failure scenarios (degradation, hallucination spike, cost blowout, agentic loop runaway, etc.) with detection/triage/mitigation/escalation |
| `/pii-scan` | PII exposure audit — maps data elements across 10 AI lifecycle stages; surfaces governance gaps; recommends ADRs |
| `/observability` | AI observability stack design — 5 signal layers, required metrics + alert thresholds, drift indicators, dashboard spec |

**AI / LLM projects:**

| Command | What it does |
|---|---|
| `/eval-design` | LLM eval framework — metric taxonomy by task type, test set minimums, pass/fail thresholds, drift triggers |
| `/prompt-review` | 9-dimension prompt health score — clarity, injection risk, role/persona, output format, token efficiency, hallucination surface, fallback, PII, versioning |
| `/rag-design` | RAG system design — context window vs. RAG decision, chunking, embedding, vector store, retrieval pattern, reranking, freshness, observability |
| `/agent-design` | Agentic system design — loop architecture, tool manifest, guardrails checklist, HITL design, fallback paths, observability |
| `/red-team` | 4-phase AI red team battery — base model, application layer, infrastructure, operational (phases scaled to risk tier) |
| `/model-card` | Model documentation — 9 sections: overview, intended use, training data, evals, limitations, risks, governance, versioning, ownership |
| `/supply-chain-review` | AI supply chain audit — 6 layers (foundation model, training data, embedding, frameworks, plugins, AI-BOM) with production gate checklist |
| `/cost-optimize` | Token spend analysis — model tier decision tree (Opus/Sonnet/Haiku), prompt caching strategy, batch vs. real-time, token budget sizing |
| `/feedback-loop` | Production feedback loop design — signal taxonomy, review queue sampling, annotation workflow, signal → eval routing, improvement cadence |
| `/fine-tune` | Fine-tune vs. prompt-engineer decision tree — dataset requirements, pre/post eval plan, cost-benefit analysis, training data format |

**Data engineering:**

| Command | What it does |
|---|---|
| `/pipeline-design` | Data pipeline architecture — batch vs. streaming decision, orchestration, idempotency, backfill strategy, error handling, SLA |
| `/schema-design` | Data modeling — dimensional vs. 3NF vs. OBT decision, SCD types, partitioning strategy, schema evolution policy |
| `/data-quality` | Quality gate design — validation rules by dimension, anomaly detection thresholds, quarantine + replay strategy, SLAs |
| `/data-contract` | Producer/consumer data contract — schema ownership, SLAs, versioning, breaking change policy, enforcement |
| `/dbt-review` | dbt model review — naming, ref/source usage, incremental correctness, test coverage, documentation |
| `/sql-review` | SQL query review — join correctness, fanout bugs, partition pruning, performance anti-patterns, readability |
| `/data-cleanse` | Data cleansing workflow — dirty data taxonomy, detection rules, remediation strategy, audit trail, cleansing order |
| `/dedup` | Deduplication & entity resolution — exact vs. fuzzy decision, blocking strategy, algorithm selection, confidence scoring, golden record, merge rules |
| `/schema-harmonization` | Multi-source schema merging — conflict taxonomy, canonical schema design, type/semantic/enum resolution, source priority policy |
| `/timeseries-resample` | Time series resampling — upsample (interpolation by metric type) vs. downsample (aggregation), gap handling, temporal alignment |
| `/class-balancing` | ML class imbalance handling — strategy by imbalance ratio, SMOTE/oversample/weights, eval setup, threshold tuning |
| `/annotation-design` | Annotation schema design — label taxonomy, decision tree, edge case catalog, calibration process |
| `/label-quality` | Label quality assurance — IAA metrics (κ/α), sampling strategy, adjudication workflow, quality thresholds |
| `/active-learning` | Active learning strategy — query strategy by labeled set size, uncertainty/diversity sampling, stopping criteria |
| `/split-design` | Train/val/test split — random/temporal/group decision, ratios by dataset size, stratification, minimum eval sizes |
| `/cross-validation` | CV strategy — k-fold variant selection, time series CV, group k-fold, nested CV for hyperparameter tuning |
| `/leakage-audit` | Data leakage detection — temporal, target, group, and preprocessing-order leakage with code fixes |

**ML algorithm selection / tuning:**

| Command | What it does |
|---|---|
| `/algo-select` | Algorithm selection — task type × dataset size × constraint decision tree; baseline + failure mode per recommendation |
| `/hyperparameter-tuning` | Tuning strategy — random vs. Bayesian vs. async; search space by algorithm; complete Optuna/sklearn code |
| `/model-comparison` | Statistical model comparison — test selection, effect size, practical significance threshold, production verdict |

**Feature engineering:**

| Command | What it does |
|---|---|
| `/feature-engineering` | Encoding (categorical cardinality rules), numeric transforms, date extraction, aggregation features, sklearn Pipeline |
| `/feature-selection` | Filter (variance, correlation, MI) → embedded (LASSO, permutation importance) → wrapper (RFECV); selection inside CV |
| `/feature-store-design` | Online/offline store architecture, feature definition schema, point-in-time correct joins, backfill strategy, skew prevention |

**Data gathering:**

| Command | What it does |
|---|---|
| `/data-collection-design` | Data volume targets by task type, collection strategy decision tree, representativeness checklist, labeling plan |
| `/synthetic-data-gen` | Synthesis by data type (tabular/text/image/time-series), quality gates, synthetic-to-real ratio, placement rules |
| `/data-sourcing` | Public registry search, vendor evaluation checklist, license interpretation guide, per-source verdict |

**Data filtering / outlier handling:**

| Command | What it does |
|---|---|
| `/outlier-detection` | Method selection (Z-score / IQR / Isolation Forest / Mahalanobis / LOF), treatment by situation, outlier report, audit trail |
| `/data-filtering` | Domain rule filters, quality/completeness thresholds, relevance scoring, near-dedup — prescribed order + audit report |
| `/sparse-class-grouping` | Collapse rare classes — frequency cutoff, domain hierarchy, embedding clustering, target-rate binning; MI validation |

**Model validation:**

| Command | What it does |
|---|---|
| `/model-validation` | Pre-deploy checklist (9 gates), CI bootstrap, slice analysis, edge case stress tests, latency gate, Go/No-Go verdict |
| `/model-calibration` | ECE diagnosis, reliability diagram, Platt/isotonic/temperature scaling, AUC-preservation check |
| `/model-drift` | Data/concept/prediction drift detection (KS/PSI), severity levels, retraining triggers, daily monitoring pipeline |

**Model deployment:**

| Command | What it does |
|---|---|
| `/model-deployment` | Artifact packaging checklist, phased rollout (shadow→canary→limited→full GA), automated + manual rollback triggers, deployment.yaml |
| `/inference-service-design` | Serving pattern decision (REST/gRPC/batch), latency budget breakdown, scaling spec, circuit breaker + safe fallback, observability signals |
| `/model-decommissioning` | Retire a model — retirement criteria, dependency audit, consumer notification, archive policy, retention schedule |

**Responsible AI:**

| Command | What it does |
|---|---|
| `/fairness-audit` | Demographic parity, disparate impact ratio (80% rule), equal opportunity, protected-attribute slice analysis, mitigation strategies |
| `/explainability` | SHAP / LIME / PDP / counterfactuals — global + local explanations, method selection by model type, audience-appropriate output |

**MLOps / Lifecycle:**

| Command | What it does |
|---|---|
| `/experiment-tracking` | Run logging schema (params, metrics, artifacts, env), registry promotion criteria, reproducibility checklist |
| `/ab-test-design` | Sample size calculation, assignment strategy, guardrail metrics, stopping rules, analysis plan + decision criteria |
| `/retraining-strategy` | Trigger types (drift/calendar/performance), data window design, full vs. incremental, validation gates before promotion |
| `/data-versioning` | Dataset versioning approach (DVC/time-travel/snapshot), registration schema, lineage chain, reproducibility checklist |
| `/mlops-cicd` | ML CI/CD pipeline stages, model quality gates (performance/fairness/latency), artifact registration schema, rollback triggers, GitHub Actions YAML |
| `/responsible-ai-governance` | Risk tier classification (T1–T4), 5-pillar governance framework, MRM checklist, pre-deploy gate matrix, EU AI Act flags |
| `/model-compression` | Compression technique selection (PTQ/QAT/pruning/distillation/GPTQ), ready-to-run code, eval plan on target hardware |
| `/feature-monitoring` | Production feature health — freshness SLAs, null rate baselines, schema drift, PSI per feature, dashboard spec, anomaly playbook |

---

## Stack add-ons

The base template is stack-agnostic. The [`stacks/`](stacks/) directory has drop-in additions for specific languages.

**Available stacks:**

| Stack | Commands added | What it includes |
|---|---|---|
| [`stacks/python/`](stacks/python/) | `/test-gen`, `/type-fix`, `/deps-audit` | pytest test generation, mypy/pyright error fixes, dependency CVE + outdated audit, ruff/mypy allowlist entries, Python CLAUDE.md block |

**To adopt a stack (3 steps):**
```bash
# 1. Copy skills
cp -r stacks/python/skills/* .claude/skills/

# 2. Merge settings — add entries from stacks/python/settings-snippet.json into .claude/settings.json
# 3. Paste stacks/python/claude-md-addendum.md into your CLAUDE.md
```

See [`stacks/README.md`](stacks/README.md) for how to add a new stack (TypeScript, Go, etc.).

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

**Hooks.** Claude Code hooks run shell commands before or after tool calls. Common patterns:
- Block secrets from being committed (`pre-commit` hook scanning for API keys)
- Run linter before file edits land
- Log cost metrics per session

See the [Claude Code hooks documentation](https://docs.claude.com/en/docs/claude-code/hooks) for setup.

---

## License

[Choose your license — MIT, Apache 2.0, CC-BY, etc.]
