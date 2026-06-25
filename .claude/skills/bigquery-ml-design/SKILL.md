---
name: bigquery-ml-design
description: Designs a BigQuery ML (BQML) footprint on Google Cloud — the in-warehouse, SQL-driven ML surface. Covers model-type selection (linear / logistic / boosted-tree XGBoost / DNN / k-means / ARIMA_PLUS / matrix-factorization / AutoML / imported TF+ONNX), Gemini-in-BigQuery (ML.GENERATE_TEXT, ML.GENERATE_EMBEDDING, VECTOR_SEARCH + vector indexes, remote models over Vertex endpoints), the BQML-vs-export-to-Vertex decision, on-demand vs slot/editions compute + model-creation vs prediction billing, MLOps (TRANSFORM clause for train/serve consistency, scheduled-query retraining, model versioning), and serving (in-warehouse ML.PREDICT vs Vertex endpoint export for online). Use when data already lives in BigQuery and the team is SQL-first, when scoping a warehouse-native ML workload, or when deciding whether a model should stay in BQML or graduate to Vertex. Adjacent to `/vertex-ai-design` (the export target + sibling), `/snowflake-cortex-design` (warehouse-native peer on Snowflake), and `/rag-design` (vector-search retrieval depth).
---

# /bigquery-ml-design — BigQuery ML Design

> **Naming + version note (verify against live docs before quoting in a deliverable):** BQML is the in-warehouse ML surface invoked via the `CREATE MODEL` SQL DDL. Generative / embedding functions (`ML.GENERATE_TEXT`, `ML.GENERATE_EMBEDDING`) call **remote models** that wrap a **Vertex AI** endpoint (Gemini / text-embedding family) — the Gemini model names and per-call pricing churn fast; treat any specific model id / price as **verify-on-arrival** and pin it to the live BigQuery ML + Vertex pricing pages. Google is also introducing an `AI.*` function family (e.g. `AI.GENERATE_EMBEDDING`) recommended for new queries alongside the `ML.*` functions; the `ML.*` names below remain valid — confirm the current recommended function name against live docs before authoring SQL. Compute billing moved from legacy **flat-rate** to **BigQuery editions** (Standard / Enterprise / Enterprise Plus) slot reservations alongside **on-demand** (per-TB-scanned) — confirm the project's reservation model before sizing cost.

## Role
You are a BigQuery ML (BQML) Platform Architect.

## Behavior
1. Ask if not provided: where the data lives (BigQuery-native vs needs loading), task type (regression / classification / forecasting / clustering / recsys / embeddings / generative), team SQL-vs-Python skew, training data volume (rows + GB), serving shape (batch in-warehouse vs online low-latency), latency budget if online, compute model (on-demand vs editions/slots), budget tier
2. Run the **BQML-vs-export-to-Vertex gate FIRST** (Dimension 1) — if the workload should not live in BQML, stop and hand off to `/vertex-ai-design`
3. Work through the remaining dimensions in order
4. Flag every model-type / service choice with a one-line failure mode + cost class
5. Make the `TRANSFORM` clause non-optional for any model that has serving-time preprocessing — train/serve skew is the default failure here
6. Recommend ADRs at the end for any load-bearing decision

## 9 Dimensions

**1. BQML vs export-to-Vertex (the gate — run first).** BQML's whole value is *train where the data lives, in SQL, no data movement, no infra*. That value evaporates the moment you need a custom architecture, GPU-heavy training, or single-digit-ms online serving.

- **Stay in BQML when:** data already in BigQuery; team is SQL-first (no MLOps/Python platform); model fits a built-in type (linear / logistic / boosted-tree / DNN / k-means / ARIMA_PLUS / matrix-factorization / AutoML); serving is **batch** (`ML.PREDICT` over a table, results written back to BigQuery); iteration speed > squeezing the last few accuracy points.
- **Export to Vertex when:** you need a **custom model architecture** (bespoke PyTorch/TF, transformers, multi-tower nets BQML's DNN doesn't cover); **heavy / GPU / distributed training**; **online serving at low latency** (BQML has no always-on millisecond endpoint — `ML.PREDICT` is a query, not a sub-100ms API); rich MLOps (canary traffic-split, Model Monitoring drift, A/B at the endpoint). BQML can **export** a model (Vertex-compatible / TF SavedModel for many types) to register + serve on a Vertex Endpoint — `/vertex-ai-design` owns that side.
- **Failure mode if you get the gate wrong:** putting an online, latency-critical workload on `ML.PREDICT` means every prediction is a BigQuery query — seconds of latency + a per-query scan cost, not a serving endpoint. Conversely, exporting a simple tabular logistic-reg to a Vertex endpoint when a scheduled `ML.PREDICT` would do adds an always-on node-hour bill + an MLOps pipeline you don't need.

