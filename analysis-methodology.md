# OCLC API Analysis — Methodology, Lessons Learned, Advisor Feedback

**Date:** 2026-05-06  
**Scope:** 21 production OCLC APIs across 5 service areas

---

## Methodology

### Phase 1 — Discovery and inventory

**Goal:** Catalogue every production API with primary-source-verified attributes.

1. Fetched the OCLC developer API listing page (`oclc.org/developer/api/oclc-apis.en.html`) via `ctx_fetch_and_index` — kept raw output out of context window
2. Catalogued all 21 APIs by service area: Discovery, Metadata, Management (WMS), Resource Sharing, Licensed Collection
3. For each API, recorded: sandbox availability, auth method, supported operations (CRUD), protocol, access requirement, notable limits
4. For disputed or ambiguous attributes, found and cited a primary source before recording the claim

**Primary sources used:**
- OCLC API listing page (per-API descriptions and access requirements)
- `OCLC-Developer-Network` GitHub organization (OpenAPI specs, auth helpers, circulation API source)
- `OCLC-Developer-Network/prototype-api-docs` (7 OpenAPI YAMLs — used as supporting evidence only; see lessons learned)
- Per-API OCLC documentation pages (fetched individually for Resource Sharing, WMS Circulation, License Manager)
- PyPI and npm (to verify SDK publication status)

### Phase 2 — Shortcomings analysis

**Goal:** Identify and categorize gaps with severity ratings.

1. Grouped findings from inventory into themes: auth fragmentation, sandbox gaps, protocol legacy, functional gaps, access barriers
2. For each shortcoming, wrote: what the problem is, what the impact is on integrators, severity (High / Medium / Low)
3. Separated technical shortcomings (things OCLC engineers could fix) from functional shortcomings (product/business decisions with technical consequence)
4. Used `Grep` across all 5 output files after each edit pass to catch cross-file inconsistencies

### Phase 3 — Recommendations

**Goal:** Prioritized fix list with effort and impact estimates.

1. Mapped shortcomings to fixes; assigned priority tiers:
   - P0: Bugs / production blockers
   - P1: High friction — major integration barriers
   - P2: Developer experience gaps
   - P3: Polish and maintenance
2. Every recommendation required a named trade-off or failure mode — no universally-best options
3. Effort rated Low / Medium / High; Impact rated Low / Medium / High / Critical

### Phase 4 — Executive summary

**Goal:** One-page brief for a technical audience unfamiliar with the full analysis.

1. Synthesized top-5 problems from P0/P1 findings
2. Built service-area score table: sandbox coverage, auth consistency, functional completeness, overall rating
3. Built strategic gaps table comparing OCLC to typical modern API platforms
4. Listed recommended investment order (highest impact / lowest effort first)

### Phase 5 — Options analysis

**Goal:** Multi-option trade-off analysis for the 12 most complex issues.

For each issue: defined the problem, listed 2–4 response options, built a trade-off table (effort, risk, impact, precedent), gave a recommended option with failure mode.

### Phase 6 — Verification passes

**Goal:** Ensure all claims are defensible and cross-file consistent.

- Called `advisor()` after each major editing pass
- Grepped all 5 files for any claim that appeared in multiple places before declaring a fix done
- Each advisor call returned specific issues; fixed all flagged issues before the next advisor call

---

## Advisor feedback — what was flagged and fixed

### Round 1 — CRUD claims "inferred from absence"

**Flagged:** Three capability claims lacked primary-source citations:
- WMS Circulation API: operations column said `R, W` but no source for what W covered
- Resource Sharing Request API: "no update or cancel" — cited from absence, not a spec
- License Manager API: "read-only" — same problem

**Fix applied:**
- WMS Circulation: found `OCLC-Developer-Network/prototype-api-docs/wms-circulation` OpenAPI YAML; confirmed exactly 5 endpoints: `GET /pulllist/{branchId}`, `POST mark-pulled`, `POST mark-inventoried`, `POST mark-non-loan-return`, `POST forward-hold` — no checkout/checkin
- Resource Sharing Request: found OCLC API listing text: *"Create new resource sharing requests, obtain lists of requests, and get request details"* — no update/cancel confirmed by what was listed, not by absence
- License Manager: found OCLC API listing text: *"Search, Read, and List institution-specific license details"* — read-only confirmed by enumeration

### Round 2 — "No official SDK" overclaimed

**Flagged:** Initial claim said no SDK existed. GitHub org listing showed auth helper libraries for Python, Node.js, PHP, Ruby.

**Fix applied:**
- Checked PyPI and npm — auth helpers not published to either registry
- Checked `worldcat-discovery-php` README — explicitly states "WARNING: This library is no longer maintained"
- Updated claim to: "Auth helper libraries exist on GitHub (Python, Node.js, PHP, Ruby) but are not published to PyPI or npm; Discovery wrappers (PHP, Ruby) are explicitly marked abandoned"

### Round 3 — OpenAPI "None published" contradicted by prototype repo

**Flagged:** Exec summary gap table said `None published` for OpenAPI specifications. But during CRUD verification, 7 OpenAPI YAMLs were found at `OCLC-Developer-Network/prototype-api-docs`.

