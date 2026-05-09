# SECURITY_MODEL.md

The threat model and per-invariant enforcement layer for [PROJECT NAME]. Auto-loaded by Claude Code as a source-of-truth doc. Update on every change to: auth provider, DB schema, API surface, file storage, role definitions.

> **How to use this template**
>
> 1. Replace `[PROJECT NAME]` and bracketed placeholders.
> 2. Fill §1–§3 from your stack: what auto-generates endpoints, what auth roles exist, what columns/operations are sensitive.
> 3. Fill §4 (the enforcement table). **Empty cells = KNOWN GAPS.** Don't leave cells empty without a corresponding row in §6.
> 4. Wire §5 (CI checks). Each row in §4 should have a static or runtime check.
> 5. Run `/security-audit` to surface findings against current code; record under §7.
>
> Stack-specific scaffolding examples in commented blocks below (`<!-- SUPABASE -->`, `<!-- FIREBASE -->`, `<!-- HASURA -->`, `<!-- EXPRESS-FASTAPI-FLASK -->`). Delete the blocks that don't apply.

---

## 1. Auto-generated endpoint surfaces

Endpoints exposed by the stack that we did NOT explicitly write. These are first-class attack surfaces — server-action / API-route invariants do not protect them.

| Surface | Reachable with | Notes |
| ------- | -------------- | ----- |
|         |                |       |

<!-- SUPABASE
| PostgREST `https://<project>.supabase.co/rest/v1/*` | NEXT_PUBLIC_SUPABASE_ANON_KEY (public) | Every public table is reachable for SELECT/INSERT/UPDATE/DELETE. RLS-gated. |
| Realtime `wss://<project>.supabase.co/realtime/v1` | Same anon key | postgres_changes subscriptions filtered server-side IF Realtime RLS is on. |
| Storage public URLs | Public per bucket policy | |
| GoTrue Auth `/auth/v1/*` | Anon key | Direct OTP requests bypass UI gates. |
SUPABASE -->

<!-- FIREBASE
| Firestore SDK | Project ID + auth state | Gated only by Firestore Security Rules. |
| Storage URLs | Public per Storage Rules | |
| Realtime listeners | Same Rules apply | |
FIREBASE -->

<!-- HASURA
| Hasura GraphQL `/v1/graphql` | Role headers; admin secret bypasses | Permission rules in metadata/databases/*/tables/*.yaml. |
HASURA -->

<!-- EXPRESS-FASTAPI-FLASK
| Auto-generated docs (FastAPI /docs, /openapi.json; Express swagger) | Public unless gated | Disable or password-gate in prod. |
| ORM admin tooling (alembic CLI, Prisma Studio) | Local | Don't expose. |
EXPRESS-FASTAPI-FLASK -->

**Implication:** every server-action invariant must independently exist at the data layer. Server actions are a UI convenience layer; auto-generated endpoints are reachable with curl + the public credential.

---

## 2. Auth roles / principals

| Role | Source | Bypass | Reachable from |
| ---- | ------ | ------ | -------------- |
|      |        |        |                |

<!-- SUPABASE
| anon | unauthenticated; anon key | No | Browser, curl with public anon key |
| authenticated | JWT-bearing user | No | Browser after login, curl with JWT |
| service_role | SUPABASE_SERVICE_ROLE_KEY (server-only) | YES | server-only via `import "server-only"` |
| supabase_auth_admin | GoTrue's role | No (rolbypassrls=f) — needs SECURITY DEFINER for cross-table reads from triggers | Auth triggers only |
| admin (app-level) | users.roles array contains 'admin' | No (RLS uses is_admin() function) | App routes that check is_admin() |
SUPABASE -->

<!-- FIREBASE
| anonymous | no auth | n/a | Public browser |
| authenticated | request.auth != null | n/a | Signed-in users |
| admin | custom claims (request.auth.token.admin == true) | n/a | Admin-promoted users |
| Firebase Admin SDK | server-only | bypasses all rules | Server functions |
FIREBASE -->

---

## 3. Sensitive operations

PII, financial, role-grants, location, anything that bypasses a state machine. Fill in for THIS project:

- [ ] User profile fields (which?)
- [ ] Role / permission columns (which table.column?)
- [ ] Financial fields (amount, currency, beneficiary)
- [ ] Location / address fields (which table.column?)
- [ ] State-machine columns (which?)
- [ ] File / media references (which buckets / public URLs?)
- [ ] Audit / log writes (where; append-only enforced?)

---

## 4. Enforcement table

For each (sensitive operation × auth role × surface) cell — what enforces it? **Empty cells are KNOWN GAPS, not "TBD".**

| Operation | Auth role | Surface | Enforcement layer | Status |
| --------- | --------- | ------- | ----------------- | ------ |
|           |           |         |                   |        |

Acceptable enforcement values:

- `RLS WITH CHECK (state='X')` — Postgres RLS policy that pins the value
- `BEFORE-UPDATE trigger raises if NEW.col != OLD.col` — for column-protection (column-level RLS doesn't exist in Postgres)
- `Firestore rule: allow update if resource.data.X == "approved"` — Firebase
- `Hasura permission _check: { state: { _eq: "X" } }` — Hasura
- `Service-role-only writes (user-level UPDATE policy dropped)` — drop the user policy entirely; only the elevated client can mutate
- `REVOKE SELECT (col) FROM role` — column-level read restriction
- `CHECK constraint at table-create` — Postgres CHECK
- `pydantic schema with strict types + Field(constraints) at the route boundary` — FastAPI
- `Validation in app layer ONLY` — DOCUMENTS A KNOWN GAP. Acceptable only if surface is genuinely single-path (e.g., bare Express with no auto-generated endpoint AND no leaked DB credential risk).

---

## 5. CI checks

What automated checks enforce the invariants in §4? Each row in §4 should have a corresponding CI check OR a written justification for why it doesn't need one.

| Invariant | CI check | Status |
| --------- | -------- | ------ |
|           |          |        |

Patterns that work statically (no infra needed):

- **Migration-set parsing** — walk DB migration files, assert REVOKE/RLS/trigger statements exist for sensitive tables/columns. Pattern: parse SQL with regex, fail on missing statements OR on later GRANT that overrides. (Plotspot's `scripts/check-column-grants.mjs` is a 70-line example.)
- **Config-file diff** — parse Firestore rules / Hasura permissions / IAM policy files; assert each sensitive operation has a matching rule. Fail PRs that delete or weaken rules without explicit acknowledgment.
- **Code-level grep gates** — disallow `service_role` outside `lib/admin/`, raw SQL string interpolation, `--no-verify`, etc.

A CI check that catches one regression per year pays for itself.

---

## 6. Known-gap registry

Cells in §4 marked "Validation in app layer ONLY" or empty. Each must have a JIRA / GitHub issue + a target close date. If the gap predates this doc, mark "predates SECURITY_MODEL.md".

| Gap | Severity | Issue | Target close |
| --- | -------- | ----- | ------------ |
|     |          |       |              |

---

## 7. Last audit

- **Date:**
- **Audit type:** `/security-audit` skill / external pen-test / informal review
- **Findings link:**
- **Triage status:**

Re-audit cadence: after every multi-PR sprint touching DB/auth, before every production deploy, quarterly otherwise.