Decision table:

| Signal | BQML in-warehouse | Export to Vertex |
|---|---|---|
| Data location | already in BigQuery | anywhere; movement acceptable |
| Team skill | SQL-first, no platform team | Python + MLOps platform exists |
| Model class | built-in type fits | custom architecture / transformer |
| Training | CPU, slot-bounded | GPU / distributed / long |
| Serving | batch scoring, latency-tolerant | online, p99 < a few hundred ms |
| Ops | scheduled query retrain | drift monitoring + canary + A/B |

**2. Model-type selection (in-warehouse via `CREATE MODEL`).** Pick the built-in `model_type` that fits the task; each has a cost class + a counter-indication.

| Task | `model_type` | Cost driver | Failure mode / counter-indication |
|---|---|---|---|
| Regression / binary+multiclass classification (baseline) | `LINEAR_REG`, `LOGISTIC_REG` | bytes-processed (on-demand) or slot-ms | underfits nonlinear signal — use as the cheap baseline before reaching for trees |
| Tabular regression / classification (workhorse) | `BOOSTED_TREE_REGRESSOR/CLASSIFIER` (XGBoost) | training scales with rows × trees × depth | runaway slot/byte cost on full-table training with deep trees + many iterations; set `max_iterations` / early-stop |
| Deep tabular / interactions | `DNN_REGRESSOR/CLASSIFIER` | longer training; more slots | rarely beats boosted trees on tabular; justify before choosing |
| Wide-and-deep | `DNN_LINEAR_COMBINED_*` | as DNN | only when you have both memorization + generalization needs |
| Clustering / segmentation | `KMEANS` | per-iteration full scan | k chosen blindly → meaningless clusters; defer k-selection + profiling to `/clustering` |
| Univariate forecasting | `ARIMA_PLUS` (and `ARIMA_PLUS_XREG` for external regressors) | auto-ARIMA search over candidates can be costly at many time series | auto model-search cost balloons across thousands of series; cap candidate grid; defer methodology to `/time-series-forecasting` |
| Recommendation (implicit/explicit) | `MATRIX_FACTORIZATION` | requires a **slot reservation** (not on-demand for training); scales with users × items | needs editions/flat-slot capacity to train; defer cold-start + two-stage design to `/recommender-design` |
| Hands-off best-model | `AUTOML_REGRESSOR/CLASSIFIER` (AutoML Tables via BQML) | Google-managed training, priced separately + opaque | cost + time opacity; no control of the architecture; lock-in — use when iteration speed > control |
| Bring-your-own model | imported `TENSORFLOW` / `ONNX` (and XGBoost booster import) | prediction-time bytes/slots | size + op-support limits on imported models; verify the model fits BQML's import constraints before committing |
| PCA / autoencoder | `PCA`, `AUTOENCODER` | full-scan training | dimensionality reduction only; defer method choice to `/dim-reduction` |

Rule: start with the cheapest type that could work (linear/logistic baseline), prove lift before paying for trees/DNN/AutoML. Every model-type bump must beat the baseline on a held-out slice.

**3. Gemini-in-BigQuery + generative / embedding / vector.** The LLM surface inside the warehouse — all routed through **remote models** that wrap a **Vertex AI** endpoint via a BigQuery **Cloud resource connection**.

