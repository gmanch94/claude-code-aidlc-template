# ADR-0048: Three-Tier Confidence-Based Action Routing (AUTO / PROPOSE / FLAG)

**Date:** 2026-04-29
**Status:** Accepted
**Domain:** [llm] [governance]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

After `CorrectionResolverAgent` retrieves similar past corrections and computes a confidence score, the system must decide whether to apply the correction automatically, route it to a human for approval, or escalate without applying a fix. This routing decision determines trust scope — how much authority Argus has to act autonomously versus when human judgment is required.

A binary AUTO / MANUAL split would either over-automate (unsafe) or under-automate (defeats the purpose). The system needs a graduated response that matches confidence level to action authority.

## Decision

Implement three action tiers mapped to confidence score ranges:

| Tier | Confidence | Action |
|------|-----------|--------|
| **AUTO** | ≥ 0.72 | Apply correction immediately; log; notify |
| **PROPOSE** | 0.50 – 0.71 | Post to Slack for merchandiser approval; wait for click |
| **FLAG** | < 0.50 | Stop pipeline; escalate to manual review; no write |

Thresholds are environment-configurable, not hardcoded. Initial values are conservative — start low on AUTO, raise as correction history grows and approval rates validate the scoring.

The orchestrator routes by reading the `tier` field returned by `CorrectionResolverAgent`. No LLM judgment is applied at the routing step — tier assignment is deterministic from the confidence score.

## Rationale

Three tiers balance automation velocity against risk:

- **AUTO** is only triggered when evidence from past corrections is strong and consistent. The threshold (0.72) means the system has seen highly similar, approved corrections before.
- **PROPOSE** captures the middle ground where a correction is plausible but not proven — surfaces it to a human who can approve with one click rather than drafting a fix from scratch.
- **FLAG** is the safety valve: when the system lacks evidence, it escalates rather than guesses. A wrong auto-correction in a product catalog has downstream pricing, search, and fulfillment consequences.

Deterministic routing (not LLM-decided) prevents the orchestrator from rationalizing a tier upgrade on ambiguous inputs.

## Consequences

### Positive
- Humans remain in the loop for all uncertain corrections — governance by design
- AUTO tier creates a scalable path: as correction history grows, more items graduate from PROPOSE to AUTO without code changes
- FLAG tier is an explicit safety net — unknown violations never silently pass
- Configurable thresholds allow tuning per violation type or category without code changes

### Negative / Trade-offs
- Initial deployments with sparse history will see high FLAG rates — requires synthetic seed data
- PROPOSE tier creates approval queue load; merchandisers must be trained on the Slack workflow
- Single global threshold; category-specific tuning (e.g., lower AUTO bar for price anomalies) requires future work

### Risks
- [RISK: MED] Threshold miscalibration early on — monitor AUTO approval rate vs. merchandiser override rate; adjust thresholds if >5% of AUTOs are reversed
- [RISK: LOW] PROPOSE queue saturation if confidence scoring is too conservative — track PROPOSE volume and bump AUTO threshold if queue grows unsustainably

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Binary AUTO / MANUAL | Too coarse — forces either over-automation or no automation at launch |
| Four tiers (ADD FLAG_SUGGEST) | Proposal had FLAG_SUGGEST (weak match with suggestion) — collapsed into PROPOSE to reduce orchestrator complexity; suggestion included in PROPOSE payload |
| LLM decides tier | Non-deterministic routing; governance risk; harder to audit why a correction was auto-applied |
| Per-category thresholds | Correct long-term; deferred — requires enough per-category history to calibrate meaningfully |

## Related ADRs

| ADR | Relationship |
|-----|-------------|
| [ADR-0046](ADR-0046-argus-adk-multi-agent-orchestration.md) | Routing logic lives in orchestrator instruction prompt |
| [ADR-0047](ADR-0047-argus-bigquery-vector-search-rag.md) | BQ retrieval produces the confidence score that drives tier assignment |
| [ADR-0049](ADR-0049-argus-slack-human-in-the-loop-approval.md) | PROPOSE tier triggers the Slack approval flow |

## Implementation Notes

1. Confidence computation in `app/tools/confidence_scorer.py` — inputs: `matches_json`, `field_name`
2. Tier assignment: `AUTO` if score ≥ 0.72, `PROPOSE` if ≥ 0.50, else `FLAG`
3. Thresholds read from env vars (`ARGUS_AUTO_THRESHOLD`, `ARGUS_PROPOSE_THRESHOLD`) — default 0.72 / 0.50
4. Orchestrator instruction encodes routing explicitly: "Do NOT call approval_orchestrator for AUTO tier"
5. `CatalogWriterAgent` called only for AUTO (with synthetic approval JSON) and PROPOSE-approved paths
6. Eval must cover all three tier paths — see `tests/eval/evalsets/`
7. Audit log records `tier` and `confidence_score` on every correction record for retrospective threshold tuning
