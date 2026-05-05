# ADR-0039: Open-Source — MLOps Platforms & Workflow Orchestration

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

ML and LLM workloads require experiment tracking, model registry, pipeline orchestration, and reproducible workflow execution. The OSS landscape includes general workflow orchestrators (Airflow, Prefect), ML-native pipeline frameworks (Kubeflow, Flyte, ZenML, Metaflow), and the de facto experiment tracking standard (MLflow). Without a canonical selection, teams operate duplicate infrastructure, lose experiment reproducibility, and face fragmented model lineage.

## Decision

We adopt a **function-driven MLOps stack**:

- **Experiment tracking + model registry + GenAI eval:** **MLflow** — lingua franca of experiment tracking; 20K+ GitHub stars; MLflow 3.0 adds LLM tracing and hallucination detection (see ADR-0037 cross-reference).
- **Cloud-agnostic ML pipelines (primary):** **ZenML** — portable pipelines across any cloud or local; strong governance (audit trails, stack components, step caching) with Apache 2.0 core.
- **Kubernetes-native ML platform (when K8s is the deployment target):** **Kubeflow** — full ML platform (Pipelines, Training Operator, Katib HPO, KServe) for teams operating Kubernetes clusters.
- **Complex ML workflows with strict reproducibility:** **Flyte** — type-safe, versioned tasks with data lineage; preferred when workflow correctness guarantees are non-negotiable.
- **Data-science-friendly scale-out (no K8s):** **Metaflow** — Python-native local dev to cloud scale; preferred for data science teams without Kubernetes expertise.
- **External dependency orchestration:** **Apache Airflow** or **Prefect** — for ML pipelines with significant external dependencies (databases, APIs, data warehouses); Prefect preferred for new projects due to lower ops overhead.

## Rationale

1. **MLflow as the experiment tracking standard** — MLflow is the most widely deployed OSS experiment tracking tool. Its model registry, artifact store, and Projects format create a complete ML lineage record. MLflow 3.0's LLM tracing and eval integration bridges classic MLOps and GenAI workloads.
2. **ZenML for portable pipelines** — ZenML's stack abstraction (orchestrator + artifact store + container registry) allows pipelines to run locally, on Kubeflow, on Airflow, or on cloud-managed services without code changes. This satisfies the multi-cloud and portability principle without Kubernetes dependency.
3. **Kubeflow when K8s is already the platform** — For teams operating Kubernetes production clusters, Kubeflow provides end-to-end ML infrastructure (Pipelines, Training Operator, KServe) without vendor lock-in. Not justified if K8s is not already in the stack.
4. **Flyte for reproducibility guarantees** — Flyte's type system ensures data contracts between workflow tasks are enforced at compile time, not runtime. Data lineage and version pinning are automatic. The right choice when audit trails of data transformations are a compliance requirement.
5. **Prefect over Airflow for new projects** — Airflow's static DAG model and operator complexity add friction for dynamic ML workflows. Prefect's Python-native dynamic DAGs, built-in retry logic, and lower ops overhead make it the better default for new orchestration needs; Airflow remains valid for teams with existing investment.

## Consequences

### Positive
- MLflow provides a single source of truth for experiment results, model versions, and (with 3.0) LLM evaluation metrics — one platform for the full ML lifecycle
- ZenML portability means pipelines developed locally run unchanged on production infrastructure — eliminates "works on my machine" pipeline failures
- Flyte's data lineage is automatic — audit trails are produced by the framework, not manually maintained

### Negative / Trade-offs
- ZenML + MLflow overlap on artifact storage — define a clear ownership boundary (ZenML owns pipeline artifacts; MLflow owns model registry and eval results)
- Kubeflow deployment complexity is substantial — etcd, MinIO, Istio, Knative; do not select without dedicated MLOps engineering capacity
- Metaflow's cloud scale relies on AWS Step Functions or Azure Batch — introduces cloud provider dependency for scale-out; document this in the team ADR supplement

### Risks
- [RISK: HIGH] Running both ZenML and Airflow creates duplicate pipeline definitions — enforce a single orchestration layer per project; ZenML can wrap Airflow as its orchestrator if Airflow investment exists
- [RISK: MED] MLflow model registry versioning requires discipline — teams that don't tag model versions (staging → production) lose the lineage benefit; enforce via code review checklist
- [RISK: LOW] Kubeflow version upgrades are complex — Kubeflow depends on specific K8s API versions; test upgrades in staging cluster before production

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| DVC (Data Version Control) | Strong for data versioning; orchestration capabilities limited; better used as a complement to ZenML/Flyte, not a replacement |
| Kedro | Data pipeline framework with good lineage; smaller ecosystem than ZenML/Flyte; less community momentum for LLM workloads |
| Dagster | Strong asset-based orchestration; good for data engineering; ML-specific features (experiment tracking, model registry) require MLflow integration anyway |
| Argo Workflows | Lower-level K8s workflow engine; Kubeflow Pipelines wraps Argo — prefer Kubeflow for ML workloads unless extremely custom K8s workflow requirements |

## Implementation Notes

1. MLflow: set `MLFLOW_TRACKING_URI=http://mlflow-server:5000`; log params, metrics, and artifacts with `mlflow.log_param()`, `mlflow.log_metric()`, `mlflow.log_artifact()`
2. MLflow model registry: enforce three-stage lifecycle (`staging → champion → archived`); use `mlflow.register_model()` in CI after eval gates pass (ADR-0037)
3. ZenML: define stack components in `zenml stack register`; use `@step` and `@pipeline` decorators; store stack configs in `stacks/` directory under version control
4. Flyte: define workflows with `@task` and `@workflow` decorators; use `FlyteFile` and `FlyteDirectory` for data contracts between tasks
5. Prefect: use `@flow` and `@task` decorators; deploy flows via `prefect deploy`; configure Prefect Cloud or self-hosted server in `prefect.yaml`
6. Airflow: store DAGs in `dags/` directory; use `KubernetesPodOperator` for ML tasks to ensure clean environments per task run

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
