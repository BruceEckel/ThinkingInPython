#!/usr/bin/env python
"""List `TODO(tag): ...` markers left in the book's Markdown.

A marker is an HTML comment, invisible in the rendered site (pandoc
strips HTML comments) but greppable in the source:

    <!-- TODO(py315-deps): NumPy has no Python 3.15 wheel yet. Once it
    does, convert this indented block to a real, fenced, tested example. -->

The tag in parentheses groups related markers (several `py315-deps`
markers all point at the same underlying blocker) and doubles as a plain
`grep -rn "TODO(py315-deps)" Chapters/` search when you only care about
one of them. This tool is informational, not a gate: it always exits 0,
and is not part of `verify`/`gate`/`ci`. Run it now and then, the same
way `make links` is, to see what is still waiting on something outside
the book's control.

Usage:
    python tools/list_todos.py            # every marker in Chapters/
    python tools/list_todos.py Chapters/18_Performance.md
"""

import argparse
import re
from pathlib import Path

from tools_repo import add_paths_arg, md_files

TODO_RE = re.compile(r"<!--\s*TODO\(([^)]+)\):\s*(.*?)-->", re.DOTALL)


def find_todos(path: Path) -> list[tuple[int, str, str]]:
    """(line, tag, note) for each TODO(...) marker in `path`, in order."""
    text = path.read_text(encoding="utf-8")
    found: list[tuple[int, str, str]] = []
    for m in TODO_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        tag = m.group(1).strip()
        note = " ".join(m.group(2).split())
        found.append((line, tag, note))
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    args = ap.parse_args(argv)

    total = 0
    for path in md_files(args.paths):
        for line, tag, note in find_todos(path):
            print(f"{path}:{line}: TODO({tag}): {note}")
            total += 1

    print(f"\n{total} TODO marker(s)." if total else "\nNo TODO markers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
