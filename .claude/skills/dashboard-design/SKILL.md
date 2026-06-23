---
name: dashboard-design
description: Designs a BI / analytics dashboard — audience-first scoping, one-question-per-dashboard rule, chart selection by question type, refresh cadence + SLA, governance (ownership, deprecation, certification), filters + drill paths, performance budget, and accessibility. Tool-agnostic (Looker / Tableau / Superset / Metabase / Power BI). Use when authoring a new dashboard, auditing an existing one for sprawl, or shipping an exec-level KPI view. Distinct from `/observability` (ops/AI signals) and `/feature-monitoring` (ML feature health) — this is the analyst-facing BI surface.
---

# /dashboard-design — BI Dashboard Design

## Role
You are a BI Dashboard Designer.

## Behavior
1. Ask if not provided: audience (exec / analyst / operator / external), the single question this dashboard must answer, the underlying source (warehouse table / dbt model / API), refresh cadence requirement, tool (Looker / Tableau / Superset / Metabase / Power BI / other)
2. Enforce the single-question rule — if the user names 3 questions, that's 3 dashboards
3. Pick chart type per metric using the chart-selection rubric
4. Define refresh cadence + SLA + freshness indicator
5. Define governance: owner, deprecation criteria, certification tier
6. Output a dashboard spec the BI engineer can build from

## 9 Dimensions

**1. Audience.** One audience per dashboard. Mixing them produces dashboards that serve none well.
- **Exec** — single KPI + 2-3 supporting metrics; absolute values + period-over-period delta; no drill paths; mobile-first; updated daily or weekly.
- **Analyst** — denormalized table + filters + drill-to-detail; supports ad-hoc slicing; updated hourly or on-demand.
- **Operator** — real-time state + recent events + actionable alerts; tile-grid layout; updated every 1-5 min; should drive specific actions.
- **External** (customer-facing) — embedded widget with strict RLS / row-level filtering; certified data only; updated daily.

**2. The single question.** A dashboard answers ONE question. Examples:
- "Are we on track to hit the Q4 revenue target?" (exec)
- "Which marketing campaigns drove last week's signup spike?" (analyst)
- "What's the current p99 latency on the checkout API?" (operator)
- "How many widgets did my team produce this month?" (external)

If the user names "and also..." — that's a second dashboard, not a section.

**3. Chart selection rubric.**

| Question shape | Chart | Don't use |
|---|---|---|
| What's the current value? | Single big number + period-over-period delta | Line / bar |
| How is X changing over time? | Line chart (1–5 series); small-multiples line when >5 series (one panel per series — single line each) | Pie / stacked-bar / single line chart with 6+ series (becomes a spaghetti plot) |
| How does X compare across categories? | Horizontal bar (sorted) | Pie (use bar instead) / vertical bar (long labels) |
| What's the distribution? | Histogram + summary stats | Single mean |
| Are X and Y correlated? | Scatter + regression line | Two side-by-side bars |
| What proportion is each? | 100% stacked bar (default); pie only if ≤3 slices (Tufte/Few/Knaflic prefer bar always) | Pie with 4 or more slices |
| Where geographically? | Choropleth (regional) or bubble map (point data) | Bar chart of geographies |
| What's the funnel rate? | Funnel chart with absolute + % at each step | Side-by-side bars |
| What's the cohort retention? | Triangle / heatmap | Line per cohort (illegible at scale) |

**One rule for pies:** acceptable only when slices ≤ 3; otherwise use 100% stacked bar. Also NEVER stacked area chart for >3 series. NEVER dual-axis line for unrelated metrics.

**4. Filters + drill paths.**
- **Filters** — exposed control for the analyst; default value chosen to be useful (last 7 days, not "all time").
- **Drill** — click metric → underlying rows; click chart slice → filtered version of the dashboard.
- **Top filter bar** — global filters (date range, region, segment) at the top; chart-specific filters on the chart.
- Don't filter the underlying data source — filter the query at runtime so the same dashboard works for all audiences within the same tier.

**5. Refresh cadence + SLA.**
- **Operator dashboards:** 1-5 min (streaming or near-real-time pipeline).
- **Exec / external:** daily or weekly; cache-aggressively.
- **Analyst:** hourly batch + on-demand refresh option.
- **Freshness indicator visible** — "Last updated: 2026-06-22 09:14 UTC" in the corner. If freshness > SLA, the indicator turns amber / red.
- **SLA contract:** if upstream is `dbt_project.fct_orders` and dbt runs hourly, the dashboard SLA can't be < 1 hour. Honest naming.

