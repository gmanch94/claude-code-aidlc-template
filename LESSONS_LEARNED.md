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
