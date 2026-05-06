"""PreToolUse hook: block destructive infrastructure commands.

Reads the tool-call JSON from stdin. Exits 2 to block. Exits 0 to allow.

Blocks:
- ``terraform destroy``
- ``kubectl delete namespace/ns`` or ``kubectl delete ... --all``
- ``aws s3 rm`` with ``--recursive`` or a bare bucket path
- ``aws ec2 terminate-instances``
- ``aws rds delete-db-instance``
- ``aws eks delete-cluster``
- ``gcloud sql instances delete``
- ``gcloud compute instances delete``
- ``gcloud container clusters delete``
- ``az group delete`` (deletes all resources in a resource group)
- ``az vm delete``
- ``az sql db delete``

No escape hatch -- these operations always need explicit user
confirmation before Claude executes them. If the user explicitly
asked, tell them to run the command themselves.

HOW TO ENABLE:
  Wire in .claude/settings.json under PreToolUse / Bash:
  {
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_infra_destroy.py\""}]
  }
  See .claude/hooks/README.md for the full wiring snippet.
"""

from __future__ import annotations

import json
import re
import sys

PATTERNS: list[tuple[str, str]] = [
    # Terraform
    (
        r"\bterraform\s+destroy\b",
        "terraform destroy is destructive -- confirm with the user before running. "
        "Ask them to run it themselves if they explicitly want to proceed.",
    ),
    # Kubernetes -- mass / namespace deletion
    (
        r"\bkubectl\s+delete\s+(namespace|ns)\b",
        "kubectl delete namespace deletes all resources in the namespace -- "
        "confirm with the user before running.",
    ),
    (
        r"\bkubectl\s+delete\b[^|;&]*--all\b",
        "kubectl delete --all destroys all matching resources -- "
        "confirm with the user before running.",
    ),
    # AWS S3 -- recursive deletion or bare bucket
    (
        r"\baws\s+s3\s+rm\b[^|;&]*--recursive\b",
        "aws s3 rm --recursive deletes all objects in the path -- "
        "confirm with the user before running.",
    ),
    (
        r"\baws\s+s3\s+rm\s+s3://[^/\s]+/?(\s|$)",
        "aws s3 rm on a bare bucket root deletes all objects -- "
        "confirm with the user before running.",
    ),
    # AWS compute / data
    (
        r"\baws\s+ec2\s+terminate-instances\b",
        "aws ec2 terminate-instances permanently destroys EC2 instances -- "
        "confirm with the user before running.",
    ),
    (
        r"\baws\s+rds\s+delete-db-instance\b",
        "aws rds delete-db-instance deletes the database -- "
        "confirm with the user before running.",
    ),
    (
        r"\baws\s+eks\s+delete-cluster\b",
        "aws eks delete-cluster destroys the EKS cluster and its node groups -- "
        "confirm with the user before running.",
    ),
    # GCP
    (
        r"\bgcloud\s+sql\s+instances\s+delete\b",
        "gcloud sql instances delete destroys the Cloud SQL instance -- "
        "confirm with the user before running.",
    ),
    (
        r"\bgcloud\s+compute\s+instances\s+delete\b",
        "gcloud compute instances delete destroys GCE instances -- "
        "confirm with the user before running.",
    ),
    (
        r"\bgcloud\s+container\s+clusters\s+delete\b",
        "gcloud container clusters delete destroys the GKE cluster -- "
        "confirm with the user before running.",
    ),
    # Azure
    (
        r"\baz\s+group\s+delete\b",
        "az group delete destroys the resource group and everything inside it -- "
        "confirm with the user before running.",
    ),
    (
        r"\baz\s+vm\s+delete\b",
        "az vm delete destroys the Azure VM -- "
        "confirm with the user before running.",
    ),
    (
        r"\baz\s+sql\s+db\s+delete\b",
        "az sql db delete destroys the Azure SQL database -- "
        "confirm with the user before running.",
    ),
]


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd:
        return 0

    for pattern, message in PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(f"BLOCKED: {message}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
