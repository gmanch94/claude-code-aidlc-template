---
name: mcp-design
description: Designs MCP (Model Context Protocol) servers — tool/resource/prompt manifests, transport choice (stdio vs Streamable HTTP), auth model, schema discipline, scope/permission boundaries, error contract, idempotency, deferred-tool surfaces, host-compatibility matrix, and observability. Use when authoring a new MCP server or auditing an existing one before shipping. Complements `/agent-design` (consumer-side) — this is the producer side.
---

# /mcp-design — MCP Server Design

## Role
You are an MCP Server Designer.

> **Spec-currency note (verify before shipping):** The MCP spec moves fast. As of mid-2026 the 2026-07-28 release candidate landed several breaking changes vs the 2025-06-18 baseline this skill was originally written against. Highlights to verify in your target host's supported spec version:
> - **Stateless core** — sessions removed (SEP-2567) + handshake removed (SEP-2575). Servers no longer hold per-connection state; resumability lives in the client.
> - **Extensions framework** (SEP-2133) — capabilities are now namespaced by reverse-DNS IDs and negotiated per extension; the core surface is intentionally small.
> - **Tasks demoted to an extension** — `tools/call` returns a task handle; `tasks/list` was removed entirely. Breaking change for anyone on the 2025-11-25 experimental Tasks API.
> - **Roots / Sampling / Logging deprecated under SEP-2577** — annotation-only (methods continue to work ≥1 year); recommended replacements: tool params or resource URIs (instead of Roots), direct LLM API calls (instead of Sampling), stderr or OpenTelemetry (instead of Logging).
> - **MCPB packaging** — `.dxt` Desktop Extensions renamed to `.mcpb` MCP Bundles; OS-keychain secret storage; auto-updates.
> - **AAIF governance handoff (2025-12-09)** — Anthropic donated MCP to the Linux Foundation's Agentic AI Foundation; co-founders are **Anthropic + Block + OpenAI**, with Google/Microsoft/AWS/Cloudflare/Bloomberg as supporters. Spec evolution now lives at the foundation.
> - **HTTP+SSE transport** — already deprecated since 2025-03-26; hosts are enforcing the cutover (e.g. Keboola dropped SSE 2026-04-01; Atlassian Rovo deadline 2026-06-30).
>
> Pin the spec date your server targets in its README and re-check this list against the [current spec](https://modelcontextprotocol.io/specification/) before publishing.

## Behavior
1. Ask if not provided: the server's job, the host(s) it targets (Claude Code / Claude Desktop / Cursor / Cline / generic), the resources/tools/prompts it will expose, transport (stdio/HTTP), the auth model (none / OAuth / API key / mTLS), the **sandbox / network-reach posture** (where tools execute, what they can reach), and the **MCP spec version** the server targets
2. Work through the 10 dimensions in order
3. Flag every tool whose side effects are irreversible as **[RISK: HIGH]** — must require explicit confirmation in the tool description and write to an audit log
4. Produce the server manifest + a host-compatibility matrix + a sandbox/reach matrix
5. Recommend ADRs at the end for any decision the answers reveal as load-bearing

## 10 Dimensions

**1. Capability split.** What goes where?
- **Tools** — model-callable functions with side effects (read, write, search, compute). Each tool is a public API call from the model's perspective.
- **Resources** — addressable read-only content (files, DB rows, API responses) the host can subscribe to and pass to the model verbatim.
- **Prompts** — reusable templated workflows the user can invoke (often as a slash command in the host).
- Default rule: read-only **and** large → resource. Write-side-effect → tool. User-invokable template → prompt.

**2. Transport choice.** stdio vs Streamable HTTP.
- **stdio** — local single-tenant, no auth needed (host is the trust boundary). Default for Claude Desktop / Claude Code local installs.
- **Streamable HTTP** — multi-tenant, hosted, requires auth. Pick when the server has shared state, costs money per request, or the host is remote. (The earlier `HTTP+SSE` transport from the 2024-11-05 spec is **deprecated** since 2025-03-26; retain only for backwards-compat with old hosts.)
- Mixing is allowed: stdio for dev, HTTP for prod, same handler code.

**3. Schema discipline.** Tool input/output schemas — the MCP spec pins to **JSON Schema 2020-12**. Author to that draft; older drafts (7 / 2019-09) work in practice but strict-mode hosts validate against 2020-12.
- **Every** tool ships with a complete `inputSchema`. Optional params have defaults; required params are listed. No `additionalProperties: true` on internal tools.
- Tool descriptions are written for the model, not the human — include the WHEN (trigger conditions) and the NOT-when. "Use when X. Do NOT use for Y."
- Output schemas are recommended when the model needs to chain tool calls; required when consumers do programmatic parsing.
- Reject silently-coerced types: a tool that accepts `count` as string AND int is a bug magnet.

**4. Auth model.**
- **stdio:** none — host is trust boundary. Document any env-var secrets the server reads (`API_KEY`, etc.) and where to put them.
- **HTTP:** OAuth 2.1 + PKCE — per the current MCP authorization spec, MCP servers (acting as OAuth resource servers) **MUST** expose **protected resource metadata (RFC 9728**, published as Proposed Standard April 2025**)**. The authorization server **MUST** provide **either** OAuth 2.0 Authorization Server Metadata (**RFC 8414**) **OR** OpenID Connect Discovery 1.0 — either satisfies the discovery requirement. Clients **SHOULD** use **resource indicators (RFC 8707)** to identify the MCP server itself as the target resource (not "downstream APIs"). **Dynamic Client Registration (RFC 7591) is deprecated / optional** in the current spec — prefer **OAuth Client ID Metadata Documents** (`draft-ietf-oauth-client-id-metadata-document`), which servers/clients **SHOULD** support. Clients **MUST** validate the **`iss` parameter (RFC 9207)** on authorization responses. Per-tenant API key or mTLS are alternatives only for service-to-service / non-OAuth deployments. Bearer tokens in `Authorization: Bearer` header. Pin the MCP spec version your server targets in the README — the spec evolves.
- **Per-user scoping:** if the server has access to user-specific data (Gmail, Slack, GitHub), each session carries a per-user token; the server NEVER returns another user's data because of a session mix-up.
- **Token storage:** never log tokens; never return them in tool outputs; rotate on revocation.

**5. Permission / scope boundaries.**
- Tools that mutate get a scope label: `read`, `write`, `admin`. Hosts can pre-allow by scope.
- Destructive ops (delete, force, mass-update) require explicit `--force` or `confirm: true` param.
- Default deny: if the host doesn't request a tool, the server doesn't surface it.
- Per-tool rate limits in the spec, not just in code — the limit is part of the contract.

**6. Error contract.** What does the host see when something goes wrong?
- **Structured errors** — return `{ error: { code, message, retryable } }`, not free-text exceptions.
- Distinguish: user error (4xx — bad input, missing scope) vs server error (5xx — transient, retryable) vs auth error (re-auth needed).
- Never silently swallow errors; never return `null` on failure — the model can't recover from absence.
- Idempotency: writes accept an `idempotency_key`; replays with the same key return the original result, not a duplicate write.

**7. Deferred / lazy-loaded tools.** When the toolset is large (>30) or context is constrained.
- Mark non-core tools as deferred; expose a search/discovery tool the model uses to load the rest on demand.
- Description-only listing in the initial manifest; full JSON Schema fetched per call.
- Trade-off: deferred tools require one extra round-trip but keep the system prompt 10×–100× smaller.

**8. Sandbox + network reach.** Where does the tool's code actually run, and what can it touch?
- **Execution environment:** in-process (stdio) / agent host's worker (HTTP, host-trusted) / vendor MicroVM (sandboxed, e.g. E2B/Daytona/Modal/Runloop) / customer VPC (self-hosted). State this for every tool — not just "it runs server-side."
- **Network reach:** public internet only / customer-VPC private endpoints (mTLS or PSC tunnel) / both. Tools that hit a private VPC require a reach mechanism in the spec: PrivateLink/PSC endpoint, mTLS proxy, Tailscale-style overlay, or vendor tunneling product.
- **Blast radius if rogue:** for each [RISK: HIGH] tool, name what the worst-case wrong-input call can do (delete prod row / publish public message / spin up paid resource). Pair with the sandbox to constrain it (read-only DB role / staging-only API key / per-call spend cap).
- **Secrets boundary:** which env vars / vault leases the tool reads. Sandbox should hand the tool only the secrets it needs, never the union of all tool secrets.
- **Egress policy:** allowlist (default-deny outbound) for sandboxed tools; document any tool that requires unrestricted egress.

**9. Host-compatibility matrix.** Which hosts the server targets and what each supports.

| Host | Transport | Tools | Resources | Prompts | Auth | Notes |
|---|---|---|---|---|---|---|
| Claude Desktop | stdio | yes | yes | yes | env-var only | restart on config change |
| Claude Code | stdio + HTTP | yes | yes | yes | env-var + OAuth | deferred-tool aware |
| **Anthropic Messages API `mcp_servers` param** | HTTP (remote-only, public HTTPS, Streamable HTTP / SSE, Anthropic egress IPs) | **yes (tools only — no resources / prompts)** | no | no | OAuth supported | Beta header `mcp-client-2025-11-20` (previous `mcp-client-2025-04-04` deprecated). Third deployment target alongside Claude Desktop / Claude Code |
| **OpenAI Realtime API native MCP** | HTTP (remote) | yes | varies | varies | OAuth | `gpt-realtime` GA 2025-08-28 added native remote-MCP server support; pair with image input + SIP phone calling |
| Cursor | stdio | yes | partial | no | env-var | check version pinning |
| Cline | stdio | yes | yes | yes | env-var | — |
| Generic OpenAI-clients | HTTP | yes | varies | varies | OAuth | spec-compliant only |

Test against at least 2 hosts before declaring the server done. Note: the Anthropic `mcp_servers` HTTP target is **tools-only** — design tool surfaces to not depend on Resources / Prompts when this host matters.

**10. Observability.**
- **Per-call:** tool name, latency, success/fail, error code, token count (if LLM-internal), caller identity hash.
- **Per-session:** session id, tool-call sequence, total wall time, error rate.
- **Aggregates:** top-N tools, top-N error codes, p50/p95/p99 latency per tool, daily active sessions.
- **Audit log** for every tool flagged [RISK: HIGH] — what was called, by which session/user, when, what changed.
- Logs ship to stdout/stderr by default (host captures); env-var override for file/HTTP sink.

## Output

```
### MCP Server Design: <server-name>

**Job:** <one sentence — what this server does>
**Target host(s):** <Claude Code / Claude Desktop / Cursor / generic>
**Transport:** <stdio / Streamable HTTP>
**Auth:** <none / API key / OAuth 2.1+PKCE / mTLS>

**Capability split:**
- Tools (N): <list with [RISK: HIGH] markers>
- Resources (M): <list>
- Prompts (P): <list>

**Schema discipline:** <one-line summary of input/output schema rules>
**Permission / scopes:** <scope labels in use; destructive-op confirm rules>
**Error contract:** <structured-error format; idempotency strategy>
**Deferred tools:** <yes/no; trigger threshold>
**Host compatibility matrix:** <table>
**Observability:** <metrics + audit log destinations>

**[RISK: HIGH] tools requiring HITL:** <list, or "none">
**Recommended ADRs:**
- <ADR 1 — e.g. "transport: stdio vs HTTP for v1">
- <ADR 2 — e.g. "auth: API-key per tenant vs OAuth">
- <ADR 3 — e.g. "schema: strict mode (additionalProperties=false) repo-wide">
```

## Quality bar

- Every tool has a complete `inputSchema` — no `additionalProperties: true` on internal tools
- Tool descriptions name WHEN to use AND when NOT to use — vague descriptions cause mis-invocations
- Destructive tools require explicit confirmation params (`confirm: true` / `--force`) — never inferred
- HTTP-transport servers ship with OAuth 2.1 + PKCE (or per-tenant API key + rotation policy)
- Audit log is mandatory for [RISK: HIGH] tools — what + who + when + what-changed
- Server must declare its full host-compatibility matrix before shipping; test ≥2 hosts
- Tokens never appear in tool outputs, logs, or error messages
- Idempotency-key support on every write tool

## What this skill does NOT do

- Does NOT write the server code — produces the design spec; implementation is a separate step
- Does NOT pick the language/framework — model-protocol design is language-agnostic
- Does NOT replace `/agent-design` — that's consumer-side; this is producer-side
- Does NOT cover MCP host development — only servers
