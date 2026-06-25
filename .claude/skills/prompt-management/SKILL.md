---
name: prompt-management
description: Designs a PromptOps / prompt-lifecycle pipeline — prompt versioning + registry, environment promotion (dev→staging→prod, build-once-promote-many), eval-gated rollout, A/B-in-prod + canary for prompt variants, regression rollback, and change-control governance. Emits a PromptOps design doc (registry schema + promotion gates + rollback trigger spec + change policy). Use when asked about "prompt versioning", "prompt registry", "PromptOps", "promote a prompt to prod", "prompt rollback", "who approves a prompt change", "A/B test a prompt", or shipping prompt changes safely. DEFER eval metric/test-set design to /eval-design, one-time prompt quality scoring to /prompt-review, model-object lifecycle to /experiment-tracking + /model-deployment.
---

# Prompt Management

## Role
You are a PromptOps Lifecycle Engineer.

## What this skill owns vs. defers

You own the **prompt-artifact CD pipeline**: how a prompt is versioned, registered, promoted across environments, A/B-tested in prod, rolled back, and change-controlled. The prompt is a deployable artifact with its own release lifecycle — treat it like one.

| Concern | Owner |
|---|---|
| Prompt versioning, registry schema, env promotion, A/B/canary, rollback, change-control | **this skill** |
| Eval metric definition + test-set design (what to measure, how big the set) | defer to `/eval-design` — you **consume** its thresholds as promotion gates, you don't design the metrics |
| One-time prompt quality scoring (clarity, injection risk, the 9 dimensions) | defer to `/prompt-review` — that gates an authored prompt before it enters the registry |
| Model-object lifecycle (weights, training runs, model registry stages) | defer to `/experiment-tracking` (run logging) + `/model-deployment` (model rollout) |
| LLM routing / model-tier selection at request time | defer to `/llm-routing` |

A silent prompt edit shipped to prod with no version and no rollback is a common production-incident cause for LLM systems. The whole point of this skill is to make that impossible.

## Quick start

Every prompt that reaches prod is a pinned, immutable, content-addressed version in a registry. Code references it by **id/alias, never by inline string**. Promotion dev→staging→prod copies the *same* artifact (build-once-promote-many) — you never re-author at the prod boundary. Every prod change clears an eval gate and has a named rollback target that is already live-loadable.

## Workflow

1. Ask if not provided: how many prompts / templates, current storage (inline in code? a file? a vendor tool?), eval harness available (and its thresholds — from `/eval-design`), environments (dev/staging/prod or fewer), traffic volume (does in-prod A/B make sense?), and who is allowed to approve a prod prompt change.
2. Design the **registry schema** (§1) — versioning scheme + metadata to log.
3. Define **environment promotion** (§2) — pinning + build-once-promote-many.
4. Wire **eval-gated promotion** (§3) — consume thresholds, don't design metrics.
5. Design **A/B-in-prod + canary** (§4) for variant comparison.
6. Specify the **rollback trigger spec** (§5).
7. Define **change-control governance** (§6).
8. Emit the **PromptOps design doc** (§7).

### 1. Prompt versioning + registry

**Versioning scheme — pick one, state the tradeoff:**

| Scheme | Use when | Failure mode |
|---|---|---|
| **Content-addressed** (`sha256(template + params + model_id)[:12]`) | You want guaranteed immutability + dedup; an identical prompt always resolves to the same id | Hash is opaque to humans — pair with a human alias (`summarizer@prod`) or nobody can talk about "the current prod prompt" |
| **Semver** (`summarizer/2.3.0`) | Humans reason about MAJOR (breaking output-contract change) / MINOR (behavior tweak) / PATCH (typo) | Semver is a *claim*, not enforced — a "PATCH" can silently change behavior; require an eval diff to justify the bump level |
| **Monotonic int** (`summarizer/v17`) | Small team, low ceremony | Carries no signal about blast radius; reviewer can't tell a typo fix from a rewrite |

Default: **content-address for the immutable id, semver alias for humans, environment alias for resolution** (`summarizer@prod` → `summarizer/2.3.0` → `sha256:a1b2c3…`). Three names, one artifact.

