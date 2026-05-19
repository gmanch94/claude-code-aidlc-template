"""PreToolUse hook: warn when an eval/experiment config sets a primary metric
without a sibling guardrail / counter-metric.

Goodhart's law applied: any single metric optimized hard enough gets gamed.
Every primary metric should have at least one counter-metric that would
degrade if the primary were gamed (post-click satisfaction, default rate,
re-open rate, worst-group accuracy, etc.).

Reads tool-call JSON from stdin. Exits 0 always (warn-only); writes to stderr.

Applies to: YAML / TOML / JSON files in paths matching eval, experiment,
metric, or config patterns.

Heuristic:
  If the file contains a key like ``primary_metric``, ``optimization_metric``,
  ``main_metric``, or ``objective_metric`` AND lacks a sibling key like
  ``guardrail_metric``, ``counter_metric``, ``secondary_metric``,
  ``guardrail_metrics``, or ``counter_metrics`` -- emit a warning.

Escape hatches:
  - File anywhere with ``# metric-ok`` or ``# goodhart-ok`` on the line above
    the primary metric definition is allowed.
  - Test/fixture/example/docs paths downgrade WARN to NOTE.

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_metric_guardrail.py\""}]
  }
"""

from __future__ import annotations

import json
import re
import sys

_RELEVANT_PATH = re.compile(
    r"(eval|experiment|metric|objective|optuna|train|model_config|configs?)",
    re.IGNORECASE,
)
_RELEVANT_EXT = (".yaml", ".yml", ".toml", ".json")

_LENIENT_PATH_PATTERNS: list[str] = [
    r"/tests?/",
    r"\\tests?\\",
    r"/fixtures?/",
    r"\\fixtures?\\",
    r"/examples?/",
    r"\\examples?\\",
    r"/docs?/",
    r"\\docs?\\",
]

_PRIMARY_KEY = re.compile(
    r'^\s*["\']?(primary_metric|optimization_metric|main_metric|objective_metric|'
    r'metric_to_optimize|target_metric|key_metric)["\']?\s*[:=]',
    re.IGNORECASE | re.MULTILINE,
)

_GUARDRAIL_KEY = re.compile(
    r'\b(guardrail_metric|guardrail_metrics|counter_metric|counter_metrics|'
    r'secondary_metric|secondary_metrics|safety_metric|safety_metrics|'
    r'tracked_metric|tracked_metrics)\b',
    re.IGNORECASE,
)


def _is_relevant_file(path: str) -> bool:
    if not path.lower().endswith(_RELEVANT_EXT):
        return False
    return bool(_RELEVANT_PATH.search(path))


def _is_lenient_path(path: str) -> bool:
    for p in _LENIENT_PATH_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def _line_has_optout(lines: list[str], primary_match: re.Match[str], content: str) -> bool:
    # Find the line number of the primary match.
    line_no = content[: primary_match.start()].count("\n")
    # Check the line above for opt-out comment.
    if line_no > 0:
        prev = lines[line_no - 1]
        if "# metric-ok" in prev or "# goodhart-ok" in prev:
            return True
    # Also accept trailing same-line comment.
    if line_no < len(lines):
        cur = lines[line_no]
        if "# metric-ok" in cur or "# goodhart-ok" in cur:
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
    if not _is_relevant_file(path):
        return 0

    content = inp.get("content") or inp.get("new_string") or ""
    if not content:
        return 0

    primary = _PRIMARY_KEY.search(content)
    if not primary:
        return 0

    if _GUARDRAIL_KEY.search(content):
        return 0  # Guardrail present -- all good.

    lines = content.splitlines()
    if _line_has_optout(lines, primary, content):
        return 0

    severity = "NOTE" if _is_lenient_path(path) else "WARNING"
    print(
        f"{severity} (Goodhart's law): {path} defines a primary metric "
        f"but no guardrail / counter-metric. Any metric optimized hard enough "
        f"gets gamed -- add at least one counter-metric that would degrade if "
        f"the primary were gamed (post-click satisfaction, default rate, re-open "
        f"rate, worst-group accuracy, etc.). Suppress with '# metric-ok'.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