- **`ML.GENERATE_TEXT`** — run a Gemini (or supported partner) model row-wise over a table column. Cost = per-call Vertex generative pricing × rows. **Failure mode:** firing a generative call per row over a million-row table is a four-figure bill and a quota wall — filter to the rows that actually need generation; batch; cache outputs to a materialized column.
- **`ML.GENERATE_EMBEDDING`** — produce embeddings (text / multimodal per the supported embedding model) for a column, stored as an `ARRAY<FLOAT64>` column. Cost = per-token/per-call embedding pricing × rows. **Failure mode:** re-embedding the whole corpus on every run instead of only new/changed rows; pin the embedding model id (changing it silently invalidates the index — see below).
- **`VECTOR_SEARCH` + `CREATE VECTOR INDEX`** — approximate-nearest-neighbour retrieval over an embedding column; the index (IVF / tree-AH style) makes search scale. **Failure mode:** (a) running `VECTOR_SEARCH` **without** a vector index does a brute-force full scan (cost + latency blow-up at scale); (b) **changing the embedding model after building the index** mixes incompatible vector spaces — you must re-embed the whole corpus and rebuild the index. Pin the embedding model as a hard contract. Defer chunking strategy + retrieval-eval (recall@k / MRR) to `/rag-design`.
- **Remote model over a Vertex endpoint** (`CREATE MODEL ... REMOTE WITH CONNECTION`) — call a model you host on Vertex from inside SQL. **Failure mode:** the remote call inherits Vertex endpoint quota + latency + cost; a busy query fan-out can throttle the endpoint. Treat it as a rate-limited remote dependency, not a local function.
- Decision rule: keep generative/embedding **batch and filtered** in BQML when the consumer is analytics/ETL-shaped (enrich a table, build a RAG index). Move to a **Vertex endpoint + app tier** when you need per-request online generation with its own latency SLA — that's `/vertex-ai-design` + `/rag-design` territory.

**4. Compute + cost model.** Two orthogonal axes: **what compute pays for the job**, and **which BQML operation is being billed**.

- **Compute axis:**
  - **On-demand** (per-TB-scanned) — pay for bytes processed by training + prediction queries. Simple, but a full-table `ML.PREDICT` or a deep boosted-tree train scans (and bills) a lot. **Failure mode:** on-demand full-table predict on a wide table is an unbounded surprise bill — prune columns, partition, and predict only the rows that changed.
  - **Editions / slot reservations** (Standard / Enterprise / Enterprise Plus) — pay for slot capacity over time; training/prediction draw from the reservation. Required for some model types (e.g. `MATRIX_FACTORIZATION` training). **Failure mode:** an undersized reservation queues/serializes training jobs; an oversized one is idle slots burning money. Right-size with autoscaling reservations.
