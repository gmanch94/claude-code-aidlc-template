#!/usr/bin/env python3
"""shadow_git_checkpoint.py — PreToolUse hook for Write|Edit|Bash mutations.

Snapshots the working tree to a SHADOW Git repo at .claude/checkpoints/
BEFORE every mutating tool call. Enables one-click rollback per tool call
without polluting the project's real Git history.

Mirrors Cline's shadow-Git checkpoint pattern (docs.cline.bot/features/checkpoints).
The shadow repo:
  - Is separate from the project's Git (.claude/checkpoints/.git, not .git)
  - Captures untracked files too (the project's .gitignore is respected by
    the project's .git; the shadow repo uses its own minimal .gitignore)
  - Commits one snapshot per tool call with the tool name + timestamp + a
    short summary as the commit message
  - Never pushes anywhere — local-only

Pair with `/rollback-checkpoint` skill for the rollback UX.

Exit codes:
  0 — checkpoint taken (or skipped: not a mutating tool, opt-out, init failure)
  Never blocks — this hook is passive and best-effort.

Opt-out: place a file `.claude/checkpoints/.disabled` to skip checkpointing.

Wiring (.claude/settings.json):
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Write|Edit|Bash",
          "hooks": [{ "type": "command",
                      "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/shadow_git_checkpoint.py\"" }]
        }
      ]
    }
  }

Stdlib only. Run-everywhere.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MUTATING_TOOLS = {"Write", "Edit", "Bash", "NotebookEdit"}
# Bash commands that are safe-to-skip (read-only). If the entire command matches
# one of these prefixes, no checkpoint is taken.
READ_ONLY_BASH_PREFIXES = (
    "ls ", "cat ", "head ", "tail ", "grep ", "find ",
    "git status", "git log", "git diff", "git show", "git branch",
    "git remote", "git rev-parse", "git ls-files", "pwd", "echo ",
    "which ", "type ", "wc ", "uname",
)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0  # malformed input; never block

    if not isinstance(payload, dict):
        return 0  # JSON parsed but not an object; defensive

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    if tool_name not in MUTATING_TOOLS:
        return 0

    # Skip read-only Bash
    if tool_name == "Bash":
        cmd = (tool_input.get("command") or "").strip()
        if not cmd or any(cmd.startswith(p) for p in READ_ONLY_BASH_PREFIXES):
            return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    project = Path(project_dir).resolve()
    shadow_root = project / ".claude" / "checkpoints"

    if (shadow_root / ".disabled").exists():
        return 0

    try:
        _ensure_shadow_repo(project, shadow_root)
        _snapshot(project, shadow_root, tool_name, tool_input)
    except Exception as exc:
        # Best-effort: never block on shadow failure
        sys.stderr.write(f"shadow_git_checkpoint: skipped ({exc})\n")
        return 0

    return 0


def _ensure_shadow_repo(project: Path, shadow_root: Path) -> None:
    shadow_root.mkdir(parents=True, exist_ok=True)
    git_dir = shadow_root / ".git"
    if git_dir.exists():
        return
    subprocess.run(
        ["git", "init", "--initial-branch=shadow", "--quiet"],
        cwd=str(shadow_root), check=True,
    )
    # Mirror .gitignore + add our own carve-outs for noisy paths the shadow
    # should not track. Keep small; the goal is fidelity to project state,
    # not pristine OSS-cleanliness.
    shadow_ignore = shadow_root / ".gitignore"
    shadow_ignore.write_text(
        "node_modules/\n"
        ".venv/\n"
        "venv/\n"
        ".pytest_cache/\n"
        "dist/\n"
        "build/\n"
        ".next/\n"
        ".turbo/\n"
        "__pycache__/\n"
        "*.pyc\n"
        ".DS_Store\n"
        ".claude/checkpoints/\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "-C", str(shadow_root), "config", "user.email", "shadow-checkpoint@local"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(shadow_root), "config", "user.name", "shadow-checkpoint"],
        check=True,
    )


def _snapshot(project: Path, shadow_root: Path, tool_name: str, tool_input: dict) -> None:
    # Sync project state into shadow repo via a working-tree mirror.
    # We use git --work-tree to point at the project dir while keeping
    # the shadow .git in .claude/checkpoints/.git.
    env = os.environ.copy()
    git_dir = shadow_root / ".git"
    work_tree_args = [
        "git",
        f"--git-dir={git_dir}",
        f"--work-tree={project}",
    ]

    # Stage everything; rely on shadow .gitignore + project .gitignore (git
    # respects the project's .gitignore when work-tree is the project root).
    subprocess.run(work_tree_args + ["add", "-A"], env=env, check=True)

    # If nothing changed since the last snapshot, skip.
    diff_check = subprocess.run(
        work_tree_args + ["diff", "--cached", "--quiet"],
        env=env,
    )
    if diff_check.returncode == 0:
        return  # no changes to snapshot

    summary = _summarize(tool_name, tool_input)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg = f"checkpoint {ts} | {tool_name} | {summary}"
    subprocess.run(
        work_tree_args + ["commit", "-m", msg, "--quiet", "--allow-empty"],
        env=env, check=True,
    )


def _summarize(tool_name: str, tool_input: dict) -> str:
    if tool_name in {"Write", "Edit", "NotebookEdit"}:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or "?"
        return f"{Path(path).name}"
    if tool_name == "Bash":
        raw = (tool_input.get("command") or "").strip()
        if not raw:
            return "bash"
        first_line = raw.splitlines()[0] if raw.splitlines() else raw
        return first_line[:80] or "bash"
    return "mutation"


if __name__ == "__main__":
    sys.exit(main())
