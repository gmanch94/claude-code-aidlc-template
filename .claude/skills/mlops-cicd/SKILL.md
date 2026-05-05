---
name: mlops-cicd
description: Design ML CI/CD pipelines with model artifact gates, automated quality checks, and deployment automation. Use when setting up or reviewing ML pipeline automation, model promotion workflows, GitHub Actions/GitLab CI for ML, or automated model testing in CI.
---

# MLOps CI/CD

## Role
You are an MLOps Pipeline Engineer.

## Quick start

Gather: model framework, artifact store (MLflow/S3/GCS), target environment (k8s/SageMaker/Vertex), current manual steps, latency SLA.

Output: pipeline YAML skeleton + gate checklist + rollback trigger spec.

---

## Pipeline architecture

### Stage sequence

```
Code commit
    ↓
[1] Lint + unit tests          ← fast gate (<2 min)
    ↓
[2] Data validation            ← schema check + freshness
    ↓
[3] Training (triggered)       ← on data change OR schedule
    ↓
[4] Model quality gates        ← performance + fairness + latency
    ↓
[5] Artifact registration      ← MLflow/registry + SHA256
    ↓
[6] Shadow deploy              ← traffic split 0% → metrics
    ↓
[7] Canary promote             ← 5% → 20% → 100% (with auto-halt)
    ↓
[8] Notify + audit log
```

### Trigger matrix

| Trigger | Pipeline stages | When |
|---|---|---|
| Code PR | 1 + unit model tests | Every PR |
| Data drift alert | 3 → 4 → 5 | PSI > 0.25 |
| Scheduled | 3 → 8 | Weekly/monthly |
| Manual | Any stage | On demand |
| Rollback | 7 reversed | Auto (p50 latency >2× baseline or error rate >1%) |

---

## Model quality gates (Stage 4)

Gate fails CI if any condition triggers:

| Gate | Condition | Severity |
|---|---|---|
| Performance regression | Primary metric < prod − threshold | BLOCK |
| Fairness check | Disparate impact ratio < 0.80 | BLOCK |
| Latency p99 | > SLA budget | BLOCK |
| Data schema | Input schema mismatch | BLOCK |
| Training data freshness | Stale by > 2× window | WARN |
| Calibration ECE | > 0.05 vs. prod | WARN |
| Model size | > 2× prior artifact | WARN |

Define thresholds in `model-config.yaml` — never hardcode in CI YAML.

---

## GitHub Actions skeleton

```yaml
name: ml-pipeline

on:
  push:
    paths: ["src/models/**", "src/features/**"]
  schedule:
    - cron: "0 2 * * 1"   # weekly Monday 2am

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements-dev.txt
      - run: ruff check src/ && pytest tests/unit/ -q

  data-validation:
    needs: lint-test
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/validate_data.py --config data-config.yaml

  train-evaluate:
    needs: data-validation
    runs-on: [self-hosted, gpu]      # GPU runner for training
    steps:
      - run: python scripts/train.py --config model-config.yaml
      - run: python scripts/evaluate.py --gate-config gates.yaml
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: model-artifact
          path: artifacts/

  register:
    needs: train-evaluate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: python scripts/register_model.py --stage Staging

  deploy-shadow:
    needs: register
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/deploy.py --mode shadow --traffic 0
```

---

## Artifact registration spec

Each artifact commit must include:

```yaml
# model-artifact.yaml
model_name: <name>
version: <semver>
sha256: <hash>           # of serialized model file
training_run_id: <mlflow_run_id>
training_data_version: <dataset_sha_or_tag>
eval_metrics:
  primary_metric: 0.847
  latency_p99_ms: 45
  fairness_dir: 0.92
gate_results:
  performance: PASS
  fairness: PASS
  latency: PASS
promoted_by: <ci_job_id>
promoted_at: <iso8601>
```

---

## Rollback trigger spec

Automated rollback fires if **any** of:
- Error rate > 1% (5-min window)
- p50 latency > 2× pre-deploy baseline
- p99 latency > SLA budget
- Primary metric degradation > threshold (requires real-time label feedback)

Rollback = re-deploy previous registered artifact (not re-train).

Manual rollback: `python scripts/deploy.py --version <prior_version> --mode immediate`

---

## Output

Deliver:
1. **Pipeline YAML** — stages + triggers + gate definitions
2. **Gate config** — `gates.yaml` with numeric thresholds
3. **Artifact schema** — `model-artifact.yaml` spec
4. **Rollback runbook** — automated + manual triggers
