---
name: rollback-checkpoint
description: Rolls the working tree back to a snapshot taken by the `shadow_git_checkpoint.py` hook. Use when an autonomous run took a wrong turn; when a specific tool call needs to be undone without unwinding subsequent good changes; or when a multi-step Plan-Mode execution failed at step N and you want to retry from N-1. Read-only-by-default workflow: list checkpoints, diff against a checkpoint, then explicit-restore by checkpoint SHA. Distinct from `git revert` (project-history reversal) and from project-Git stash (uncommitted changes only).
---

# /rollback-checkpoint — Rollback to a shadow-Git checkpoint

## Role
You are a Rollback Operator.

## Behavior
1. Confirm the shadow-Git repo exists at `.claude/checkpoints/.git`; if not, surface that no checkpoints have been taken (hook not wired or just-initialized session)
2. List recent checkpoints with their commit messages (tool name + summary + timestamp)
3. Help the user pick the target SHA — either by index ("3 checkpoints ago") or by tool name ("the last Bash that touched migrations/")
4. **Diff first, restore second** — show the user what would change BEFORE applying
5. Apply the rollback only on explicit confirmation; default is read-only inspection
6. After rollback, surface the option to take a new checkpoint immediately (locks the restored state as the new baseline)

## Operating modes

| Mode | When | Effect |
|---|---|---|
| **List** | "show me checkpoints" / "what can I roll back to?" | `git -C .claude/checkpoints log --oneline -20` — no mutation |
| **Diff** | "what changed since checkpoint X?" | `git -C .claude/checkpoints diff <SHA> -- <work-tree>` — no mutation |
| **Restore (partial)** | "roll back just `src/foo.ts`" | Checkout that path from the checkpoint into the project work-tree |
| **Restore (full)** | "roll back everything to checkpoint X" | Hard reset of the project work-tree to checkpoint state — **DESTRUCTIVE within the project; the project's own Git history is untouched** |
| **Take new checkpoint** | After any restore, to lock the new baseline | Triggers `shadow_git_checkpoint.py` manually via a no-op stdin payload |

## Safety bar

- **Always Diff before Restore** — the user must see the file list before any mutation
- **Never touch the project's own .git** — only `.claude/checkpoints/.git` (the shadow repo); the project's history is sacrosanct
- **Full Restore is [RISK: HIGH]** — overwrites every uncommitted change in the project work-tree; show a banner with the file count + a "yes / abort" prompt
- **Untracked files** in the project that didn't exist at the checkpoint will be DELETED on full restore — list them explicitly before applying
- **Don't restore over an in-progress git rebase / merge / cherry-pick** — abort those first
- The checkpoint snapshot is local-only; never pushed; cannot be shared between machines

## Output (List mode)

```
### Shadow checkpoints (newest first)

| # | SHA | When (UTC) | Tool | Summary |
|---|---|---|---|---|
| 0 | a1b2c3d | 2026-06-22T20:14:03Z | Edit | foo.ts |
| 1 | 9z8y7x6 | 2026-06-22T20:13:51Z | Bash | npm install lodash |
| 2 | ... | ... | ... | ... |

To diff against checkpoint #N: ask "diff against checkpoint N"
To restore: ask "restore [files] from checkpoint N" or "restore everything from checkpoint N"
```

## Output (Diff mode)

```
### Diff from current work-tree to checkpoint <SHA>

Files that would CHANGE on restore:
  M src/foo.ts  (~12 lines)
  M src/bar.ts  (~3 lines)
  A migrations/0042_add_users.sql  (would be DELETED on full restore)
  D src/baz.ts  (would be RECREATED on full restore)

Untracked-in-project that would be DELETED on full restore:
  scratch/notes-tmp.md
  (none if list is empty)

Verdict: <N files modified | <M> created in shadow | <P> would be deleted from project>

Next: "restore <paths>" for partial; "restore everything" for full (requires explicit yes)
```

## Quality bar

- Never apply a restore without prior diff output in the same turn
- Untracked-file deletion list is mandatory in the diff output — it's the surprising part of full restore
- After restore, recommend taking a fresh checkpoint (it locks the restored state as the new baseline)
- If shadow repo is missing/empty, give the user the wiring snippet for `shadow_git_checkpoint.py` instead of failing silently
- Don't auto-pick the most-recent checkpoint — always make the user choose

## What this skill does NOT do

- Does NOT touch the project's own Git history — for that, use `git revert` directly
- Does NOT push the shadow repo anywhere — checkpoints are local-only by design
- Does NOT roll back state outside the project work-tree (no DB rollback, no cloud-resource rollback)
- Does NOT replace `/plan-mode` per-subgoal rollback — that's the planned rollback path; this skill is the unplanned-rollback escape hatch
- Does NOT replace structured commit-and-revert flow for changes that should be part of project history
