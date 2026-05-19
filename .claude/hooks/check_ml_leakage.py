"""PreToolUse hook: block data leakage patterns in ML code (Write / Edit).

Reads the tool-call JSON from stdin. Exits 2 to block. Exits 0 to allow.
Applies to Python files only.

Blocks:
  fit_transform() on test/val data
    scaler.fit_transform(X_test)   # leaks test distribution into preprocessing
    pipe.fit_transform(val_data)
    Fix: fit on train only, then transform: scaler.fit(X_train); scaler.transform(X_test)

  fit() on test/val data
    model.fit(X_test, y_test)      # trains on held-out data
    scaler.fit(X_val)
    Fix: fit on training data only.

Warns:
  train_test_split() without random_state
    train_test_split(X, y, test_size=0.2)
    Fix: add random_state=<int> for reproducible splits.
    Handles multiline calls correctly via bracket-matching (not line-by-line).

  Preprocessing-order leakage (fit_transform before split)
    scaler.fit_transform(X)
    X_train, X_test = train_test_split(X_scaled, ...)   # leak: scaler saw test rows
    Fix: split FIRST, then fit on X_train only.

  Operational-availability feature names
    Feature names like *_outcome, *_result, *_after_decision, *_post_diagnosis
    suggest the value is recorded after the prediction event -- likely target leakage.
    Fix: confirm each flagged feature exists in the upstream system at inference time.

Variable name heuristics (test/val data detection):
  Matches names ending in _test or _val (X_test, features_val),
  starting with test_ or val_ (test_data, val_features),
  or the short-forms X_te / X_va.

NOT covered:
  - Target leakage (features derived from the label) -- requires semantic analysis
  - Temporal leakage in time-series splits -- requires call-graph context
  - Pipeline leakage where fit() is hidden inside a wrapper -- AST needed
  - Cross-validation leakage (preprocessing outside CV loop) -- too contextual

Escape hatches:
  - Lines containing ``# nosec`` are skipped
  - Paths matching test/fixture/example/docs patterns downgrade BLOCK to WARNING

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_ml_leakage.py\""}]
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

# Matches variable names that are clearly test or validation data.
# Covers sklearn convention (X_test, y_val), reversed (test_data, val_features),
# and short-forms (X_te, X_va).
_TEST_VAL_VAR = r"(?:\w+_(?:test|val)|(?:test|val)_\w+|\bX_te\b|\bX_va\b)"

_BLOCK_PATTERNS: list[tuple[str, str]] = [
    (
        rf"\.fit_transform\s*\(\s*{_TEST_VAL_VAR}",
        "ML LEAKAGE: fit_transform() on test/val data leaks distribution statistics "
        "into preprocessing -- the scaler or encoder learns from held-out data. "
        "Fit on training data only: "
        "scaler.fit(X_train) then scaler.transform(X_test).",
    ),
    (
        rf"\.fit\s*\(\s*{_TEST_VAL_VAR}",
        "ML LEAKAGE: fit() called on test/val data trains the estimator or transformer "
        "on held-out samples. Fit on training data only.",
    ),
]


def _is_lenient_path(path: str) -> bool:
    for p in _LENIENT_PATH_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def _find_call_bodies(content: str, func_name: str) -> list[str]:
    """Return the argument body (between outer parens) of each call to func_name."""
    bodies: list[str] = []
    pattern = re.compile(r"\b" + re.escape(func_name) + r"\s*\(")
    for m in pattern.finditer(content):
        start = m.end()
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == "(":
                depth += 1
            elif content[i] == ")":
                depth -= 1
            i += 1
        bodies.append(content[start : i - 1])
    return bodies


def _check_train_test_split(content: str) -> bool:
    """Return True if any train_test_split call is missing random_state."""
    for body in _find_call_bodies(content, "train_test_split"):
        if not re.search(r"\brandom_state\s*=", body):
            return True
    return False
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
    if not path.endswith(".py"):
        return 0

    content = inp.get("content") or inp.get("new_string") or ""
    if not content:
        return 0

    lenient = _is_lenient_path(path)
    lines = content.splitlines()
    exit_code = 0

    for pattern, message in _BLOCK_PATTERNS:
        for line in lines:
            if "# nosec" in line:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                if lenient:
                    print(f"WARNING (test/example path -- not blocked): {message}", file=sys.stderr)
                else:
                    print(f"BLOCKED: {message}", file=sys.stderr)
                    exit_code = 2
                break

    if "train_test_split" in content and _check_train_test_split(content):
        print(
            "WARNING: train_test_split() called without random_state. "
            "Add random_state=<int> for reproducible splits across runs.",
            file=sys.stderr,
        )

    # Preprocessing-order leakage: fit_transform appears before train_test_split.
    if "train_test_split" in content:
        ft_pos = re.search(r"\.fit_transform\s*\(", content)
        tts_pos = re.search(r"\btrain_test_split\s*\(", content)
        if ft_pos and tts_pos and ft_pos.start() < tts_pos.start():
            # Extract the fit_transform line (handle final-line / no-trailing-newline case).
            nl = content.find("\n", ft_pos.start())
            ft_line = content[ft_pos.start() :] if nl == -1 else content[ft_pos.start() : nl]
            # Skip if the fit_transform argument is a training-only variable.
            if not re.search(r"\.fit_transform\s*\(\s*\w*_train\b", ft_line):
                print(
                    "WARNING: fit_transform() appears before train_test_split() in this file. "
                    "If the fitted transformer saw the full dataset, it leaks test "
                    "distribution into preprocessing. Split FIRST, then fit on X_train only.",
                    file=sys.stderr,
                )

    # Operational-availability leakage: feature names suggesting post-event values.
    leaky_name_pattern = re.compile(
        r"['\"](\w*(?:_outcome|_result|_after_(?:decision|event|diagnosis|treatment|"
        r"discharge|approval|prediction)|_post(?:outcome|diagnosis|treatment|event)|"
        r"_label_leaks?|_was_(?:fraud|approved|denied|admitted)))['\"]",
        re.IGNORECASE,
    )
    flagged = set()
    for line in lines:
        if "# nosec" in line or "# leakage-ok" in line:
            continue
        for m in leaky_name_pattern.finditer(line):
            flagged.add(m.group(1))
    if flagged:
        names = ", ".join(sorted(flagged)[:5])
        print(
            f"WARNING: feature name(s) suggest post-event values (operational-availability leakage): "
            f"{names}. Confirm each exists in the upstream system AT inference time, "
            f"not recorded after the prediction event. Suppress per-line with '# leakage-ok'.",
            file=sys.stderr,
        )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
