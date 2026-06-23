#!/usr/bin/env python3
"""staleness_check.py — SessionStart hook.

Flags stale bookmarks at session start:
  1. NEXT_SESSION.md HEAD declaration vs current git HEAD (warn if >7 days
     behind master commits OR if explicit "Last working session: YYYY-MM-DD"
     is >30 days old)
  2. Any "(as of YYYY-MM-DD)" or "verified YYYY-MM-DD" stamps in repo-root
     markdown files (CLAUDE.md, README.md, NEXT_SESSION.md, LESSONS_LEARNED.md,
     operating-philosophy.md, analysis-methodology.md) that are >30 days old

Never blocks. Prints WARNINGs to stderr so the next session sees them in
its bootstrap output.

Pair with `/doc-ci-check` skill which catches the same drift in CI; this
hook surfaces it at session-start time so the human notices immediately.

Wiring (.claude/settings.json):
  {
    "hooks": {
      "SessionStart": [
        {
          "hooks": [{ "type": "command",
                      "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/staleness_check.py\"" }]
        }
      ]
    }
  }

Stdlib only. Exit 0 always (warn-only).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DOCS_TO_SCAN = (
    "CLAUDE.md", "README.md", "NEXT_SESSION.md", "LESSONS_LEARNED.md",
    "operating-philosophy.md", "analysis-methodology.md",
)
HEAD_RE = re.compile(r"HEAD\s*=\s*([a-f0-9]{7,40})", re.IGNORECASE)
LAST_SESSION_RE = re.compile(r"Last\s+working\s+session:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
DATE_STAMP_RE = re.compile(
    r"(?:as\s+of|verified|updated|refresh(?:ed)?|stamp(?:ed)?|snapshot|"
    r"current\s+as\s+of)\s+(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)

HEAD_STALE_DAYS = 7
DATE_STAMP_STALE_DAYS = 30


def main() -> int:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    project = Path(project_dir).resolve()

    today = datetime.now(timezone.utc).date()
    warnings: list[str] = []

    # Check NEXT_SESSION.md HEAD vs git HEAD
    ns = project / "NEXT_SESSION.md"
    if ns.exists():
        try:
            text = ns.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""

        m_head = HEAD_RE.search(text)
        if m_head:
            declared = m_head.group(1)
            try:
                actual = subprocess.check_output(
                    ["git", "rev-parse", f"--short={len(declared)}", "HEAD"],
                    cwd=str(project), text=True,
                ).strip()
                if declared != actual:
                    # Count commits between declared and actual (declared->actual on master/main)
                    drift_days = _commit_age_days(project, declared, actual, today)
                    if drift_days is not None and drift_days > HEAD_STALE_DAYS:
                        warnings.append(
                            f"NEXT_SESSION.md HEAD={declared} is ~{drift_days}d behind git HEAD={actual}. "
                            "Refresh the bookmark."
                        )
                    elif drift_days is None:
                        warnings.append(
                            f"NEXT_SESSION.md HEAD={declared} doesn't match git HEAD={actual}. "
                            "Verify or refresh."
                        )
            except Exception:
                pass

        m_last = LAST_SESSION_RE.search(text)
        if m_last:
            try:
                last = datetime.strptime(m_last.group(1), "%Y-%m-%d").date()
                age = (today - last).days
                if age > DATE_STAMP_STALE_DAYS:
                    warnings.append(
                        f"NEXT_SESSION.md 'Last working session: {m_last.group(1)}' is {age}d old "
                        f"(>{DATE_STAMP_STALE_DAYS}d). Refresh bookmark or confirm it's still current."
                    )
            except Exception:
                pass

    # Check date stamps in other repo docs
    for doc_name in DOCS_TO_SCAN:
        doc = project / doc_name
        if not doc.exists():
            continue
        try:
            text = doc.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for match in DATE_STAMP_RE.finditer(text):
            try:
                stamp = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                age = (today - stamp).days
                if age > DATE_STAMP_STALE_DAYS:
                    warnings.append(
                        f"{doc_name}: stamp '{match.group(0)}' is {age}d old "
                        f"(>{DATE_STAMP_STALE_DAYS}d). Re-verify or refresh."
                    )
            except Exception:
                continue

    if warnings:
        sys.stderr.write("STALENESS CHECK -- warnings (non-blocking):\n")
        for w in warnings:
            sys.stderr.write(f"  - {w}\n")

    return 0


def _commit_age_days(project: Path, sha: str, head_sha: str, today) -> int | None:
    """Return days between commit `sha` and today, or None if sha is missing."""
    try:
        iso = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", sha],
            cwd=str(project), text=True,
        ).strip()
        if not iso:
            return None
        # %cI is committer ISO-8601 strict; just take the date part
        commit_date = datetime.fromisoformat(iso).date()
        return (today - commit_date).days
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
