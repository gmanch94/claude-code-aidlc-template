---
name: test-gen
description: Generates runnable Go test files covering happy path, edge cases, error cases, and contract invariants using table-driven tests. Use when asked to write tests for a Go function or package, or when test coverage is missing.
---

# /test-gen — Generate Go Tests

## Behavior
1. Read the target code — understand inputs, outputs, error returns, side effects
2. Check for existing tests first — match project's table-driven style if present
3. Generate across 4 categories: happy path, edge cases, error cases, contract invariants
4. Use table-driven tests (`[]struct{ ... }`) for any function with more than one scenario
5. Ask before writing if target test file already exists with content

## 4 Categories
- **Happy path** — primary use case and documented variants
- **Edge cases** — empty string/slice, zero value, nil pointer, max/min int, single element
- **Error cases** — verify `err != nil`; check error type/message where meaningful
- **Contract cases** — documented invariants ("output length always equals input length")

## Conventions
- File: `<package>_test.go` in the same package (white-box) or `<package>_test` package (black-box)
- Use `t.Run(name, func(t *testing.T) {...})` inside table-driven loops
- Use `t.Helper()` in assertion helpers
- Mock interfaces via hand-written fakes or `testify/mock`; avoid mocking concrete types
- Test observable behavior — not unexported implementation details
- Prefer `testify/assert` and `testify/require` over raw `t.Error`/`t.Fatal` for readability

## Output skeleton

```go
// <package>_test.go
package <package>_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func Test<Target>(t *testing.T) {
    tests := []struct {
        name    string
        input   <InputType>
        want    <OutputType>
        wantErr bool
    }{
        // Happy path
        {name: "<scenario>", input: <value>, want: <expected>},
        // Edge cases
        {name: "empty input", input: <zero>, want: <expected>},
        // Error cases
        {name: "<bad input> returns error", input: <bad>, wantErr: true},
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            got, err := <Target>(tc.input)
            if tc.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tc.want, got)
        })
    }
}
```

## Quality bar
- Every test must be runnable — no `t.Skip()` stubs without explanation
- Don't test unexported functions from a black-box `_test` package
- Table-driven for ≥2 scenarios — flat tests only for truly single-case functions
- Parallel tests: add `t.Parallel()` inside subtests when there are no shared mutable fixtures
