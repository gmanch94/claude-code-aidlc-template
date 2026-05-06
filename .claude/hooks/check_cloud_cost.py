"""PreToolUse hook: warn on high-cost cloud resource configurations (Write / Edit).

Reads the tool-call JSON from stdin. Exits 0 (warn-only — never blocks).
Cost is context-dependent; the hook surfaces the risk, the user decides.

Covers:
  Expensive compute: EC2/EKS instance families p4d, p3dn, p3.8xl+, x1, x1e,
    u-*tb1 bare-metal, g5.48xlarge, inf2.48xlarge
  Expensive databases: RDS/Aurora instance classes db.x1e, db.x2g,
    db.r6g.16xlarge, db.r5.24xlarge, db.r5b.24xlarge, db.r6i.32xlarge,
    db.r7g.16xlarge
  Deletion protection disabled: deletion_protection = false on a database
    resource (losing a prod DB is expensive to recover)
  Public RDS endpoint: publicly_accessible = true increases attack surface
    and often indicates a misconfigured, over-provisioned setup

NOT covered (too contextual for regex):
  - Missing auto-scaling (can't infer expected load)
  - Spot vs on-demand choice (depends on workload type)
  - S3 lifecycle policies (depends on data retention requirements)
  - Reserved vs on-demand billing (account-level config, not IaC)
  - Cost allocation tags (project-specific naming convention)

Escape hatches:
  - Lines with ``# cost-ok`` or ``# noqa-cost`` are skipped
  - Paths matching test/example/docs patterns skip the expensive-instance check
    (test fixtures legitimately reference large instance types)

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Write|Edit:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check_cloud_cost.py\""}]
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

# Each entry: (regex, human message)
# All warnings — never blocks. Per-line # cost-ok suppresses.
_WARN_PATTERNS: list[tuple[str, str]] = [
    # Expensive EC2 / EKS instance families
    (
        r"\b(p4d|p3dn|p3\.(8|16)xlarge|x1e?\.\w+|u-\d+tb1\.\w+|g5\.48xlarge|inf2\.48xlarge)\b",
        "COST WARNING: High-cost compute instance type detected. "
        "Verify this is intentional and not left over from a test. "
        "Add # cost-ok to suppress if confirmed.",
    ),
    # Expensive RDS / Aurora instance classes
    (
        r"\bdb\.(x1e|x2g|r6g\.16xlarge|r5\.24xlarge|r5b\.24xlarge|r6i\.32xlarge|r7g\.16xlarge)\b",
        "COST WARNING: High-cost RDS/Aurora instance class detected. "
        "Confirm this tier is required for the expected workload. "
        "Add # cost-ok to suppress if confirmed.",
    ),
    # Deletion protection explicitly disabled on a database
    (
        r"\bdeletion_protection\s*=\s*false\b",
        "COST WARNING: deletion_protection = false on a database resource. "
        "Recovering from accidental deletion is expensive and slow. "
        "Set to true unless this is a disposable dev/test instance.",
    ),
    # RDS publicly accessible
    (
        r"\bpublicly_accessible\s*=\s*true\b",
        "COST + SECURITY WARNING: publicly_accessible = true exposes the database "
        "endpoint to the internet. Use a VPC private subnet + bastion/VPN instead.",
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

    lenient = _is_lenient_path(path)
    lines = content.splitlines()

    for pattern, message in _WARN_PATTERNS:
        # Skip expensive-instance check for test/example paths; keep
        # deletion_protection and publicly_accessible checks everywhere.
        is_instance_check = "instance" in message.lower() or "class" in message.lower()
        if lenient and is_instance_check:
            continue

        for line in lines:
            if "# cost-ok" in line or "# noqa-cost" in line:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                print(message, file=sys.stderr)
                break  # one message per pattern

    return 0


if __name__ == "__main__":
    sys.exit(main())
