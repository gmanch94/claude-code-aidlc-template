---
name: type-fix
description: Explains and fixes Go compiler type errors and staticcheck/vet warnings with minimal changes. Use when 'go build', 'go vet', or staticcheck reports errors.
---

# /type-fix — Fix Go Compiler and Vet Errors

## Behavior
1. Read the error output — parse tool, file, line, and message
2. Read the flagged code — understand the surrounding context before proposing a fix
3. Explain the error in one sentence: what Go expected vs. what it got
4. Propose the minimal fix — do not refactor surrounding code
5. If the correct type is ambiguous, ask one targeted question rather than guessing

## Common error patterns

| Error | Meaning | Fix approach |
|---|---|---|
| `cannot use X (type T) as type U` | Type mismatch in assignment or call | Fix the type; add explicit conversion if types are convertible |
| `X declared but not used` | Unused variable | Remove the variable or use `_` if intentional |
| `undefined: X` | Missing import or wrong package | Add import; check package name spelling |
| `too many arguments in call to X` | Wrong arity | Fix the call site; check function signature |
| `X does not implement Y (missing method Z)` | Interface not satisfied | Add the missing method; check receiver type (pointer vs value) |
| `invalid operation: X (mismatched types T and U)` | Binary op on incompatible types | Convert one operand explicitly |
| `cannot take the address of X` | Non-addressable value | Assign to a variable first, then take address |
| `assignment to entry in nil map` | Write to uninitialized map | Initialize with `make(map[K]V)` before writing |

## Rules

1. Never use `interface{}` / `any` to bypass a type error — find the correct concrete type or define an interface
2. Explicit type conversions (`int32(x)`, `string(b)`) are correct; implicit coercion is not valid in Go
3. Pointer vs. value receiver mismatch on interface implementation: check whether the method set of `T` vs `*T` satisfies the interface
4. `staticcheck` SA-series warnings are real bugs — treat as errors, not style suggestions
5. Do not add blank imports (`_ "pkg"`) to fix undefined errors — find the actual missing dependency
6. `go vet` `printf` format mismatches are bugs — fix the format verb or the argument type

## Output format

```
**Error:** [go build / go vet / staticcheck] — <short description>
**File:** <path>:<line>

**What Go sees:** <what type it inferred or found>
**What it expected:** <what type is required>

**Fix:**
[minimal code change — diff style preferred]

**Why this fixes it:** [one sentence]
```
