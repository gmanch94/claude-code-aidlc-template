"""PostToolUse hook: redact secrets / SSNs / payment cards from tool output before the model reads it.

DLP defense-in-depth. Even if sensitive data reaches a tool result -- a Bash
command that echoes an env var, a file Read that contains a key or a card number --
redact it from the output the model sees, and therefore from the transcript,
audit log, and any downstream context assembly.

Covers: the secret key shapes, PEM private keys (including a truncated BEGIN
marker), US SSNs, and Luhn-valid payment cards. Entropy is deliberately NOT
redacted here -- masking every high-entropy string would corrupt legitimate
output (git SHAs, UUIDs, base64 blobs), which defeats the tool the model called.

Mechanism (verified against code.claude.com/docs/en/hooks):
  PostToolUse receives the tool result on stdin as ``tool_response``. To replace
  it, the hook prints to stdout (exit 0):
    {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                            "updatedToolOutput": <same shape as tool_response>}}
  ``updatedToolOutput`` MUST match the tool's output shape or it is IGNORED and
  the original output is used. So this hook re-emits the FULL original structure
  with only string values masked -- shape and keys preserved exactly.

FAIL-SAFE (by construction):
  - Output is rewritten ONLY when something was actually redacted (count > 0);
    otherwise the hook prints nothing and exits 0, leaving the original intact.
  - The replacement is the original object with string values masked in place, so
    if the shape still doesn't match a given tool's schema, Claude Code ignores it
    and uses the original. Worst case is a MISSED redaction, never a corrupted or
    dropped tool result. One serialization path, exercised only on a real hit.

Patterns mirror scan_secrets.py -- self-contained (stdlib only, no shared import).

HOW TO ENABLE:
  Wire in .claude/settings.json under PostToolUse (scope to output-bearing tools):
  {
    "matcher": "Bash|Read|WebFetch",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/redact_tool_output.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import re
import sys

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS-KEY"),
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "AWS-TOKEN"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GITHUB-TOKEN"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "SLACK-TOKEN"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"), "API-KEY"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "GOOGLE-KEY"),
    (re.compile(r"\bsk_live_[0-9A-Za-z]{24,}\b"), "STRIPE-KEY"),
    (
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"
            r"(?:[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----)?"
        ),
        "PRIVATE-KEY",
    ),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "US-SSN"),
]

# Payment cards need Luhn + issuer-prefix validation (not a plain regex sub).
_CARD_IIN = re.compile(
    r"^(?:4|5[1-5]|2(?:2[2-9]|[3-6]\d|7[01]|720)|3[47]|6011|65|64[4-9]|35\d\d|30[0-5]|3[689])"
)
_CARD_CANDIDATE = re.compile(r"(?<![\d.])(?:\d[ -]?){12,18}\d(?![\d.])")
_TEST_CARDS = {
    "4111111111111111", "4012888888881881", "4242424242424242", "5555555555554444",
    "5105105105105100", "2223003122003222", "378282246310005", "371449635398431",
    "6011111111111117", "6011000990139424", "3530111333300000", "3566002020360505",
    "30569309025904", "38520000023237",
}


def _luhn_ok(digits: str) -> bool:
    total, parity = 0, len(digits) % 2
    for i, ch in enumerate(digits):
        d = ord(ch) - 48
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0

# Only mask string values living at these keys inside a structured tool_response
# (avoids masking ids / file paths / flags that merely look secret-ish).
_TEXT_KEYS = ("stdout", "stderr", "content", "output", "result", "text", "data", "body")
_PLACEHOLDERS = ("EXAMPLE", "YOUR-", "REDACTED", "XXXX")


def _redact_str(s: str) -> tuple[str, int]:
    count = 0
    for rx, label in _PATTERNS:
        def _sub(m: re.Match[str]) -> str:
            nonlocal count
            if any(p in m.group(0) for p in _PLACEHOLDERS):
                return m.group(0)
            count += 1
            return f"[REDACTED:{label}]"

        s = rx.sub(_sub, s)

    def _card_sub(m: re.Match[str]) -> str:
        nonlocal count
        digits = re.sub(r"[ -]", "", m.group(0))
        if digits in _TEST_CARDS or len(digits) not in (13, 14, 15, 16, 19) \
                or not _CARD_IIN.match(digits) or not _luhn_ok(digits):
            return m.group(0)
        count += 1
        return "[REDACTED:CARD]"

    s = _CARD_CANDIDATE.sub(_card_sub, s)
    return s, count


def _redact_any(obj: object) -> tuple[object, int]:
    """Preserve shape; mask string values. Returns (new_obj, redaction_count)."""
    if isinstance(obj, str):
        return _redact_str(obj)
    if isinstance(obj, dict):
        total = 0
        out: dict = {}
        for k, v in obj.items():
            if isinstance(v, str):
                if k in _TEXT_KEYS:
                    nv, c = _redact_str(v)
                    out[k] = nv
                    total += c
                else:
                    out[k] = v
            elif isinstance(v, (dict, list)):
                nv, c = _redact_any(v)
                out[k] = nv
                total += c
            else:
                out[k] = v
        return out, total
    if isinstance(obj, list):
        total = 0
        out_list: list = []
        for v in obj:
            nv, c = _redact_any(v)
            out_list.append(nv)
            total += c
        return out_list, total
    return obj, 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if "tool_response" not in data:
        return 0

    new_response, count = _redact_any(data["tool_response"])
    if count <= 0:
        return 0  # nothing redacted -> never round-trip the original output

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "updatedToolOutput": new_response,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
