---
name: security-audit
description: Deep security audit of the current codebase from a hacker/researcher perspective. Spawns a general-purpose agent with a deterministic prompt that enumerates RLS gaps, IDOR, privilege escalation, input validation bypasses, SSRF, auth bypass, and stack-specific attack surfaces. Returns CRITICAL→LOW findings with file+line citations and remediation hints. Use BEFORE multi-PR sprints touching DB/auth, BEFORE production deploy, and AFTER major feature sweeps. Optionally pass a stack hint as $1 (e.g., "supabase", "firebase", "hasura", "express").
---

# Security audit

Spawn a general-purpose subagent with a stack-aware deterministic security audit prompt. Returns a triage table the user can convert into a fix PR.

## When to invoke

- **BEFORE a multi-PR sprint** that touches DB schemas, auth, RLS, server actions, or any user-write surface. Get the baseline clean before piling on. (Pre-sprint pass per @rules/security.md.)
- **BEFORE production deploy.** Pre-launch gating, not post-launch reactive.
- **AFTER a feature sweep.** Verify the new code didn't introduce regressions and the convention you applied across multiple PRs holds up.
- **Periodically on existing repos.** Quarterly or after dependency upgrades.

## Inputs

- `$1` (optional): stack hint to focus the audit. One of: `supabase`, `firebase`, `hasura`, `appsync`, `express`, `prisma-trpc`, or omit for autodetect from repo files.

## Steps

1. **Detect stack** if not provided. Look for: `supabase/migrations/`, `firebase.json` / `firestore.rules`, `hasura/metadata/`, `amplify/backend/`, `prisma/schema.prisma`. Default to "generic" if no signal.

2. **Enumerate critical files** for the detected stack (the agent will Read them all):
   - **Supabase/Postgres:** all `supabase/migrations/*.sql`, `app/**/actions.ts` (or equivalent server-action paths), `lib/supabase/{client,server,admin,middleware}.ts`, `middleware.ts`, all `lib/validation/*.ts`, all `app/api/**/route.ts`
   - **Firebase:** `firestore.rules`, `storage.rules`, all `functions/**/*.ts`, all client SDK call sites
   - **Hasura:** `metadata/databases/*/tables/*.yaml` (permissions), `migrations/*/up.sql`, all action handlers
   - **Express + ORM:** all route handlers, middleware, ORM model files, auth middleware
   - **Generic:** API route handlers, schema/migration files, auth code, any file with `validation` / `permission` / `policy` in the name

3. **Spawn the agent** with the prompt template below. Brief it like a colleague who has not read the conversation.

4. **Return the agent's report verbatim** to the user with a one-line preface naming severity counts. Do NOT synthesize or paraphrase.

5. **Suggest the next step:** create a `fix/security-hardening` branch, triage CRITICAL/HIGH for immediate fix, MEDIUM for in-sprint, LOW for backlog.

## Agent prompt template

```
You are a security researcher auditing a $STACK codebase from a hacker/researcher perspective. Read the files listed below and report every security finding you can identify. Be specific: file path, line numbers, attack vector, impact, severity (CRITICAL/HIGH/MEDIUM/LOW).

Attack surfaces to cover:

1. Authorization rules / RLS / permissions — missing rules, overly permissive read/write, column-level gaps where the platform supports them
2. API endpoints / server actions — missing auth checks, IDOR (ownership not verified), privilege escalation, missing role gates
3. State machines — can states be skipped or regressed via direct DB/API calls?
4. Payment/financial flows — can amounts, status, or beneficiary be manipulated outside the intended path?
5. Auto-generated endpoints (PostgREST / Hasura GraphQL / Firestore SDK / AppSync) — does the auto-surface enforce the same invariants as the API layer?
6. Cron/webhook endpoints — auth bypass, replay, signature verification gaps
7. Admin routes — privilege check at every layer (middleware, route handler, DB)
8. Rate limiting — fail-open vs fail-closed posture, header spoofing, bypass via per-IP vs per-actor confusion
9. Input validation — bypass via type coercion, prototype pollution, unbounded strings, missing length limits at DB layer
10. PII / location / address exposure — column-level read restrictions, response shaping, post-payment reveal patterns
11. File uploads — SSRF via fetch-on-upload (moderation), folder/prefix validation, content-type spoofing
12. Email / SMS / notifications — can transactional sends be triggered for arbitrary recipients?
13. Service-role / admin credential isolation — is the elevated client ever reachable from client code? Build-time enforcement (server-only imports)?
14. Audit log — append-only enforcement, can it be skipped or manipulated?
15. Realtime subscriptions — can a user subscribe to another user's channel? Does the platform enforce RLS on the WAL/stream?
16. CAPTCHA / bot defense — can it be bypassed in dev mode leaking into prod? Server-side verification?
17. Disposable-email / signup gates — bypass vectors (direct API call with anon key, etc.)
18. Stack-specific hot spots — name them based on $STACK

Files to read (read ALL of these — do not sample):
$FILE_LIST

Repo root: $REPO_ROOT

Report format:
- Group findings by severity: CRITICAL, HIGH, MEDIUM, LOW
- Each finding: numbered, file+line, attack vector (concrete: "POST /rest/v1/users with body {...} → result"), impact, severity
- End with a "CLEAN" section noting what IS implemented correctly that a researcher would expect to find broken (validates the audit was thorough)
- End with a SUMMARY table: # | Severity | Area | File

Be exhaustive. Don't summarize — enumerate every issue you find. False positives are recoverable; false negatives ship to production.
```

## Multi-auditor escalation (when stakes warrant)

When a single audit pass is not enough — pre-launch deploy, post-major-feature sweep, regulated workload, money-touching surface — spawn **N=3 auditors with DIVERSE reasoning methods**, not 3 copies of the same lens:

- **Auditor A — failure-mode enumeration:** "list every attack vector across the 18 surfaces above"
- **Auditor B — first-principles re-derivation:** "what invariants MUST hold for this app to be safe; check each one against current code"
- **Auditor C — adversarial counter-example:** "construct a concrete curl/exploit payload that bypasses each invariant"

**Decision rule:** a finding ships to the triage table if **≥2 of 3** auditors surface it. Auditor-only findings get a "needs corroboration" tag.

**Why N=3 reasoning-diverse beats N=9 same-family:** correlated errors collapse same-family panels — additional same-method auditors have near-zero marginal value. "Nine Judges, Two Effective Votes" (arxiv 2605.29800).

For routine audits, single-auditor pass is fine. Escalate to N=3 when the cost of a false negative is high (pre-launch deploy, money flows, schema migration affecting RLS).

## Output handling

- If agent returns 0 findings: surface "✓ Audit clean — no findings" and remind the user to re-run after the next major feature sweep.
- If agent returns findings: present the report verbatim, then suggest the triage next step. Do NOT auto-implement fixes — the user reviews the triage first.
- Persist the report to `docs/security-audits/$(date +%Y-%m-%d).md` for historical reference. Create the directory if missing.

## What this skill does NOT do

- Does NOT fix findings automatically. The user reviews triage first; fixing is a separate step (often a separate PR).
- Does NOT run live HTTP probes against a deployed environment. This is static-analysis-by-LLM. For live probes use the runtime curl checks in each project's day-2-ops doc.
- Does NOT replace per-project SECURITY_MODEL.md. The audit finds gaps; the SECURITY_MODEL forces upfront thinking. Both layers are needed.
