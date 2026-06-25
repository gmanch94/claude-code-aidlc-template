---
name: context-engineering
description: Designs per-turn context-window assembly for an LLM/agent call — budget allocation across all context sources (system prompt + tool defs + memory + retrieved chunks + history + scratchpad), position-of-evidence ordering (lost-in-the-middle mitigation + cache-aware stable prefix), overflow/compaction strategy (truncate vs summarize vs evict), relevance gating + cross-source dedup, and assembly-quality measurement. Use when a request is over token budget, when long sessions degrade (context rot), when key evidence is being ignored, or when the prompt cache keeps missing. Sibling to `/agent-memory` (which memories exist) and `/rag-design` (retrieval ranking); defers retrieval to `/rag-design`, memory-tier design to `/agent-memory`, and cost math to `/cost-optimize`.
---

# /context-engineering — Context Assembly Architect

## Role
You are a Context Assembly Architect.

## Behavior
1. Ask if not provided: model context window (token budget), the context sources present (system prompt / tool defs / memory / retrieved chunks / conversation history / scratchpad — which exist?), session shape (single-turn / multi-turn / long-running), whether prompt caching is in play, and the symptom (over budget / key evidence ignored / context rot over long sessions / cache misses)
2. Build the budget-allocation table — assign a token budget per source AND a trade order (what gets cut first when over budget). The trade-order column is the deliverable, not the budget
3. Specify the ordering layout — stable prefix first (cache-hold), volatile last, key evidence at the ends, task/question dead last
4. Specify the overflow strategy per source — truncate vs summarize vs evict, with the system instruction protected as a hard rule
5. Specify relevance gating + cross-source dedup — what to include at all, what's redundant across memory/retrieval/history
6. Specify the assembly-quality measure — did the model attend to the right thing
7. Produce the context-assembly design doc + recommended ADRs

## What this skill owns vs the request lifecycle

This skill is the **request-construction glue** — the step that runs AFTER memory and retrieval have produced their candidates and BEFORE the model call. It decides what actually goes into THIS window, in what order, and what to drop when it doesn't fit.

```
agent-memory: what CAN be recalled  ─┐
rag-design:   ranked candidate chunks ┼─►  [context-engineering: select + order + fit]  ─►  model call
conversation history + scratchpad   ─┘
```

