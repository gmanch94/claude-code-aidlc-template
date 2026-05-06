---
name: type-fix
description: Explains and fixes TypeScript compiler errors (tsc) and ESLint type warnings with minimal changes. Use when tsc or eslint reports type errors, or when 'any' needs to be replaced with correct types.
---

# /type-fix — Fix TypeScript Type Errors

## Behavior
1. Read the error output — parse error code, file, line, and message
2. Read the flagged code — understand the surrounding context before proposing a fix
3. Explain the error in one sentence: what TypeScript expected vs. what it got
4. Propose the minimal fix — do not refactor surrounding code
5. If the correct type is ambiguous, ask one targeted question rather than guessing

## Common error patterns

| Error code | Meaning | Fix approach |
|---|---|---|
| TS2322 | Type X is not assignable to type Y | Narrow the type; add type guard; fix the assignment |
| TS2339 | Property does not exist on type | Add property to interface; use optional chaining; cast if external |
| TS2345 | Argument of type X not assignable to param type Y | Fix caller; widen param type if intentional |
| TS2532 | Object is possibly undefined | Add null check; use `??`; assert non-null with `!` only if provably safe |
| TS2571 | Object is of type 'unknown' | Add type guard (`typeof`, `instanceof`, `in`); use `as` only if provably correct |
| TS7006 | Parameter implicitly has 'any' type | Add explicit type annotation |
| TS2554 | Expected N arguments, got M | Fix call site; check for optional params |

## Rules

1. Never use `as any` to silence an error — find the correct type or use `unknown` + type guard
2. `// @ts-ignore` is only acceptable for a third-party type definition bug — requires a comment explaining why
3. `as <Type>` (type assertion) only when you have provably correct runtime knowledge the compiler can't infer
4. Prefer type narrowing (`typeof`, `instanceof`, discriminated union) over casting
5. `!` (non-null assertion) only when null/undefined is impossible at that point and you can explain why
6. Do not widen a function's parameter type to fix a call-site error without checking all other call sites

## Output format

```
**Error:** TS<code> — <short description>
**File:** <path>:<line>

**What TypeScript sees:** <what type it inferred>
**What it expected:** <what type is required>

**Fix:**
[minimal code change — diff style preferred]

**Why this fixes it:** [one sentence]
```
