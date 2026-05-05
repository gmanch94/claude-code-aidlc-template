---
name: dbt-review
description: Reviews dbt models for structure, naming conventions, ref/source usage, incremental model correctness, test coverage, and documentation. Use when reviewing a dbt PR, auditing a dbt project for quality gaps, or asked to improve a specific dbt model.
---

# /dbt-review — dbt Model Review

## Behavior
1. Review model structure and naming
2. Check ref/source usage
3. Audit incremental model correctness
4. Assess test coverage
5. Verify documentation completeness

## Finding format
- **[BLOCKER]** — Must fix. Data correctness risk, broken ref, missing PK tests.
- **[SUGGESTION]** — Should fix. Meaningful improvement, not blocking.
- **[NITPICK]** — Take or leave. Style, minor naming, documentation gap.

Format: `[SEVERITY] model.sql:line — **Issue** · Recommendation`

## Review checklist

**Structure and naming**
- [ ] Layer prefix correct: `stg_`, `int_`, `fct_`, `dim_` used consistently
- [ ] One model = one grain — no mixing aggregation levels in a single model
- [ ] CTEs used for each logical step; final SELECT is a simple projection (no logic)
- [ ] CTE names describe what they contain (`user_orders` not `cte1`)

**ref / source usage**
- [ ] No hardcoded schema or table references — all upstreams use `{{ ref() }}` or `{{ source() }}`
- [ ] `{{ source() }}` used for raw/landing layer only; `{{ ref() }}` for all dbt-managed models
- [ ] No circular refs

**Incremental models**
- [ ] `unique_key` defined — required to prevent duplicates on re-run (BLOCKER if missing)
- [ ] `is_incremental()` filter uses a reliable watermark (`updated_at` or `event_time` — not `inserted_at` alone)
- [ ] Late-arriving data: watermark lookback window defined (e.g., `>= MAX(event_time) - INTERVAL '3 hours'`)
- [ ] Full-refresh produces same result as incremental on same data — test this

**Tests**
- [ ] `unique` + `not_null` on every primary key (BLOCKER if missing)
- [ ] `accepted_values` on all enum columns
- [ ] `relationships` test on FK → dim joins
- [ ] At least one custom test on business-critical columns (`amount > 0`, `rate BETWEEN 0 AND 1`)

**Documentation**
- [ ] Model-level description in schema.yml
- [ ] Column descriptions for non-obvious fields
- [ ] `meta.owner` set — someone is accountable for this model

## Output format

```
### dbt Review: [model name]

[BLOCKER] model.sql:line — **Issue** · Recommendation
[SUGGESTION] ...
[NITPICK] ...

**Verdict:** Approve / Request changes
**Blockers:** N | **Suggestions:** N | **Nitpicks:** N
```

## Quality bar
- Missing `unique` + `not_null` on PK is always BLOCKER — data correctness cannot be assumed
- Incremental model without `unique_key` silently produces duplicates — always BLOCKER
- Hardcoded schema references break cross-environment deploys — always BLOCKER
- Documentation gaps are NITPICK unless the model is BI-facing or consumed by > 3 teams