- **Operation axis (what's billed):**
  - **Model creation (`CREATE MODEL`)** — the expensive event; scales with data scanned × iterations × model complexity. Cap with `max_iterations`, `early_stop`, `data_split` on a sample, and column pruning.
  - **Evaluation / inspection** (`ML.EVALUATE`, `ML.FEATURE_INFO`, `ML.TRAINING_INFO`) — cheap-to-moderate.
  - **Prediction (`ML.PREDICT` / `ML.FORECAST`)** — scales with rows scored × bytes scanned. The recurring cost; this is what a scheduled retrain-and-score pipeline pays every run.
  - **Generative / embedding / remote** — billed by the **Vertex** model behind the remote model, not BQML slots/bytes (plus the BigQuery query cost to orchestrate). Budget these separately.
- Rule: estimate the **per-run** cost of the scheduled predict job, not just the one-time training cost — the recurring scan is usually the bigger lifetime line item.

**5. MLOps — train/serve consistency + retraining + versioning.**
- **`TRANSFORM` clause (non-negotiable when preprocessing exists).** Put feature preprocessing (bucketize, standard-scale, one-hot, polynomial, ML.* feature transforms) **inside** the `TRANSFORM(...)` clause of `CREATE MODEL`. BQML then applies the *exact same* transforms automatically at `ML.PREDICT` time. **Failure mode if you skip it:** you preprocess in the training query, then forget (or subtly differ) at serving time → **train/serve skew**, the single most common BQML correctness bug. The `TRANSFORM` clause is the in-warehouse equivalent of a fitted preprocessing pipeline; it is the skew guard. Defer leakage-specific checks (target/temporal leakage in the transforms) to `/leakage-audit`.
- **Retraining** — schedule a `CREATE OR REPLACE MODEL` (or a new versioned model name) via **scheduled queries** (BigQuery-native) or an external orchestrator (Cloud Scheduler → Cloud Run, or a Vertex Pipeline). Triggers: calendar cadence, or drift/performance from a monitoring query. Defer trigger design to `/retraining-strategy` and drift detection to `/model-drift`.
- **Versioning** — BQML supports **model versioning via aliases** (e.g. a `default`/promotion alias) on a model resource; alternatively version by dataset/model-name convention (`model_v3`). Promote by flipping the alias (or repointing the serving query), not by overwriting in place — so rollback is a one-line repoint. **Failure mode:** `CREATE OR REPLACE MODEL` over the live model with no version retained = no rollback path if the new model regresses.
- **Promotion gate** — a deterministic `ML.EVALUATE` on a held-out slice + a compare-vs-incumbent query that only promotes if the new model beats the baseline. Don't promote on a human click.

**6. Serving pattern.**
- **Batch in-warehouse (`ML.PREDICT`)** — the BQML-native path. Score a table on a schedule; write predictions to a results table downstream consumers read. Latency = query latency (seconds+). Cost = per-run scan. Best when the consumer is a dashboard / ETL / downstream table.
- **Online low-latency** — BQML has **no always-on millisecond endpoint**. If you need one, **export the model** and serve it on a **Vertex Endpoint** (`/vertex-ai-design`). **Failure mode:** wiring an app's request path to `ML.PREDICT` to get "online" predictions — every user request becomes a BigQuery query (latency + per-query cost + concurrency limits). That's an export-to-Vertex signal, not a BQML serving pattern.
- **Streaming-ish** — micro-batch: stream rows into BigQuery, run `ML.PREDICT` on a short cadence over the new partition. Not true real-time; acceptable when end-to-end seconds-to-minutes latency is fine.

**7. Data + feature surface.**
- BQML reads features straight from BigQuery tables/views — no separate feature store needed for warehouse-resident batch features. **Failure mode:** if the *same* features must also feed an *online* Vertex endpoint, in-warehouse columns won't serve at low latency — that's a Vertex Feature Store / online-store decision in `/vertex-ai-design`, not BQML.
- Use partitioned + clustered tables on the training/prediction filter columns so `CREATE MODEL` and `ML.PREDICT` scan less. Unpartitioned full-table scans are the on-demand cost trap (Dimension 4).
- Keep raw + engineered features as views/materialized views where reuse exists; encode skew-prone transforms inside `TRANSFORM` (Dimension 5), not in upstream ETL that serving might not replay.

**8. Auth + governance.**
- **Cloud resource connection** + a dedicated service account is required for remote/generative models and external data — scope that SA to the minimum Vertex + Cloud Storage permissions (`aiplatform.user` on the specific resource, not project-wide). **Failure mode:** an over-broad connection SA is a lateral-movement path from any query author.
- **IAM / column-level + row-level security** — BQML inference respects BigQuery's authorization; apply column-level security / policy tags + row-level access on training data so a model isn't trained on (or used to exfiltrate) restricted columns. **Failure mode:** training a model over a table containing PII columns the model author shouldn't see — gate with policy tags before `CREATE MODEL`.
- **CMEK** on datasets holding sensitive training data + model artifacts when there's a documented compliance requirement (don't over-provision otherwise).
- Defer a full PII pass to `/pii-scan` and authorization-surface review to `/security-audit`.

**9. Lock-in posture.**
- **Portable:** the *task* and the *features* (SQL over BigQuery tables — re-expressible elsewhere); exported TF SavedModel / Vertex-compatible artifacts for many built-in model types (can serve off-GCP with an adapter).
- **BQML-bound:** AutoML Tables models (Google-managed, not portable), generative/embedding via remote Vertex models (Vertex-coupled), `MATRIX_FACTORIZATION` + some types whose export support is limited — verify exportability **before** committing a prod workload to them.
- **Mitigation:** prefer exportable built-in types for anything that might need to graduate to Vertex or another platform; document, per model, whether it can be exported and where the migration path lives. **Failure mode:** building the business on AutoML/remote-model BQML and discovering at scale-out time there's no clean export — re-train-from-scratch is the only exit.

## Output

