---
name: model-deployment
description: Deploy an ML model to production. Use when packaging a trained model, registering in a model registry, containerizing for serving, designing a phased rollout, or defining rollback triggers.
---

# Model Deployment

## Pre-deploy gates (must pass before this workflow)

- `/model-validation` checklist: all 9 gates ✅
- `/model-calibration`: ECE < 0.05 if probabilities used
- `/leakage-audit`: clean
- Feature parity: all training features available in prod data pipeline

## Step 1 — Model artifact packaging

```python
import mlflow
import mlflow.sklearn   # or mlflow.lightgbm, mlflow.pytorch, etc.

with mlflow.start_run(run_name="churn-v2-deploy"):
    mlflow.log_params(best_params)
    mlflow.log_metrics({"auc": 0.887, "ece": 0.031, "p99_ms": 41})
    mlflow.log_artifact("feature_list.json")
    mlflow.log_artifact("train_feature_stats.parquet")  # drift baseline
    mlflow.sklearn.log_model(
        pipeline,           # sklearn Pipeline including preprocessor + model
        artifact_path="model",
        registered_model_name="churn-classifier",
        input_example=X_test.iloc[:3],
        signature=mlflow.models.infer_signature(X_test, y_pred),
    )
```

Artifact checklist — every registered model must include:
```
□ Trained model + preprocessing pipeline (one artifact, not two)
□ Feature list + expected dtypes (feature_list.json)
□ Training feature distributions (train_feature_stats.parquet) — drift baseline
□ Model card: task, metric, threshold, owner, training date, data version
□ Input/output signature (schema enforcement at serving time)
□ Performance summary: AUC, ECE, p99 latency, test set date range
```

## Step 2 — Container image

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model_artifacts/ ./model_artifacts/
COPY serve.py .
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/health || exit 1
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

Image must pass:
- `docker scan` or Trivy: no critical CVEs
- Image size < 2GB; layer cache optimized (deps before code)
- Non-root user in container

## Step 3 — Phased rollout

```
Shadow mode (week 1)
  → New model runs in parallel; predictions logged but NOT served
  → Compare output distribution to incumbent; verify no crashes
  → Gate: prediction distribution within expected range

Canary (week 2 — 5% traffic)
  → New model serves 5% of live requests
  → Monitor: latency p99, error rate, prediction distribution
  → Gate: error rate < 0.1%; p99 within SLA; no business metric regression

Limited GA (week 3 — 25% traffic)
  → Expand if canary gate passes; monitor business KPIs
  → Gate: business metric (conversion, revenue) not degraded vs. baseline

Full GA (week 4+)
  → 100% traffic; decommission previous model after 2-week overlap
```

## Rollback triggers (automated + manual)

```
Automated rollback:
  □ Error rate > 1% for 5 consecutive minutes
  □ p99 latency > 2× SLA for 3 consecutive minutes
  □ Prediction null/NaN rate > 0.1%

Manual rollback (human decision):
  □ Business KPI drops > 5% vs. baseline in canary
  □ Unexpected prediction distribution shift
  □ Data quality issue in upstream pipeline
```

Rollback procedure: flip traffic weight to previous model version in registry; keep new model image for investigation.

## Step 4 — Deployment metadata

```yaml
# deployment.yaml — stored in git alongside model artifacts
model_name: churn-classifier
version: v2.1.0
deployed_by: ml-team
deploy_date: 2026-05-04
training_data_range: 2025-01-01 to 2026-04-01
test_auc: 0.887
test_ece: 0.031
p99_latency_ms: 41
rollback_to: v2.0.3
feature_count: 24
serving_env: k8s-prod-us-east
drift_baseline: s3://model-artifacts/churn-v2/train_feature_stats.parquet
```

## Failure modes

- Deploying model without preprocessing pipeline: training-serving skew; always package as one artifact
- No shadow mode: first production signal is real user impact; shadow is free insurance
- Rollback target not pre-deployed: rollback takes minutes instead of seconds when the previous image isn't warm
- Drift baseline not saved at deploy: drift monitoring is impossible without training reference

Pair with `/inference-service-design` for the API and scaling design, `/model-drift` for the post-deploy monitoring setup.
