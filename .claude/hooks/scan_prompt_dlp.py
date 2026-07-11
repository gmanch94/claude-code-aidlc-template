"""UserPromptSubmit hook: block prompts that contain a secret / SSN / payment card.

Prompt-side DLP. Stops a pasted AWS key, private-key block, SSN, or card number
from entering the model context -- and therefore the transcript and any logging --
in the first place. Blocks the submit (exit 2); the stderr reason is shown to the
user so they can redact and resubmit.

Verified against code.claude.com/docs/en/hooks: a UserPromptSubmit hook receives
`prompt: string` on stdin; exit 2 blocks the prompt and shows stderr to the user.

Scope: HIGH-CONFIDENCE shapes only. Blocking a user's prompt is high-friction, so
this fires on known secret-key shapes, PEM private keys, US SSN (dashed), and
Luhn-valid payment cards -- NOT on generic entropy heuristics (too many false
positives on legitimate pasted text).

Escape hatch:
  - Set DLP_ALLOW_PROMPT_SECRETS=1 to disable for a session.
  - Include the literal token `dlp-ok` in the prompt to override one submit.

Patterns mirror scan_secrets.py -- each hook is self-contained (stdlib only, no
shared import) so a break in one can't disable the rest. Keep them in sync.

HOW TO ENABLE:
  Wire in .claude/settings.json under UserPromptSubmit:
  {
    "matcher": "*",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/scan_prompt_dlp.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import os
import re
import sys

_SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"\bASIA[0-9A-Z]{16}\b", "AWS session token"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "GitHub token"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "Slack token"),
    (r"\bsk-[A-Za-z0-9_-]{32,}\b", "OpenAI/Anthropic-style key"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "Google API key"),
    (r"\bsk_live_[0-9A-Za-z]{24,}\b", "Stripe live key"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----", "Private key block"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "US SSN"),
]
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
_PLACEHOLDERS = ("EXAMPLE", "XXXXXX", "000000", "your-", "YOUR-", "REPLACE", "REDACTED", "redacted")


def _is_placeholder(text: str) -> bool:
    return any(tok in text for tok in _PLACEHOLDERS)


def _valid_ssn(m: str) -> bool:
    area, group, serial = m[:3], m[4:6], m[7:11]
    if area in ("000", "666") or area[0] == "9":
        return False
    return group != "00" and serial != "0000"


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


def _findings(prompt: str) -> list[str]:
    found: list[str] = []
    for pattern, label in _SECRET_PATTERNS:
        for m in re.finditer(pattern, prompt):
            if _is_placeholder(m.group(0)):
                continue
            if label == "US SSN" and not _valid_ssn(m.group(0)):
                continue
            found.append(label)
    for m in _CARD_CANDIDATE.finditer(prompt):
        digits = re.sub(r"[ -]", "", m.group(0))
        if digits not in _TEST_CARDS and len(digits) in (13, 14, 15, 16, 19) \
                and _CARD_IIN.match(digits) and _luhn_ok(digits):
            found.append("Payment card (PCI)")
    return sorted(set(found))


def main() -> int:
    if os.environ.get("DLP_ALLOW_PROMPT_SECRETS", "").strip() in ("1", "true", "yes"):
        return 0
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    prompt = data.get("prompt", "")
    if not prompt or "dlp-ok" in prompt:
        return 0

    found = _findings(prompt)
    if found:
        print(
            "BLOCKED (prompt DLP): your prompt appears to contain "
            f"{', '.join(found)}. Sending it would put the value into the model "
            "context, transcript, and logs. Redact it and resubmit -- or set "
            "DLP_ALLOW_PROMPT_SECRETS=1 / include 'dlp-ok' to override.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
