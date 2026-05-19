"""PreToolUse hook: block class-balancing operations applied to test/val data.

Reads tool-call JSON from stdin. Exits 2 to block, 0 to allow.
Applies to Python files only.

Hard rule from imbalanced-data design: test sets must NEVER be balanced.
Balancing test data makes evaluation meaningless -- precision/recall measured
on a distribution that doesn't match production.

Blocks (high-confidence patterns):
  SMOTE().fit_resample(X_test, y_test)
  RandomOverSampler().fit_resample(X_val, y_val)
  ADASYN().fit_resample(X_test, y_test)
  ClusterCentroids().fit_resample(X_test, y_test)
  resample(X_test, ...)            # from sklearn.utils
  Pipeline-level: any *_sampler.fit_resample(...) on test/val variables

Variable detection: same convention as check_ml_leakage.py --
  Names ending in _test or _val, starting with test_ or val_, or X_te / X_va.

Escape hatches:
  - Lines containing ``# nosec`` are skipped
  - Test/fixture/example/docs paths downgrade BLOCK to WARNING

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_test_set_balancing.py\""}]
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

_TEST_VAL_VAR = r"(?:\w+_(?:test|val)|(?:test|val)_\w+|\bX_te\b|\bX_va\b)"

# Known imbalanced-learn samplers + sklearn.utils.resample.
_SAMPLERS = (
    r"SMOTE|SMOTENC|SMOTEN|BorderlineSMOTE|SVMSMOTE|KMeansSMOTE|"
    r"ADASYN|RandomOverSampler|RandomUnderSampler|"
    r"ClusterCentroids|TomekLinks|EditedNearestNeighbours|"
    r"AllKNN|InstanceHardnessThreshold|NeighbourhoodCleaningRule|"
    r"OneSidedSelection|NearMiss|CondensedNearestNeighbour"
)

# Any object whose name ends in _sampler / _resampler -- generic catch-all.
_SAMPLER_VAR = r"\w*(?:_sampler|_resampler|_smote|_oversampler|_undersampler)"

_BLOCK_PATTERNS: list[tuple[str, str]] = [
    (
        rf"\b(?:{_SAMPLERS})\s*\([^)]*\)\s*\.\s*fit_resample\s*\(\s*{_TEST_VAL_VAR}",
        "TEST-SET CONTAMINATION: class-balancing sampler applied directly to test/val data. "
        "Balancing held-out data makes evaluation meaningless -- you measure precision/recall "
        "on a distribution that doesn't match production. Apply balancing to TRAINING data only; "
        "evaluate on the original class distribution.",
    ),
    (
        rf"\b{_SAMPLER_VAR}\s*\.\s*fit_resample\s*\(\s*{_TEST_VAL_VAR}",
        "TEST-SET CONTAMINATION: sampler.fit_resample() called on test/val data. "
        "Apply class balancing to training data only; evaluate on original distribution.",
    ),
    (
        rf"\bresample\s*\(\s*{_TEST_VAL_VAR}",
        "TEST-SET CONTAMINATION: sklearn.utils.resample() called on test/val data. "
        "Resampling held-out data breaks evaluation integrity.",
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
            if "# nosec" in line or "# balance-ok" in line:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                if lenient:
                    print(f"WARNING (test/example path -- not blocked): {message}", file=sys.stderr)
                else:
                    print(f"BLOCKED: {message}", file=sys.stderr)
                    exit_code = 2
                break

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