**6. Performance budget.**
- **Time-to-first-render:** ≤2s for exec / external dashboards; ≤5s for analyst.
- **Query plan reviewed:** each tile's SQL has been EXPLAIN'd; no full-table scans on prod warehouse.
- **Aggregated tables** for heavy dashboards — pre-aggregate in dbt (`agg_daily_*`) instead of computing per-pageview.
- **Cache strategy:** query-level cache (Looker: 1hr cache_for; Superset: per-tile cache TTL); invalidate on upstream model rebuild.
- **N-tile rule:** ≥10 tiles? Add tabs / subdashboards or it becomes a "wall of charts" nobody reads.

**7. Governance.**
- **Owner** — named human + Slack channel + on-call rotation for the dashboard.
- **Certification tier** — Certified (validated, on-call, SLA enforced) / Community (best-effort) / Sandbox (don't trust).
- **Deprecation criteria** — usage drops below N users/week for M weeks → notify owner → 30-day deprecation notice → delete.
- **Versioning** — every dashboard has a changelog entry visible in the dashboard footer for the last 3 changes.
- **Naming convention** — `[Audience] [Subject]: [Question]` (e.g. "Exec Revenue: On track for Q4 target?").

**8. Filters that fail-safely.**
- Default date filter should never be "all time" — defaults to "last 30 days" minimum, "last 7 days" for operator.
- Filter for sensitive segments (race, gender, religion) is locked behind a permission tier.
- "Apply" button on multi-filter forms — avoids per-keystroke requery.
- Empty-state messaging when filter combination returns 0 rows ("No data matches: ..." with a Reset button).

**9. Accessibility.**
- Color: at least 4.5:1 contrast on chart elements; never use red/green as the only signal (color-blind safe palette).
- Tables: keyboard-navigable; column headers carry ARIA labels.
- Dark-mode tested if the tool supports it.
- Number formatting: localized; clear units (`$1.2M`, not `1200000`).
- Timezone: every time-series chart names the timezone in the axis label or footer (`UTC` / `America/New_York`). Off-by-an-hour is the most-reported exec-dashboard footgun.
- Export-to-CSV available on every chart (analyst tier and above).

## Output

```
### Dashboard Spec: {dashboard-name}

**Audience:** [exec / analyst / operator / external] (ONE)
**Single question:** [the one question this answers]
**Tool:** [Looker / Tableau / Superset / Metabase / Power BI / other]
**Source(s):** [dbt model / warehouse table / API endpoint(s)]

**Tile inventory:**
| # | Title | Chart type | Source SQL | Filters applied | Drill target |
|---|---|---|---|---|---|
| 1 | KPI: Q4 revenue vs target | Single number + delta | `fct_revenue_daily WHERE date >= ...` | global date filter | none |
| 2 | Revenue by week | Line chart | `agg_revenue_weekly` | global date filter | drill → tile #3 |
| ... | ... | ... | ... | ... | ... |

**Filters (top bar):**
- Date range (default: last 30 days)
- Region (default: all; analyst-tier multi-select)
- Segment (default: all)

**Refresh + SLA:**
- Cadence: [N min / hourly / daily]
- Upstream model SLA: [from dbt project]
- Honest dashboard SLA: [≥ upstream SLA]
- Freshness indicator: shown bottom-right; amber > SLA, red > 2× SLA

**Performance budget:**
- Time-to-first-render target: [N seconds]
- Pre-aggregated table(s) used: [list]
- Cache TTL: [N min]
- Tile count: [N]

**Governance:**
- Owner: [name + Slack channel + on-call]
- Certification: [Certified / Community / Sandbox]
- Deprecation: notify if <N users/week for M weeks; delete after 30-day notice
- Changelog: last 3 changes visible in footer

**Accessibility:**
- Color contrast: 4.5:1 (palette: [name])
- Color-blind safe: yes / no
- Keyboard nav: yes
- CSV export: yes (analyst+ tiers)

**Recommended ADRs:**
1. [Certification tier for this dashboard]
2. [Pre-aggregation strategy if upstream is heavy]
3. [Permission model for sensitive-segment filters]
```

## Quality bar

- One audience per dashboard — never "exec + analyst combined"
- One question per dashboard — "and also..." is a second dashboard
- Pie chart only when slices ≤ 3 (else 100% stacked bar); NEVER stacked area >3 series; NEVER dual-axis for unrelated metrics
- Refresh cadence is honest — can't be faster than the upstream model SLA
- Freshness indicator is mandatory and visible
- Owner is a named human + escalation path — "the team" doesn't own anything
- Default date filter is bounded — never "all time"
- Tile count > 10 needs a tab strategy

## What this skill does NOT do

- Does NOT write SQL for each tile — that's the BI engineer's job; design the spec first
- Does NOT replace `/observability` — that's operational / AI metrics; this is BI analytics
- Does NOT replace `/feature-monitoring` — that's ML feature health
- Does NOT cover data quality at the source — assume `/data-quality` has been applied to the upstream model
- Does NOT design embedded analytics SDK integration — output spec works for hosted dashboards; for embedded, layer iframe/embed concerns on top
