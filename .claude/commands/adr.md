# Skill: /adr — Architecture Decision Record

## Trigger
User runs `/adr` followed by a decision to document, or a description of a choice that was made.

## Behavior
1. Ask (if not provided):
   - What decision was made (or needs to be made)?
   - What alternatives were considered?
   - What constraints drove the choice (latency, cost, team expertise, existing stack)?
   - What are the known trade-offs or risks?
2. Draft an ADR following the format below
3. Propose a filename and location (e.g., `decisions/ADR-NNNN-short-title.md`)
4. Ask for confirmation before writing to disk

## Output format

```markdown
# ADR-NNNN: [Short title]

**Status:** Proposed | Accepted | Superseded by ADR-XXXX
**Date:** [YYYY-MM-DD]
**Domain:** [area — e.g., data, auth, infra, api, testing]

---

## Context

[What problem exists? Why is a decision needed now? What constraints apply?
1–3 paragraphs. No solution here — just the problem space.]

## Decision

[What was decided, in one clear sentence. Then the detail.]

## Rationale

[Why this option over the alternatives? Number the reasons. Be specific — cite latency numbers, cost bands, team constraints, whatever actually drove the call.]

1. [Reason one]
2. [Reason two]
3. [Reason three]

## Consequences

### Positive
- [What improves]
- [What becomes easier]

### Negative / Trade-offs
- [What gets harder]
- [What you give up]
- [Ongoing maintenance burden]

## Alternatives considered

| Option | Rejected because |
|--------|-----------------|
| [Option A] | [Specific reason — not "didn't fit"] |
| [Option B] | [Specific reason] |

## Risks not fully mitigated

- [RISK: HIGH/MED/LOW] [What could go wrong that this decision doesn't fully address]
```

## Quality bar
- Context section must not mention the solution — it's the problem space only
- Rationale must be specific: if the reason is "cost," say what the cost difference is
- Alternatives must have real reasons for rejection — "didn't investigate" is a valid honest answer
- At least one negative consequence — no decision is trade-off-free
- Status starts as "Proposed" until the team confirms — don't mark "Accepted" on first draft