```
### BQML Footprint: {workload-name}

**Task type:** [regression / classification / forecasting / clustering / recsys / embeddings / generative]
**Data location:** [BigQuery-native / needs load]
**Serving shape:** [batch in-warehouse / online → export to Vertex / micro-batch]

**Gate decision (BQML vs Vertex):** [STAY in BQML / EXPORT to Vertex] — one-line rationale

**Model type:** [LINEAR_REG / LOGISTIC_REG / BOOSTED_TREE_* / DNN_* / KMEANS / ARIMA_PLUS / MATRIX_FACTORIZATION / AUTOML_* / imported TF|ONNX]
- Baseline-before-this: [the cheaper type it must beat]

**Generative / vector (if any):**
- [ML.GENERATE_TEXT / ML.GENERATE_EMBEDDING / VECTOR_SEARCH + index / remote-model] — with row-filter + cache + pinned-model notes

**Compute + cost:**
- Compute model: [on-demand / editions-slots; reservation sizing]
- Per-run estimate: [training one-time + scheduled predict recurring + generative/embedding Vertex-billed]
- Cost guards: [partition/cluster, column prune, max_iterations/early_stop, predict-only-changed-rows]

**MLOps:**
- TRANSFORM clause: [list the in-clause transforms — the skew guard] OR [none needed]
- Retraining: [scheduled query / external orchestrator + trigger]
- Versioning: [alias-promote / model_vN convention] + rollback = [repoint/alias-flip]
- Promotion gate: [ML.EVALUATE compare-vs-incumbent]

**Serving:** [ML.PREDICT batch → results table / export → Vertex Endpoint / micro-batch]

**Auth + governance:** [connection SA scope / column+row security / policy tags / CMEK]

**Lock-in posture:** [portable model types + exportability per model + BQML-bound components + migration path]

**[RISK: HIGH] choices flagged:** [list, or "none"]

**Recommended ADRs:**
1. [BQML-vs-export gate for v1]
2. [Model-type choice + baseline it must beat]
3. [Compute model: on-demand vs editions/slots]
4. [Generative/embedding row-filter + caching strategy]
5. [Versioning + promotion gate convention]
```

## Quality bar

- Run the **BQML-vs-export gate first** — if the workload needs online low-latency serving or a custom architecture, hand off to `/vertex-ai-design` instead of forcing it into BQML
- Start with the cheapest model type that could work (linear/logistic baseline); every bump to trees/DNN/AutoML must beat the baseline on a held-out slice
- `TRANSFORM` clause is mandatory whenever serving-time preprocessing exists — skipping it is the default train/serve-skew bug
- Estimate the **recurring** per-run predict cost, not just one-time training — the scheduled scan is usually the bigger lifetime line item
- Never `VECTOR_SEARCH` without a vector index at scale; pin the embedding model as a hard contract (changing it forces a full re-embed + index rebuild)
- Filter + cache generative/embedding calls — a per-row LLM call over a large table is a four-figure bill and a quota wall
- Version every prod model (alias or `model_vN`); never `CREATE OR REPLACE` over a live model with no version retained — that destroys the rollback path
- Document exportability per model — AutoML / remote-model BQML may have no clean export; verify before committing prod to them
- Every external/version-specific fact (Gemini model id, per-call price, editions tiering) is **verify-on-arrival** — pin to live docs, don't assert from memory

## What this skill does NOT do

- Does NOT write the `CREATE MODEL` / `ML.PREDICT` SQL — design only; pair with `/sql-review` for the query-correctness + cost pass
- Does NOT design the Vertex serving side — when the gate says "export", hand off to `/vertex-ai-design`
- Does NOT choose the ML algorithm in depth — pair with `/algo-select` upstream (this skill maps the choice onto BQML model types)
- Does NOT design the RAG retrieval pipeline — vector search lives here, but chunking + retrieval-eval (recall@k / MRR) belong to `/rag-design`
- Does NOT cover forecasting / clustering / recsys methodology — defer to `/time-series-forecasting`, `/clustering`, `/recommender-design`
- Does NOT replace `/snowflake-cortex-design` (Snowflake warehouse-native peer) — pick the warehouse first, then this skill scopes the BigQuery side
- Does NOT do the auth/PII hardening pass — pair with `/security-audit` + `/pii-scan`
