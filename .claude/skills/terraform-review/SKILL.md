---
name: terraform-review
description: Reviews a Terraform diff or repository — state backend + locking, module structure, variable / output discipline, provider versioning, secrets handling, blast-radius gates, drift detection, plan-vs-apply CI pattern, and destructive-op safety. Returns [BLOCKER] / [SUGGESTION] / [NITPICK] findings with file+line citations. Use BEFORE `terraform apply` in any environment with shared state, BEFORE merging an IaC PR, and AFTER any provider upgrade. Adjacent to `/sagemaker-design`, `/vertex-ai-design`, `/databricks-asset-bundles` for the ML platform side.
---

# /terraform-review — Terraform IaC Review

## Role
You are a Terraform Reviewer.

## Behavior
1. Ask if not provided: the path to review (file, directory, or `terraform plan` output), target environment (dev/staging/prod), provider list, state backend type
2. Walk the 9 review dimensions in order
3. Group findings by severity: [BLOCKER] / [SUGGESTION] / [NITPICK] with file+line
4. Distinguish CODE issues (in `.tf`) from PLAN issues (in `terraform plan` output)
5. End with a one-line verdict: SHIP / SHIP-WITH-FIXES / DO-NOT-SHIP

## 9 Review Dimensions

**1. State backend + locking.**
- Backend declared? (`backend "s3"` / `gcs` / `azurerm` / `remote` for legacy Terraform Enterprise) OR the top-level `cloud` block for **HCP Terraform** (rebrand of "Terraform Cloud", 2024) and Terraform Enterprise. Prefer the `cloud` block over `backend "remote"` for new work.
- Locking enabled?
  - **S3**: prefer native S3 state locking via `use_lockfile = true` (Terraform 1.10+). DynamoDB-based locking is **deprecated** but still works; migrate when convenient.
  - **GCS**: native object lock.
  - **HCP Terraform / TFE**: workspace-managed locking.
- State encrypted? (`encrypt = true` for S3; KMS key for sensitive workspaces).
- State NOT committed to git? (`.tfstate` / `.tfstate.backup` in `.gitignore`).
- Workspace separation: per-env workspaces OR per-env backend keys — never a single shared workspace across envs.

**2. Module structure.**
- Modules under `modules/<name>/` with `main.tf` / `variables.tf` / `outputs.tf` / `versions.tf`.
- Root configs under `live/<env>/` or `environments/<env>/`.
- Module versions pinned (`source = "git::...?ref=v1.2.3"` or registry version constraint) — never `?ref=main`.
- Output values minimal — only what consumers need; no secret leakage.
- Inputs have type constraints + descriptions; sensitive inputs marked `sensitive = true`.

**3. Variable / output discipline.**
- `variable` blocks: `type`, `description`, `validation` (range, regex, enum) where applicable; `default` only when truly optional.
- `output` blocks: `description`; `sensitive = true` on anything that contains secrets / IAM principals / connection strings.
- No `locals` doing the work of `variable` — locals are derived; variables are inputs.

**4. Provider versioning.**
- Top-level `required_providers` block with version constraint (e.g. `~> 5.0`) — never unbounded.
- `required_version` for Terraform itself (`>= 1.10, < 2.0`) — pin floor high enough for native S3 lockfile (`use_lockfile`), `replace_triggered_by`, `precondition` / `postcondition`, and `action_trigger`.
- Provider aliases when targeting multiple regions / accounts / projects.
- No mixing of provider versions across modules in the same root — leads to subtle drift.

**5. Secrets handling.**
- NO secrets in plain `.tfvars` or in `default` values.
- Secrets sourced from: AWS Secrets Manager (for credentials needing rotation — RDS, API keys, OAuth) / SSM Parameter Store SecureString (config + non-rotating secrets; no native rotation) / GCP Secret Manager / Azure Key Vault / Vault provider. Pick by rotation requirement: rotation needed → Secrets Manager; static config → Parameter Store (cheaper).
- `terraform plan` output sanitization — any provider returning secret strings should be wrapped in `nonsensitive()` only with explicit justification.
- Workspace-level env vars (`TF_VAR_<name>` via OIDC-injected) preferred over committed tfvars for CI.

**6. Blast-radius gates.**
- `lifecycle { prevent_destroy = true }` on irreplaceable resources (prod RDS / state buckets / KMS keys / IAM roles backing CI).
  - Gotcha 1: `prevent_destroy` blocks `terraform destroy` even when the resource is no longer in code. Remove from state first (`terraform state rm <addr>`) before destroying the residual cloud resource manually, or land a separate prior PR that flips `prevent_destroy = false` before the deletion PR.
  - Gotcha 2: `prevent_destroy` is NOT a multi-PR forcing function on its own. Removing the lifecycle block AND deleting the resource in the SAME PR will apply cleanly — the check happens at plan-construction, and the block is gone before the destroy plans. Enforce the 2-PR gap in CI (require the lifecycle-flip PR to be merged + applied to prod before the deletion PR can plan green).
- `lifecycle { ignore_changes = [...] }` only with one-line comment justifying each ignored attribute (drift detection becomes blind otherwise).
- `lifecycle { replace_triggered_by = [<reference>] }` (TF 1.2+) — forces replace when an upstream resource attribute changes; cleaner than `null_resource` + provisioners for cascade-replace patterns.
- `lifecycle { precondition { condition = ..., error_message = "..." } }` / `postcondition { ... }` (TF 1.2+) — assert invariants at plan/apply time; preferred over external script gates for resource-local invariants (e.g. "AMI must be in approved-list", "subnet must be in expected CIDR").
- `lifecycle { action_trigger { events = [before_create / after_create / before_update / after_update], actions = [...] } }` (TF 1.13+) — invokes ordered actions in response to lifecycle events; cleaner than `null_resource` + provisioners for run-X-after-Y patterns.
- Plan-time blast-radius scan: any resource flagged for `replace` / `destroy` in plan must be explicitly acknowledged in the PR description.
- Resource targeting (`-target`) only as last resort; never as the default apply mode.

