---
name: deps-audit
description: CVE scan, outdated package check, and upgrade recommendations for Node.js/TypeScript projects. Use when running npm/pnpm/yarn audit, checking for outdated packages, or evaluating dependency health.
---

# /deps-audit — Node.js Dependency Audit

## Behavior
1. Detect package manager: check for `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`
2. Run security audit (CVEs)
3. Check for outdated packages
4. Produce a prioritised report: Critical → High → Medium, then outdated majors

## Commands by package manager

```bash
# npm
npm audit --json
npm outdated

# pnpm
pnpm audit --json
pnpm outdated

# yarn (v1)
yarn audit --json
yarn outdated
```

## Severity triage

| Severity | Action |
|---|---|
| Critical | Fix immediately — block PR if in production dependency |
| High | Fix before next release |
| Medium | Fix in current sprint |
| Low | Backlog; fix opportunistically |
| Dev-only CVE | Lower priority — not in production bundle |

## Upgrade decision rules

| Situation | Recommendation |
|---|---|
| Patch upgrade (1.2.3 → 1.2.4) | Apply immediately — no API changes |
| Minor upgrade (1.2.x → 1.3.x) | Apply after checking changelog for deprecations |
| Major upgrade (1.x → 2.x) | Read migration guide; check for breaking changes; test first |
| Transitive CVE, no direct fix | Pin transitive via `overrides` (npm/pnpm) or `resolutions` (yarn) as temporary mitigation |

## Output format

```
### Dependency Audit: <project>

**Package manager:** [npm / pnpm / yarn] | **Date:** [today]

**Security findings**
| Package | Severity | CVE | Affected versions | Fix version | Direct/Transitive |
|---|---|---|---|---|---|
| [pkg] | [Critical/High/Medium] | [CVE-xxxx] | [range] | [version] | [direct/transitive] |

**Outdated packages (majors only)**
| Package | Current | Latest | Breaking changes summary |
|---|---|---|---|
| [pkg] | [x.y.z] | [a.b.c] | [key changes] |

**Actions**
1. [Immediate] [package] — [reason]
2. [This sprint] [package] — [reason]
3. [Backlog] [package] — [reason]
```

## Rules

1. Dev-only dependencies (devDependencies) with CVEs are lower priority — they never ship to production
2. Always check if a CVE is exploitable in your usage pattern before treating as Critical
3. Major upgrades: test the full suite before merging — don't batch multiple major upgrades in one PR
4. Transitive-only CVEs with no direct fix: use `overrides`/`resolutions` as a temporary pin, not permanent solution
5. `npm audit fix --force` is destructive — never run without reviewing what it will change
