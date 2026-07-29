#!/usr/bin/env python
"""Enforce the book's comment-period policy in ```python listings.

A one-line comment ends without a period. Only a multiline comment (a block of
two or more consecutive full-line `#` comments) reads as sentences and keeps its
periods. So this flags, and with --fix removes, a trailing period on:

  * an inline comment (always one line), and
  * a lone full-line comment (no `#` comment line directly above or below it).

It is string-aware (a `#` inside a string is not a comment) and only touches
```python blocks. An ellipsis (`...`) is left alone, and so is a period that is
not the last visible character.

Default mode reports `path:line` and exits non-zero, so it is a gate. Pass --fix
to remove the periods.
"""
import argparse
from collections.abc import Iterator

from tools_markdown import Document
from tools_pycode import scan_line
from tools_report import Check, Finding, report
from tools_repo import add_paths_arg, md_files, write_text_lf


def _comment_starts(block: list[str]) -> list[int]:
    """For each line, the index of its real `#` comment, or -1."""
    starts = []
    triple = None
    for line in block:
        hash_i, triple = scan_line(line, triple)
        starts.append(hash_i)
    return starts


def _strip_targets(block: list[str]) -> dict[int, str]:
    """Map block-line index -> rewritten line, for one-line comments to fix."""
    starts = _comment_starts(block)

    def full_line_comment(i: int) -> bool:
        return starts[i] != -1 and block[i][:starts[i]].strip() == ""

    fixes: dict[int, str] = {}
    for i, line in enumerate(block):
        hash_i = starts[i]
        if hash_i == -1:
            continue
        if line[hash_i:hash_i + 2] == "#:":
            continue  # `#: ...` is a captured-output marker, not a comment
        if full_line_comment(i):
            prev_c = i > 0 and full_line_comment(i - 1)
            next_c = i + 1 < len(block) and full_line_comment(i + 1)
            if prev_c or next_c:
                continue  # part of a multiline comment block
        after = line[hash_i + 1:].rstrip()
        if after.endswith(".") and not after.endswith(".."):
            fixes[i] = line[:hash_i] + "#" + after[:-1]
    return fixes


def find(doc: Document) -> Iterator[Finding]:
    """Every one-line comment in a python listing ending with a period."""
    for block in doc.python_blocks():
        for idx in sorted(_strip_targets(block.lines)):
            yield Finding(
                doc.path, block.line_number(idx),
                "one-line comment ends with a period",
            )


def fixed(doc: Document) -> str | None:
    """The file with those periods removed, or None if there are none."""
    out = list(doc.lines)
    changed = False
    for block in doc.python_blocks():
        for idx, new_line in _strip_targets(block.lines).items():
            out[block.start + idx] = new_line
            changed = True
    return doc.rendered(out) if changed else None


CHECK = Check(
    name="comment-periods",
    doc="one-line listing comments must not end with a period",
    run=find,
    clean="Comment periods OK.",
    problem="{n} one-line comment(s) end with a period. "
            "Fix with: python tools/comment_periods.py --fix",
    fixer=fixed,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fix", action="store_true",
                    help="remove the trailing periods in place")
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
            print(f"Removed {total} trailing period(s).")
            return 0
        print(CHECK.clean)
        return 0

    findings = (f for doc in docs for f in find(doc))
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
