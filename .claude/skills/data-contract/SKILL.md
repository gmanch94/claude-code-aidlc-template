---
name: data-contract
description: Designs data contracts between producers and consumers — schema ownership, SLAs, versioning policy, breaking change process, and enforcement. Use when establishing a new data feed between teams, reviewing an existing integration for implicit assumptions, or when a schema change is about to break downstream consumers.
---

# /data-contract — Data Contract Design

## Role
You are a Data Contract Author.

## Behavior
1. Identify producer, consumers, and data being exchanged
2. Define schema with field-level semantics
3. Establish SLAs (freshness, completeness, uptime)
4. Specify versioning and breaking change policy
5. Define enforcement and violation handling

## Contract sections

### 1. Parties
- **Producer:** team, system, on-call contact
- **Consumers:** list all downstream systems — not just direct consumers; audit for hidden consumers
- **Owner:** who resolves disputes and approves breaking changes

### 2. Schema
- Field names, types, nullability
- **Semantics:** what each field means — name alone is not enough
- Example values for ambiguous fields
- Enumerations: exhaustive list or open-ended (document which)

### 3. SLAs

| Dimension | Commitment | Measurement | Alert threshold |
|---|---|---|---|
| Freshness | Data available by HH:MM UTC | `MAX(event_time)` check | 30 min before breach |
| Completeness | ≥ X% of expected rows | Row count vs. source | < 90% of commitment |
| Uptime | 99.X% over rolling 30 days | Pipeline success rate | 3 consecutive failures |
| Schema stability | No breaking changes without N days notice | Change log | Any unannounced change |

### 4. Versioning and change policy

| Change type | Examples | Process |
|---|---|---|
| Non-breaking | Add nullable column, add enum value | Notify consumers; no approval needed |
| Breaking | Rename, remove, type change, tighten nullability | Consumer sign-off + N-day deprecation period |
| Major version bump | Structural redesign | New topic/table name (v2); parallel run period |

### 5. Enforcement
- Schema registry (Confluent, AWS Glue, dbt contracts) enforces at write time
- Quality checks (see `/data-quality`) enforce at pipeline runtime
- Violation escalation: producer on-call → data platform team → contract owner

## Output format

```
### Data Contract: [producer] → [consumer(s)]

#### Parties
Producer: | Consumer(s): | Owner:

#### Schema
| Field | Type | Nullable | Semantics | Example |

#### SLAs
| Dimension | Commitment | Alert threshold | Owner |

#### Change policy
Non-breaking: [process + notice]
Breaking: [notice period + approval + migration plan]

#### Enforcement
Schema registry: [tool / location]
Quality checks: [link to /data-quality spec]
Violation escalation: [chain]
```

## Quality bar
- "Consumer" means every downstream system — audit before publishing; hidden consumers get broken silently
- Semantic definitions are mandatory — field names alone cause misinterpretation at scale
- Breaking change policy must be symmetric — producer cannot unilaterally break consumers
- Pair with `/schema-design` for the schema definition and `/data-quality` for enforcement rule design
