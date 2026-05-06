# Claude Code hooks

Reference hooks for guardrails. **None are wired by default** — copy
the settings snippet below into your `.claude/settings.json` to enable.

---

## Hook inventory

| Script | Event | Matcher | Behaviour |
|---|---|---|---|
| `block_dangerous_git.py` | PreToolUse | Bash | Blocks `--no-verify`, `--no-gpg-sign`, GPG-bypass via `-c`, force-push to main/master, `reset --hard`, `branch -D`, `clean -f`, `checkout -- .`, `restore .` |
| `scan_secrets.py` | PreToolUse | Write\|Edit | Blocks files containing AWS / GitHub / Slack / OpenAI / Anthropic / Google / Stripe key shapes or PEM private keys. Allows placeholder tokens (`EXAMPLE`, `YOUR-`, `REDACTED`) and example paths (`.env.example`, `docs/`) |
| `audit_log.py` | PostToolUse | * | Passive: appends every tool call to `.claude/logs/audit.jsonl`. Never blocks. |

---

## Protocol

Each script reads a JSON object from stdin:

```json
{"tool_name": "Bash", "tool_input": {"command": "git push --force origin master"}}
```

Exit codes:
- `0` — allow (or no comment)
- `2` — block (PreToolUse) / ask Claude to revise (PostToolUse), stderr message shown to Claude
- other non-zero — error reported to user

Scripts use **stdlib only** — no project imports — so they run with
plain `python` on `PATH`. No venv needed.

Stderr messages use ASCII `--` instead of em-dashes for Windows
console compatibility.

---

## Settings.json wiring snippet

Paste into your `.claude/settings.json` (merge with any existing keys):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_dangerous_git.py\""
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/scan_secrets.py\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/audit_log.py\""
          }
        ]
      }
    ]
  }
}
```

**Windows note:** `${CLAUDE_PROJECT_DIR}` is resolved by the Claude
Code harness, not by the shell. The double-quotes inside the string
handle paths with spaces.

---

## Smoke tests

```bash
# Dangerous git -- should exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"git commit --no-verify -m x"}}' \
  | python .claude/hooks/block_dangerous_git.py
# expect: exit=2, stderr=BLOCKED: ...

# Force-push to master -- should exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin master"}}' \
  | python .claude/hooks/block_dangerous_git.py
# expect: exit=2, stderr=BLOCKED: ...

# Real-shaped AWS key -- should exit 2
echo '{"tool_name":"Write","tool_input":{"file_path":"config.py","content":"key=AKIA1234567890ABCDEF"}}' \
  | python .claude/hooks/scan_secrets.py
# expect: exit=2, stderr=BLOCKED: ...

# Placeholder key -- should exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"config.py","content":"key=AKIAIOSFODNN7EXAMPLE"}}' \
  | python .claude/hooks/scan_secrets.py
# expect: exit=0

# Audit log -- should always exit 0
echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' \
  | python .claude/hooks/audit_log.py
# expect: exit=0, .claude/logs/audit.jsonl appended
```

---

## Adding a hook

1. Write `.claude/hooks/<name>.py` (stdlib only, exit 0/2)
2. Wire in `.claude/settings.json` under the appropriate event + matcher
3. Smoke-test by piping a sample JSON to the script

## Disabling a hook temporarily

Remove or comment out its entry in `.claude/settings.json`. The script
file stays in place.
