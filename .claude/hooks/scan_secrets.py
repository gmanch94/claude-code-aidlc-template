"""PreToolUse hook: block writes that contain secrets, PII, or payment-card data.

Extends the original secret-shape scanner with DLP data classes:
- Secrets (unchanged): AWS / GitHub / Slack / OpenAI / Anthropic / Google /
  Stripe key shapes and PEM private-key blocks. Content-wide, high-confidence.
- Keyword-gated high-entropy strings: a generic API token that does not match a
  known prefix but is assigned to a secret-ish name (key/token/secret/password).
- PII: US Social Security Numbers (dashed).
- PCI: Luhn-valid payment-card numbers carrying a real issuer prefix.

Low-recall by design -- only high-confidence shapes, so this stays a *block*
hook without drowning legitimate writes in false positives.

Escape hatches (any one allows the finding):
- Placeholder tokens inside the match (EXAMPLE, YOUR-, REDACTED, XXXX, 0000).
- Example/template paths (.env.example, README.md, docs/, tests/fixtures/).
- Canonical test payment cards (4111.., 4242.., Amex/Discover test PANs).
- Per-line ``# dlp-ok`` / ``# nosec`` / ``# pii-ok`` comment (PII / card / entropy).

Detection patterns for the secret + entropy + card classes mirror the DLP hooks
(scan_prompt_dlp.py, redact_tool_output.py) and scripts/dlp_fingerprint_scan.py.
Keep them in sync -- each hook is self-contained (stdlib only, no shared import)
so a broken module can't take down every guardrail at once.

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/scan_secrets.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter

# --- Secrets: content-wide, always block (unchanged behaviour) ---------------
SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"\bASIA[0-9A-Z]{16}\b", "AWS session token"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "GitHub token"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "Slack token"),
    (r"\bsk-[A-Za-z0-9_-]{32,}\b", "OpenAI/Anthropic-style key"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "Google API key"),
    (r"\bsk_live_[0-9A-Za-z]{24,}\b", "Stripe live key"),
    (
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
        "Private key block",
    ),
]

# --- PII: line-aware, block with per-line opt-out ----------------------------
PII_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "US SSN"),
]

# Keyword-gated high-entropy secret. Group 1 = the candidate secret value.
_ENTROPY_ASSIGN = re.compile(
    r"(?i)\b(?:secret|token|passwd|password|api[_-]?key|apikey|"
    r"access[_-]?key|auth[_-]?token|client[_-]?secret)\b"
    r"\s*[:=]\s*['\"]?([A-Za-z0-9+/_\-]{20,})['\"]?"
)
_ENTROPY_BITS_MIN = 4.0

# Canonical test PANs -- never block these (payment docs, fixtures use them).
_TEST_CARDS = {
    "4111111111111111", "4012888888881881", "4242424242424242",
    "5555555555554444", "5105105105105100", "2223003122003222",
    "378282246310005", "371449635398431", "6011111111111117",
    "6011000990139424", "3530111333300000", "3566002020360505",
    "30569309025904", "38520000023237",
}
# Real issuer prefixes -- a Luhn-valid run without one is almost never a card.
_CARD_IIN = re.compile(
    r"^(?:4|5[1-5]|2(?:2[2-9]|[3-6]\d|7[01]|720)|3[47]|"
    r"6011|65|64[4-9]|35\d\d|30[0-5]|3[689])"
)
_CARD_CANDIDATE = re.compile(r"(?<![\d.])(?:\d[ -]?){12,18}\d(?![\d.])")

_PLACEHOLDER_PATHS = (
    ".env.example", "readme.md", "/docs/", "/tests/fixtures/",
)
_PLACEHOLDER_TOKENS = (
    "EXAMPLE", "XXXXXX", "000000", "your-", "YOUR-",
    "REPLACE", "redacted", "REDACTED",
)
_LINE_OPT_OUT = ("# dlp-ok", "# nosec", "# pii-ok")


def _content_for(tool: str, ti: dict) -> str:
    if tool == "Edit":
        return str(ti.get("new_string", ""))
    if tool == "Write":
        return str(ti.get("content", ""))
    if tool == "NotebookEdit":
        return str(ti.get("new_source", ""))
    return ""


def _is_placeholder(text: str) -> bool:
    if any(tok in text for tok in _PLACEHOLDER_TOKENS):
        return True
    # Documented test vectors (e.g. an AKIA...1234567890... in a README smoke
    # test) carry sequential or heavily-repeated runs a real random key won't.
    if re.search(r"123456|234567|345678|456789|567890|abcdef|ABCDEF", text):
        return True
    if re.search(r"(.)\1{5,}", text):
        return True
    return False


def _valid_ssn(m: str) -> bool:
    """m == 'ddd-dd-dddd'. Reject reserved area/group/serial to cut false hits."""
    area, group, serial = m[:3], m[4:6], m[7:11]
    if area in ("000", "666") or area[0] == "9":
        return False
    return group != "00" and serial != "0000"


def _luhn_ok(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        d = ord(ch) - 48
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _looks_like_card(digits: str) -> bool:
    if len(digits) not in (13, 14, 15, 16, 19):
        return False
    if not _CARD_IIN.match(digits):
        return False
    return _luhn_ok(digits)


def _shannon_bits(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool = data.get("tool_name")
    if tool not in ("Edit", "Write", "NotebookEdit"):
        return 0
    ti = data.get("tool_input", {}) or {}
    path = str(ti.get("file_path") or ti.get("notebook_path") or "").replace("\\", "/")
    content = _content_for(tool, ti)
    if not content:
        return 0

    is_example_path = any(frag in path.lower() for frag in _PLACEHOLDER_PATHS)
    findings: list[str] = []

    # 1. Secrets (keys / PEM): high-confidence -- block on ANY path (incl. docs /
    #    fixtures / *.example) unless the value is a placeholder / test vector.
    #    A real key does not belong in a doc; documented vectors are exempted by
    #    _is_placeholder (sequential/repeated runs).
    for pattern, label in SECRET_PATTERNS:
        for m in re.finditer(pattern, content):
            text = m.group(0)
            if _is_placeholder(text):
                continue
            preview = text[:8] + "..." if len(text) > 8 else text
            findings.append(f"  - {label}: {preview} at offset {m.start()}")

    # 2. PII / PCI / entropy -- line-aware, per-line opt-out.
    if not is_example_path:
        for idx, line in enumerate(content.splitlines(), start=1):
            if any(tok in line for tok in _LINE_OPT_OUT):
                continue

            for pattern, label in PII_PATTERNS:
                for m in re.finditer(pattern, line):
                    val = m.group(0)
                    if _is_placeholder(val):
                        continue
                    if label == "US SSN" and not _valid_ssn(val):
                        continue
                    findings.append(f"  - {label}: line {idx} ({val})")

            for m in _CARD_CANDIDATE.finditer(line):
                digits = re.sub(r"[ -]", "", m.group(0))
                if digits in _TEST_CARDS:
                    continue
                if _looks_like_card(digits):
                    findings.append(
                        f"  - Payment card (PCI): line {idx} "
                        f"(...{digits[-4:]}, Luhn-valid)"
                    )

            for m in _ENTROPY_ASSIGN.finditer(line):
                val = m.group(1)
                if _is_placeholder(val):
                    continue
                bits = _shannon_bits(val)
                if bits >= _ENTROPY_BITS_MIN:
                    findings.append(
                        f"  - High-entropy secret: line {idx} "
                        f"({val[:6]}..., {bits:.1f} bits/char)"
                    )

    if findings:
        print(
            f"BLOCKED ({path}): possible secret / PII / PCI content detected. "
            f"If intentional, use placeholder markers (EXAMPLE / YOUR- / REDACTED), "
            f"write to .env.example / docs/, or add '# dlp-ok' on the line. Findings:",
            file=sys.stderr,
        )
        print("\n".join(findings), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
