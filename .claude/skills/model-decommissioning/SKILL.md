---
name: model-decommissioning
description: Retire a production ML model — retirement criteria, migration plan, downstream notification, registry deprecation, archival policy. Use when asked to "retire a model", "decommission", "sunset", "replace a model", "turn off a model in production", or when a model has been superseded by a newer version.
---

# Model Decommissioning

## Quick start

Never delete a model from registry without: (1) successor serving 100% traffic, (2) rollback window expired, (3) downstream consumers notified, (4) artifacts archived.

## Workflow

### 1. Retirement criteria (any one triggers)

- Successor model at full GA for > 2 weeks with no rollback event
- Primary metric degraded > 10% vs. launch baseline (sustained 14 days)
- Upstream feature pipeline deprecated (model inputs no longer available)
- Compliance / legal hold removed or policy changed
- Infrastructure end-of-life (container runtime, cloud service deprecated)
- Business use case eliminated

**Do not retire** on schedule alone — confirm the successor is stable first.

### 2. Dependency audit

Before any retirement action:

```bash
# Find all services calling this model endpoint
grep -r "model-name\|/predict\|model_version" infrastructure/ configs/ --include="*.yaml" --include="*.json"
```

Downstream consumers to notify:
- [ ] Teams calling the inference endpoint
- [ ] Pipelines reading from the prediction store / feature store
- [ ] Dashboards or reports citing model metrics
- [ ] Data contracts referencing this model's output schema
- [ ] Batch jobs consuming offline predictions

### 3. Migration plan

```
Phase 1 — Shadow period (2 weeks)
  Successor at 100% traffic; old model still deployed but receiving 0% traffic.
  Purpose: instant rollback if successor failure detected within window.
  Gate: no rollback events in 14 days.

Phase 2 — Decommission announcement
  Notify all downstream consumers with:
  - Retirement date (minimum 2 weeks notice for internal; 4 weeks for external API consumers)
  - Successor endpoint / version identifier
  - Migration guide (diff of request/response schema if changed)
  - Rollback unavailability after retirement date

Phase 3 — Traffic cutover confirmation
  Verify: no traffic hitting old endpoint for 72 consecutive hours.
  Command: check access logs / Prometheus request_count metric = 0.

Phase 4 — Registry deprecation
  Mark version as DEPRECATED in model registry. Do NOT delete yet.
  Set registry retention policy: keep for 90 days post-deprecation.

Phase 5 — Archive (90 days post-deprecation)
  Move artifacts to cold storage (S3 Glacier / GCS Archive).
  Artifacts to retain: trained model + preprocessor, feature_list.json,
  model_card.md, deployment.yaml, performance snapshots at each rollout phase.
  Retention: 3 years minimum (adjust for regulatory jurisdiction).

Phase 6 — Hard delete (after retention period)
  Requires written sign-off from model owner + data governance.
  Delete: registry entry, inference container image, serving infrastructure.
```

### 4. Notification template

```
Subject: [ACTION REQUIRED] Model <name> v<version> retiring <date>

Model <name> version <X.Y.Z> will be retired on <date>.

Successor: <name> v<A.B.C> — currently serving 100% of traffic since <date>.

Breaking changes:
  [NONE — same request/response schema]
  OR
  [Response field "probability" renamed to "score" — update consumers]

Action required by <date - 5 days>:
  [ ] Confirm your service has been updated to use the successor endpoint
  [ ] Run integration test against successor: <test endpoint URL>

After <retirement date>: old endpoint will return 410 Gone.

Questions: <owner email / Slack channel>
```

### 5. Decommissioning checklist

```
Pre-retirement:
  [ ] Retirement criteria confirmed (which criterion triggered?)
  [ ] Dependency audit complete — all consumers identified
  [ ] All consumers confirmed migrated to successor
  [ ] No traffic for 72 consecutive hours (log evidence)
  [ ] Model owner sign-off

Registry:
  [ ] Version marked DEPRECATED with retirement date
  [ ] Successor version marked as replacement in registry metadata

Archive:
  [ ] Model artifact + preprocessor archived to cold storage
  [ ] Artifact path recorded in registry metadata (post-deprecation pointer)
  [ ] Performance snapshots archived
  [ ] model_card.md updated with retirement reason + date

Infrastructure:
  [ ] Inference endpoint decommissioned / scaled to 0
  [ ] Container image retained in registry (not deleted) until retention expiry
  [ ] Monitoring alerts suppressed for retired model

Documentation:
  [ ] Internal wiki / model catalog updated
  [ ] Any data contracts referencing this model closed or renegotiated
  [ ] Retirement recorded in changelog / incident tracker
```

### 6. Post-retirement archive record (output)

```
Model:              [name + version]
Retired:            [date]
Retirement reason:  [criterion that triggered]
Successor:          [name + version + registry path]
Archive location:   [cold storage path]
Retention until:    [date — 3 years default]
Hard delete after:  [date — after retention period, with required sign-off]
Owner at retirement:[name + team]
```

## Rules

- Never delete model artifacts during the 90-day deprecation window — production incidents may require forensic comparison.
- Retirement announcement must go to all downstream consumers, not just the immediate calling team.
- If a model is under a legal hold, do not decommission regardless of business status — escalate to legal.
- Archival is not optional. Regulators can request model artifacts years after retirement.
