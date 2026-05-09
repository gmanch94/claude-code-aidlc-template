# Operating Philosophy

A portable reference — paste the relevant sections into any project's CLAUDE.md.

---

## Communication style

- Terse. Drop articles, filler words, verbose phrasing. Fragments fine when clear.
- Numeric over adjective: "11 of 21 APIs (52%)" not "more than half"; "42% latency reduction" not "significant improvement"
- Every recommendation names a trade-off or failure mode — no universally-best options
- No emojis unless explicitly requested
- No trailing summaries ("I have completed X and Y") — state results directly, then stop

---

## Context management

Large outputs go to the context-mode sandbox, not inline. Tool selection hierarchy:

1. **Research**: `ctx_batch_execute` — runs commands + auto-indexes output; one call replaces many steps
2. **Follow-up**: `ctx_search` — all follow-up questions in one call (multi-query)
3. **Processing**: `ctx_execute` / `ctx_execute_file` — analysis, data processing, API calls

Raw tool output exceeding ~20 lines must not enter the main context window. No `Bash` for commands producing large output — use `ctx_batch_execute`. No `WebFetch` — use `ctx_fetch_and_index`.

---

## Advisor protocol

Call `advisor()`:
- **Before** committing to a non-obvious approach — before writing, before building on an assumption
- **After** completing significant work, before declaring done (make the deliverable durable first — write the file, then call)
- **When stuck** — errors recurring, approach not converging, results that don't fit
- **When changing approach** — don't silently switch; surface the conflict

Give advice serious weight. If advisor flags an issue, fix it before calling again. If primary-source evidence conflicts with advisor guidance, surface the conflict explicitly — don't silently pick one side.

Minimum cadence on non-trivial tasks: one advisor call before approach crystallizes, one before declaring done.

---

## Research & verification standards

- **Primary-source discipline**: verify claims from primary sources (official docs, GitHub specs, API listings) before recording. "Inferred from absence" is not sufficient for capability claims.
- **Distinguish precision levels**: "no specs in the current developer portal" ≠ "no specs exist anywhere." Nuance must be exact and consistent.
- **Prototype ≠ production**: label sources accurately. A 2021 prototype repo is supporting evidence, not current documentation.
- **Cross-file consistency**: if a claim appears in N files, all N must match. When fixing a claim, grep all files for the same claim and update every occurrence in the same pass.

---

## Session management

- Read session bookmark (NEXT_SESSION.md or equivalent) before any tool calls beyond orientation
- Confirm git state matches the bookmark (`git status` + `git log --oneline -5`)
- Do not start work proactively — ask what the user wants after orientation
- Update the session bookmark at end of session with: HEAD, branch, what landed, open items, things NOT to do without explicit instruction

---

## Git & file hygiene

- No push to remote without explicit per-session authorization
- No commit to main/master directly — feature branch + PR unless the repo convention says otherwise
- PowerShell commit messages: inline `-m "..."` only — no long here-strings (hits 948-byte parse limit on Windows)
- No `--no-verify`, no `--force` unless user explicitly requests

---

## Confusion Protocol

When facing an ambiguous requirement, contradictory sources, or an undocumented design decision: stop and surface the conflict explicitly before proceeding. Ask one targeted question. Never guess on design decisions or silently resolve contradictions.

---

## Karpathy failure modes

Guard against these four in every session:

| Failure mode | What it looks like | Defense |
|---|---|---|
| **Wrong assumptions** | Guessing at intent; building on unstated premise | Surface the assumption; ask one question |
| **Overcomplexity** | Adding abstraction, generalization, or flexibility the task doesn't require | Scope to exactly what was asked |
| **Orthogonal edits** | Touching files/sections outside the stated task | Stay in scope; no drive-by cleanup |
| **Imperative over declarative** | Prescribing steps instead of describing the desired outcome | State what should be true, not how to get there |
| **Single-path-of-control** | Treating the API endpoint as the only writer when the platform exposes auto-generated alternatives (PostgREST, Firestore SDK, Hasura GraphQL) | "I check it in the action" is decorative if curl bypasses it. Every invariant needs a data-layer mirror. |
| **Convention-level compounding** | Same shape of bug shows up in multiple PRs in a sprint | Stop adding PRs. The convention itself is wrong. Fix the foundation, then resume. |

---

## Security thinking

The API endpoint you wrote is one path to the data. Stack-specific auto-generated endpoints (Supabase PostgREST, Firebase Firestore SDK, Hasura GraphQL, AWS AppSync) are others. **Every invariant the API enforces must independently exist at the data layer**, on every path that reaches the data.

### Think-first protocol (mandatory before any non-trivial change to API / DB / auth / file uploads / public reads)

Write the design intent in user-visible text BEFORE coding. Answer four questions:

1. **What invariants does this enforce?** State machine? Role gate? Value bounds? Ownership? "Column X must be Y before Z"? List them.
2. **What is the attack surface?** List every path that reaches the data being mutated/read. Your API is one. The auto-generated endpoint (if any) is another. Realtime subscriptions, mobile SDK queries, public file URLs — list them all.
3. **For each invariant × each surface — where is it enforced?** Acceptable: RLS `WITH CHECK` on values, Firestore rule, Hasura permission, BEFORE-UPDATE trigger, column-level `REVOKE`, service-role-only writes (with the user-level mutation policy dropped). **Unacceptable: "the API checks it"** (covers only one path).
4. **What's the failure mode if X breaks?** Concrete sentence per invariant. If you can't name the failure, you don't yet understand the invariant.

If the design clears all four, code. If anything is hand-wavy, stop and surface.

### Pre-merge independent reviewer

For PRs touching auth flow, RLS / authorization rules, DB triggers/functions, payment state, or any "safety property" comment: spawn an **independent code-reviewer subagent** before merge. Brief like a colleague who hasn't read the conversation; ask for severity-tagged findings + verdict. Skip only for trivial single-file changes.

### Pre-sprint security pass

For multi-PR sweeps that touch DB schemas, auth, or any user-write surface: run `/security-audit` on the EXISTING attack surface BEFORE the sprint starts. Triage: CRITICAL/HIGH must be fixed pre-sprint. The cost of catching the same shape of bug in 10 places after a 20-PR sprint is days of remediation; the pre-sprint pass is hours.

### Per-project SECURITY_MODEL.md

Every project with a user-facing surface should have `docs/SECURITY_MODEL.md` (run `/security-model-init` to scaffold). Five sections: (1) auto-generated endpoints, (2) auth roles, (3) sensitive operations, (4) per-(operation × role × surface) enforcement table, (5) static CI checks. Empty cells in §4 = known gaps. Filling the doc forces upfront thinking; the audit agent verifies the doc matches reality.

---

## Design philosophy

- Three similar lines is better than a premature abstraction
- No error handling for scenarios that can't happen — trust internal code and framework guarantees
- Validate only at system boundaries (user input, external APIs)
- No feature flags or backwards-compatibility shims when you can just change the code
- If unused, delete it — no renaming to `_unused_`, no `# removed` comments
- Default to no comments in code; add one only when the WHY is non-obvious and would surprise a future reader
