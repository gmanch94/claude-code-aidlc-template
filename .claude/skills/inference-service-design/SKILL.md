---
name: inference-service-design
description: Design an ML inference service for production. Use when choosing between REST/gRPC/batch, sizing replicas, setting latency budgets, designing health checks, or building circuit breakers and fallbacks.
---

# Inference Service Design

## Role
You are a Inference Service Designer.

## Quick start

Tell me: latency requirement + request volume (RPS) + model size + whether batch is acceptable.

## Serving pattern decision

```
Latency requirement?
├── < 100ms (real-time, user-facing)
│   ├── Single model, simple features → REST API (FastAPI/Flask)
│   ├── High RPS (> 1K/s)            → gRPC + connection pooling
│   └── Feature lookup needed         → REST + online feature store call
├── 100ms–2s acceptable
│   → REST API; async if downstream pipeline
└── Minutes acceptable (batch scoring)
    → Batch job (Spark/pandas); no serving layer needed

Batch requests common?
  Yes (offline scoring, bulk API) → Batch endpoint; async job queue
  No (user-triggered one at a time) → Synchronous REST
```

## API contract (REST)

```python
# FastAPI minimal inference service
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.sklearn
import numpy as np

app = FastAPI()
model = mlflow.sklearn.load_model("models:/churn-classifier/Production")

class PredictRequest(BaseModel):
    features: dict[str, float | str | int | None]

class PredictResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str
    request_id: str

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        X = pd.DataFrame([req.features])
        prob = model.predict_proba(X)[0, 1]
        return PredictResponse(
            prediction=int(prob >= 0.65),
            probability=round(float(prob), 4),
            model_version="v2.1.0",
            request_id=str(uuid4()),
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/ready")
def ready(): return {"status": "ready", "model_loaded": model is not None}
```

## Health and readiness endpoints (required)

```
/health  — liveness: is the process alive? Returns 200 if yes; 500 if not
/ready   — readiness: is the model loaded and warm? k8s uses this to gate traffic
/metrics — Prometheus scrape: request_count, latency_p50/p99, error_rate, prediction_mean
```

## Latency budget

```
End-to-end SLA: 100ms
  Feature retrieval:      10ms   (online store or request payload)
  Preprocessing:          5ms    (sklearn ColumnTransformer)
  Model inference:        20ms   (LightGBM / logistic regression)
  Serialization:          5ms    (JSON response)
  Network overhead:       10ms
  Safety margin:          50ms
```

If preprocessing + inference > 50% of SLA: profile first — usually preprocessing, not model.

## Scaling design

```
Stateless containers → horizontal scaling only (no sticky sessions)

Scaling triggers:
  CPU > 70% sustained 2 min   → scale out
  p99 latency > 0.8× SLA      → scale out
  Queue depth > 100 (async)   → scale out

Min replicas: 2 (HA; never 1)
Max replicas: sized for 3× peak RPS with headroom

Memory request = model size × 2 (headroom for request processing)
CPU request: profile under load; avoid over-provisioning
```

## Circuit breaker + fallback

```python
# Fallback: return a safe default when model unavailable
FALLBACK_RESPONSE = PredictResponse(
    prediction=0,
    probability=0.5,
    model_version="fallback",
    request_id="fallback",
)

# Circuit breaker pattern (use tenacity or pybreaker)
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, reset_timeout=30)

@breaker
def call_model(X):
    return model.predict_proba(X)[0, 1]

@app.post("/predict")
def predict(req: PredictRequest):
    try:
        prob = call_model(pd.DataFrame([req.features]))
        ...
    except Exception:
        # Circuit open or model error → return safe fallback
        return FALLBACK_RESPONSE
```

## Required observability signals

```
Request metrics:  request_count, error_count, latency_p50/p99/p999
Model metrics:    prediction_mean (rolling), prediction_distribution
Resource metrics: CPU%, memory%, replica count
Business proxy:   conversion rate, revenue per request (if available)
```

Alert on: error_rate > 0.1%, p99 > SLA, prediction_mean shifts > 0.05 (prediction drift signal).

## Failure modes

- Model loaded at request time (not startup): first request is slow; load model in startup event
- No /ready endpoint: k8s sends traffic before model warm; use readiness probe, not liveness
- Synchronous feature store call on critical path: one slow lookup blocks all requests; set timeout + fallback
- Single replica: one pod restart = full outage; always min 2
- No fallback: model error surfaces as 500 to user; always return safe default, never propagate model exception

Pair with `/model-deployment` for the rollout strategy and registry, `/model-drift` for the monitoring signals wired into this service.
