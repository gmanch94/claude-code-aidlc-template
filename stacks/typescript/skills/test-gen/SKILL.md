---
name: test-gen
description: Generates runnable Vitest/Jest test files covering happy path, edge cases, error cases, and contract invariants. Use when asked to write tests for a TypeScript function, class, or module, or when test coverage is missing.
---

# /test-gen — Generate Vitest/Jest Tests

## Behavior
1. Read the target code — understand inputs, outputs, side effects, error paths
2. Detect test runner: check `package.json` for `vitest` or `jest`; default to Vitest if both absent
3. Check for existing tests first — match project's fixture and naming conventions if present
4. Generate across 4 categories: happy path, edge cases, error/exception cases, contract invariants
5. Ask before writing if target test file already exists with content

## 4 Categories
- **Happy path** — primary use case and documented variants
- **Edge cases** — empty inputs, undefined/null, zero, single-item, max sizes, special chars
- **Error cases** — verify thrown errors with `expect(...).toThrow()`; wrong types where applicable
- **Contract cases** — documented invariants ("output is always sorted", "returned length equals input")

## Conventions
- File: `<module>.test.ts` co-located or `__tests__/<module>.test.ts`; naming: `describe('<target>') > it('<scenario>')`
- Use `beforeEach` for repeated setup; `it.each` / `test.each` for parametrized cases
- Mock external I/O (network, filesystem, time) with `vi.mock()` (Vitest) or `jest.mock()` (Jest)
- Test observable behavior — not implementation details
- Prefer `expect(result).toEqual(expected)` over `toBe` for objects

## Output skeleton

```typescript
// <module>.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest' // or jest equivalents
import { <target> } from './<module>'

describe('<target>', () => {
  // --- Happy path ---
  it('<scenario>', () => {
    expect(<target>(<args>)).toEqual(<expected>)
  })

  // --- Edge cases ---
  it.each([
    [<input1>, <expected1>],
    [<input2>, <expected2>],
  ])('<scenario> %s', (<input>, <expected>) => {
    expect(<target>(<input>)).toEqual(<expected>)
  })

  // --- Error cases ---
  it('throws <ErrorType> when <condition>', () => {
    expect(() => <target>(<bad_args>)).toThrow(<ErrorType>)
  })

  // --- Contract ---
  it('<invariant>', () => { ... })
})
```

## Quality bar
- Every test must be runnable — no `TODO`, no empty bodies
- Don't test private methods — test through the public API
- Async functions: always `await` inside `async` test bodies
- Ambiguous behavior without type annotations → ask before assuming
