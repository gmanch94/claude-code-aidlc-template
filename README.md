# claude-code-template

A GitHub template repo for Claude Code projects. Pre-wires the four things that determine whether Claude Code is genuinely useful on a project — or just occasionally helpful.

---

## The problem

Most projects using Claude Code get less out of it than they could:

| Missing | Effect |
|---|---|
| No `CLAUDE.md` | Claude doesn't know the project's conventions, tone, or what not to do — rediscovers them every session |
| No session bookmark | After `/clear`, Claude re-derives context that was already established. First 10–15 min of every session is orientation |
| No permission allowlist | Every read-only command (`git log`, `gh pr view`, analysis tools) triggers an approval prompt |
| No slash commands | Useful workflows (code review, ADRs, tradeoff analysis) get re-typed from memory or done inconsistently |

This template fixes all four in under 5 minutes of setup.

---

## What's included

| File | What it does |
|---|---|
| `CLAUDE.md` | Auto-loaded every session. Defines project posture, session-start protocol, tone constraints, and things to avoid. Fill in 5 placeholders. |
| `LESSONS_LEARNED.md` | Process lessons that accumulate across sessions. Pre-seeded with 8 generalizable lessons; add project-specific ones as you work. |
| `scratch/NEXT_SESSION.md` | Session bookmark — HEAD, branch, what landed, what's open. Claude reads it first after `/clear`. Gitignored (personal workspace). |
| `.claude/settings.json` | Permission allowlist. Pre-populated with context-mode MCP tools (see below). Add project-specific read-only patterns here. |
| `.claude/commands/review.md` | `/review` — code review with [BLOCKER] / [SUGGESTION] / [NITPICK] format. |
| `.claude/commands/adr.md` | `/adr` — draft an Architecture Decision Record with full rationale and alternatives. |
| `.claude/commands/tradeoff.md` | `/tradeoff` — structured tradeoff analysis: options × pros/cons/failure-mode + recommendation with named constraint. |
| `memory/MEMORY.md` | Index for Claude's persistent project memory. |
| `.gitignore` | Gitignores `scratch/` (personal workspace) and `.claude/settings.local.json`. |

---

## Setup (5 minutes)

**1. Create your repo from this template**

Click **Use this template** → **Create a new repository** on GitHub. Or clone and re-init:

```bash
git clone https://github.com/gmanch94/claude-code-template your-project
cd your-project
rm -rf .git && git init && git add . && git commit -m "init from claude-code-template"
```

**2. Fill in `CLAUDE.md`**

Five placeholders to replace:
- `[PROJECT NAME]` — what the repo is
- The one-sentence description
- `[FILENAME]` — your source of truth file
- Working conventions for your stack
- The "things to avoid" list

Start minimal — one or two entries per section. The file compounds over time.

**3. Start your first session**

Open Claude Code in your repo. Claude reads `CLAUDE.md` automatically. It will follow the session-start protocol and ask what you want to work on.

**4. End your first session**

Update `scratch/NEXT_SESSION.md` with: current HEAD hash, branch, what landed, what's open. This is the resume point for every future session.

Done. The template is live.

---

## Slash commands

Type these in the Claude Code prompt:

| Command | What it does |
|---|---|
| `/review` | Code review with [BLOCKER] / [SUGGESTION] / [NITPICK] grading. Pass a file path, diff, or "staged changes." |
| `/adr` | Draft an Architecture Decision Record. Prompts for context, options, constraints, and rationale. |
| `/tradeoff` | Structured tradeoff analysis for a decision. Produces options × pros/cons/failure-mode table + recommendation with named constraint. |

Add your own: drop a `.md` file in `.claude/commands/` and it becomes `/command-name`.

---

## Optional: context-mode MCP (for large codebases)

The `.claude/settings.json` pre-allowlists five context-mode tools. These are no-ops until you install the MCP server — safe to ignore if your codebase is small.

**What it does:** Runs shell commands and indexes their output into a sandboxed full-text search database. Instead of `cat bigfile.log` flooding your context window with 2,000 lines, `ctx_batch_execute` indexes the output and you query what you need. Prevents context exhaustion on large repos, long build logs, and multi-file analysis.

**When you need it:** When you hit context limits mid-task — build logs, dependency graphs, large refactors, or any codebase where multiple files need to be understood together.

**Install:**

```bash
# Requires Node.js 18+
npm install -g @anthropic-ai/context-mode
```

Then add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "context-mode": {
      "command": "context-mode",
      "args": ["serve"]
    }
  }
}
```

Restart Claude Code. The `ctx_*` tools in `.claude/settings.json` are already allowlisted — no further config needed.

> **Without context-mode:** Everything works. The allowlist entries are inert. Skip this section entirely for projects where context limits aren't a problem.

---

## Customizing the permission allowlist

`.claude/settings.json` controls which commands auto-approve without a prompt. Add patterns you use frequently that are read-only (no side effects, no state mutation):

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run typecheck)",
      "Bash(pytest --co -q *)",
      "Bash(gh pr view *)"
    ]
  }
}
```

Rules:
- Use `Bash(command *)` for prefix matching (space before `*` is required)
- Use `Bash(exact command)` for a single fixed invocation
- Never wildcard interpreters (`python3 *`, `node *`) — those allow arbitrary code execution
- `git`, `gh`, `ls`, `cat`, `grep`, `find` are auto-allowed by Claude Code — no entry needed

---

## How the session protocol works

Every session, Claude reads `CLAUDE.md` and follows:

```
scratch/NEXT_SESSION.md  →  LESSONS_LEARNED.md  →  CLAUDE.md  →  git status + log
                                                                          ↓
                                                              Ask what to work on
```

At the end of each session, you (or Claude) update `scratch/NEXT_SESSION.md` with HEAD, what landed, and what's open. The next session picks up exactly where the last one left off — no re-orientation.

`scratch/` is gitignored, so NEXT_SESSION.md stays local. If you work across machines, copy it manually or move it to a committed location.

---

## What to add over time

**More slash commands.** Every repeated workflow is a candidate:
- `/changelog` — draft a changelog entry from recent commits
- `/test-plan` — generate a test plan for a feature
- `/standup` — summarize yesterday's commits as a standup update

**More LESSONS_LEARNED entries.** Every time something goes wrong or unusually right, add a one-liner with a **Why:** line. The file compounds — after 10 sessions it's the most valuable thing in the repo.

**Hooks.** Claude Code hooks run shell commands before or after tool calls. Common patterns:
- Block secrets from being committed (`pre-commit` hook scanning for API keys)
- Run linter before file edits land
- Log cost metrics per session

See the [Claude Code hooks documentation](https://docs.claude.com/en/docs/claude-code/hooks) for setup.

---

## License

[Choose your license — MIT, Apache 2.0, CC-BY, etc.]
