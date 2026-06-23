# LESSONS_LEARNED.md

Process lessons from working in this repo. Re-read at the start of each session.

The goal is not to document *what* was done — that's in git. The goal is to document *how* to work well here, so each session benefits from prior sessions.

Add entries when: something went wrong and you want to prevent it repeating; or something worked unusually well and you want to lock it in.

---

## Pre-loaded: generalizable lessons

These ship with the template because they apply to almost every project. Add project-specific entries below.

---

### Update NEXT_SESSION.md before ending any session

Write the resume bookmark before `/clear` or closing the session. Include: HEAD commit hash, branch, tree status, what landed, what's open, and a "things NOT to do without explicit instruction" list.

**Why:** Claude Code sessions don't share memory. Without this file, each session re-derives context that was already established — wasting the first 10–15 minutes on orientation that was already done.

---

### Commit before calling advisor()

Make your deliverable durable before calling `advisor()`. Write the file, save the result, commit the change. The advisor call takes time; if the session ends during it, an uncommitted change is lost.

**Why:** `advisor()` forwards your entire conversation history — it can take 30–60 seconds. An unstaged change that exists only in a tool call result is gone if the session dies mid-call.

---

### Ask before sweeps — "I noticed X" ≠ "fix X"

When you observe something (broken URL, wrong naming pattern, inconsistent format), ask before sweeping — don't treat an observation as an authorization to rewrite the codebase.

**Why:** A user saying "the URLs look wrong" may be asking for confirmation, not authorizing 28 edits. An unauthorized sweep is hard to review and harder to undo cleanly.

---

### Source-of-truth-first ritual

Before editing any derived file (README, docs, generated output), edit the source of truth first. If there's a canonical schema, feature list, or spec — edit it first, then propagate to downstream files.

**Why:** Derived files that drift from the source of truth are worse than no documentation. Claude editing the artifact before the source of truth makes the source stale on the same commit.

---

### Read before Edit

The Edit tool requires a prior Read of the file in the same session. If Edit fails with "file has not been read yet," do a minimal Read first, then retry.

**Why:** This is a tool precondition, not a bug. The Read establishes the baseline so the Edit can diff correctly and fail gracefully on mismatched strings.

---

### Check cwd when paths don't resolve

When a file path or filename doesn't resolve, check the working directory before searching deeper. Wrong cwd is the most common cause of "file not found" on a path that looks correct.

**Why:** In multi-repo sessions or after directory changes, the assumed cwd may not match actual cwd. `pwd` before a deeper search saves multiple wasted tool calls.

---

### Label rules of thumb explicitly

When citing field practice rather than primary documentation, label it "rule of thumb" inline. Don't present a sizing heuristic as if it's a vendor-documented specification.

**Why:** Readers make architectural and budget decisions from these numbers. Unlabeled rules of thumb get cited as hard constraints. The label preserves the epistemic gap.

---

### Allowlist patterns: narrowest that covers usage

When adding entries to `.claude/settings.json`, use the narrowest pattern that covers the actual observed usage. Never wildcard interpreters, shells, or package runners — those grant arbitrary code execution.

**Why:** `Bash(python3 *)` allows running any Python. An allowlist entry is a trust grant; scope it to exactly what was observed in transcripts.

---

## Project-specific lessons

---

### Update NEXT_SESSION.md immediately after every merged PR — no prompt needed

After `gh pr merge`, update HEAD, git log snapshot, and "what landed" in NEXT_SESSION.md, then commit and push — without waiting for the user to ask.

**Why:** User had to prompt for this repeatedly. It should be automatic. NEXT_SESSION.md is the session resume bookmark; a stale one wastes the next session's orientation time.

---

### Keep PowerShell commands short — no large inline blocks

Avoid large hashtables, multiline blocks, or long here-strings in PowerShell commands. Use inline `-m "..."` for commit messages, not here-strings. Split into multiple short commands if needed.

**Why:** PowerShell command strings hit a ~948-byte parse limit and get rejected. Here-strings in particular cause parse failures on commit messages.

---

### Fix staleness in all affected files in the same PR

When adding skills, stacks, or prompts — update counts and tables in README.md and CLAUDE.md in the same commit. Don't leave them stale for a follow-up.

**Why:** README said "65+ skills" after 5 more were added; stacks table omitted TypeScript/Go after they were added. Required separate cleanup PRs that should not have been needed.

---

### Server-side checks are one path; auto-generated endpoints are another

If your stack auto-generates REST/GraphQL endpoints (Supabase PostgREST, Firebase Firestore SDK, Hasura, AWS AppSync), the public anon key reaches the underlying DB directly with `curl`. Row-ownership rules (RLS / Firestore Rules / Hasura permissions) gate WHO can hit a row — they do NOT restrict WHICH columns they can write or what values they submit. **Every server-action invariant must independently exist at the data layer**: `RLS WITH CHECK` on the value, BEFORE-UPDATE trigger, column-level `REVOKE`, service-role-only writes (with user-level mutation policy dropped), or platform-equivalent.

