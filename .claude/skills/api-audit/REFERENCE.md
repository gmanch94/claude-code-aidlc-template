# /api-audit — Reference

## Pre-sign-off checklist

Run before calling `advisor()` for final review:

### Inventory
- [ ] Every capability claim (CRUD, sandbox, auth, protocol) has a named primary source
- [ ] No `[unverified]` entries remain
- [ ] Prototype / archived sources are labeled as such
- [ ] Partner-only and bundle-gated APIs are flagged

### Shortcomings
- [ ] Technical shortcomings separated from commercial/structural ones
- [ ] Every severity rating is justified by integrator impact, not opinion
- [ ] Numeric throughout — no adjectives doing numeric work

### Recommendations
- [ ] Every recommendation names a specific fix (not "improve X")
- [ ] Every recommendation names a trade-off or failure mode
- [ ] Priority tiers are consistent with severity ratings in shortcomings

### Cross-file consistency
- [ ] Grepped all output files for every claim that appears in more than one file
- [ ] All occurrences updated in the same pass
- [ ] Qualifications are appropriate at the scope where they appear (portfolio-wide vs. per-API)

### Executive summary
- [ ] Top-5 problems match P0/P1 findings — no new claims introduced
- [ ] Score table reflects inventory data, not impressions
- [ ] Strategic gaps table references real peer platforms, not hypothetical ones

---

## Advisor cadence

| After | Call advisor? |
|-------|--------------|
| Phase 2 (inventory complete) | Yes — before shortcomings |
| Phase 4 (recommendations complete) | Yes — before executive summary |
| Phase 6 / final pass | Yes — before declaring done |
| After non-trivial fixes from advisor | Yes — call again |

Do not declare done without final advisor sign-off.

---

## Source quality tiers

| Tier | Examples | How to use |
|------|----------|------------|
| Primary | Official docs page, current OpenAPI spec, API listing with enumerated operations | Assert directly |
| Supporting | Prototype repo, archived docs, pre-GA spec | Assert with label: "per [year] prototype spec" |
| Indirect | Stack Overflow, blog posts, third-party wrappers | Do not assert capability claims — use only for leads to find primary sources |
| Absent | Could not find source | Mark `[unverified]` — do not assert |
