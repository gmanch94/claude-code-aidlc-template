# Skill: /tradeoff — Structured Tradeoff Analysis

## Trigger
User runs `/tradeoff` followed by a decision, approach, or "should we X or Y."

## Behavior
1. Identify the 2–4 realistic options (ask if only one is stated — a tradeoff requires alternatives)
2. For each option: concrete pros, concrete cons, failure mode (what breaks when it goes wrong), best-fit scenario
3. Give a recommendation with the specific constraint that drives it
4. Flag the assumption that would reverse the recommendation — so the user knows when to revisit

## Output format

### Tradeoff: [decision]

**Options compared:** [A] vs. [B] (vs. [C])

---

#### [Option A]
**Pros:** [specific — avoid "simpler" without saying simpler than what]
**Cons:** [specific — avoid "slower" without saying slower by how much]
**Failure mode:** [what breaks in production when this goes wrong]
**Best fit:** [the scenario where this is clearly the right call]

#### [Option B]
[same structure]

---

**Recommendation:** [option] — [one sentence: the specific reason this wins given the current constraints]

**Key constraint:** [the assumption that, if it changed, would flip the recommendation]

**What I'd need to know to change this recommendation:** [concrete — e.g., "if latency SLA tightens to < 50ms" or "if team grows past 5 engineers"]

## Quality bar
- Never recommend without naming a constraint — "it depends" with no constraint is not useful
- Failure mode must be concrete — "it breaks" is not a failure mode; "cache stampede on cold start after deploy" is
- If the options are not actually comparable (different problem spaces), say so before proceeding
- If only one option was given, ask for at least one alternative before generating the analysis
