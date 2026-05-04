# CLAUDE.md

Guidance for Claude Code working in this repo. Auto-loaded at the start of every session.

---

## What this repo is

**[PROJECT NAME]** — [one sentence: what it is, who it's for, what problem it solves].

[Optional: one sentence on what this repo is NOT — helps Claude avoid scope creep.]

---

## Session-start protocol

Before any tool calls beyond basic orientation:

1. Read [`scratch/NEXT_SESSION.md`](scratch/NEXT_SESSION.md) — resume bookmark: HEAD, branch, what landed last session, open items, things NOT to do without explicit instruction
2. Read [`LESSONS_LEARNED.md`](LESSONS_LEARNED.md) — process lessons from prior sessions; re-reading prevents repeat mistakes
3. Read this file — repo posture and constraints
4. `git status` + `git log --oneline -5` — confirm state matches the bookmark
5. Only then ask the user what they want to work on — do not start anything proactively

---

## Source of truth

**[FILENAME]** is the canonical source for [what it defines — e.g., schema, feature list, API spec, pricing].

The `[Used in / Referenced by]` column (or equivalent) maps each row to downstream files that need follow-up edits.

**Never** edit a derived file without updating the source of truth in the same change.

---

## Repo structure

```
[PROJECT NAME]/
├── CLAUDE.md                  ← This file
├── LESSONS_LEARNED.md         ← Process lessons (re-read each session)
├── scratch/                   ← Gitignored; NEXT_SESSION.md and personal workspace
├── memory/                    ← Claude's persistent project memory
│   └── MEMORY.md              ← Memory index
└── [your project files here]
```

---

## Working conventions

[Fill in project-specific conventions. Examples:]

- [Naming conventions — files, variables, branches]
- [How tests are run and what "passing" means]
- [Where the source of truth lives for each type of content]
- [PR / commit conventions]
- [Any file that must never be edited directly (generated files, etc.)]

---

## Tone and output constraints

[Fill in. Remove any that don't apply to your project. Examples:]

- No emojis in [artifacts / commits / output] unless explicitly requested
- Numeric where possible — no adjectives doing numeric work ("significant improvement" fails; "42% latency reduction" passes)
- Every recommendation names a failure mode — no universally-best options
- Comments in code: only when the WHY is non-obvious. No "this function does X" comments.
- [Language / framework style guide link if applicable]

---

## Things to avoid

[Fill in. Add to this list as you learn what goes wrong. Examples:]

- Don't [X] without explicit instruction
- Don't add [Y] — explicit decision: [reason]
- Don't edit [Z] — it's auto-generated
- Don't push to main directly — branch + PR required

---

## Automation

[Fill in any slash commands, hooks, or scheduled routines.]

**Custom slash commands** (type in Claude Code prompt):
- `/review` — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format
- `/adr` — draft an Architecture Decision Record
- `/tradeoff` — structured tradeoff analysis for a decision

**Hooks:** [List any hooks in `.claude/hooks/` and what they do.]

**Scheduled routines:** [List any automated agents or cron routines.]