**Why:** A real audit on a 20-PR sprint surfaced 10 vulnerabilities of this exact shape. Each individual PR was "fine" because the server action checked the invariant — but a `curl PATCH /rest/v1/users` with `{"roles":["admin"]}` bypassed the action entirely and let any user self-promote to admin. Same shape for `bookings.state='paid'` (free booking), `listings.status='published'` (skip approval gate), `precise_lat/lng` returned to anon. The unifying error: treating "the action validates it" as sufficient. Pre-merge mental model: "could `curl` against the auto-surface bypass this?"

**How to apply:** Before any PR touching API/server-action + DB write, ask the four questions in `operating-philosophy.md` § Security thinking. For new projects with user-facing surfaces, run `/security-model-init` to scaffold `docs/SECURITY_MODEL.md`; fill the (operation × role × surface) enforcement table. For audits, run `/security-audit`.

---

### Sprint without security pass = compounding risk; audit BEFORE the next sprint, not after

A multi-PR feature sprint without an explicit security checkpoint surfaces the same shape of vulnerability across the sprint — every PR builds on the same wrong mental model. The audit at the end finds them in a batch, but remediation cost scales with sprint size: more migrations, more code paths to switch to service-role, more docs to update, more risk that the fix introduces a regression in something the original PR had right.

**Why:** A 20-PR feature sweep without anyone asking "does this auto-generated endpoint enforce the same checks the server action does?" produced 10 audit findings. Two CRITICAL, four HIGH, all the same shape. Each individual PR was "fine" by the convention applied. But the convention itself was the bug. A pre-sprint pass — even 30 minutes — would have caught the convention-level error and saved every subsequent PR from inheriting it.

**How to apply:** Before kicking off a multi-PR sprint that touches DB schemas, RLS / authorization rules, server actions, or any user-write surface — run `/security-audit` on the EXISTING attack surface first. Triage: CRITICAL/HIGH must be fixed before sprint starts. MEDIUM/LOW can be in-sprint or backlog. After the sprint, re-audit to verify the convention held. Pre-launch security pass is gating, not optional.

---

### PR descriptions are ephemeral; operator actions belong in a file

When a PR introduces work that requires operator-action-after-merge — _rotate this secret, set this env var, configure this allowlist, run this migration, tighten this IAM scope_ — the actions must land as a checklist file in the repo, in the same PR. The PR description should reference the checklist, not be it.

**Why:** PR descriptions are ephemeral. After merge they're buried in the GitHub PR archive that nobody opens, and a different operator deploying the same code never sees them. The only durable store for "you must do X to operate this safely" is a file in the repo.

**How to apply:** Before declaring any PR ready, scan its description for these verbs — _rotate, set, configure, grant, wire, create, enable, verify, audit, distribute, disable, migrate, run, sign off_. Each is a candidate for a checklist row. If there are zero, the PR is self-contained. If there are any, write the file (cross-referenced from `SECURITY_MODEL.md` / `launch.md` / `day-2-operations.md`). **Test:** after the PR is merged and squash-deleted, can a fresh operator find this? If no, write a file.

---

### GH Actions default shell is `bash -e -o pipefail` — grep returning "no match" fails the step

`grep` returns exit code 1 when it finds zero matches. Under `bash -e`, that exits the shell — which on GH Actions means the WHOLE step fails, even if the no-match was expected (e.g. scanning an empty file). `pipefail` extends this to pipelines: any grep in `a | grep | b` returning 1 fails the pipeline, fails the command substitution `$()`, fails the step.

**Why:** Authored a `doc-ci.yml` link-check step that ran `grep -oE '\]\(([^)]+)\)' "$f"` on every root `*.md`. One of them (`analysis-methodology.md`) had no markdown links → grep exit 1 → step failed with the unhelpful "Process completed with exit code 1." Took two reactive commits to diagnose (re-checking ML/regex correctness first; the actual bug was the shell defaults).

**How to apply:**
- Any GH Actions step that uses `grep` (or `find`, `diff`, any command that can legitimately return non-zero on "nothing to report") needs `set +e` at the top, with exit-code management via a `$fail` aggregator.
- Prefer shell built-ins over `echo | grep -qE '^https?://'` style guards: `case "$link" in http*|https*|"#"*) continue ;; esac` and parameter expansion (`"${link%%#*}"`) are exit-0-on-mismatch by design.
- For pipelines that may have a stage return non-zero validly, append `|| true` (`grep ... | sed ... > "$tmp" || true`), then check the tempfile size (`[ ! -s "$tmp" ] && continue`).
- Test: scan a deliberately-empty input through the workflow before merging — if it fails, the step is fragile.

---
