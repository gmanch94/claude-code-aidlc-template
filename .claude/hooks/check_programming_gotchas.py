"""PreToolUse hook: block high-confidence Python programming gotchas (Write / Edit).

Reads the tool-call JSON from stdin. Exits 2 to block. Exits 0 to allow.

Covers three Python patterns with near-zero false-positive rates:

  GOTCHA-1 Mutable default argument
    def foo(items=[]):   # list shared across all calls
    def foo(cache={}):   # dict shared across all calls
    def foo(seen=set()): # set shared across all calls
    Fix: use None as default and initialise inside the function body.

  GOTCHA-2 Bare except clause
    except:              # catches BaseException incl. KeyboardInterrupt, SystemExit
    Fix: except Exception: at minimum; ideally name the specific exception.

  GOTCHA-3 Identity comparison to None with == / !=
    if x == None:        # works by coincidence; breaks for objects overriding __eq__
    if x != None:
    Fix: use ``is None`` / ``is not None``.

NOT covered (too many false positives with regex):
  - is-comparison to literals (``if x is 1:``) — CPython caches small ints,
    making this unreliable to detect without an AST
  - String concatenation in loops — common in logging, template building
  - Catching broad Exception — legitimate in top-level handlers
  - JS/TS gotchas (== vs ===, var) — better enforced by ESLint
  - TODO/FIXME markers — too noisy without scope context

Escape hatches:
  - Lines containing ``# nosec`` are skipped (per-line opt-out)
  - Paths matching test/fixture/example/docs patterns downgrade BLOCK to WARNING

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_programming_gotchas.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import re
import sys

_LENIENT_PATH_PATTERNS: list[str] = [
    r"/tests?/",
    r"\\tests?\\",
    r"/fixtures?/",
    r"\\fixtures?\\",
    r"/examples?/",
    r"\\examples?\\",
    r"/docs?/",
    r"\\docs?\\",
    r"README",
]

# Each entry: (regex, message)
# All are HIGH severity (exit 2); lenient paths downgrade to WARN (exit 0).
_PATTERNS: list[tuple[str, str]] = [
    (
        r"\bdef\s+\w+\s*\([^)]*=\s*(\[\s*\]|\{\s*\}|set\s*\(\s*\))",
        "GOTCHA Mutable default argument: the default value is created once at "
        "function definition time and shared across all calls. "
        "Use None as the default and initialise inside the function body.",
    ),
    (
        r"^\s*except\s*:",
        "GOTCHA Bare except: catches BaseException including KeyboardInterrupt and "
        "SystemExit, masking fatal signals. "
        "Use ``except Exception:`` at minimum, or name the specific exception.",
    ),
    (
        r"\b(?:==|!=)\s*None\b|\bNone\s*(?:==|!=)",
        "GOTCHA Identity check with ==: use ``is None`` / ``is not None`` instead. "
        "== None works by coincidence but breaks for objects that override __eq__.",
    ),
]


def _is_lenient_path(path: str) -> bool:
    for p in _LENIENT_PATH_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool = data.get("tool_name", "")
    if tool not in ("Write", "Edit"):
        return 0

    inp = data.get("tool_input", {})
    path = inp.get("file_path", "")

    # Only apply to Python files — these patterns are Python-specific.
    if not path.endswith(".py"):
        return 0

    content = inp.get("content") or inp.get("new_string") or ""
    if not content:
        return 0

    lenient = _is_lenient_path(path)
    lines = content.splitlines()
    exit_code = 0

    for pattern, message in _PATTERNS:
        for line in lines:
            if "# nosec" in line:
                continue
            if re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                if lenient:
                    print(f"WARNING (test/example path -- not blocked): {message}", file=sys.stderr)
                else:
                    print(f"BLOCKED: {message}", file=sys.stderr)
                    exit_code = 2
                break  # one message per pattern

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
