"""PreToolUse hook: gate data-exfiltration-shaped Bash commands by destination host.

DLP egress control. Flags commands that SEND data to a host -- the shapes that
move bytes OUT of the machine:

  curl / wget with an upload flag  (-d/--data*, -F/--form, -T/--upload-file,
    --json, -X POST|PUT|PATCH, --post-data/--post-file/--body-*)
  scp / rsync / sftp to a remote   [user@]host:path
  nc / ncat / netcat  host port

Plain downloads (curl/wget GET) are NOT flagged -- pulling bytes in is not
exfiltration. Git is intentionally OUT of scope: `git push` to a normal remote
is the most common dev op, and block_dangerous_git.py already owns dangerous git.

Enforcement is progressive, so wiring the hook never breaks a workflow on day one:
  - No allowlist file present -> WARN only (exit 0); tells you how to enforce.
  - Allowlist file present     -> BLOCK (exit 2) any exfil to a non-listed host.

Allowlist file: .claude/dlp/egress_allowlist.txt -- one host or dot-suffix per
line (`# comments` ok). A shipped .example is inert; rename it (drop `.example`)
to switch this hook from warn to block. Built-in always-allowed: localhost,
127.0.0.1, ::1, 0.0.0.0.

Escape hatches:
  - Append `# dlp-ok` to the command.
  - Set ALLOW_EGRESS=<host> (a named host, like ALLOW_PROD_WRITE) for one call;
    ALLOW_EGRESS=all disables the check (discouraged -- a set-once blanket flag
    is the whole problem).

Host extraction is regex over the literal command and covers explicit URLs,
scheme-less curl/wget targets, scp/rsync/sftp remotes, and nc. A destination
hidden behind $VAR, $(subshell), or piped stdin can't be read -- so when an
exfil-shaped command yields NO confirmable host, the hook fails CLOSED in enforce
mode (blocks) and warns in warn mode, rather than waving it through. This catches
accidents and obvious exfil; a determined adversary who can already run arbitrary
bash is out of scope. Command SHAPES are matched the way the sibling Bash hooks
match theirs.

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Bash:
  {
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_egress_allowlist.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_DEFAULT_ALLOW = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}

# curl upload flags => an OUTBOUND request body.
_CURL_UPLOAD = re.compile(
    r"(?:^|\s)(?:-d\b|--data(?:-raw|-binary|-urlencode)?\b|-F\b|--form\b|"
    r"-T\b|--upload-file\b|--json\b)"
)
_METHOD_WRITE = re.compile(
    r"(?:^|\s)(?:-X|--request)\s+(?:POST|PUT|PATCH|DELETE)\b", re.IGNORECASE
)
_WGET_UPLOAD = re.compile(
    r"(?:^|\s)--(?:post-data|post-file|body-data|body-file)\b|"
    r"(?:^|\s)--method=(?:POST|PUT|PATCH)\b",
    re.IGNORECASE,
)
_URL = re.compile(r"""https?://(?:[^/@\s"']+@)?([^/:\s"']+)""", re.IGNORECASE)
# Scheme-less curl/wget target: a bare host[:port][/path] token (curl defaults to
# http://). Requires a dotted domain or an IPv4 so it doesn't match flags/paths.
_BARE_HOST = re.compile(
    r"""(?:^|[\s"'=])(?:[A-Za-z0-9._%+-]+@)?"""
    r"""((?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}|\d{1,3}(?:\.\d{1,3}){3})"""
    r"""(?::\d+)?(?:/\S*)?(?=\s|$|["'])"""
)
# scp/rsync/sftp remote target: [user@]host:path  (not http:// -- lookahead bars //)
_REMOTE = re.compile(
    r"""(?:^|[\s"'=])(?:[A-Za-z0-9._%+-]+@)?([A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?):(?![/\\])"""
)
_NC = re.compile(
    r"\b(?:nc|ncat|netcat)\b\s+(?:-\S+\s+)*([A-Za-z0-9.-]+)\s+\d{1,5}\b"
)


