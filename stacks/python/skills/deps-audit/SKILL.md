---
name: deps-audit
description: Audits Python dependencies for CVEs, outdated packages, unpinned versions, and abandoned packages, then recommends a versioned upgrade path. Use when asked to check dependencies, audit packages, or run pip-audit.
---

# /deps-audit — Python Dependency Audit

## Behavior
1. Locate dependency files: `requirements.txt`, `requirements/*.txt`, `pyproject.toml`, `setup.cfg`, `Pipfile`
2. Run `pip-audit` for CVEs; fall back to PyPI lookup if unavailable
3. Run `pip list --outdated` (or `uv pip list --outdated`)
4. Categorize findings by severity; recommend a versioned upgrade path

## Finding categories

| Category | Severity | Action |
|---|---|---|
| Known CVE in installed version | CRITICAL / HIGH | Upgrade immediately; note breaking changes |
| Archived / abandoned package | HIGH | Find replacement or vendor |
| Major version behind | MED | Plan upgrade; check changelog |
| Minor / patch behind | LOW | Next maintenance window |
| Unpinned dependency | MED | Pin to current known-good version |
| Overly wide constraint (`>=1.0`) | LOW | Tighten to `>=1.0,<3.0` |

## Output

```
### Dependency Audit: [project]
Date: | Files: | Overall: GREEN / AMBER / RED

#### Security findings
| Package | Installed | CVE | Severity | Fix Version | Breaking? |

#### Outdated
| Package | Installed | Latest | Type | Action |

#### Pinning issues
| Package | Current constraint | Recommended |

#### Upgrade commands
pip install package==X.Y.Z  # security first
pip install package==X.Y.Z  # routine, next window

#### Action list (by severity)
```

## Quality bar
- CVEs are always CRITICAL/HIGH — don't downgrade because "we don't use that code path"
- Check transitive deps — CVEs in indirect deps are equally exploitable
- No version pins = [MED] risk even with zero CVEs — flag it
- Never recommend `pip install --upgrade <package>` without a specific version
- If `pip-audit` not installed: recommend `pip install pip-audit` before proceeding
