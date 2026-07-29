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

import argparse
from collections.abc import Iterator

from tools_markdown import Document
from tools_pycode import scan_line
from tools_report import Check, Finding, report
from tools_repo import add_paths_arg, md_files, write_text_lf


def _in_string(lines: list[str]) -> list[bool]:
    """For each line, whether it STARTS inside a triple-quoted string."""
    out: list[bool] = []
    triple: str | None = None
    for line in lines:
        out.append(triple is not None)
        _, triple = scan_line(line, triple)
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


def find(doc: Document) -> Iterator[Finding]:
    """Every blank line a listing should not have."""
    for block in doc.python_blocks():
        for idx, reason in _removals(block.lines):
            yield Finding(doc.path, block.line_number(idx), reason)


def fixed(doc: Document) -> str | None:
    """The file with those blank lines dropped, or None if there are none."""
    drop: set[int] = set()
    for block in doc.python_blocks():
        drop.update(block.start + idx for idx, _ in _removals(block.lines))
    if not drop:
        return None
    return doc.rendered(
        [ln for k, ln in enumerate(doc.lines) if k not in drop]
    )


CHECK = Check(
    name="listings",
    doc="python listings keep blank lines minimal",
    run=find,
    clean="Listings OK: blank lines are minimal.",
    problem="{n} blank-line issue(s). Fix with: "
            "python tools/listing_format.py --fix",
    fixer=fixed,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fix", action="store_true",
                    help="remove the offending blank lines in place")
    args = ap.parse_args(argv)

    docs = [Document.parse(p) for p in md_files(args.paths)]
    if args.fix:
        total = 0
        for doc in docs:
            total += sum(1 for _ in find(doc))
            new_text = fixed(doc)
            if new_text is not None:
                write_text_lf(doc.path, new_text)
        if total:
            print(f"Removed {total} blank line(s).")
            return 0
        print(CHECK.clean)
        return 0

    findings = (f for doc in docs for f in find(doc))
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
