#!/usr/bin/env python3
"""DLP scanner for CI: block secrets / PII / PCI and exact-match fingerprints in a diff.

Two independent detectors over ADDED lines (default) or the whole tree (--all):

1. Pattern scan  -- secret shapes, US SSN, Luhn-valid payment cards, keyword-gated
   high-entropy strings. Mirrors .claude/hooks/scan_secrets.py (kept in sync by
   hand; each is self-contained so a break in one can't disable the other).

2. Exact-data-match (fingerprint) -- SHA-256 of known-sensitive tokens (a canary
   string, a specific customer email, an internal hostname) listed as HASHES ONLY
   in .claude/dlp/fingerprints.txt. The raw sensitive data never enters the repo;
   the scanner hashes each candidate token in the diff and checks membership.

Exit 1 on any finding (fails the PR); exit 0 clean. Findings print as
`path:line: [CLASS] detail` plus a GitHub `::error` annotation.

Usage:
  python scripts/dlp_fingerprint_scan.py            # scan added lines in the diff
  python scripts/dlp_fingerprint_scan.py --all      # scan all tracked text files
Base ref for the diff: $DLP_DIFF_BASE, else $GITHUB_BASE_REF, else HEAD~1.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_FINGERPRINT_FILE = _REPO / ".claude" / "dlp" / "fingerprints.txt"

# --- pattern set (mirrors scan_secrets.py) -----------------------------------
_SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"\bASIA[0-9A-Z]{16}\b", "AWS session token"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "GitHub token"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "Slack token"),
    (r"\bsk-[A-Za-z0-9_-]{32,}\b", "OpenAI/Anthropic-style key"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "Google API key"),
    (r"\bsk_live_[0-9A-Za-z]{24,}\b", "Stripe live key"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----", "Private key block"),
]
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_ENTROPY_ASSIGN = re.compile(
    r"(?i)\b(?:secret|token|passwd|password|api[_-]?key|apikey|"
    r"access[_-]?key|auth[_-]?token|client[_-]?secret)\b"
    r"\s*[:=]\s*['\"]?([A-Za-z0-9+/_\-]{20,})['\"]?"
)
_CARD_IIN = re.compile(
    r"^(?:4|5[1-5]|2(?:2[2-9]|[3-6]\d|7[01]|720)|3[47]|6011|65|64[4-9]|35\d\d|30[0-5]|3[689])"
)
_CARD_CANDIDATE = re.compile(r"(?<![\d.])(?:\d[ -]?){12,18}\d(?![\d.])")
_TOKEN = re.compile(r"[A-Za-z0-9._@+/-]{8,}")
_PLACEHOLDERS = ("EXAMPLE", "XXXXXX", "000000", "your-", "YOUR-", "REPLACE", "REDACTED", "redacted")
_TEST_CARDS = {
    "4111111111111111", "4012888888881881", "4242424242424242", "5555555555554444",
    "5105105105105100", "2223003122003222", "378282246310005", "371449635398431",
    "6011111111111117", "6011000990139424", "3530111333300000", "3566002020360505",
    "30569309025904", "38520000023237",
}
_LINE_OPT_OUT = ("# dlp-ok", "# nosec", "# pii-ok")
_TEXT_EXCLUDE = re.compile(r"\.(png|jpe?g|gif|webp|ico|pdf|zip|gz|tar|woff2?|ttf|eot|mp4|mov)$", re.I)
# Mirror scan_secrets.py: in example/doc paths, PLACEHOLDER shapes are expected, so
# the pattern detectors are skipped there. Fingerprint (exact-value) matching still
# runs on EVERY path -- a known-sensitive value must never appear, even in a doc.
_EXAMPLE_PATHS = (".env.example", "readme.md", "/docs/", "/tests/fixtures/")


def _is_example_path(path: str) -> bool:
    p = path.replace("\\", "/").lower()
    return p.endswith(".example") or any(frag in p for frag in _EXAMPLE_PATHS)


def _is_placeholder(text: str) -> bool:
    if any(tok in text for tok in _PLACEHOLDERS):
        return True
    if re.search(r"123456|234567|345678|456789|567890|abcdef|ABCDEF", text):
        return True
    if re.search(r"(.)\1{5,}", text):
        return True
    return False


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


def _shannon_bits(s: str) -> float:
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())


def _load_fingerprints() -> set[str]:
    try:
        text = _FINGERPRINT_FILE.read_text(encoding="utf-8")
    except OSError:
        return set()
    out: set[str] = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip().lower()
        if re.fullmatch(r"[0-9a-f]{64}", line):
            out.add(line)
    return out


def scan_line(line: str, fingerprints: set[str], example_path: bool = False) -> list[str]:
    """Return a list of finding labels for one line of added content."""
    if any(tok in line for tok in _LINE_OPT_OUT):
        return []
    found: list[str] = []
    # Key / PEM secrets: run on ALL paths (a real key doesn't belong in a doc);
    # documented test vectors are exempted by _is_placeholder.
    for pattern, label in _SECRET_PATTERNS:
        for m in re.finditer(pattern, line):
            if not _is_placeholder(m.group(0)):
                found.append(label)
    # SSN / card / entropy: skipped in example/doc paths where placeholders live.
    if not example_path:
        for m in _SSN_RE.finditer(line):
            v = m.group(0)
            if not _is_placeholder(v) and _valid_ssn(v):
                found.append("US SSN")
        for m in _CARD_CANDIDATE.finditer(line):
            digits = re.sub(r"[ -]", "", m.group(0))
            if digits not in _TEST_CARDS and len(digits) in (13, 14, 15, 16, 19) \
                    and _CARD_IIN.match(digits) and _luhn_ok(digits):
                found.append(f"Payment card (PCI) ...{digits[-4:]}")
        for m in _ENTROPY_ASSIGN.finditer(line):
            val = m.group(1)
            if not _is_placeholder(val) and _shannon_bits(val) >= 4.0:
                found.append("High-entropy secret")
    if fingerprints:
        for m in _TOKEN.finditer(line):
            if hashlib.sha256(m.group(0).encode("utf-8")).hexdigest() in fingerprints:
                found.append("Fingerprint match (known-sensitive value)")
    return found


def _iter_added_lines(diff_text: str):
    path, new_lineno = None, 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            p = p[2:] if p.startswith("b/") else p
            path = None if p == "/dev/null" else p
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            new_lineno = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            if path:
                yield path, new_lineno, line[1:]
            new_lineno += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif line.startswith(" "):
            new_lineno += 1


def _diff_base() -> str:
    base = os.environ.get("DLP_DIFF_BASE") or os.environ.get("GITHUB_BASE_REF") or ""
    base = base.strip()
    if base and "/" not in base and not re.match(r"^[0-9a-f]{7,40}$", base):
        base = f"origin/{base}"
    return base or "HEAD~1"


def _git(*args: str) -> str:
    # Force UTF-8 decode: git output (diffs of any file) contains bytes the
    # Windows default (cp1252) can't decode, which otherwise crashes the reader
    # thread and yields None. errors="replace" keeps a benign diff scannable.
    return subprocess.run(
        ["git", *args], cwd=_REPO, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    ).stdout or ""


def _scan_diff(fingerprints: set[str]) -> list[str]:
    base = _diff_base()
    diff = _git("diff", "--unified=0", "--no-color", f"{base}...HEAD")
    if not diff:
        diff = _git("diff", "--unified=0", "--no-color", "HEAD~1...HEAD")
    findings: list[str] = []
    for path, lineno, text in _iter_added_lines(diff):
        if _TEXT_EXCLUDE.search(path):
            continue
        for label in scan_line(text, fingerprints, _is_example_path(path)):
            findings.append(f"{path}:{lineno}: [{label}]")
    return findings


def _scan_all(fingerprints: set[str]) -> list[str]:
    files = _git("ls-files").splitlines()
    findings: list[str] = []
    for path in files:
        if _TEXT_EXCLUDE.search(path):
            continue
        try:
            content = (_REPO / path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        example = _is_example_path(path)
        for idx, text in enumerate(content.splitlines(), start=1):
            for label in scan_line(text, fingerprints, example):
                findings.append(f"{path}:{idx}: [{label}]")
    return findings


def main() -> int:
    fingerprints = _load_fingerprints()
    scan_all = "--all" in sys.argv[1:]
    findings = _scan_all(fingerprints) if scan_all else _scan_diff(fingerprints)

    if findings:
        print(f"DLP scan FAILED -- {len(findings)} finding(s):", file=sys.stderr)
        for f in findings:
            path, rest = f.split(":", 1)
            print(f"::error file={path}::DLP: {rest}")
            print(f"  {f}", file=sys.stderr)
        print(
            "\nIf a finding is a false positive, add '# dlp-ok' on the line, or "
            "use a placeholder marker (EXAMPLE / YOUR- / REDACTED).",
            file=sys.stderr,
        )
        return 1

    scope = "tree" if scan_all else "diff"
    print(f"DLP scan clean ({scope}); {len(fingerprints)} fingerprint(s) loaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
