# ADR-0044: Model Supply Chain & Provenance Policy

**Status:** Accepted  
**Domain:** [governance]  
**Date:** 2026-04-22

---

## Context

AI systems depend on a layered supply chain — foundation models, embedding models, training datasets, ML frameworks, plugins, and third-party APIs — each of which is a potential compromise vector. OWASP LLM Top 10 2025 elevated Supply Chain Vulnerabilities to **#3** (up from #5) citing increased real-world incidents involving trojanized models, poisoned public datasets, and malicious HuggingFace packages.

MITRE ATLAS v5.1.0 documents **AML.T0010 (AI Supply Chain Compromise)** and **AML.T0110 (AI Agent Tool Poisoning)** as high-frequency enterprise attack paths. The OpenSSF released the **Model Signing (OMS) Specification** (June 2025) and the **SPDX 3.0 standard** added AI/ML extensions, making cryptographic model provenance verifiable at production scale.

Current practice in this workspace has no documented policy for:
- Which model sources are trusted
- How model integrity is verified at deploy time
- Whether an AI Bill of Materials (AI-BOM) is required
- How third-party APIs are classified and approved

Without this policy, teams make ad hoc decisions that create unacknowledged risk.

---

## Decision

All production AI systems must meet the following supply chain requirements before deployment. The `/supply-chain-review` command is the canonical tool for auditing compliance.

### Principle: No Provenance, No Prod

Any model, dataset, plugin, or third-party API component that cannot demonstrate provenance (traceable origin + integrity verification) is classified **UNTRUSTED** and blocks production deployment until resolved.

### Trusted Model Sources

| Source | Status | Conditions |
|--------|--------|------------|
| Anthropic API (Claude) | TRUSTED | DPA required for user-data workloads |
| Azure OpenAI / AWS Bedrock / GCP Vertex AI | TRUSTED | Platform SLA + DPA cover provenance |
| OpenAI direct API | TRUSTED | DPA required for user-data workloads |
| HuggingFace — verified organization models | CONDITIONAL | Must pin exact commit hash; hash verified at load time; model card reviewed |
| HuggingFace — community / unknown org | UNTRUSTED | Requires security review before use |
| Internal model registry (MLflow, Vertex Model Registry) | TRUSTED | Internal provenance assumed; still requires version pinning |
| Other third-party or self-hosted | UNTRUSTED by default | Requires architecture review and explicit approval |

### Model Integrity Requirements

1. **Version pinning** — all model references in code and config must specify an exact version, tag, or commit SHA. `latest`, `main`, or floating references are prohibited in production.
2. **Hash verification** — SHA256 hash of model weights must be checked at deploy time. For HuggingFace models, verify against the `sha256` field in the model repository. For commercial APIs, verify API endpoint and key fingerprint.
3. **OMS signature** (for self-hosted or registry-stored models) — sign model artifacts using the OpenSSF Model Signing specification. Verify signature at load time in the serving container.
4. **Model card required** — every model used in production must have an associated model card documenting: training data sources, intended use, known limitations, eval results, and license. Use `/model-card` to generate if none exists.

### AI Bill of Materials (AI-BOM)

An AI-BOM must be generated and committed to the repository before production deployment. Use SPDX 3.0 AI/ML extensions as the format standard.

**Required AI-BOM fields:**

| Field | Required |
|-------|----------|
| Foundation model name, version, source URL, hash | Yes |
| Embedding model name, version, source URL, hash | Yes |
| Training datasets: name, version, license, source | Yes |
| Fine-tuning data sources (if applicable) | Yes |
| Framework versions (LangChain, LlamaIndex, FastAPI, etc.) | Yes |
| Third-party APIs: name, version, DPA status | Yes |
| Model card reference | Yes |
| AI-BOM generation date and owner | Yes |

The AI-BOM is a living document — update it whenever any component changes.

### Framework & Library Dependencies

1. All Python / Node dependencies must be pinned to exact versions in `requirements.txt`, `pyproject.toml`, or `package-lock.json`
2. A CVE scan (`pip-audit`, `trivy`, or `snyk`) must pass with zero HIGH/CRITICAL findings in CI before any deployment
3. A traditional SBOM (CycloneDX or SPDX) must be generated for the deployment container image
4. Unpinned `latest` tags in Dockerfiles or dependency files must fail CI

