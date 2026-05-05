---
name: cost-optimize
description: Analyzes token spend and recommends cost optimizations — model tier selection (Opus/Sonnet/Haiku), prompt caching strategy, batch vs. real-time decisions, and token budget sizing. Use when asked to reduce AI costs, select the right model tier, size a budget, or optimize an LLM-powered feature's spend.
---

# /cost-optimize — AI Cost Optimization

## Behavior
1. Identify workload type and volume
2. Apply model tier decision tree
3. Analyze prompt caching eligibility
4. Evaluate batch vs. real-time trade-off
5. Output prioritized action list with $ impact estimate

## Model tier decision tree

```
< 500ms response time required?
  Yes → Haiku (validate quality first) or Sonnet
  No  → > 60% of input tokens stable across requests?
          Yes → Sonnet + prompt caching (60–80% reduction on cached tokens)
          No  → Complex reasoning / multi-step agentic?
                  Yes → Opus (justified)
                  No  → Sonnet (default)
```

## Quick rules

| Situation | Recommendation | Savings |
|---|---|---|
| Stable system prompt > 1024 tokens | Enable prompt caching | 60–80% on cached tokens |
| Same document analyzed repeatedly | Cache document block | 60–80% on cached tokens |
| Non-time-sensitive batch jobs | Batch API | ~50% |
| Simple classification / extraction | Haiku | 10–20× vs. Sonnet |
| Multi-turn chat with long history | Cache conversation prefix | 60–80% on prefix |
| Agentic loop with tools | Sonnet unless reasoning fails | 3–5× vs. Opus |

## Token budget analysis

For each prompt, classify and measure:
- **System prompt tokens** — caching candidate if > 1024 and stable across requests
- **Context/document tokens** — caching candidate if reused
- **Dynamic tokens** — cannot be cached; minimize here
- **Output tokens** — most expensive; always set explicit `max_tokens`

## Output format

```
### Cost Analysis: [feature / system]

Current: $X/day · Y tokens/request average

#### Model tier recommendation
[model] because [reason]. Est. savings vs. current: $Z/day.

#### Caching opportunities
| Prompt section | Tokens | Cacheable? | Est. savings/day |

#### Batch candidates
[workloads that can tolerate async + 50% discount]

#### Token reduction wins
[specific prompt sections to trim + token estimate]

#### Priority action list
1. [highest ROI] — est. $X/mo savings
2. ...
```

## Quality bar
- Always give $ or % impact — "cheaper" without a number fails
- Caching savings assume > 60% cache hit rate — flag if hit rate unknown
- Haiku recommendation requires a quality threshold check before committing
- Tier-down decisions must include a regression eval — cost wins mean nothing if quality drops
- See REFERENCE.md for pricing table, caching math, and workload × tier matrix
