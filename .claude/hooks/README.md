# Claude Code hooks

Reference hooks for guardrails. **None are wired by default** — copy
the settings snippet below into your `.claude/settings.json` to enable.

---

## Hook inventory

| Script | Event | Matcher | Behaviour |
|---|---|---|---|
| `block_dangerous_git.py` | PreToolUse | Bash | Blocks `--no-verify`, `--no-gpg-sign`, GPG-bypass via `-c`, force-push to main/master, `reset --hard`, `branch -D`, `clean -f`, `checkout -- .`, `restore .` |
| `scan_secrets.py` | PreToolUse | Write\|Edit | Blocks files containing AWS / GitHub / Slack / OpenAI / Anthropic / Google / Stripe key shapes or PEM private keys. Allows placeholder tokens (`EXAMPLE`, `YOUR-`, `REDACTED`) and example paths (`.env.example`, `docs/`) |
| `block_infra_destroy.py` | PreToolUse | Bash | Blocks `terraform destroy`, `kubectl delete namespace/--all`, mass-delete on AWS (EC2/RDS/EKS/S3), GCP (SQL/GCE/GKE), and Azure (resource group/VM/SQL). No escape hatch -- always requires explicit user confirmation. |
| `check_sql_safety.py` | PreToolUse | Bash, Write\|Edit | Blocks `DROP TABLE/DATABASE/SCHEMA` without `IF EXISTS`, `TRUNCATE`, and `DELETE FROM` without a `WHERE` clause. Downgrades to warning for test/seed/fixture paths. |
| `check_unsafe_patterns.py` | PreToolUse | Write\|Edit | Flags OWASP A02/A03/A05/A08 patterns and XSS: `eval`/`exec`, `subprocess shell=True`, raw SQL f-strings, weak crypto (MD5/SHA-1/DES/ECB), `DEBUG=True`, `pickle.loads`, unsafe `yaml.load`, `innerHTML=`, `document.write`. Per-line `# nosec` opt-out. |
| `check_cloud_cost.py` | PreToolUse | Write\|Edit | Warns on expensive EC2/EKS instance families (p4d, p3dn, x1e, u-*tb1), high-cost RDS classes, `deletion_protection = false`, and `publicly_accessible = true`. Warn-only. Per-line `# cost-ok` opt-out. |
| `check_programming_gotchas.py` | PreToolUse | Write\|Edit | Blocks three high-confidence Python gotchas: mutable default arguments, bare `except:`, and `== None` identity comparison. `.py` files only. Test/fixture paths downgrade to warning. Per-line `# nosec` opt-out. |
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
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_infra_destroy.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_sql_safety.py\""
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/scan_secrets.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_sql_safety.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_unsafe_patterns.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_cloud_cost.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_programming_gotchas.py\""
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

# terraform destroy -- should exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"terraform destroy -auto-approve"}}' \
  | python .claude/hooks/block_infra_destroy.py
# expect: exit=2, stderr=BLOCKED: ...

# DROP TABLE without IF EXISTS -- should exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"psql -c \"DROP TABLE users;\""}}' \
  | python .claude/hooks/check_sql_safety.py
# expect: exit=2, stderr=BLOCKED: ...

# DROP TABLE IF EXISTS -- should exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"migration.sql","content":"DROP TABLE IF EXISTS users;"}}' \
  | python .claude/hooks/check_sql_safety.py
# expect: exit=0

# eval() in Python -- should exit 2
echo '{"tool_name":"Write","tool_input":{"file_path":"app.py","content":"result = eval(user_input)"}}' \
  | python .claude/hooks/check_unsafe_patterns.py
# expect: exit=2, stderr=BLOCKED: ...

# nosec opt-out -- should exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"app.py","content":"result = eval(expr)  # nosec"}}' \
  | python .claude/hooks/check_unsafe_patterns.py
# expect: exit=0

# expensive EC2 instance in Terraform -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"main.tf","content":"instance_type = \"p4d.24xlarge\""}}' \
  | python .claude/hooks/check_cloud_cost.py
# expect: exit=0, stderr=COST WARNING: ...

# cost-ok opt-out -- should exit 0, no warning
echo '{"tool_name":"Write","tool_input":{"file_path":"main.tf","content":"instance_type = \"p4d.24xlarge\"  # cost-ok"}}' \
  | python .claude/hooks/check_cloud_cost.py
# expect: exit=0, no stderr

# mutable default argument -- should exit 2
echo '{"tool_name":"Write","tool_input":{"file_path":"utils.py","content":"def process(items=[]):\n    pass"}}' \
  | python .claude/hooks/check_programming_gotchas.py
# expect: exit=2, stderr=BLOCKED: ...

# bare except -- should exit 2
echo '{"tool_name":"Write","tool_input":{"file_path":"app.py","content":"try:\n    run()\nexcept:\n    pass"}}' \
  | python .claude/hooks/check_programming_gotchas.py
# expect: exit=2, stderr=BLOCKED: ...

# non-Python file -- should exit 0 (gotchas hook is Python-only)
echo '{"tool_name":"Write","tool_input":{"file_path":"app.js","content":"if (x == null) {}"}}' \
  | python .claude/hooks/check_programming_gotchas.py
# expect: exit=0
```

---

## Adding a hook

1. Write `.claude/hooks/<name>.py` (stdlib only, exit 0/2)
2. Wire in `.claude/settings.json` under the appropriate event + matcher
3. Smoke-test by piping a sample JSON to the script

## Disabling a hook temporarily

Remove or comment out its entry in `.claude/settings.json`. The script
file stays in place.
