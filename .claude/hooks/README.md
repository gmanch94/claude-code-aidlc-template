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
| `check_ml_leakage.py` | PreToolUse | Write\|Edit | Blocks ML data leakage: `fit_transform(X_test)`, `.fit(X_test)`. Warns on `train_test_split()` missing `random_state`, preprocessing-order leakage (`fit_transform` before `train_test_split` in same file), and operational-availability feature names (`*_outcome`, `*_after_decision`, `*_post_diagnosis`). `.py` files only. Per-line `# nosec` / `# leakage-ok` opt-out. |
| `block_test_set_balancing.py` | PreToolUse | Write\|Edit | Blocks class-balancing on test/val data: `SMOTE().fit_resample(X_test)`, `RandomOverSampler().fit_resample(X_val)`, `*_sampler.fit_resample(X_test)`, `sklearn.utils.resample(X_test)`. `.py` files only. Per-line `# nosec` / `# balance-ok` opt-out. |
| `check_metric_guardrail.py` | PreToolUse | Write\|Edit | Warns when eval/experiment YAML/TOML/JSON config sets a primary metric (`primary_metric`, `optimization_metric`, etc.) without any sibling guardrail / counter-metric. Goodhart's-law check. Path-filtered to `eval/`, `experiment/`, `metric/`, `config/` etc. Per-line `# metric-ok` / `# goodhart-ok` opt-out. |
| `check_pii_in_logs.py` | PreToolUse | Write\|Edit | Warns when `print` / `logging.*` / `logger.*` calls reference PII-shaped variables (email, ssn, dob, phone, address, credit_card, mrn, patient_name, full_name, etc.). Skips lines containing `redact`, `mask`, `hash`, `obfuscate`, `pseudo`, `anon`. `.py` files only. Per-line `# pii-ok` opt-out. |
| `check_prompt_safety.py` | PreToolUse | Write\|Edit | Warns on prompt injection risk (f-string/concat with user vars), and hardcoded absolute model paths. Warn-only. Per-line `# nosec` opt-out. |
| `audit_log.py` | PostToolUse | * | Passive: appends every tool call to `.claude/logs/audit.jsonl`. Never blocks. |
| `shadow_git_checkpoint.py` | PreToolUse | Write\|Edit\|Bash\|NotebookEdit | Snapshots the working tree to a SHADOW Git repo at `.claude/checkpoints/` BEFORE every mutating tool call. Enables one-click rollback per tool call without polluting project Git history. Mirrors Cline's shadow-Git pattern (docs.cline.bot/features/checkpoints). Pair with the `/rollback-checkpoint` skill. Never blocks; best-effort. Opt-out: touch `.claude/checkpoints/.disabled`. |
| `staleness_check.py` | SessionStart | — | Flags `NEXT_SESSION.md` HEAD bookmark stale by >7 days behind git HEAD; flags `Last working session: YYYY-MM-DD` stamps >30d old; flags `(as of YYYY-MM-DD)` / `verified YYYY-MM-DD` stamps >30d old in repo-root markdown. Warn-only; never blocks. Pair with `/doc-ci-check` (same drift caught in CI). |

---

## Hook event catalog (2026)

