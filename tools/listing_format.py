#!/usr/bin/env python
"""Keep blank lines minimal in fenced ```python listings.

The book favors dense listings: at most one blank line in a row, and no blank
line between import groups (imports stay grouped and sorted, just without the
separator). Two gaps make this hard to maintain by hand:

  * Ruff enforces the import layout on the extracted .py files, but it cannot
    fix the Markdown source, and it does not check blank-line counts between
    defs at all.

So this tool checks the Markdown directly. It is string-aware: blank lines
inside triple-quoted strings are never touched. Only ```python blocks are
inspected; prose, indented output blocks, and other fences are left alone.

Default mode reports offending blank lines and exits non-zero, so it works as a
gate (run by `make listings`, part of the `gate` recipe). Pass --fix to remove
them (run by `make fix-listings`).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

_FENCE = re.compile(r"^\s*```")
_PY_OPEN = re.compile(r"^\s*```python\s*$")


def _in_string(lines: list[str]) -> list[bool]:
    """For each line, whether it STARTS inside a triple-quoted string."""
    out: list[bool] = []
    triple: str | None = None
    for line in lines:
        out.append(triple is not None)
        i, n = 0, len(line)
        sq = dq = False
        while i < n:
            c = line[i]
            if triple:
                if line.startswith(triple, i):
                    i += 3
                    triple = None
                    continue
                i += 1
                continue
            if sq:
                i += 2 if c == "\\" else 1
                if c == "'":
                    sq = False
                continue
            if dq:
                i += 2 if c == "\\" else 1
                if c == '"':
                    dq = False
                continue
            if c == "#":
                break
            if line.startswith("'''", i) or line.startswith('"""', i):
                triple = line[i:i + 3]
                i += 3
                continue
            if c == "'":
                sq = True
                i += 1
                continue
            if c == '"':
                dq = True
                i += 1
                continue
            i += 1
    return out


def _is_import(line: str) -> bool:
    s = line.strip()
    return s.startswith("import ") or (s.startswith("from ") and " import " in s)


def _removals(block: list[str]) -> list[tuple[int, str]]:
    """Block-line indices to remove, with a reason.

    A run of blank lines between two imports collapses to nothing; any other
    run of two or more blank lines collapses to one. Blank lines inside a
    string are never counted.
    """
    in_str = _in_string(block)
    n = len(block)

    def blank(i: int) -> bool:
        return block[i].strip() == "" and not in_str[i]

    out: list[tuple[int, str]] = []
    i = 0
    while i < n:
        if not blank(i):
            i += 1
            continue
        j = i
        while j < n and blank(j):
            j += 1
        between_imports = (
            i > 0 and j < n and _is_import(block[i - 1]) and _is_import(block[j]))
        if between_imports:
            out.extend((k, "blank line between imports") for k in range(i, j))
        elif j - i >= 2:
            out.extend(
                (k, "more than one blank line") for k in range(i + 1, j))
        i = j
    return out


def check_file(path: Path, fix: bool) -> list[tuple[int, str]]:
    """Return (line_number, reason) findings; rewrite the file if `fix`."""
    lines = path.read_text(encoding="utf-8").split("\n")
    findings: list[tuple[int, str]] = []
    drop: set[int] = set()  # absolute line indices to remove
    i, n = 0, len(lines)
    while i < n:
        if not _PY_OPEN.match(lines[i]):
            i += 1
            continue
        start = i + 1
        j = start
        while j < n and not _FENCE.match(lines[j]):
            j += 1
        block = lines[start:j]
        for idx, reason in _removals(block):
            findings.append((start + idx + 1, reason))  # 1-based line number
            drop.add(start + idx)
        i = j + 1

    if fix and drop:
        kept = [ln for k, ln in enumerate(lines) if k not in drop]
        path.write_text("\n".join(kept), encoding="utf-8", newline="\n")
    return findings


def _iter_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        files.extend(sorted(path.glob("*.md")) if path.is_dir() else [path])
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files or directories (default: Markdown/)")
    ap.add_argument("--fix", action="store_true",
                    help="remove the offending blank lines in place")
    args = ap.parse_args(argv)

    files = _iter_files(args.paths or ["Markdown"])
    total = 0
    for path in files:
        for lineno, reason in check_file(path, args.fix):
            if not args.fix:
                print(f"{path}:{lineno}: {reason}")
            total += 1

    if total and args.fix:
        print(f"Removed {total} blank line(s).")
        return 0
    if total:
        print(f"\n{total} blank-line issue(s). Fix with: "
              "python tools/listing_format.py --fix")
        return 1
    print("Listings OK: blank lines are minimal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
