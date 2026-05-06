---
name: deps-audit
description: CVE scan, outdated module check, and upgrade recommendations for Go projects. Use when running govulncheck, checking for outdated modules, or evaluating go.mod dependency health.
---

# /deps-audit — Go Dependency Audit

## Behavior
1. Run `govulncheck` for CVE detection
2. Run `go list -m -u all` to find outdated modules
3. Check `go.mod` for indirect dependencies that should be direct
4. Produce a prioritised report: Critical → High → Medium, then outdated majors

## Commands

```bash
# CVE scan (install once: go install golang.org/x/vuln/cmd/govulncheck@latest)
govulncheck ./...

# Outdated modules
go list -m -u all

# Tidy check (should produce no diff if go.mod is clean)
go mod tidy && git diff go.mod go.sum

# Module graph (for understanding transitive deps)
go mod graph
```

## Severity triage

| Severity | Action |
|---|---|
| Critical / High (govulncheck) | Fix immediately — govulncheck only reports reachable vulnerabilities |
| Medium | Fix before next release |
| Low | Backlog |
| Transitive only, not reachable | govulncheck will not report; verify with `go mod why` |

## Upgrade decision rules

| Situation | Recommendation |
|---|---|
| Patch upgrade (v1.2.3 → v1.2.4) | Apply immediately — `go get pkg@v1.2.4` |
| Minor upgrade (v1.2.x → v1.3.x) | Apply after checking CHANGELOG; run tests |
| Major upgrade (v1 → v2) | Major version is a different module path in Go — requires import path update; read migration guide |
| Indirect dep with CVE | Upgrade the direct dep that pulls it in; or use `go get` to force a min version |

## Output format

```
### Dependency Audit: <module>

**Go version:** [go X.Y] | **Date:** [today]

**Security findings (govulncheck)**
| Module | Severity | CVE | Affected versions | Fix version | Reachable |
|---|---|---|---|---|---|
| [module] | [Critical/High/Medium] | [CVE/GO-xxxx] | [range] | [version] | [yes/no] |

**Outdated modules (majors / notable minors)**
| Module | Current | Latest | Notes |
|---|---|---|---|
| [module] | [v1.x.x] | [v2.x.x] | [breaking changes summary] |

**go.mod hygiene**
- [ ] `go mod tidy` produces no diff
- [ ] No unnecessary `replace` directives
- [ ] Indirect deps promoted to direct where appropriate

**Actions**
1. [Immediate] [module] — [reason]
2. [This sprint] [module] — [reason]
3. [Backlog] [module] — [reason]
```

## Rules

1. `govulncheck` only reports vulnerabilities in reachable code paths — a listed CVE that is unreachable is not an immediate risk
2. Go major version upgrades change the import path (e.g., `v1` → `v2`) — this is not a simple `go get` bump
3. Run `go mod tidy` after any upgrade — keeps `go.sum` consistent and removes unused entries
4. Never edit `go.sum` manually — it is generated; regenerate with `go mod tidy`
5. `replace` directives in `go.mod` are temporary workarounds — remove as soon as the upstream fix is available
