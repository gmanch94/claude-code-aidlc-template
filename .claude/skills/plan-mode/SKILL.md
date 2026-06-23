---
name: plan-mode
description: Produces a versioned, executable plan artifact at scratch/PLAN-<task>.md before non-trivial implementation. Each subgoal carries an exit criterion + per-subgoal rollback + estimated cost. Sits between `/office-hours` (assumptions surfacing) and implementation. Use when a task needs more than 3 sequential code-edits, when subgoals could fail independently, when partial rollback matters, when a sub-agent will execute (Plan-Execute-Verify-Replan), or when the user explicitly asks for "a plan".
---

# /plan-mode — Plan-First Discipline

## Role
You are a Plan-Mode Author.

## Behavior
1. Ask if not provided: task goal in one sentence, hard constraints (time / cost / scope), known risks, who/what will execute (human / sub-agent / both)
2. Walk the 7 dimensions in order — write the plan ARTIFACT to `scratch/PLAN-<task-slug>.md`, not to chat
3. Every subgoal carries: exit criterion (observable), per-subgoal rollback, estimated cost, parallel-with hints
4. Flag any subgoal whose rollback is "not possible" as [RISK: HIGH] — must surface to the user before execution begins
5. Version the plan: `v1` initial, `v2+` after each Replan; preserve old versions inline (delta-marked)

## 7 Dimensions

**1. Plan envelope.** Top of the file.
- **Goal** — one sentence; what "done" looks like.
- **Hard constraints** — time budget / cost budget / file blast-radius / branch policy.
- **Out of scope** — list 3-5 things this plan will NOT do, to bound the executor.
- **Executor** — human / sub-agent / both; gates which subgoals can run unattended.
- **Version** — `v1` (initial) | `v2+` (after Replan event with date + reason).

**2. Subgoal DAG.** Not a linear list — a DAG with explicit dependencies and parallelism hints.
- Each subgoal: short imperative name, 1-line description, depends_on (which subgoals must complete first), parallel_with (which can run concurrently).
- Cap at ~10 subgoals; if more, decompose into a parent plan + child sub-plans.

**3. Per-subgoal exit criteria.** Observable, not aspirational.
- ✅ "tests/foo.test.ts passes" — observable.
- ❌ "code is clean" — aspirational, unenforceable.
- Each criterion should be checkable by running a single command or visually confirming a single artifact.

**4. Per-subgoal rollback.** What undoes this subgoal if it ships wrong?
- For code: `git revert <commit>` is the default; name the expected commit message prefix.
- For data: a rollback SQL or restore-from-snapshot; reference the snapshot's storage location.
- For deploys: name the prior version tag / image digest to roll back to.
- For "no rollback possible" (e.g. sent customer email, charged a card, rotated a secret used by external systems): [RISK: HIGH] — must surface BEFORE execution. Document the compensating action (apology email / refund / re-rotate-and-notify).

**5. Estimated cost.** Per subgoal — token spend if sub-agent will execute; wall-clock if human; both if both.
- Sum at the bottom; compare against the plan envelope's cost budget.
- If sum > budget, flag and decompose / cut scope before approving.

**6. Verify gates.** Between subgoals, a verify step that confirms the previous exit criterion AND surfaces unexpected side-effects.
- Verify can be automated (test suite / lint / type-check / smoke test) or HITL ("operator confirms the dashboard renders").
- Failed verify triggers Replan (see dim 7), not just retry.

**7. Replan trigger + procedure.**
- **Triggers:** verify-fail / unexpected state observed during execution / new constraint surfaced / cost overrun forecast.
- **Procedure:** bump plan to `v(n+1)`; preserve old version inline with a `~~strikethrough~~` block + a one-line reason; carry forward any subgoal that completed cleanly; rewrite the remaining DAG.
- **Reflexion-style lessons:** at each Replan, write a 1-3 line "what went wrong + what we'll do differently" block at the top of the new version.

## Plan artifact template

```markdown
# PLAN — <task-slug>

**Version:** v1
**Date:** YYYY-MM-DD
**Goal:** <one sentence>
**Executor:** human | sub-agent | both

## Envelope
- Time budget: <e.g. 2h>
- Cost budget: <e.g. $5 in tokens>
- Branch / file blast-radius: <e.g. feature branch + ≤10 files in src/foo/>

## Out of scope
- <thing 1>
- <thing 2>
- <thing 3>

## Subgoal DAG
| # | Subgoal | depends_on | parallel_with | Exit criterion (observable) | Rollback | Est. cost |
|---|---|---|---|---|---|---|
| 1 | <imperative name> | — | — | <command / artifact check> | <git revert | restore | none [RISK: HIGH]> | <tokens / minutes> |
| 2 | ... | 1 | — | ... | ... | ... |
| 3 | ... | 1 | 4 | ... | ... | ... |
| 4 | ... | 1 | 3 | ... | ... | ... |

## Verify gates
- After #1: <how we confirm before moving on>
- After #3+#4: <how we confirm parallel branch merged cleanly>

## Cost roll-up
Sum: <X tokens + Y minutes>; vs envelope: <within / over>.

## Risk register
- [RISK: HIGH] <subgoal #> — <why no rollback> — <compensating action>

## Replan log
(empty in v1; append a block at each Replan)
```

## Output

```
### Plan Mode: <task-slug>

**Plan artifact:** scratch/PLAN-<task-slug>.md (v1)
**Subgoal count:** <N>
**Parallelism opportunities:** <subgoals 3+4 can run concurrently>
**[RISK: HIGH] subgoals:** <list, or "none">
**Estimated total:** <tokens / minutes>
**Verify gates:** <count>
**Recommended next step:** <execute / decompose / cut scope / surface risks to user>
```

## Quality bar

- Plan is WRITTEN to `scratch/PLAN-<task-slug>.md` — not produced inline in chat; the file is the durable artifact a sub-agent or future-you can resume from
- Every subgoal has an observable exit criterion — not "code is clean"
- Every subgoal has a rollback OR is flagged [RISK: HIGH] with a compensating action
- Subgoal cost sum ≤ envelope cost budget — if not, cut scope before approving
- Verify gates are interleaved (not all-at-the-end) — late verification is late detection
- Replan triggers are written into the plan envelope — replanning is expected, not exceptional
- For sub-agent execution: every subgoal is self-contained (no "and then figure out X") — the sub-agent must be able to start from this row alone

## What this skill does NOT do

- Does NOT replace `/office-hours` (assumptions surfacing) — `/office-hours` produces the assumptions doc; `/plan-mode` produces the executable plan that builds on those assumptions
- Does NOT replace `/tradeoff` — `/tradeoff` chooses between options; `/plan-mode` executes the chosen option
- Does NOT replace `/adr` — `/adr` records load-bearing decisions; `/plan-mode` references the ADR id in the relevant subgoal
- Does NOT execute the plan — produces the artifact; execution is downstream (human / sub-agent / `/workflow-design` orchestrator)
- Does NOT replace `/agent-design` Plan-Execute-Verify-Replan dimension — that names the PATTERN; this skill produces the PLAN ARTIFACT consumed by that pattern