### Embedding Model Policy

The embedding model is a first-class supply chain component with a unique risk: a model change silently corrupts the entire vector store if the embedding space changes.

- Embedding model must be version-pinned with hash verified (same standard as foundation models)
- Any embedding model change must trigger a full corpus re-index before queries resume
- The re-index process must be documented and tested before the model is upgraded
- Embedding model changes are treated as a breaking change — they require an explicit deployment step, not a silent config update

### Third-Party API Trust Classification

| Classification | Criteria | Deployment Gate |
|---------------|----------|----------------|
| TRUSTED | Tier-1 cloud provider (Azure, AWS, GCP) with DPA in place; SOC2 Type II certified | No additional gate |
| CONDITIONAL | Known vendor; DPA signed; SOC2 certification; data residency confirmed | Document mitigation before prod |
| UNTRUSTED | Unknown vendor; no DPA; no SOC2; data residency unconfirmed | Blocks production |

A Data Processing Agreement (DPA) is mandatory for any third-party API that processes user data or proprietary data. Absence of a DPA is always [RISK: HIGH].

### Plugin & Tool Approval

All LLM plugins, tools, and MCP servers used by agents must be reviewed before production use:

1. Source must be auditable (open source with pinned version, or internal)
2. Tool's side effects must be documented in the agent's tool manifest (see `/agent-design`)
3. Tools with irreversible side effects (write, delete, send, publish) require HITL confirmation gates
4. Community-contributed plugins with no clear maintainer are UNTRUSTED by default

---

## Consequences

**Positive:**
- Eliminates silent model drift via version pinning and hash verification
- AI-BOM provides an audit artifact — essential for incident forensics and regulatory inquiries
- DPA requirement closes a frequently overlooked compliance gap for third-party LLM APIs
- Embedding model policy prevents the common failure mode of invisible semantic drift after model upgrade

**Negative:**
- Hash verification at load time adds ~seconds per cold start — acceptable for most serving patterns; negligible for batch
- AI-BOM maintenance adds overhead, especially for systems with frequently updated components
- HuggingFace community models are UNTRUSTED by default — teams must go through review, which may slow early-stage prototyping

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Allowlist by model family (e.g., "any Llama 3 model is trusted") | Model family trust does not guarantee per-artifact integrity; trojanized fine-tunes can impersonate legitimate families |
| Rely on cloud provider scanning only | Cloud scanning covers container CVEs but does not verify model weights or training data lineage |
| AI-BOM optional for internal tools | Internal tools are on the same attack surface as production; a compromised internal tool can pivot to prod via shared infrastructure |

---

## Implementation Notes

1. Add hash verification to the model loading code in all serving containers — fail fast if hash doesn't match
2. Create an internal model registry entry for every model used in production, with AI-BOM attached
3. Add `pip-audit` (or equivalent) to the CI pipeline for all AI-related repositories — fail on HIGH/CRITICAL
4. Run `/supply-chain-review` before each major release and document results in the deployment checklist
5. Track DPA status for all third-party APIs in the AI-BOM — assign an owner for renewal tracking

---

## Related Decisions

- **ADR-0043** — AI Red Team Policy: LLM03 (Supply Chain) and LLM06 (Excessive Agency) red-team tests operationalize the provenance requirements defined here; a supply-chain component change triggers a mandatory red-team re-run
- **ADR-0042** — Command Security Policy: `/update-cheatsheet-*` commands fetch external content — those fetched sources (HuggingFace blog, cloud release notes) are themselves supply-chain inputs and must be treated as untrusted per that ADR
- **ADR-0012 / ADR-0021 / ADR-0030** — Cloud Governance: cloud-native model registries (Azure ML, AWS Bedrock, GCP Vertex) are TRUSTED sources per the tier table above; their DPA and audit controls are documented in those ADRs

---

## Risks Not Fully Mitigated

- [RISK: MED] Training data poisoning via public datasets is detectable at the data pipeline stage but not at inference time. Mitigation: data pipeline must include statistical anomaly detection on training distributions; document known dataset risks in model card.
- [RISK: LOW] OMS signature verification requires key management infrastructure that may not exist in all environments. Mitigation: prioritize hash verification (SHA256) as the baseline control; OMS signatures are the target state for HIGH tier systems.
