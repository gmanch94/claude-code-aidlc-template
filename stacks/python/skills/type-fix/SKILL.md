---
name: type-fix
description: Explains and fixes mypy or pyright type errors with minimal code changes, grouping errors by root cause. Use when a user pastes type checker output, shares a file with type errors, or asks to run mypy/pyright.
---

# /type-fix — Fix mypy / pyright Errors

## Behavior
1. Parse error output (or run type checker if given a path)
2. Group errors by file and root cause
3. For each error: one-sentence root cause + minimal fix
4. Apply only after user confirms — don't silently rewrite files

## Common patterns

| Error | Root cause | Minimal fix |
|-------|-----------|------------|
| `Incompatible type "Y"; expected "Z"` | Caller passes wrong type | Fix caller or widen signature if both valid |
| `Item "None" of "X \| None" has no attribute` | Missing None guard | Add `if x is not None:` or `assert x is not None` |
| `Return type incompatible with declared` | Annotation wrong or return wrong | Fix whichever is incorrect |
| `Cannot determine type of "X"` | Assigned conditionally; can't infer | Add explicit annotation |
| `Module "X" has no attribute "Y"` | Wrong import path | Fix import; don't suppress |
| `Missing return statement` | Not all paths return | Add missing return or `-> None` |

## Fix principles
- **Minimal change first** — fix the specific line; don't restructure surrounding code
- **No `# type: ignore`** without a comment explaining the false positive — flag every suppression
- **No `Any`** to silence errors — find the correct type or ask
- **Don't change public signatures** without flagging it — it's a breaking change for callers
- `X | None` preferred over `Optional[X]` (Python 3.10+) unless project uses `Optional` consistently

## Quality bar
- Read 10–20 lines of context before suggesting a fix — the error location ≠ the fix location
- If fixing N reveals N+1 (cascading types), show the full chain before applying
- Same root cause producing 10 errors → fix the root once, not each call site