**Template vs. instance — separate them.** The *template* is the versioned artifact (with `{{slots}}`). The *instance* is template + runtime-filled variables for one call. Version templates; log instances (rendered prompt + var values) to the trace store for debugging. Never version a rendered instance — that explodes the registry and leaks PII into it.

**Metadata to log per registered version (the registry row):**

```json
{
  "prompt_id":      "summarizer/2.3.0",
  "content_hash":   "sha256:a1b2c3d4e5f6",
  "template":       "Summarize the following...\n{{document}}",
  "input_schema":   {"document": "string"},
  "target_model":   "<your-pinned-model-id>", // a prompt is co-versioned with its model; pin the exact id
  "model_params":   {"temperature": 0.2, "max_tokens": 1024},
  "eval_score":     {"suite": "summ-eval-v4", "faithfulness": 0.94, "pass_rate": 0.97},
  "eval_run_id":    "eval-run-8821",         // link to the /eval-design run that gated it
  "review_status":  "approved",              // from /prompt-review, see §6
  "author":         "a.patel",
  "approved_by":    "m.chen",
  "created_at":     "2026-06-20T14:02:00Z",
  "parent_version": "summarizer/2.2.1",      // lineage for diff + rollback
  "status":         "production"             // none | staging | production | archived
}
```

The **`target_model` field is load-bearing**: a prompt tuned on one model is not validated on another. Pin the (prompt × model × params) triple as the deployable unit. Bumping the model is a new prompt version and re-clears the eval gate — defer the *model choice itself* to `/llm-routing`, but the prompt registry records which model the version was validated against.

Backing store options:

| Store | Use when | Counter-indication |
|---|---|---|
| Git (prompts as files, PR-reviewed) | You want diff/review/rollback for free and prompts change at code cadence | No runtime hot-swap — a prompt fix needs a deploy; bad if you need sub-minute rollback |
| DB / KV registry table | Runtime resolution by alias, hot-swap without deploy | You must rebuild git's review + diff + audit trail yourself, or you get silent edits — the exact failure this skill exists to prevent |
| Vendor PromptOps (LangSmith / Langfuse / Humanloop / vendor prompt-mgmt) | You want registry + eval + trace in one place | Lock-in; export the registry to git on every promotion so you can leave |

Default for a code-cadence team: **git as source of truth + a thin runtime resolver** that reads the pinned version. You get review/diff/audit from git and avoid the silent-edit class entirely.

### 2. Environment promotion (build-once-promote-many)

```
dev  ──author + iterate──►  staging  ──eval gate──►  prod
 │                            │                        │
 alias: summarizer@dev    @staging                  @prod
 points at: latest        a frozen candidate        a frozen, eval-passed version
```

Rules:
- **Each environment resolves a prompt only through its alias.** Application code at every tier reads `registry.get("summarizer", env=ENV)` — never an inline string, never a hardcoded version number.
- **Build-once-promote-many.** Promotion is a *pointer move* of the env alias to an already-registered version. You do NOT re-author or re-render at the prod boundary. The artifact that ran in staging is byte-identical to the one that runs in prod (same `content_hash`). Re-authoring at the boundary is how "it passed staging but broke prod" happens.
- **Prod is pinned to an exact version, never to `@latest`.** `@latest` in prod means an unrelated dev edit can reach users with no gate. Pin `@prod → summarizer/2.3.0`; promotion changes the pin explicitly.
- **Promotion is auditable.** Each alias move writes a record: who, when, from-version, to-version, eval_run_id, approver.

Failure mode: aliases that resolve to `@latest` in prod. A teammate iterating in dev ships to users instantly. Pin prod to an immutable version; only an explicit, approved promotion moves the pin.

### 3. Eval-gated promotion

You **consume** eval thresholds; you do **not** design the metrics or the test set — that is `/eval-design`'s job. Your job is to wire the gate into the promotion path so no version reaches prod without clearing it.

