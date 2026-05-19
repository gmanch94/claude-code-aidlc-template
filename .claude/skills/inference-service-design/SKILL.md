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

---

## Edge / IoT / resource-constrained deployment

When the target is a mobile phone, embedded device, browser, robot, vehicle, or any device with bounded memory / compute / power / connectivity, the cloud-serving guidance above doesn't apply. Different decision tree:

### Cloud vs on-device decision

| Factor | Favors cloud | Favors on-device |
|---|---|---|
| Connectivity | Stable, low-latency network | Intermittent or offline-first (drones, vehicles, rural) |
| Latency target | > 200ms acceptable | < 50ms or hard real-time |
| Privacy posture | PII can leave device with consent | PII must not leave device (health, biometric, regulated) |
| Inference cost @ scale | Few requests / costly model | Millions of devices, recurring inference — cloud cost dominates |
| Model size vs device RAM | Model >> device memory | Model fits with headroom |
| Update cadence | Daily / hourly | Monthly or slower; OTA cycle |
| Battery budget | N/A | Inference must respect power budget |

Hybrid is common: on-device for fast / private path; cloud for confident-on-cloud-only path; on-device first, fallback to cloud when local confidence is low.

### Resource constraints by target

| Target | Typical RAM | Compute | Power | Implication |
|---|---|---|---|---|
| Modern phone (high-end) | 6–16 GB | CPU + GPU + NPU | Battery | Sub-100 MB model; quantized; hardware-accelerated runtime |
| Mid-range phone | 2–4 GB | CPU + lightweight NPU | Battery | < 20 MB model; INT8; ARM-optimized |
| Embedded MCU / IoT | 256 KB – 64 MB | MCU; no GPU | Battery / coin cell | TinyML; < 1 MB model; INT8 / binary nets |
| Browser (WebAssembly / WebGPU) | bounded by user RAM | varies | Plugged | < 50 MB; ONNX Runtime Web / WebLLM |
| Robotics / vehicle | Multi-GB but hard real-time | GPU / FPGA / ASIC | Vehicle power | Deterministic latency more important than size |

### Compression techniques (pair with `/model-compression`)

| Technique | Size reduction | Accuracy cost | When to use |
|---|---|---|---|
| **Quantization (INT8)** | 4× smaller, 2–4× faster | < 1% typical | Default for any edge deployment |
| **Quantization (INT4 / binary)** | 8–32× smaller | 1–5% | Memory-bound MCU; tolerable accuracy hit |
| **Pruning (structured)** | 2–5× smaller | < 2% | Compute-bound; works with hardware accelerators |
| **Distillation (teacher-student)** | Can be orders of magnitude | Recover most accuracy with sufficient data | When a much smaller architecture is acceptable |
| **Architecture search / mobile-first arch** | 5–20× | Comparable to large model on task | Use MobileNet / EfficientNet / DistilBERT / TinyLlama family |

### Runtime choices

| Runtime | Targets | Strengths |
|---|---|---|
| TensorFlow Lite / LiteRT | Android, iOS, embedded | Mature; broad op support; NNAPI / Core ML delegates |
| Core ML | iOS only | Tightest iOS integration; ANE acceleration |
| ONNX Runtime (Mobile / Web) | Cross-platform | Framework-agnostic; broad accelerator support |
| ExecuTorch | PyTorch-native edge | Newer; PyTorch ecosystem |
| llama.cpp / GGUF | LLMs on consumer hardware | CPU + GPU LLM inference; aggressive quantization |
| TFLite Micro / Edge Impulse | MCU-class | Sub-MB models; tinyML |

### Update strategy (over-the-air)

On-device models can't be hot-swapped like cloud endpoints. Plan for:
- **Bundled model:** ships with app update; slow but reliable
- **OTA model download:** decouple model from app; verify signature; staged rollout (1% → 10% → 100%); always keep last-known-good version on device for rollback
- **Differential updates:** ship delta vs current model where supported (TFLite delta, ONNX delta) to save bandwidth
- **Background pre-fetch:** download new model while old model serves; atomic swap on success

### Edge-specific failure modes

- **Model bigger than available RAM:** OOM kills the app; profile peak memory on the lowest-spec target device, not the dev machine
- **First inference slow:** model loading + warm-up takes hundreds of ms; pre-load on app start, not first request
- **Thermal throttling:** sustained inference on phone overheats and slows; budget compute for sustained operation, not peak
- **Battery drain:** continuous inference shortens battery life noticeably; document expected impact; offer power-saver mode
- **Stale model on offline devices:** device offline for months still runs an old model; track per-device model version server-side; trigger update prompts
- **Heterogeneous hardware:** same OS version, different chips — test on real lowest-spec device, not emulator

### Decision additions for cloud-vs-edge

Add these to the decision in §"Serving pattern":

```
Target is a phone / embedded / browser / robot / vehicle?
└── Yes → use this Edge section, not the cloud REST/gRPC pattern
   ├── Privacy: must not leave device → on-device only
   ├── Connectivity: intermittent → on-device with cloud assist
   └── Cost @ scale dominates → on-device to amortize
```

Pair with `/model-compression` for the technique details, `/model-deployment` for OTA rollout discipline.