**7. Drift detection.**
- Scheduled `terraform plan` (daily / weekly) against prod state with diff → Slack / GH issue when non-zero.
- Out-of-band changes (console clicks) are the most common drift source — drift detection catches them.
- `ignore_changes` blocks are exceptions to drift detection — track them in a known list.

**8. CI / plan-vs-apply pattern.**
- PR workflow: `terraform fmt -check` → `terraform validate` → `tflint` → `terraform plan` → comment plan on PR.
- Apply workflow: requires PR-approval + `terraform plan` artifact match (replay protection) → `terraform apply -auto-approve` on merge to main.
- OIDC-based auth to cloud — no long-lived access keys committed to CI secrets. Per-cloud: AWS = OIDC trust + IAM role with `sts:AssumeRoleWithWebIdentity`; GCP = Workload Identity Federation; Azure = federated credentials on an app registration.
- Per-env workflows / runners — staging apply does not have prod credentials.
- Plan artifact retained for audit (90+ days).

**9. Destructive-op safety.**
- Any `destroy` / `replace` / `force_destroy = true` on stateful resources requires:
  (a) explicit acknowledgment in PR
  (b) snapshot / export before apply
  (c) `prevent_destroy` lifecycle removal as a separate prior PR
- `terraform destroy` is a console-only / break-glass tool — never wired into a CI auto-apply path.
- `force_destroy = true` on S3 buckets / GCS buckets / Azure containers is [BLOCKER] outside dev — buckets with data should require manual data-clear.
- Cross-resource cascading deletes (e.g. dropping a VPC that has dependents) require explicit `depends_on` cleanup ordering.

## Findings format

```
### Terraform Review: {path}

Environment: {env}  |  Verdict: SHIP / SHIP-WITH-FIXES / DO-NOT-SHIP
Counts: {N} [BLOCKER], {M} [SUGGESTION], {P} [NITPICK]

[BLOCKER]
1. {file}:{line} — {one-line summary}
   What: {what is wrong}
   Why blocker: {what happens if shipped — data loss / outage / privilege escalation}
   Fix: {concrete diff or recipe}

[SUGGESTION]
1. {file}:{line} — {summary}
   What: {what's suboptimal}
   Recommendation: {concrete fix}

[NITPICK]
1. {file}:{line} — {summary}
   (cosmetic / convention; non-blocking)

CLEAN
- {what IS done right that a reviewer would expect to find broken}
```

## Severity rubric

| Severity | What qualifies |
|---|---|
| **[BLOCKER]** | Data loss path, secret leak, prod blast-radius without gate, missing state locking (neither `use_lockfile` for S3 nor DynamoDB nor HCP/GCS native), unpinned provider in prod, `force_destroy = true` on prod bucket, missing `prevent_destroy` on irreplaceable, `terraform destroy` in CI auto-path |
| **[SUGGESTION]** | Module not pinned, missing variable validation, undocumented `ignore_changes`, missing output description, secret in tfvars but env-injected at apply time, drift detection not scheduled |
| **[NITPICK]** | Formatting (covered by `fmt`), naming convention drift, missing `description` on minor variables, comment style |

## Quality bar

- Always group by severity — never present findings as a flat list
- Every [BLOCKER] names a concrete failure (data loss / outage / privilege escalation / drift), not just "this is bad"
- Every finding includes a concrete fix (diff or recipe), not "consider improving"
- The CLEAN section is required — validates the review was thorough, not just complaint-listing
- For `terraform plan` review: distinguish "what the code says" from "what the plan will do" — the same code can produce different plans depending on state
- Distinguish prod from dev — many [SUGGESTION] in dev become [BLOCKER] in prod (esp. `force_destroy`, lifecycle gates, secret handling)
- Provider-upgrade reviews: scrutinize every `replace` in plan output — provider updates often silently force-replace resources

## What this skill does NOT do

- Does NOT run `terraform plan` / `terraform apply` — those are out-of-band; this skill reads existing code + plan output
- Does NOT validate cloud-side IAM / network policies — pair with `/security-audit` and the platform skill (`/sagemaker-design`, `/vertex-ai-design`, `/databricks-asset-bundles`)
- Does NOT review Pulumi / CDK / CloudFormation — Terraform-specific
- Does NOT design the IaC structure from scratch — pair with the relevant platform skill for the architecture; this skill reviews what's been written
- Does NOT replace `tflint` / `checkov` / `tfsec` — encode-once policy linters; this skill catches design + intent issues those can't

## OpenTofu compatibility

The 9 dimensions above apply identically to **OpenTofu** (MPL-licensed Linux Foundation fork after HashiCorp's August 2023 BSL re-license). OpenTofu 1.12.x is a serious enterprise-grade alternative (backed by Spacelift, Gruntwork, Harness, Env0). Most `.tf` configurations work unchanged; some recent HashiCorp-only features (provider-defined functions, certain `cloud` block options) may not yet be in OpenTofu. When reviewing for an OpenTofu shop:
- Substitute `tofu` for `terraform` in command examples.
- Drop the `cloud` block (use `backend "remote"` against TFE or self-hosted state).
- Verify any feature flagged "TF 1.x+" against the OpenTofu changelog.
