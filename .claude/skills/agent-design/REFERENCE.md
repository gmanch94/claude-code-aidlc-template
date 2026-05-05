# /agent-design — Reference

## Tool Manifest Template

| Tool Name | Description | Inputs | Outputs | Side Effects | Auth Required |
|-----------|-------------|--------|---------|--------------|---------------|
| | | | | None / Reversible / **Irreversible** | |

## Production Readiness Gate

Before production deployment:
- [ ] All irreversible tools have HITL or scope constraints documented
- [ ] Termination conditions defined and tested on representative tasks
- [ ] Max iteration limit set and circuit breaker wired
- [ ] Observability stack instrumented (tool traces, thought traces, step count)
- [ ] Fallback paths tested for each failure mode
- [ ] Tool manifest reviewed for scope creep risk
- [ ] `/threat-model` completed — indirect injection via tool output is HIGH priority
- [ ] `/pii-scan` completed if any tool handles personal data

## Key Risk Register (common agents)

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Agent takes irreversible action without confirmation | HIGH | HITL gate on all irreversible tools |
| Agent loops without terminating | HIGH | Max iteration + circuit breaker |
| Indirect prompt injection via tool output | HIGH | Validate tool outputs before passing to model |
| Scope creep — acts outside intended domain | MED | Scope validation in tool routing |
| Partial state on cancellation | MED | Checkpoint + rollback design |
