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

---

## Design philosophy

- Three similar lines is better than a premature abstraction
- No error handling for scenarios that can't happen — trust internal code and framework guarantees
- Validate only at system boundaries (user input, external APIs)
- No feature flags or backwards-compatibility shims when you can just change the code
- If unused, delete it — no renaming to `_unused_`, no `# removed` comments
- Default to no comments in code; add one only when the WHY is non-obvious and would surprise a future reader
