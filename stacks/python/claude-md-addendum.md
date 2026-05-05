# CLAUDE.md Addendum — Python Stack

Paste this block into your project's `CLAUDE.md` under a `## Python` section. Fill in the bracketed placeholders.

---

## Python

### Toolchain

| Tool | Version | Purpose |
|---|---|---|
| Python | [e.g., 3.12] | Runtime |
| Package manager | [pip / uv / poetry / pipenv] | |
| Linter | [ruff / flake8] | |
| Formatter | [ruff format / black] | |
| Type checker | [mypy / pyright] | |
| Test runner | [pytest] | |
| Test coverage | [pytest-cov / coverage] | |

**Run checks:**
```bash
# Lint
[ruff check . / flake8 .]

# Format check (non-destructive)
[ruff format --check . / black --check .]

# Type check
[mypy . / pyright]

# Tests
[pytest / uv run pytest]

# Dependency audit
[pip-audit / uv run pip-audit]
```

### Project structure

```
[project_name]/
├── src/
│   └── [package_name]/    ← source root
├── tests/                 ← mirror src/ structure
│   └── [package_name]/
├── pyproject.toml         ← single config file (preferred over setup.cfg + requirements.txt)
└── [requirements.txt]     ← if not using pyproject.toml
```

### Conventions

- **Imports:** stdlib → third-party → local, separated by blank lines (enforced by ruff/isort)
- **Type annotations:** required on all public functions and methods; `x | None` over `Optional[x]` (Python 3.10+)
- **Docstrings:** [Google / NumPy / reStructuredText] style — [choose one]
- **Test naming:** `test_<function>_<scenario>` — descriptive enough to read without opening the file
- **Fixtures:** in `tests/conftest.py` for shared fixtures; inline for single-test fixtures
- **Mocking:** `unittest.mock.patch` or `pytest-mock`; mock at the boundary (I/O, network, time), not internals

### Things to avoid

- Don't add `# type: ignore` without a comment explaining why it's a false positive
- Don't use `Any` to silence type errors — find the correct type or ask
- Don't use `assert` for runtime validation in non-test code — use explicit `if / raise`
- Don't import from private modules (`_internal`, `__private`) of third-party packages
- Don't leave `print()` statements in non-script code — use `logging`
- Don't pin to `latest` or use unpinned ranges like `>=1.0` in production dependencies

### Slash commands (Python)

- `/test-gen` — generate pytest tests for a function/class (happy path, edge, error, contract)
- `/type-fix` — explain and fix mypy/pyright errors with minimal changes
- `/deps-audit` — CVE scan + outdated package check + upgrade recommendations