Claude Code now exposes **12+ lifecycle events** for hook wiring (the reference hooks above target only `PreToolUse` and `PostToolUse`; the rest are unused capacity in this repo). Verify the current list against the [official hooks docs](https://code.claude.com/docs/en/hooks) before relying on any specific event — names and payloads continue to evolve.

| Event | When it fires | Common uses |
|---|---|---|
| `SessionStart` | New session begins | Greet, run staleness check, log session id, load resume bookmark |
| `UserPromptSubmit` | User submits a prompt before model receives it | Prompt-time guardrails, refuse certain topics, prepend project context |
| `PreToolUse` | Before a tool runs | Block dangerous ops, scan secrets, force confirmation |
| `PostToolUse` | After a tool returns | Audit log, mutate output via `hookSpecificOutput.updatedToolOutput`, record `duration_ms` |
| `PostToolUseFailure` | Tool errored out | Capture failure for triage, escalate, alert |
| `PostToolBatch` | Batch of tool calls completed | Aggregate metrics, summarize what changed |
| `Stop` | Turn ends cleanly | Refuse turn-end with uncommitted changes, flush audit log, post turn summary |
| `StopFailure` | Turn ends with an error | Capture stack, open issue, escalate |
| `SubagentStop` | A subagent finished | Roll up subagent transcript, attribute spend, write to parent log |
| `TaskCreated` / `TaskCompleted` | TaskCreate / Task completed via Task API | Update external tracker, time per task |
| `TeammateIdle` | Background teammate idle | Idle-pool reclaim, status flip |
| `WorktreeCreate` / `WorktreeRemove` | Git worktree lifecycle | Track scratch worktrees, auto-cleanup |
| `CwdChanged` | Working directory changed mid-session | Reload project rules, re-read CLAUDE.md, log boundary cross |
| `SessionEnd` | Session terminated | Final audit-log flush, commit reminder, durable bookmark update |
| `PreCompact` | Just before context compaction | Write in-progress work to disk (this repo's existing precompact_checkpoint.py) |

**Capability notes:**
- `PostToolUse` now ships `duration_ms` in its event payload — enables latency budgets per tool.
- `PostToolUse` can mutate the tool result the model sees via `hookSpecificOutput.updatedToolOutput` (e.g. redact PII before the model reads it).
- Some sources catalog 32+ events including more granular subagent + worktree variants — the 12+ above is conservative-stable.

**Suggested hooks this repo doesn't yet ship** (gap analysis):
- `UserPromptSubmit` guardrail — refuse prompts that ask for credential extraction / silent destructive-op patterns.
- `Stop` guardrail — refuse to end a turn with uncommitted destructive changes.
- `SessionEnd` audit-log finalize — rotate `.claude/logs/audit.jsonl`, append turn summary.

(Two of the previously-suggested gaps now ship as reference hooks: `staleness_check.py` and `shadow_git_checkpoint.py`. None are wired by default — see settings snippets below.)

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
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_ml_leakage.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_test_set_balancing.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_metric_guardrail.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_pii_in_logs.py\""
          },
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_prompt_safety.py\""
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

### Optional add-ons (shadow-Git + staleness)

To enable the shadow-Git checkpoint hook (best-effort, never blocks) and the session-start staleness check, merge these into the same `hooks` block:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/shadow_git_checkpoint.py\""
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/staleness_check.py\""
          }
        ]
      }
    ]
  }
}
```

Pair `shadow_git_checkpoint.py` with the `/rollback-checkpoint` skill for the rollback UX. Opt out per-repo by touching `.claude/checkpoints/.disabled`.

Pair `staleness_check.py` with `/doc-ci-check` — the hook surfaces drift at session-start; the CI check fails the PR if drift ships.

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

# fit_transform on test data -- should exit 2
echo '{"tool_name":"Write","tool_input":{"file_path":"train.py","content":"X_scaled = scaler.fit_transform(X_test)"}}' \
  | python .claude/hooks/check_ml_leakage.py
# expect: exit=2, stderr=BLOCKED: ML LEAKAGE ...

# train_test_split missing random_state -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"train.py","content":"X_train, X_test = train_test_split(X, test_size=0.2)"}}' \
  | python .claude/hooks/check_ml_leakage.py
# expect: exit=0, stderr=WARNING: train_test_split ...

# train_test_split with random_state -- should exit 0, no warning
echo '{"tool_name":"Write","tool_input":{"file_path":"train.py","content":"X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)"}}' \
  | python .claude/hooks/check_ml_leakage.py
# expect: exit=0, no stderr

# prompt injection f-string -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"app.py","content":"prompt = f\"Answer: {user_input}\""}}' \
  | python .claude/hooks/check_prompt_safety.py
# expect: exit=0, stderr=WARNING: PROMPT SAFETY ...

# hardcoded model path -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"infer.py","content":"model_path = \"/home/user/models/llama\""}}' \
  | python .claude/hooks/check_prompt_safety.py
# expect: exit=0, stderr=WARNING: MODEL HYGIENE ...

# SMOTE on test set -- should exit 2
echo '{"tool_name":"Write","tool_input":{"file_path":"train.py","content":"X_res, y_res = SMOTE().fit_resample(X_test, y_test)"}}' \
  | python .claude/hooks/block_test_set_balancing.py
# expect: exit=2, stderr=BLOCKED: TEST-SET CONTAMINATION ...

# balance-ok opt-out -- should exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"train.py","content":"X_res, y_res = SMOTE().fit_resample(X_test, y_test)  # balance-ok"}}' \
  | python .claude/hooks/block_test_set_balancing.py
# expect: exit=0

# operational-availability feature names -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"train.py","content":"features = [\"age\", \"outcome_30d\", \"after_decision_status\"]"}}' \
  | python .claude/hooks/check_ml_leakage.py
# expect: exit=0, stderr=WARNING: feature name(s) suggest post-event values ...

# eval config with primary metric, no guardrail -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"configs/eval.yaml","content":"primary_metric: ctr\nbaseline: 0.04"}}' \
  | python .claude/hooks/check_metric_guardrail.py
# expect: exit=0, stderr=WARNING (Goodhart's law) ...

# eval config with both primary + guardrail -- should exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"configs/eval.yaml","content":"primary_metric: ctr\nguardrail_metric: bounce_rate"}}' \
  | python .claude/hooks/check_metric_guardrail.py
# expect: exit=0, no stderr

# print with PII variable -- should warn, exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"app.py","content":"print(f\"sending to {user.email}\")"}}' \
  | python .claude/hooks/check_pii_in_logs.py
# expect: exit=0, stderr=WARNING (PII in logs) ...

# print with hashed PII -- should exit 0
echo '{"tool_name":"Write","tool_input":{"file_path":"app.py","content":"print(f\"sending to {hash(user.email)}\")"}}' \
  | python .claude/hooks/check_pii_in_logs.py
# expect: exit=0, no stderr
```

---

## Adding a hook

1. Write `.claude/hooks/<name>.py` (stdlib only, exit 0/2)
2. Wire in `.claude/settings.json` under the appropriate event + matcher
3. Smoke-test by piping a sample JSON to the script

## Disabling a hook temporarily

Remove or comment out its entry in `.claude/settings.json`. The script
file stays in place.
