#!/usr/bin/env python
"""Normalize inline-comment spacing to two spaces in ```python listings.

An inline comment (code precedes it on the same line) must start exactly two
spaces after the code ends, this book's standard style. A full-line comment
(nothing but the comment on its line) has no code to measure the gap from and
is left alone, and so is a `#:` output marker (always at column 0, never
inline).

It is string-aware (a `#` inside a string is not a comment) and only touches
```python blocks. Any run of whitespace before the `#`, from one space to
many (including a comment deliberately column-aligned with others), collapses
to exactly two spaces; the comment's own text is untouched.

Default mode reports `path:line` and exits non-zero, so it is a gate. Pass
--fix to rewrite the spacing.
"""
import argparse
from collections.abc import Iterator

from tools_markdown import Document
from tools_pycode import scan_line
from tools_report import Check, Finding, report
from tools_repo import add_paths_arg, md_files, write_text_lf


def _spacing_targets(block: list[str]) -> dict[int, str]:
    """Map block-line index -> rewritten line, for inline comments to fix."""
    fixes: dict[int, str] = {}
    triple = None
    for i, line in enumerate(block):
        hash_i, triple = scan_line(line, triple)
        if hash_i == -1:
            continue
        if line[hash_i:hash_i + 2] == "#:":
            continue  # `#: ...` is a captured-output marker, not a comment
        code = line[:hash_i]
        if code.strip() == "":
            continue  # full-line comment, no code to measure the gap from
        wanted = code.rstrip() + "  " + line[hash_i:]
        if wanted != line:
            fixes[i] = wanted
    return fixes


def find(doc: Document) -> Iterator[Finding]:
    """Every inline comment not exactly two spaces after its code."""
    for block in doc.python_blocks():
        for idx in sorted(_spacing_targets(block.lines)):
            yield Finding(
                doc.path, block.line_number(idx),
                "inline comment is not two spaces after the code",
            )


def fixed(doc: Document) -> str | None:
    """The file with those gaps collapsed, or None if none are wrong."""
    out = list(doc.lines)
    changed = False
    for block in doc.python_blocks():
        for idx, new_line in _spacing_targets(block.lines).items():
            out[block.start + idx] = new_line
            changed = True
    return doc.rendered(out) if changed else None


CHECK = Check(
    name="comment-spacing",
    doc="inline listing comments sit two spaces after the code",
    run=find,
    clean="Comment spacing OK.",
    problem="{n} inline comment(s) misaligned. "
            "Fix with: python tools/comment_spacing.py --fix",
    fixer=fixed,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the spacing in place")
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
            print(f"Fixed {total} comment(s).")
            return 0
        print(CHECK.clean)
        return 0

    findings = (f for doc in docs for f in find(doc))
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
