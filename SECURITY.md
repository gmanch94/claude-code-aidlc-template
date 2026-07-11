# Security posture

This repo is a **Claude Code harness** — a skill library plus hooks and CI gates. It has no server, database, auth flow, or user data, so the usual web threat model (RLS, IDOR, session handling) does not apply. The surface that *does* matter is different and worth stating plainly:

> **The hooks in `.claude/hooks/` execute code on the adopter's machine, as the adopter's user, on matching tool calls — once wired.** Everything else follows from taking that seriously.

This document is the template's own security model. It is distinct from `docs/SECURITY_MODEL.md`, which `/security-model-init` generates for *your* project once it grows a user-facing surface.

---

## Trust model

Three principals:

- **Template author** — whoever authored the skills, hooks, and workflows you copied.
- **Adopter / operator** — you, running Claude Code with this repo wired in. You own the machine the hooks run on.
- **The agent** — Claude, which reads skills/prompts as guidance and calls tools that the hooks gate.

The core trust decision is the adopter's: **wiring a hook grants it execution on your machine.** The template's job is to make that decision safe to take — and reversible.

---

## Surfaces and controls

| Surface — how something harmful reaches you | Control shipped in this repo | Residual risk you still own |
|---|---|---|
| A wired hook runs code on every matching tool call | Unwired by default · stdlib-only · short and readable · no network I/O · fail-open | A malicious or buggy hook edit, wired without reading it, is arbitrary code execution. **Review any hook before wiring it.** |
| A real secret written into a committed file | `scan_secrets.py` (PreToolUse / Write) + `dlp-scan.yml` (CI) + `.gitignore` | Best-effort regex + entropy; a novel secret shape can slip. Defense-in-depth, not a guarantee. |
| A secret pasted into a prompt | `scan_prompt_dlp.py` (UserPromptSubmit) blocks it before it enters model context or the transcript | Same detection limits; the `dlp-ok` token bypasses on purpose. |
| A secret / PII echoed in tool output | `redact_tool_output.py` (PostToolUse) masks it | Regex-based; fail-safe no-op on any schema mismatch (masks or does nothing — never corrupts). |
| Data exfiltration via shell (curl / scp / rsync / nc upload) | `check_egress_allowlist.py` (PreToolUse / Bash) — warns until `.claude/dlp/egress_allowlist.txt` exists, then blocks; **fails closed** on an unconfirmable destination | Git egress is out of scope (owned by `block_dangerous_git.py`); glued-flag `nc -e` evasions are documented out-of-scope. |
| Destructive git (force-push, `reset --hard`, `--no-verify`) | `block_dangerous_git.py` (PreToolUse / Bash) | Has an intentional escape hatch for legitimate force operations. |
| CI executing on your repo | Least-privilege token on `dlp-scan.yml` (`permissions: contents: read`) · no secrets required · `actions/checkout@v4` | Add `permissions: contents: read` to any workflow you introduce (e.g. `doc-ci.yml` currently inherits the default token); pin action SHAs per your own supply-chain policy. |
| Skill and prompt text | Advisory only — read as LLM guidance, never executed; no secrets embedded | The risk is *bad advice*, not code execution. Human review of generated output still applies. |
| Doc drift breaking a stated safety property | `doc-ci.yml` — parity + relative-link + count gates | — |

Layers 1 and 3 of [`ARCHITECTURE.md`](ARCHITECTURE.md) describe where each hook attaches in the tool-call lifecycle.

---

## What this template does **not** protect against

Stated honestly, so no one leans on a guarantee that isn't there:

- **A malicious hook you wire without reading.** Unwired-by-default and readability are the mitigations; there is no sandbox. The review is yours to do.
- **DLP detection evasion.** The secret/PII scanners are pattern- and entropy-based. They raise the floor; they do not make it safe to handle real secrets carelessly.
- **Anything off the tool-call path.** Hooks only see tool calls Claude makes. Code you run yourself outside Claude Code is unguarded.
- **A wrong answer from the model.** Skills shape *how* Claude reasons about a problem; they don't make its output correct. Independent review still stands.

---

## Adopter checklist

Before wiring anything from this template into a machine you care about:

- [ ] **Read every hook you wire.** They are short and stdlib-only precisely so this is a five-minute job.
- [ ] **Keep machine-local wiring in `.claude/settings.local.json`** (gitignored). The checked-in `settings.json` stays read-only-safe for everyone.
- [ ] **Move egress from warn to block** by creating `.claude/dlp/egress_allowlist.txt` (copy the `.example`) once you know your legitimate destinations.
- [ ] **Do not commit real secrets even with the hooks on.** They are a backstop, not a licence.
- [ ] **Design your own project's model** with `/security-model-init` the moment it grows auth / DB / API / uploads / public reads — that is a different surface than this harness.

---

## Reporting

This is a template, not a hosted service. If you find a weakness in a shipped hook, CI gate, or a skill that could lead someone to an insecure design, open a GitHub issue (or a private security advisory for anything you would not want disclosed before a fix). Include the file, the bypass, and a minimal repro.
