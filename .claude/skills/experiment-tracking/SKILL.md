---
name: experiment-tracking
description: ML experiment tracking — run logging, metric comparison, artifact versioning, reproducibility checklist, registry promotion. Use when asked about "experiment tracking", "MLflow", "run comparison", "which model version was best?", "reproducing a training run", or setting up ML experiment infrastructure.
---

# Experiment Tracking

## Quick start

Log every training run. Minimum: parameters, metrics, artifact path, environment. Never compare models you can't reproduce.

## Workflow

### 1. What to log per run

**Parameters (hyperparams + config):**
```python
mlflow.log_params({
    "model_type":       "LightGBM",
    "n_estimators":     500,
    "learning_rate":    0.05,
    "max_depth":        6,
    "feature_count":    24,
    "train_data_hash":  hashlib.md5(open(train_path,"rb").read()).hexdigest(),
    "train_date_range": "2024-01-01/2025-12-31",
    "random_seed":      42,
})
```

**Metrics (train + val + test):**
```python
mlflow.log_metrics({
    "train_auc": 0.923,
    "val_auc":   0.887,
    "test_auc":  0.881,
    "val_ece":   0.031,
    "val_p99_ms": 41,
})
# Log per-epoch/fold if iterative
for fold, score in enumerate(cv_scores):
    mlflow.log_metric("cv_auc", score, step=fold)
```

**Artifacts:**
```python
mlflow.sklearn.log_model(pipeline, "model")          # model + preprocessor
mlflow.log_artifact("feature_list.json")
mlflow.log_artifact("train_feature_stats.parquet")   # drift baseline
mlflow.log_artifact("confusion_matrix.png")
```

**Environment (auto-log or explicit):**
```python
mlflow.set_tags({
    "python_version": "3.11.4",
    "git_commit":     subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip(),
    "git_branch":     subprocess.check_output(["git","rev-parse","--abbrev-ref","HEAD"]).decode().strip(),
    "dataset_version": "v2025-Q4",
    "run_by":         os.environ.get("USER", "ci"),
})
```

### 2. Run structure

```python
import mlflow

mlflow.set_experiment("churn-classifier")

with mlflow.start_run(run_name="lgbm-v2-tuned") as run:
    # ... train ...
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(pipeline, "model")
    print(f"Run ID: {run.info.run_id}")
```

Nested runs for CV:
```python
with mlflow.start_run(run_name="cv-sweep") as parent:
    for fold_i, (train_idx, val_idx) in enumerate(cv.split(X, y)):
        with mlflow.start_run(run_name=f"fold-{fold_i}", nested=True):
            mlflow.log_metric("val_auc", fold_score)
    mlflow.log_metric("mean_cv_auc", np.mean(cv_scores))
    mlflow.log_metric("std_cv_auc",  np.std(cv_scores))
```

### 3. Reproducibility checklist

A run is reproducible when all of these are logged:
- [ ] Data path + hash (or dataset version tag)
- [ ] All hyperparameters (no hardcoded defaults outside log_params)
- [ ] Random seed (numpy, random, sklearn, framework-level)
- [ ] Git commit SHA
- [ ] Package versions (`pip freeze > requirements.txt` → log_artifact)
- [ ] Preprocessing pipeline included in model artifact (not separate)
- [ ] Feature list (name + dtype) logged as artifact

### 4. Comparing runs

```python
runs = mlflow.search_runs(
    experiment_names=["churn-classifier"],
    filter_string="metrics.val_auc > 0.87",
    order_by=["metrics.val_auc DESC"],
)
runs[["run_id","params.model_type","metrics.val_auc","metrics.val_ece","metrics.val_p99_ms"]]
```

Multi-criteria selection rule: don't pick on single metric. Minimum bar:
- val_auc meets threshold AND val_ece < 0.05 AND val_p99_ms < SLA

### 5. Registry promotion

Promote to model registry only after validation gates pass:
```python
run_id = "abc123"
mlflow.register_model(f"runs:/{run_id}/model", "churn-classifier")

client = mlflow.MlflowClient()
client.transition_model_version_stage(
    name="churn-classifier",
    version=3,
    stage="Staging"   # Staging → Production via explicit promotion
)
```

Stages: None → Staging → Production → Archived. Never jump directly to Production.

### 6. Experiment tracking output

```
Experiment:     [name]
Best run:       [run_id]
Selection criteria: [metric + threshold used]
Top 3 runs:     [run_id, primary metric, secondary metrics]
Reproducibility: [checklist — all items logged?]
Registry status: [promoted / not yet / which stage]
```

## Rules

- Every training run gets a run ID before results are shared. "I got 0.89 AUC" without a run ID is not a result.
- Never compare runs trained on different data splits without noting the difference explicitly.
- Tag CI/CD runs differently from interactive notebook runs (`run_by=ci` vs. `run_by=analyst`).
- Test set metrics logged ONCE per run — after final model selection, not during tuning.
