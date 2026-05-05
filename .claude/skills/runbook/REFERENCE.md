# /runbook — Reference

## Scenario Template

```
### Scenario N: [Name]

**Detection:**
- Alert: [metric] drops below / exceeds [threshold] for [N] consecutive minutes
- Proxy signal: [user-visible indicator]

**Triage:**
1. Check: [specific thing to look at first]
2. Check: [second thing]
3. Check: [third thing — narrow to root cause]

**Mitigation:**
- If [cause A]: [specific action]
- If [cause B]: [specific action]
- Emergency: [kill switch / circuit breaker / rollback procedure]

**Escalation:** Escalate to L2 if not resolved within [N] minutes.

**Post-Incident:**
- Root cause in incident doc
- Add regression eval case for the failing query type
- [System-specific follow-up]
```

## Runbook Header

```
### Incident Runbook: [System Name]
**System:** [description]
**Stack:** [cloud / model provider / orchestration]
**Owner:** [team]
**On-call:** [rotation / contact]
**Last Updated:** [date]
**Escalation Path:** L1 → L2 → L3
```