def _is_exfil(cmd: str) -> bool:
    if re.search(r"\bcurl\b", cmd) and (
        _CURL_UPLOAD.search(cmd) or _METHOD_WRITE.search(cmd)
    ):
        return True
    if re.search(r"\bwget\b", cmd) and _WGET_UPLOAD.search(cmd):
        return True
    if re.search(r"\b(?:scp|sftp)\b", cmd):
        return True
    if re.search(r"\brsync\b", cmd) and _REMOTE.search(cmd):
        return True
    if _NC.search(cmd):
        return True
    return False


def _extract_hosts(cmd: str) -> list[str]:
    hosts: list[str] = []
    url_hosts = [m.group(1) for m in _URL.finditer(cmd)]
    hosts.extend(url_hosts)
    # Scheme-less curl/wget: only when there is no explicit http(s) URL (avoids
    # matching a domain that merely appears in a header / user-agent). curl's
    # target is its trailing URL arg, so take the LAST bare host in the command.
    if re.search(r"\b(?:curl|wget)\b", cmd) and not url_hosts:
        bare = [m.group(1) for m in _BARE_HOST.finditer(cmd)]
        if bare:
            hosts.append(bare[-1])
    if re.search(r"\b(?:scp|rsync|sftp)\b", cmd):
        for m in _REMOTE.finditer(cmd):
            hosts.append(m.group(1))
    for m in _NC.finditer(cmd):
        hosts.append(m.group(1))
    return hosts


def _find_allowlist() -> Path:
    # Anchor next to .claude/, not via CLAUDE_PROJECT_DIR (fragile on Windows).
    return Path(__file__).resolve().parent.parent / "dlp" / "egress_allowlist.txt"


def _load_allowlist(path: Path) -> set[str] | None:
    """Return the entry set if the file exists (enforce mode), else None (warn)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    entries: set[str] = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip().lower()
        if line:
            entries.add(line)
    return entries


def _host_allowed(host: str, allow: set[str]) -> bool:
    h = host.lower()
    for entry in allow:
        e = entry.lstrip(".")
        if h == e or h.endswith("." + e):
            return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd or "# dlp-ok" in cmd:
        return 0
    if not _is_exfil(cmd):
        return 0

    env_allow = os.environ.get("ALLOW_EGRESS", "")
    if env_allow.strip().lower() in ("1", "all", "*"):
        return 0

    allow = set(_DEFAULT_ALLOW)
    for h in re.split(r"[,\s]+", env_allow):
        if h:
            allow.add(h.lower())

    allowlist_path = _find_allowlist()
    file_entries = _load_allowlist(allowlist_path)
    enforce = file_entries is not None
    if file_entries:
        allow |= file_entries

    literal = [h for h in _extract_hosts(cmd) if h and "$" not in h and "`" not in h]
    if not literal:
        # Exfil shape but the destination could not be confirmed (scheme-less parse
        # failed, or the host is behind $VAR/subshell). In ENFORCE mode this is a
        # data-upload to an unverifiable host -- fail CLOSED, don't wave it through.
        detail = (
            "data-upload command detected but its destination host could not be "
            "confirmed (behind $VAR/subshell or an unparsed form)."
        )
        if enforce:
            print(
                f"BLOCKED (egress): {detail} Use an explicit URL and add the host to "
                f".claude/dlp/egress_allowlist.txt, append '# dlp-ok', or set "
                f"ALLOW_EGRESS=all.",
                file=sys.stderr,
            )
            return 2
        print(f"WARNING (egress): {detail} Verify the destination manually.", file=sys.stderr)
        return 0

    blocked = sorted({h for h in literal if not _host_allowed(h, allow)})
    if not blocked:
        return 0

    hostlist = ", ".join(blocked)
    if enforce:
        print(
            f"BLOCKED (egress): data-upload command targets non-allowlisted "
            f"host(s): {hostlist}. Add them to .claude/dlp/egress_allowlist.txt, "
            f"append '# dlp-ok', or set ALLOW_EGRESS={blocked[0]} for one call.",
            file=sys.stderr,
        )
        return 2

    print(
        f"WARNING (egress): data-upload command targets host(s) not on any "
        f"allowlist: {hostlist}. Create .claude/dlp/egress_allowlist.txt "
        f"(copy the .example) to ENFORCE -- non-listed egress will then block. "
        f"Append '# dlp-ok' to silence.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