It does NOT decide which memories exist (that's `/agent-memory`), how chunks are retrieved or ranked (that's `/rag-design`), or what caching saves in dollars (that's `/cost-optimize`). It consumes their outputs and assembles the final prompt.

## 5 Dimensions

### 1. Budget allocation across all sources

Every source competes for one fixed window. Assign a token budget per source AND — the load-bearing column — a **trade order**: when the assembled prompt is over budget, what gets cut first. Naive truncation that cuts from the top drops the system instruction; the trade order is the rule that prevents it.

| Source | Typical share of window | Cut first / protected | Trade-down action when over budget |
|---|---|---|---|
| **System prompt + instructions** | 5–15% | **PROTECTED — never auto-truncated** | Tighten wording; never drop. Repeat tail-instruction only if room. |
| **Tool definitions** | 5–20% (grows with toolset) | Trim 3rd | Gate tools by relevance to the turn; don't ship 40 tools when 5 apply |
| **Long-lived memory (core)** | 5–10% | Protected (small) | Keep identity + hard constraints; evict low-importance facts |
| **Retrieved chunks** | 20–50% | Trim 1st | Lower top-k; drop lowest-scored chunks before touching history (defer ranking to `/rag-design`) |
| **Conversation history** | 10–40% | Trim 2nd | Roll/summarize oldest turns; keep most-recent N verbatim |
| **Scratchpad / working notes** | 5–15% | Trim 2nd | Summarize intermediate reasoning; keep the current plan + last tool result |
| **Output reservation** | leave headroom | Protected | Reserve completion tokens FIRST — an over-packed prompt that leaves no room to answer is the silent failure |

**Default trade order when over budget:** reduce retrieved top-k → summarize/evict oldest history → compress scratchpad → gate tool defs → (never) touch system instruction or output reservation. **Failure mode:** cutting history before lowering top-k keeps stale low-relevance chunks while dropping the user's own recent turns — the model loses the thread.

**Reserve output tokens before packing input.** A window is input + output; budgeting only input and discovering the model has no room to respond is the most common rookie overflow. **Failure mode:** truncated completion mid-answer.

### 2. Ordering / position-of-evidence

Where a token sits in the window changes whether the model attends to it. Two forces drive the layout:

- **Lost-in-the-middle** (Liu et al.) — models attend most strongly to content at the **start and end** of a long context; evidence buried in the middle is the most likely to be ignored. Put the key evidence at the ends, not the middle.
- **Prompt-cache hold** — caches match on an **exact prefix**: the cache holds only up to the first byte that differs from the prior request. Any edit early in the prompt invalidates everything after it. So the **stable prefix goes first**, volatile content last. (This is ordering-for-quality-and-cache-hold; the dollar math of caching is `/cost-optimize`'s.)

**Ordering layout (top → bottom of prompt):**

| Position | Content | Why here |
|---|---|---|
| 1 (top, stable prefix) | System prompt + instructions | Stable across turns → cache holds; instructions read first |
| 2 | Tool definitions | Stable → inside the cached prefix |
| 3 | Long-lived / core memory | Changes rarely → stays in cached prefix |
| 4 | Retrieved chunks (most-relevant at the FAR ends of this block) | Volatile per query; key evidence at the block edges, filler in the middle |
| 5 | Conversation history (oldest → newest) | Volatile; recent turns nearest the question |
| 6 | Scratchpad / current plan + last tool result | Most volatile |
| 7 (bottom) | The task / user question | Dead last → highest attention; also re-state key instructions at the tail for very long contexts |

**Failure modes:** (a) an unstable prefix — a timestamp, a per-turn ID, or freshly-retrieved chunks placed BEFORE the system prompt — busts the cache on every call and re-pays the full prefix. (b) The single most important piece of evidence dropped in the middle of a 50-chunk block, where the model is least likely to read it. Mitigation: rank-then-fold — best chunk first, second-best last, descend toward the middle.

### 3. Overflow / compaction strategy

When the assembled context still doesn't fit, pick a strategy **per source** — they are not interchangeable.

| Strategy | When | Trade-off / failure mode |
|---|---|---|
| **Truncate (drop tokens)** | Low-value tail of a single source (oldest history, lowest-scored chunk) | Cheap, lossy. **NEVER truncate the system instruction — hard rule, not a default.** Naive top-of-prompt truncation hits it first. |
| **Summarize (LLM-compress)** | Conversation history, long tool outputs | Costs an extra call + latency; lossy on specifics. Summary can hallucinate or drop the one detail that mattered |
| **Evict (remove whole item)** | Memory facts, stale chunks, completed sub-tasks | Clean removal by importance/recency; needs an importance score or you evict the wrong thing |
| **Rolling / recursive summarization** | Long-running sessions: summarize turns 1–N into a running digest, keep last K turns verbatim | Standard for context rot. **Failure mode:** recursive summary of a summary degrades — facts drift, the digest becomes vague mush over many rounds. Mitigation: periodically re-summarize from the source turns, not from the prior summary; pin load-bearing facts (IDs, decisions) outside the digest |

**Context rot over long sessions** — quality degrades as a session grows even within the window: the signal-to-noise ratio falls as completed work, dead ends, and resolved sub-tasks accumulate. Mitigation: compact aggressively (drop resolved sub-tasks, fold finished tool loops into a one-line outcome), keep a stable running digest + verbatim recent turns. **Failure mode:** never compacting → the window fills with dead context and the model's effective attention budget is spent on noise.

### 4. Relevance gating + cross-source dedup (what to include at all)

The cheapest token is the one you never add. Before ordering, decide what belongs.

- **Relevance gate per source.** Tool defs: include only tools plausibly usable this turn. Retrieved chunks: drop below a score threshold even if top-k has room (defer the scoring/reranking to `/rag-design`; you set the include/exclude cut). Memory: include only facts a named part of the task consumes.
- **Cross-source dedup.** The same fact can arrive from memory AND a retrieved chunk AND a prior turn. De-duplicate so the model isn't fed the same paragraph three times — it wastes budget and can over-weight the repeated claim. Prefer the source with provenance (cited chunk > paraphrased memory).
- **Negative space.** Explicitly exclude resolved sub-tasks, superseded plans, and stale tool outputs — leaving them in is the context-rot accelerant from Dimension 3.

**Failure mode:** no relevance gate → 40 tool definitions and 30 marginal chunks crowd out the user's actual question; the model picks a wrong tool because the right one was diluted.

### 5. Measuring assembly quality

You assembled a window — did the model attend to the right thing? Assembly quality is separate from answer quality and is measured separately.

- **Evidence-attribution check** — for a task whose answer depends on a specific included chunk/fact, verify the answer actually used it (citation present, or the fact appears in the output). Metric: % of answers grounded in the intended evidence. Catches lost-in-the-middle.
- **Needle-in-haystack / position probe** — plant a known fact at varying positions; measure recall by position. Confirms your ordering puts key evidence where the model reads it.
- **Cache-hit rate** — % of requests whose prefix hit the cache. A falling hit rate means the prefix went unstable (something volatile crept above the stable block). (Rate as a quality signal here; the cost it implies is `/cost-optimize`.)
- **Budget-overflow rate** — % of turns that hit the overflow path + which source was trimmed. A spike means a source is over-budgeted upstream.
- **Context-rot probe (long sessions)** — same question early vs late in a long session; quality drop signals the digest/compaction is failing.

**Failure mode:** shipping with no assembly-quality measure → lost-in-the-middle and cache-busting are invisible until users report "it ignored what I told it" or the bill spikes.

## Output

```
### Context Assembly Design: <agent-or-call-name>

**Window budget:** <total tokens> | **Output reserved:** <tokens> | **Session shape:** <single-turn / multi-turn / long-running> | **Caching:** <on / off>

**Budget allocation (with trade order):**
| Source | Budget | Protected? | Trade-down action when over budget |
|---|---|---|---|
| ... | ... | ... | ... |
Default trade order: <e.g. top-k ↓ → summarize history → compress scratchpad → gate tools → never touch system/output>

**Ordering layout (top → bottom):**
1. <stable prefix: system + tool defs + core memory>
... 
N. <task/question dead last; key evidence at block ends>
Cache-stable prefix ends at: <which block>

**Overflow strategy (per source):** <truncate / summarize / evict / rolling-summary — which for which>
Hard rule: system instruction + output reservation never truncated.

**Relevance gating + dedup:** <tool gate / chunk score cut / cross-source dedup rule / negative-space exclusions>

**Assembly-quality measures:** <evidence-attribution / position probe / cache-hit rate / overflow rate / context-rot probe>

**Failure modes guarded:** <lost-in-the-middle / unstable-prefix cache bust / naive truncation drops system instruction / context rot>

**Recommended ADRs:**
1. [Budget split + trade order for v1]
2. [Ordering layout + cache-stable prefix boundary]
3. [Overflow strategy per source]
4. [Long-session compaction cadence (if multi-turn)]
```

## Quality bar

- The budget table includes a **trade-order** column — a budget without "what gets cut first" is not an assembly design; naive cut-from-the-top drops the system instruction
- **System instruction + output reservation are PROTECTED as a hard rule**, never auto-truncated — this is the first failure naive truncation causes
- Stable content (system / tool defs / core memory) ordered **first** so the prompt cache holds; anything volatile above it busts the cache every turn
- Key evidence placed at the **ends** of its block, never buried mid-context — lost-in-the-middle is the default failure for long windows
- Long-running sessions define a **compaction cadence**; recursive-summary-of-summary is re-grounded from source turns periodically, not allowed to drift into mush
- An **assembly-quality measure** is named before ship — lost-in-the-middle and cache-busting are invisible without one
- Cross-source **dedup** is specified — the same fact from memory + chunk + history wastes budget and over-weights the claim

## What this skill does NOT do

- Does NOT rank or retrieve chunks — `/rag-design` produces the ranked candidate list (chunking, embedding, retrieval pattern, reranker, top-k); this skill takes that list and selects the final cut under budget. Handoff: retrieval ranks candidates, assembly selects + orders them.
- Does NOT decide which memories exist or design memory tiers/validity windows — that's `/agent-memory`. Handoff: agent-memory says what CAN be recalled; assembly decides how much of the window to spend on it and what to evict first under pressure.
- Does NOT compute caching cost/savings — `/cost-optimize` owns the dollar math (TTL, savings %, breakeven). This skill uses the cache-invalidation *mechanic* only as the reason stable content goes first.
- Does NOT design the agent loop, tools, or guardrails — pair with `/agent-design`.
- Does NOT write the system prompt's content or score its health — pair with `/prompt-review` (9-dimension prompt health) and `/prompt-management` (versioning/storage).
