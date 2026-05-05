---
name: test-gen
description: Generates runnable pytest test files covering happy path, edge cases, error/exception cases, and contract invariants. Use when asked to write tests for a Python function, class, or module, or when test coverage is missing.
---

# /test-gen — Generate pytest Tests

## Behavior
1. Read the target code — understand inputs, outputs, side effects, error paths
2. Check for existing tests first — match project's fixture and naming conventions if present
3. Generate across 4 categories: happy path, edge cases, error/exception cases, contract invariants
4. Ask before writing if target test file already exists with content

## 4 Categories
- **Happy path** — primary use case and documented variants
- **Edge cases** — empty inputs, zero, single-item, max sizes, None, whitespace, special chars
- **Error cases** — verify correct exception type with `pytest.raises()`; wrong types if annotated
- **Contract cases** — documented invariants ("output is always sorted", "returned length equals input")

## Conventions
- File: `tests/test_<module_name>.py`; naming: `test_<function>_<scenario>`
- `pytest.fixture` for repeated setup; `@pytest.mark.parametrize` for same logic + multiple inputs
- Use `assert` not `assertEqual`; mock external I/O (network, filesystem, time) for determinism
- Test observable behavior — not implementation details

## Output skeleton

```python
# tests/test_<module>.py
import pytest
from <module> import <target>

# --- Fixtures ---
@pytest.fixture
def <name>(): ...

# --- Happy path ---
def test_<fn>_<scenario>(): ...

# --- Edge cases ---
@pytest.mark.parametrize("<param>", [<case1>, <case2>])
def test_<fn>_edge_<description>(<param>): ...

# --- Error cases ---
def test_<fn>_raises_<error>_when_<condition>():
    with pytest.raises(<ExceptionType>): ...

# --- Contract ---
def test_<fn>_<invariant>(): ...
```

## Quality bar
- Every test must be runnable — no `TODO`, no `...` bodies
- Don't test private methods — test through the public API
- Ambiguous behavior without type annotations → ask before assuming
