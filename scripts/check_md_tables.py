#!/usr/bin/env python3
"""Markdown table pipe-integrity gate (markdown-render-gotchas.md).

Detects GFM tables whose header/data rows parse to a DIFFERENT unescaped-pipe
cell count than their delimiter row. Under GitHub's GFM renderer (cmark-gfm),
every unescaped ``|`` is a cell delimiter - INCLUDING pipes inside code spans and
math (``| y - y_hat |`` absolute value, ``dict | None`` type unions). An in-cell
literal pipe therefore shreds the row: cells shift columns and trailing-column
content is silently dropped.

Pure text analysis; equivalent to the renderer for this bug class (verified
against the GitHub Markdown API). No network, no rate limit - scans every .md.

Exit status:
  * ERROR (exit 1) on the SHRED class  - row has MORE cells than the delimiter
    (unescaped in-cell pipe). This is the corruption. Fix: escape as ``\\|``.
  * WARNING (exit 0) on the SHORT class - row has FEWER cells than the delimiter
    (missing value). GFM pads a blank trailing cell; the table still renders.

Mirrors the /doc-ci-check skill; keep this and .github/workflows/doc-ci.yml in
sync (see that file's header).
"""
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "scratch", "checkpoints", ".claude-checkpoints"}
DELIM_CELL = re.compile(r"^\s*:?-{1,}:?\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def cell_count(line: str) -> int:
    """GFM cell count: neutralize escaped pipes, drop optional edge pipes, count."""
    s = line.strip()
    s = s.replace("\\|", " ").replace("&#124;", " ")  # escaped -> not a delimiter
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return s.count("|") + 1


def is_delim(line: str) -> bool:
    if "|" not in line:  # guard: hrule '---' / YAML frontmatter
        return False
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return all(DELIM_CELL.match(c) for c in s.split("|"))


def iter_md(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                yield os.path.join(dirpath, fn)


def scan(path: str, root: str):
    rel = os.path.relpath(path, root).replace("\\", "/")
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = [ln.rstrip("\r") for ln in fh.read().split("\n")]
    fenced = False
    errors, warnings = [], []
    for i, ln in enumerate(lines):
        if FENCE.match(ln):
            fenced = not fenced
            continue
        if fenced or i == 0 or not is_delim(ln):
            continue
        header = lines[i - 1]
        if not header or "|" not in header:  # delimiter needs a real header row
            continue
        cols = cell_count(ln)
        rows = [(i, header)]  # 1-based header line == index i (delim is i+1)
        j = i + 1
        while j < len(lines):
            d = lines[j]
            if d.strip() == "" or FENCE.match(d) or "|" not in d:
                break
            rows.append((j + 1, d))
            j += 1
        for n, row in rows:
            c = cell_count(row)
            if c > cols:
                errors.append(
                    f"::error file={rel},line={n}::stray-pipe phantom cells - "
                    f"table has {cols} columns but this row parses to {c}; an "
                    f"unescaped '|' inside a cell is shredding it (escape as \\|)"
                )
            elif c < cols:
                warnings.append(
                    f"::warning file={rel},line={n}::table row has {c} cells but "
                    f"the table has {cols} columns - GFM pads a blank cell "
                    f"(missing value?)"
                )
    return errors, warnings


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    all_err, all_warn = [], []
    for path in iter_md(root):
        e, w = scan(path, root)
        all_err.extend(e)
        all_warn.extend(w)
    for line in all_err + all_warn:
        print(line)
    print(f"\nmd-table-integrity: {len(all_err)} error(s), {len(all_warn)} warning(s)")
    return 1 if all_err else 0


if __name__ == "__main__":
    sys.exit(main())
