"""PreToolUse hook: flag common insecure code patterns (Write / Edit).

Reads the tool-call JSON from stdin. Exits 2 to block high-severity patterns.
Exits 0 and prints a warning to stderr for medium-severity patterns.

Covers a subset of OWASP Top 10 (2021) categories:
  A02 – Cryptographic Failures: weak algorithms (MD5/SHA-1 for security, DES, ECB mode)
  A03 – Injection: eval/exec, subprocess with shell=True, raw SQL string concat
  A05 – Security Misconfiguration: DEBUG=True, ALLOWED_HOSTS=['*']
  A08 – Software and Data Integrity: pickle.loads, yaml.load without Loader

Additionally covers:
  XSS (JS/TS): innerHTML assignment, document.write(), dangerouslySetInnerHTML

What this hook does NOT cover (out of scope — handle elsewhere):
  - SSRF, IDOR, broken access control (A01, A04) — require runtime context
  - Dependency vulnerabilities (A06) — use a dedicated deps-audit tool
  - Authentication / session management flaws (A07) — require design review
  - CORS misconfiguration — use a linter rule
  - Path traversal, command injection via complex multi-step flows
  - Any runtime or logic-level security properties

Escape hatches:
  - Lines containing ``# nosec`` are skipped (per-line opt-out)
  - Paths matching test/examples/docs/fixtures patterns downgrade HIGH→WARN

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_unsafe_patterns.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import re
import sys

# Paths that downgrade HIGH severity to a warning instead of a block
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

# Each entry: (severity, regex, human message)
# severity "HIGH" → exit 2 (block), "WARN" → exit 0 + stderr
_PATTERNS: list[tuple[str, str, str]] = [
    # A03 – Injection
    (
        "HIGH",
        r"\beval\s*\(",
        "A03 Injection: eval() executes arbitrary code. "
        "Replace with a safe alternative (ast.literal_eval for data, explicit dispatch for logic).",
    ),
    (
        "HIGH",
        r"\bexec\s*\(",
        "A03 Injection: exec() executes arbitrary code. "
        "Replace with a safe alternative.",
    ),
    (
        "HIGH",
        r"\bsubprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True",
        "A03 Injection: subprocess with shell=True is vulnerable to shell injection. "
        "Pass a list of args instead and remove shell=True.",
    ),
    (
        "HIGH",
        r'(?:execute|cursor\.execute)\s*\(\s*["\'].*%[s|d].*["\']|(?:execute|cursor\.execute)\s*\(\s*f["\']',
        "A03 Injection: raw SQL string formatting is vulnerable to SQL injection. "
        "Use parameterised queries with placeholders.",
    ),
    # A02 – Cryptographic Failures
    (
        "WARN",
        r"\bhashlib\.md5\b",
        "A02 Cryptographic Failure: MD5 is cryptographically broken. "
        "If used for security (passwords, signatures), switch to SHA-256 or bcrypt. "
        "If used only for checksums/dedup, add # nosec to suppress.",
    ),
    (
        "WARN",
        r"\bhashlib\.sha1\b",
        "A02 Cryptographic Failure: SHA-1 is cryptographically weak. "
        "For security purposes use SHA-256+. Add # nosec if this is a non-security checksum.",
    ),
    (
        "HIGH",
        r"\bDES\b|\bDES3\b|\bTripleDES\b",
        "A02 Cryptographic Failure: DES/3DES is deprecated and insecure. "
        "Use AES-256 instead.",
    ),
    (
        "HIGH",
        r"\bMODE_ECB\b|\.MODE_ECB\b|[\"']ECB[\"']",
        "A02 Cryptographic Failure: ECB mode leaks patterns in ciphertext. "
        "Use CBC, GCM, or another authenticated mode.",
    ),
    # A05 – Security Misconfiguration
    (
        "HIGH",
        r"\bDEBUG\s*=\s*True\b",
        "A05 Security Misconfiguration: DEBUG=True must never reach production — "
        "it exposes stack traces and internal config. Guard behind an env check.",
    ),
    (
        "HIGH",
        r"ALLOWED_HOSTS\s*=\s*\[\s*['\"]?\*['\"]?\s*\]",
        "A05 Security Misconfiguration: ALLOWED_HOSTS=['*'] allows any host header. "
        "List only the specific hostnames this service responds to.",
    ),
    # A08 – Software and Data Integrity
    (
        "HIGH",
        r"\bpickle\.loads?\s*\(",
        "A08 Data Integrity: pickle.loads() on untrusted data executes arbitrary code. "
        "Use JSON, msgpack, or another safe serialisation format.",
    ),
    (
        "HIGH",
        r"\byaml\.load\s*\((?![^)]*\bLoader\s*=)",
        "A08 Data Integrity: yaml.load() without an explicit Loader executes arbitrary Python. "
        "Use yaml.safe_load() or pass Loader=yaml.SafeLoader.",
    ),
    # XSS – JS/TS
    (
        "HIGH",
        r"\.innerHTML\s*=",
        "XSS: innerHTML assignment can execute injected scripts. "
        "Use textContent for plain text, or sanitise HTML with DOMPurify before assignment.",
    ),
    (
        "HIGH",
        r"\bdocument\.write\s*\(",
        "XSS: document.write() is unsafe and obsolete. "
        "Use DOM methods (createElement / appendChild) instead.",
    ),
    (
        "HIGH",
        r"\bdangerouslySetInnerHTML\b",
        "XSS: dangerouslySetInnerHTML bypasses React's XSS protection. "
        "Sanitise content with DOMPurify before use.",
    ),
]


def _is_lenient_path(path: str) -> bool:
    for p in _LENIENT_PATH_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def _check_content(content: str, path: str = "") -> tuple[int, list[str]]:
    """Return (exit_code, messages). exit_code 2=block, 0=warn-only or clean."""
    lenient = _is_lenient_path(path)
    lines = content.splitlines()
    exit_code = 0
    messages: list[str] = []

    for severity, pattern, message in _PATTERNS:
        for line in lines:
            if "# nosec" in line:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                effective = "WARN" if (lenient and severity == "HIGH") else severity
                prefix = "BLOCKED" if effective == "HIGH" else "WARNING"
                messages.append(f"{prefix}: {message}")
                if effective == "HIGH":
                    exit_code = 2
                break  # one message per pattern is enough

    return exit_code, messages


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

    exit_code, messages = _check_content(content, path)
    for msg in messages:
        print(msg, file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
