# /cost-optimize — Reference

## Model pricing (as of 2026-05 — verify at anthropic.com/pricing)

| Model | Input ($/MTok) | Output ($/MTok) | Cache write ($/MTok) | Cache read ($/MTok) |
|---|---|---|---|---|
| Claude Opus 4.7 | $15.00 | $75.00 | $18.75 | $1.50 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $3.75 | $0.30 |
| Claude Haiku 4.5 | $0.80 | $4.00 | $1.00 | $0.08 |

Batch API: 50% discount on input + output. Cache is not discounted via Batch API.

## Prompt caching break-even

At Sonnet 4.6 rates, for a 10K-token system prompt:
- Cache write: $0.0375 (one-time per 5-min TTL window)
- Cache read: $0.003 per request
- Non-cached input: $0.030 per request
- **Break-even: 1.4 requests per TTL window** — almost always worth enabling

Rule of thumb: cache any stable block > 1024 tokens that is reused > 2× within 5 minutes.

## Workload × model tier matrix

| Workload | Haiku | Sonnet | Opus |
|---|---|---|---|
| Simple classification | ✅ preferred | OK | Overkill |
| Extraction / summarization | ✅ if quality OK | Default | Overkill |
| Code generation (simple) | OK | ✅ preferred | Overkill |
| Complex reasoning / multi-step | No | ✅ preferred | If Sonnet fails |
| Agentic loops | No | ✅ preferred | Last resort |
| Creative / long-form | No | OK | ✅ if quality gap |
| Real-time chat < 500ms | ✅ preferred | OK | No |

## Batch API eligibility

**Eligible (async, user not waiting):**
- Nightly document processing
- Eval dataset runs
- Bulk classification / tagging
- Offline summarization pipelines
- Training data generation

**Not eligible:**
- User-facing chat
- Interactive agentic loops
- Streaming responses

## Common over-spend patterns

| Pattern | Waste | Fix |
|---|---|---|
| Opus for every request | 5–25× vs. Sonnet | Tier down; add quality gate |
| Large system prompt without caching | 60–80% waste on eligible tokens | Enable prompt caching |
| No `max_tokens` set | Paying for unused output budget | Set per-task ceiling |
| Synchronous batch jobs | Paying 2× vs. Batch API | Move eligible jobs to Batch API |
| Re-embedding unchanged documents | Redundant cost | Cache embeddings; embed diffs only |
| Opus in agentic loops | 5–25× per loop iteration | Sonnet for tool calls; Opus only for planning step |
