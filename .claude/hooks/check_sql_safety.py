"""PreToolUse hook: block unsafe SQL operations.

Reads the tool-call JSON from stdin. Exits 2 to block. Exits 0 to allow.
Prints a warning to stderr for suspicious but allowed operations.

Blocks (Bash tool — shell SQL commands):
- ``DROP TABLE`` / ``DROP DATABASE`` / ``DROP SCHEMA`` without ``IF EXISTS``
- ``TRUNCATE [TABLE]``
- ``DELETE FROM <table>`` without a ``WHERE`` clause

Blocks (Write / Edit tool — SQL and migration files):
- Same patterns applied to file content being written

Escape hatches:
- ``DROP ... IF EXISTS`` is always allowed (safe idempotent form)
- Paths matching test/fixture/seed patterns downgrade to a warning, not a block

NOT covered by this hook (handle elsewhere):
- Schema migration sequencing or rollback safety
- Referential integrity / FK constraint issues
- Permissions or row-level security
- NoSQL destructive ops (use block_infra_destroy.py for cloud-level)

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Bash and PreToolUse / Write|Edit:
  {
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_sql_safety.py\""}]
  },
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_sql_safety.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import re
import sys

# Paths that downgrade from BLOCK to WARN (test/fixture/seed/migration contexts)
_LENIENT_PATH_PATTERNS: list[str] = [
    r"/tests?/",
    r"\\tests?\\",
    r"/fixtures?/",
    r"\\fixtures?\\",
    r"/seeds?/",
    r"\\seeds?\\",
    r"_seed\.",
    r"_fixture\.",
    r"_test\.",
    r"test_.*\.sql$",
]

# Patterns that are ALWAYS blocked (both Bash commands and file content)
# Each entry: (regex, human-readable reason)
_BLOCK_PATTERNS: list[tuple[str, str]] = [
    (
        r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b(?!\s+IF\s+EXISTS)",
        "DROP TABLE/DATABASE/SCHEMA without IF EXISTS is destructive and irreversible. "
        "Use DROP ... IF EXISTS, or confirm with the user before running.",
    ),
    (
        r"\bTRUNCATE\b",
        "TRUNCATE deletes all rows without a WHERE clause and cannot be rolled back in many databases. "
        "Confirm with the user before running.",
    ),
    (
        r"\bDELETE\s+FROM\b(?:(?!\bWHERE\b)[^;])*(?:;|\Z)",
        "DELETE FROM without a WHERE clause destroys all rows in the table. "
        "Add a WHERE clause, or confirm with the user before running.",
    ),
]


def _is_lenient_path(path: str) -> bool:
    for p in _LENIENT_PATH_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def _check_text(text: str, context_path: str = "") -> tuple[bool, str]:
    """Return (blocked, message). blocked=False means warn-only if message set."""
    lenient = _is_lenient_path(context_path)
    for pattern, message in _BLOCK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            if lenient:
                return False, f"WARNING (test/seed path — not blocked): {message}"
            return True, f"BLOCKED: {message}"
    return False, ""


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {})

    if tool == "Bash":
        cmd = inp.get("command", "")
        if not cmd:
            return 0
        blocked, msg = _check_text(cmd)
        if msg:
            print(msg, file=sys.stderr)
        return 2 if blocked else 0

    if tool in ("Write", "Edit"):
        path = inp.get("file_path", "")
        # For Write: check full content; for Edit: check new_string
        content = inp.get("content") or inp.get("new_string") or ""
        if not content:
            return 0
        blocked, msg = _check_text(content, context_path=path)
        if msg:
            print(msg, file=sys.stderr)
        return 2 if blocked else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
