"""PreToolUse hook: warn when print/log/logger calls reference PII-shaped variables.

Reads tool-call JSON from stdin. Exits 0 always (warn-only); writes to stderr.
Applies to Python files only.

PII in logs is a common compliance failure -- logs are aggregated, indexed,
and retained, often outside the regulated data perimeter. Catch obvious cases
at write time.

Detects:
  print(..., user.email, ...)
  logger.info(f"... {ssn} ...")
  log.debug("phone: " + phone)
  print(f"... {patient.dob} ...")

PII tokens flagged (substring match on variable / attribute names):
  email, ssn, social_security, dob, date_of_birth, phone, mobile,
  address, street_address, credit_card, card_number, cvv, ccn,
  passport, drivers_license, license_number, mrn, medical_record,
  patient_name, full_name, first_name, last_name, ip_address

False positives:
  Lines containing `redact`, `mask`, `hash`, `obfuscate`, `pseudo`, `anon`
  are skipped (assumed already de-identified).

Escape hatch:
  Per-line ``# pii-ok`` comment skips the line.

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_pii_in_logs.py\""}]
  }
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
]

_PII_TOKENS = (
    "email",
    "ssn",
    "social_security",
    "dob",
    "date_of_birth",
    "phone",
    "mobile",
    "street_address",
    "credit_card",
    "card_number",
    "cvv",
    "ccn",
    "passport",
    "drivers_license",
    "license_number",
    "mrn",
    "medical_record",
    "patient_name",
    "full_name",
)

_SAFE_TOKENS = (
    "redact",
    "mask",
    "hash",
    "obfuscate",
    "pseudo",
    "anon",
    "_id",  # mrn_id, patient_id are typically opaque identifiers, not raw PII
)

# Lines that are print / log / logger calls.
_LOG_CALL = re.compile(
    r"^\s*(?:print|logging\.\w+|log\.\w+|logger\.\w+|"
    r"\w*log\w*\.\w+|sys\.stderr\.write|sys\.stdout\.write)\s*\(",
    re.IGNORECASE,
)


def _is_lenient_path(path: str) -> bool:
    for p in _LENIENT_PATH_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def _line_has_pii(line: str) -> tuple[bool, list[str]]:
    lower = line.lower()
    if any(safe in lower for safe in _SAFE_TOKENS):
        return False, []
    found: list[str] = []
    for tok in _PII_TOKENS:
        # Word boundary on left; allow dot-access or underscore on right.
        if re.search(rf"\b{re.escape(tok)}\b", lower):
            found.append(tok)
    return bool(found), found


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
    findings: list[tuple[int, list[str], str]] = []

    for idx, line in enumerate(content.splitlines(), start=1):
        if "# pii-ok" in line or "# nosec" in line:
            continue
        if not _LOG_CALL.match(line):
            continue
        has_pii, tokens = _line_has_pii(line)
        if has_pii:
            findings.append((idx, tokens, line.strip()[:120]))

    if findings:
        severity = "NOTE" if lenient else "WARNING"
        print(
            f"{severity} (PII in logs): {len(findings)} log/print call(s) "
            f"reference PII-shaped variables. Logs are aggregated, indexed, and "
            f"retained -- often outside the regulated data perimeter. Redact, "
            f"mask, or hash before logging. Suppress per-line with '# pii-ok'.",
            file=sys.stderr,
        )
        for line_no, tokens, snippet in findings[:5]:
            print(
                f"  line {line_no}: [{', '.join(tokens)}] {snippet}",
                file=sys.stderr,
            )
        if len(findings) > 5:
            print(f"  ... and {len(findings) - 5} more", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
