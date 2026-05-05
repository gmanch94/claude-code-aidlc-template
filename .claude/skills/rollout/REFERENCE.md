# /rollout — Reference

## Full Phase Gate Table

### Rollout Plan: [Feature Name]
**Feature:** | **Risk Tier:** | **Owner:** | **Approver:**

| Phase | Entry Criteria | Exit Criteria | Rollback Trigger |
|-------|---------------|--------------|-----------------|
| Shadow | Eval framework ready; runbook drafted | Eval ≥ threshold; no HIGH findings | Any HIGH finding |
| Internal | Shadow exit met | Metrics stable N days | Error rate > threshold |
| Canary | Internal exit met | Error/latency/quality within bounds | Error rate > threshold OR quality drop |
| Limited GA | Canary exit met | Cost/request within budget; no anomalies | Cost > budget OR quality drop |
| Full GA | Limited GA exit met | Sustained metrics; runbook validated | Rollback per runbook |

## Rollback Procedure
For each phase: trigger condition, who executes, execution time, user notification plan.

## Observability Required
- Quality metric (eval score or proxy) — per phase
- Latency p50/p95 — alert threshold defined
- Error rate — alert threshold defined
- Cost per request — alert on > 20% regression vs. canary baseline
- User satisfaction signal (thumbs, corrections, abandonment) — if available
