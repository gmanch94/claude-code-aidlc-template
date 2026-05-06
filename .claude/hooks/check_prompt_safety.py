"""PreToolUse hook: warn on prompt injection risks and model hygiene issues (Write / Edit).

Reads the tool-call JSON from stdin. Exits 0 (warn-only -- never blocks).
Context determines whether these patterns are truly unsafe; the hook surfaces the risk.

Covers:

  Prompt injection risk -- user-controlled data in f-string prompts
    prompt = f"Answer this: {user_input}"
    system_prompt = f"Context: {request.body}"
    Risk: an adversarial user can override instructions or exfiltrate context.
    Fix: pass user content via structured message dicts, not string interpolation:
      messages=[{"role": "user", "content": user_input}]

  Prompt concatenation with user-sourced content
    prompt += user_message
    full_prompt = system_prompt + user_query
    Same risk as above; string concatenation is equivalent to f-string embedding.

  Hardcoded absolute model paths
    model_path = "/home/user/models/llama-3"
    checkpoint = "C:\\Users\\me\\weights\\model.bin"
    Risk: non-portable, no version tracking, accidentally commits local paths.
    Fix: use an environment variable, config file, or model registry reference.

NOT covered:
  - Indirect prompt injection via retrieved documents (RAG) -- requires data-flow analysis
  - Missing output filtering / guardrails -- too contextual
  - Insecure tool definitions (over-privileged function schemas) -- schema-specific
  - max_tokens not set -- detecting absence requires AST

Escape hatches:
  - Lines containing ``# nosec`` are skipped
  - Paths matching test/example/docs patterns skip all checks

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_prompt_safety.py\""}]
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
    r"/examples?/",
    r"\\examples?\\",
    r"/docs?/",
    r"\\docs?\\",
    r"/fixtures?/",
    r"\\fixtures?\\",
    r"README",
]

# Matches variable names that are plausibly user-controlled.
_USER_VAR = r"(?:user_\w+|input\w*|query\w*|request\.\w+|message\w*)"

# Each entry: (regex, message). All warn-only -- never block.
_WARN_PATTERNS: list[tuple[str, str]] = [
    (
        # f-string containing a user-sourced variable, on a line that also
        # mentions a prompt/message/system variable.
        rf"(?:prompt|system_prompt|messages?)\s*.*?f['\"].*\{{{_USER_VAR}",
        "PROMPT SAFETY: user-controlled variable embedded directly in an f-string prompt. "
        "Prompt injection risk -- an adversarial input can override instructions. "
        "Pass user content via structured message dicts instead: "
        "messages=[{\"role\": \"user\", \"content\": user_input}].",
    ),
    (
        # prompt += user_var  or  prompt = ... + user_var
        rf"(?:prompt|system_prompt)\s*(?:\+?=)\s*.*\b{_USER_VAR}\b",
        "PROMPT SAFETY: prompt string concatenated with user-sourced content. "
        "String concatenation carries the same injection risk as f-string embedding. "
        "Use structured message dicts instead of concatenation.",
    ),
    (
        # Hardcoded absolute path in a model-loading variable
        r"(?:model_path|model_dir|checkpoint(?:_path)?|weights_path|model_name)\s*="
        r"\s*['\"](?:/(?:home|Users|data|mnt|opt|tmp|var|srv)\b|[A-Za-z]:\\)",
        "MODEL HYGIENE: hardcoded absolute model path detected. "
        "This path is non-portable and cannot be version-tracked. "
        "Use an environment variable (os.environ['MODEL_PATH']), "
        "a config file, or a model registry reference instead.",
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
    content = inp.get("content") or inp.get("new_string") or ""
    if not content:
        return 0

    if _is_lenient_path(path):
        return 0

    lines = content.splitlines()

    for pattern, message in _WARN_PATTERNS:
        for line in lines:
            if "# nosec" in line:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                print(f"WARNING: {message}", file=sys.stderr)
                break

    return 0


if __name__ == "__main__":
    sys.exit(main())