```
Promotion gate: staging → prod
  Inputs:  candidate version C, current-prod version P, eval suite from /eval-design
  Run:     eval suite on C  (same fixed test set used for P)
  Gate (ALL must hold):
    □ C primary metric  ≥ threshold        (absolute floor, from /eval-design)
    □ C primary metric  ≥ P − ε            (no regression vs. current prod; ε = noise band)
    □ C safety/guardrail pass-rate ≥ floor (refusal correctness, injection-resistance)
    □ C cost-per-call   ≤ budget           (a prompt rewrite that doubles tokens fails here)
    □ C latency p95     ≤ SLA              (longer prompt → higher TTFT)
    □ review_status == approved            (see §6)
  On pass: register C as promotable; await §6 sign-off, then move @prod pin.
  On fail: block; attach eval diff (C vs P, per-case) to the PR/record.
```

Two non-obvious gates that prompt changes specifically trip:
- **Cost regression.** A prompt that adds few-shot examples can silently 2–3× input tokens. Gate cost-per-call, not just quality.
- **Output-contract drift.** If downstream code parses the output (JSON, a tag, a fixed field), a prompt edit can break the contract while *improving* the quality metric. Add a schema-conformance check to the gate (this is the prompt analog of model-deployment's signature enforcement).

If the team has no eval harness yet: that is a blocker to safe promotion — stop and route to `/eval-design` to build one before wiring this gate. Do not invent thresholds here.

### 4. A/B-in-prod + canary for prompt variants

Two distinct rollout shapes — choose by goal:

| Shape | Goal | When |
|---|---|---|
| **Canary** | De-risk a known-better candidate | You already believe C ≥ P (eval passed); you want a live safety net before 100% |
| **A/B (split)** | *Learn* which of 2+ variants is better on a live business metric eval can't capture | Eval is inconclusive or the metric is downstream (CSAT, conversion, deflection) |

**Canary (the default for an eval-passed promotion):**
```
shadow (optional, for output-contract risk):
  C runs on a copy of live traffic; output logged, NOT returned to users
  gate: output schema conforms; no exceptions; distribution within band
canary 5%:
  C serves 5% of live requests, pinned by a stable hash of the request/user id
  monitor: error rate, output-schema-violation rate, cost/call, latency p95, guardrail trips
  gate: schema-violation rate < 0.1%; cost within budget; no guardrail-trip spike
ramp: 5% → 25% → 100%, holding ≥1 traffic cycle (e.g. a full day) at each step
```

**A/B (split test):**
- Assign by a **stable hash of a stable key** (user id, account id) so a given user sees a consistent variant — flipping a user between prompt variants mid-session corrupts both the experience and the metric.
- Pre-register the decision metric and minimum sample/duration. **Defer the sample-size math and stopping rule to `/ab-test-design`** — you wire the variant serving, it sizes the test.
- Cap concurrent prompt experiments per surface (default 1) — overlapping prompt A/Bs on the same endpoint make attribution impossible.

Failure mode: assigning A/B by random-per-request instead of per-user. The same user gets variant A then B on consecutive turns; the conversation is incoherent and the metric is noise. Hash a stable key.

### 5. Rollback trigger spec

```
Automated rollback (no human; revert @prod pin to last-good version):
  □ output-schema-violation rate > 1% for 5 consecutive minutes
  □ guardrail/refusal-trip rate > 2× the 7-day baseline for 10 minutes
  □ error/exception rate > 1% for 5 consecutive minutes
  □ cost-per-call > 1.5× the promoted budget, sustained 15 minutes

Manual rollback (human decision):
  □ business metric (CSAT, deflection, conversion) drops > X% vs. baseline in canary
  □ qualitative report of a behavior regression eval did not catch
  □ a model-side change (provider deprecation/behavior shift) invalidates the prompt
```

Rollback procedure: **move the `@prod` alias back to `parent_version`.** Because every prior version is immutable and still in the registry, rollback is a pointer move — seconds, not a re-deploy. Preconditions that make this real:
- **The last-good version must be load-loadable at all times** (don't garbage-collect the previous prod version). This is the prompt analog of "keep the rollback image warm."
- **Rollback must not require a code deploy.** If your store is git-only with no runtime resolver, a prompt rollback is a full deploy — acceptable only if your deploy is sub-minute; otherwise add a runtime registry so the pin moves without shipping code.
- After rollback, the bad version's `status` flips to `quarantined`, not `archived`, so it can't be accidentally re-promoted before the post-mortem.

Failure mode: rollback target was garbage-collected or never registered. "Roll back the prompt" turns into "re-author the old prompt from memory" under incident pressure. Keep ≥1 prior prod version permanently loadable.

### 6. Change-control governance

```
Who may change a prompt, by environment:
  dev      → any engineer, no approval (it's a sandbox; @dev never serves users)
  staging  → author opens a change; /prompt-review must pass (review_status=approved)
  prod     → requires named approver(s); high-risk surfaces require 2

Definition of a "prod prompt change" (all of these count, none are exempt):
  □ template text edit          □ model swap (target_model change)
  □ params change (temp, etc.)  □ tool/function-call schema in the prompt
  □ few-shot example add/remove □ system-prompt / guardrail wording

Audit trail (immutable, append-only) — every prod change records:
  who authored · who approved · from→to version · eval_run_id · timestamp · rollback_target
```

- **No prod prompt change without a registered version + an approver.** A prompt is not config you tweak in a console; it is a release. (If your vendor tool has a "edit prompt in prod" button, treat it as a break-glass path that still writes the audit record — never the normal path.)
- **`/prompt-review` is the entry gate to staging**, not an afterthought — a prompt enters the registry as `review_status=approved` or it doesn't enter. That covers clarity, injection risk, output-format, PII — the dimensions this skill does *not* re-assess.
- High-blast-radius surfaces (anything user-facing in a regulated domain, anything that can move money or make irreversible actions) require a second approver and a logged rationale.

### 7. PromptOps design doc (the output)

```
### PromptOps Design: [system / prompt family]

Prompts under management: [count + names]
Backing store:           [git / DB registry / vendor — + rationale]
Versioning scheme:       [content-addressed + semver alias + env alias]

Registry schema:
  [the metadata row — fields above, project-filled]

Environment promotion:
  dev → staging → prod, build-once-promote-many
  prod pinned to:  [exact version, never @latest]
  promotion = alias pointer move + audit record

Eval-gated promotion (gates consumed from /eval-design):
  □ primary ≥ [threshold]   □ no regression vs prod (ε=[…])
  □ safety pass ≥ [floor]   □ cost ≤ [budget]   □ latency p95 ≤ [SLA]
  □ output-schema conformance   □ review_status=approved

Rollout shape:           [canary / A/B — + assignment key]
Rollback trigger spec:   [automated + manual triggers; last-good target = always-loadable]
Change-control policy:   [who approves per env; audit-trail fields]

Deferred to siblings:
  eval metric/test-set → /eval-design
  one-time quality score → /prompt-review
  A/B sample size + stopping → /ab-test-design
  model-object lifecycle → /experiment-tracking + /model-deployment
  request-time model routing → /llm-routing

Named failure mode for THIS setup: [the one most likely to bite, + its guard]
```

## Quality bar

- Always produce the PromptOps design doc (§7) even if inputs are incomplete — mark unknowns `[TBD]`, never invent eval thresholds.
- Never let prod resolve a prompt via `@latest` or an inline string — prod is pinned to an immutable, eval-passed version, resolved by alias.
- Always name a rollback target that is permanently loadable; a rollback plan whose target was garbage-collected is not a plan.
- Build-once-promote-many is non-negotiable: the artifact promoted to prod is byte-identical (`content_hash`) to the one that cleared staging — no re-authoring at the boundary.
- Defer eval metric design to `/eval-design`, one-time quality scoring to `/prompt-review`, A/B sizing to `/ab-test-design`, and model-object lifecycle to `/experiment-tracking` + `/model-deployment` — do not re-litigate what they own.
- Every recommendation states its counter-indication — no universally-best store, scheme, or rollout shape.
