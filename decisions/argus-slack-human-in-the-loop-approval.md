# ADR-0049: Slack Block Kit for Human-in-the-Loop Approval Channel

**Date:** 2026-04-29
**Status:** Accepted
**Domain:** [llm] [governance]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

`ApprovalOrchestrator` must notify a merchandiser when a correction is in PROPOSE tier and wait for their decision (approve / reject) before the pipeline continues. The approval channel must:

- Reach merchandisers where they already work (low friction)
- Support structured approve/reject actions without requiring a custom UI
- Be implementable within the POC timeline without new infrastructure
- Deliver the correction context clearly so the merchandiser can make an informed decision

## Decision

Use **Slack Block Kit** as the approval channel. `ApprovalOrchestrator` posts a structured message to a configured channel containing the violation details and proposed correction. Approve and Reject buttons are rendered via Block Kit `actions` blocks. A FastAPI endpoint (`/slack/interactions`) receives the button click payload, resolves the pending approval, and unblocks the pipeline.

The approval state is held in an in-process `_pending` dict (keyed by `action_id`) that bridges the Slack webhook callback to the polling loop in the agent tool.

## Rationale

Merchandisers at the retailer already use Slack as their primary communication tool. Routing approvals to Slack means zero new tool adoption — the merchandiser receives a push notification, reviews the correction in context, and clicks a button without leaving Slack. This is materially lower friction than email, a custom web UI, or a CLI prompt.

Slack Block Kit provides first-class interactive components (buttons, structured text, markdown) without requiring a frontend build. The webhook-based callback pattern is well-understood, OAuth-free for internal workspace apps, and implementable in a single FastAPI route.

## Consequences

### Positive
- Zero new tool adoption for merchandisers — approval happens in existing workflow
- Block Kit renders violation + proposed fix clearly in a structured card
- Webhook callback is stateless — FastAPI endpoint resolves any pending approval by `action_id`
- Works end-to-end in POC with a real Slack workspace and bot token

### Negative / Trade-offs
- Slack bot token (`SLACK_BOT_TOKEN`) and channel ID (`SLACK_CHANNEL_ID`) must be configured and secret-managed
- Approval state held in-process (`_pending` dict) — not durable across server restarts; PROPOSE items in flight at restart are lost
- Polling loop (5s interval, 2min timeout) is a workaround; production should use Agent Engine's durable workflow suspend/resume
- Slack's 3-second interactive response window requires immediate HTTP 200 ack — actual processing must be async

### Risks
- [RISK: HIGH] In-process state loss on restart — any PROPOSE approval waiting at server restart is silently dropped. Acceptable for POC; must be replaced with durable queue (Pub/Sub or Agent Engine workflow) before production.
- [RISK: MED] Slack rate limits — for high PROPOSE volumes, batch or deduplicate notifications
- [RISK: LOW] Channel misconfiguration — merchandiser never sees the approval request; violation silently times out as rejected

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Email approval | Higher friction; no structured approve/reject; no existing email-to-webhook bridge |
| Custom web UI | Build cost exceeds POC timeline; requires auth, hosting, frontend |
| CLI prompt | Blocks the agent process; not viable for async/multi-item workflows |
| Agent Engine durable workflow (suspend/resume) | Correct long-term; requires Agent Engine deployment — deferred to post-POC |
| PagerDuty / Opsgenie | Operations tooling, not merchandiser-facing; wrong audience |

## Related ADRs

| ADR | Relationship |
|-----|-------------|
| [ADR-0046](ADR-0046-argus-adk-multi-agent-orchestration.md) | `ApprovalOrchestrator` is an ADK sub-agent in the orchestrator |
| [ADR-0048](ADR-0048-argus-three-tier-confidence-routing.md) | PROPOSE tier (0.50–0.71) is the trigger condition for this flow |
| [ADR-0050](ADR-0050-argus-adk-tool-dependency-injection.md) | `_pending` and `_poll_interval` DI params make Slack tools testable |

## Implementation Notes

1. Slack app configured with `chat:write` and `commands` scopes; interactive components enabled with `/slack/interactions` as the request URL
2. `app/slack_router.py` — FastAPI router for `/slack/interactions`; registered with `app.include_router()` in `fast_api_app.py`
3. `app/tools/slack_approval.py` — `post_approval_request()` and `poll_for_decision()` tools; both wrapped as `async` + `run_in_executor` to avoid blocking the ADK event loop
4. `_pending: dict[str, str | None]` holds action_id → decision; injected as `_pending` DI param for unit tests
5. Polling interval and timeout configurable via `_poll_interval` DI param (default 5s, timeout 120s for tests)
6. Production path: replace polling loop with Agent Engine `workflow.suspend()` / `workflow.resume()` on callback
7. Block Kit message includes: violation rule, field, original value, proposed correction, confidence score, and tier label
