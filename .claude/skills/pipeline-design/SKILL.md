---
name: pipeline-design
description: Designs data pipeline architecture — batch vs. streaming decision, orchestration pattern, idempotency, backfill strategy, error handling, and SLA. Use when asked to design a new data pipeline, review an existing one, or decide between batch and streaming processing.
---

# /pipeline-design — Data Pipeline Design

## Behavior
1. Identify source, transformation steps, and destination
2. Apply batch vs. streaming decision tree
3. Design orchestration and scheduling
4. Define idempotency and backfill strategy
5. Specify error handling and observability

## Batch vs. streaming decision tree

```
Data freshness requirement?
  > 1 hour acceptable   → Batch (simpler, cheaper, easier to backfill)
  < 1 hour required     →
    Exactly-once + ordering required?
      Yes → Streaming (Kafka/Flink — higher complexity + cost)
      No  → Micro-batch (Spark Structured Streaming, Kinesis — middle ground)
```

## Design checklist

**Ingestion**
- [ ] Source type: API poll / CDC / file drop / event stream / DB query
- [ ] Auth and rate limit handling defined
- [ ] Schema validation at ingestion boundary — fail fast before transformation
- [ ] Backfill mechanism: full reload vs. incremental by watermark

**Transformation**
- [ ] Idempotent: re-running the pipeline produces the same result (no duplicates, no data loss)
- [ ] Watermark or partition key defined for incremental loads
- [ ] Late-arriving data strategy: drop / reprocess / hold for window

**Load**
- [ ] Write mode: overwrite / append / merge (upsert)
- [ ] Partition strategy matches downstream query patterns
- [ ] Downstream consumers notified on schema change (see `/data-contract`)

**Orchestration**
- [ ] DAG dependencies mapped — what must succeed before this runs
- [ ] Retry policy: N retries with exponential backoff; max retry window defined
- [ ] Dead letter queue / failure sink for unprocessable records
- [ ] SLA: expected completion time; alert threshold before breach

## Output format

```
### Pipeline Design: [name]

#### Architecture
Source → [transform steps] → Destination
Mode: Batch / Micro-batch / Streaming
Schedule / trigger: [cron or event]

#### Idempotency
[how re-runs are safe — partition overwrite / upsert key / dedup step]

#### Backfill
[strategy + estimated cost at full history]

#### Error handling
[retry policy + DLQ location + alert owner]

#### SLA
Expected completion: | Alert at: | On-call:

#### Open questions
[schema unknowns, infra decisions, upstream SLA dependencies]
```

## Quality bar
- Every pipeline must be idempotent — "just delete and reload" is not a strategy
- Define the SLA before designing the schedule ��� the schedule serves the SLA
- Backfill cost estimate is required — many designs look cheap per-run but are expensive at full history
- Pair with `/data-quality` for validation rules and `/observability` for monitoring design