**Fix applied:**
- Researched the repo: last updated 2021, explicitly named "prototype", not linked from current developer portal
- Updated claim to: "No specs in current developer portal; 7 prototype specs in OCLC-Developer-Network/prototype-api-docs (GitHub, last updated 2021, marked prototype, not linked from primary docs)"
- Applied in exec summary gap table and recommendations P2-3

**Subsequent catch:** Advisor noted `oclc-api-shortcomings.md §19` (FAST-specific section) still said "No published OpenAPI spec" — added parenthetical there initially, then advisor correctly flagged that none of the 7 prototype specs cover FAST, so the parenthetical was misleading in that context. Reverted §19 to the bare claim; portal-wide nuance left only in exec summary and P2-3.

### Round 4 — WMS Circulation auth source

**Flagged:** Auth column was changed from `WSKey` to `OAuth 2.0` based solely on the 2021 prototype spec repo.

**Fix applied:** Reverted to `WSKey / OAuth 2.0` — pairing with WSKey makes the claim defensible without requiring an inline caveat about the source being a prototype.

### Round 5 — Resource Sharing score table HMAC scope

**Flagged:** Exec summary service-area score table listed Resource Sharing auth as "Most complex (HMAC)" — but HMAC applies only to Article Exchange. The other two Resource Sharing APIs (ILL Policies Directory, Resource Sharing Request) use WSKey.

**Fix applied:** Changed to "Inconsistent — HMAC for Article Exchange; WSKey for ILL Policies + Request API"

### Final sign-off

After all 5 rounds, advisor confirmed: all 5 files consistent and defensible. No open findings.

---

## Lessons learned

### 1. "Inferred from absence" is not a valid claim

Initial drafts said things like "no update or cancel operations" based on not finding them. That's not the same as a primary source confirming the operations don't exist. Fix: find the spec or the explicit API listing that enumerates what IS supported, and use that as the evidence.

**Rule added to CLAUDE.md:** *"Inferred from absence" is not sufficient for a capability claim — find the spec or the explicit documentation.*

### 2. JavaScript-rendered portals are programmatically inaccessible

`developer.api.oclc.org` OpenAPI endpoints returned HTTP 200 with empty bodies — the portal is a SPA that requires JS execution. `ctx_fetch_and_index` couldn't retrieve content. Workaround: go to GitHub org directly for specs and source code.

**Rule learned:** When a developer portal returns empty bodies, check the vendor's GitHub org for raw files.

### 3. Wrong URL wastes a fetch

Tried `/worldshare-ill-request-api.en.html` → 404. Correct URL was `/developer/api/oclc-apis.resource-sharing.en.html`. Cost: one wasted fetch and a correction.

**Rule learned:** Check URL structure against known-good OCLC pages before fetching. The pattern is `/developer/api/oclc-apis.{service-area}.en.html`.

### 4. Prototype ≠ production — label sources at time of recording

The `OCLC-Developer-Network/prototype-api-docs` repo contains useful data (WMS Circulation endpoint list, auth patterns) but is explicitly marked prototype and last updated 2021. Initial edit changed WMS Circulation auth to `OAuth 2.0` based on this source without a caveat — advisor correctly flagged this.

**Rule added to CLAUDE.md:** *Treat prototype-api-docs as supporting evidence only — do not cite as current documentation.*

### 5. Cross-file consistency requires grepping, not memory

After fixing the OpenAPI claim in the exec summary, the same "None published" phrasing still existed in `oclc-api-recommendations.md` P2-3. Caught only because advisor read across files. Memory of "I fixed this" is not sufficient — grep all files.

**Rule added to CLAUDE.md:** *When fixing a claim, grep all 5 files for the same claim and update every occurrence in the same pass.*

### 6. Scope matters for parenthetical qualifications

When the OpenAPI parenthetical ("7 prototype specs on GitHub") was added to `§19` (FAST-specific section), it implied FAST had a spec somewhere — it doesn't. The parenthetical was correct in the portfolio-wide context but misleading in the per-API context. Lesson: qualifications that are true at one scope can be false at a narrower scope.

### 7. Commercial framing vs. technical framing

Discovery API bundle lock-in was initially framed as a technical constraint. Advisor correctly identified it as a commercial/licensing structure decision — the APIs are technically separable. The distinction matters for recommendations: technical fixes go to engineering; commercial packaging goes to product/business.

**Rule applied:** Distinguish technical constraints (require engineering to fix) from commercial/licensing structures (require business decision to change).

### 8. Advisor cadence that worked

- Called advisor after completing first draft of each major artifact
- Called advisor after any multi-file editing pass
- Fixed every flagged issue before the next advisor call
- Did not declare done without final advisor sign-off

Total advisor calls: ~5. Each caught at least one issue that would have been visible to a careful human reviewer reading across files.

---

## Reusable checklist for similar API audits

**Before recording a capability claim:**
- [ ] Found a primary source that explicitly states it (not inferred from absence)
- [ ] Source is current (not a prototype or archived page)
- [ ] Source is correctly labeled in the claim if it's limited (e.g., "per 2021 prototype spec")

**After any edit pass:**
- [ ] Grepped all output files for the same claim — updated every occurrence
- [ ] Checked that qualifications are appropriate at the scope where they appear

**Before declaring done:**
- [ ] Called advisor with all output files available
- [ ] Fixed every flagged issue
- [ ] Called advisor again if fixes were non-trivial
