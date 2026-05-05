---
name: sql-review
description: Reviews SQL queries for correctness, performance, and readability — join types, NULL handling, aggregation grain, partition pruning, and common anti-patterns. Use when reviewing a SQL PR, debugging a slow query, or asked to improve a query's correctness or performance.
---

# /sql-review — SQL Query Review

## Behavior
1. Check correctness (join type, NULL handling, aggregation grain)
2. Identify performance issues (full scans, partition skip, expensive patterns)
3. Assess readability (CTE structure, naming, complexity)
4. Output findings with BLOCKER/SUGGESTION/NITPICK grading

## Finding format
- **[BLOCKER]** — Incorrect results, data loss, or production outage risk.
- **[SUGGESTION]** — Meaningful performance or readability improvement.
- **[NITPICK]** — Style or minor clarity.

## Correctness checklist

| Issue | What to look for |
|---|---|
| Wrong join type | INNER when LEFT needed — silently drops unmatched rows |
| Fanout on JOIN | Joining to a non-unique key inflates row count — verify grain of both sides |
| Aggregation after fanout | Aggregating after a join that fans out = wrong totals; aggregate in CTE first |
| NULL in aggregates | `SUM(nullable_col)` = NULL if all values are NULL — use `COALESCE` |
| Window frame assumption | Default `RANGE UNBOUNDED PRECEDING` may not match intent — make frame explicit |
| DISTINCT masking bad join | `SELECT DISTINCT` hiding a fanout — find and fix the root cause |
| Division without zero guard | `a / b` without `NULLIF(b, 0)` — divide-by-zero crash in production |

## Performance checklist

| Issue | What to look for |
|---|---|
| Missing partition filter | WHERE clause skips partition key → full table scan |
| Non-sargable filter | `WHERE YEAR(date_col) = 2024` prevents partition pruning — use range comparison |
| Implicit type cast | String vs. int comparison in WHERE bypasses indexes |
| Repeated subquery | Same subquery in SELECT and WHERE — extract to CTE |
| ORDER BY without LIMIT | Sorting a full large table is expensive and almost always unintentional |
| CROSS JOIN without intent | Cartesian product — verify it is deliberate |
| Unbounded window | `OVER ()` with no PARTITION BY on a large table = full sort |

## Readability checklist
- [ ] CTEs used for each logical step (not nested subqueries)
- [ ] CTE names describe their content (`flagged_orders` not `cte2`)
- [ ] Final SELECT is a simple projection ��� all logic lives in CTEs
- [ ] Column aliases on every computed column
- [ ] No `SELECT *` in production queries

## Output format

```
### SQL Review: [query / file name]

[BLOCKER] line N — **Issue** · Recommendation
[SUGGESTION] ...
[NITPICK] ...

**Verdict:** Approve / Request changes
**Correctness risk:** None / Low / High
**Performance note:** [qualitative impact or estimated scan reduction]
```

## Quality bar
- Fanout bugs (wrong-grain JOIN) produce silently wrong results — always BLOCKER
- Missing partition filter on a large table is SUGGESTION minimum; BLOCKER if query runs on > 1B rows in prod
- Never suggest `SELECT *` as a fix — name columns explicitly
- Read 10–15 lines of surrounding context before flagging — the issue location ≠ the fix location
