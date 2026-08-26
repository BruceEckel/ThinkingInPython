#!/usr/bin/env python
"""Report listing lines wider than the book's 60-character limit.

Code listings must fit small screens (phones, e-ink readers), so
every line of every ```python block, including `#:` output markers
and fragment blocks that extract_examples.py never extracts, is
measured against WIDTH_LIMIT. This is deliberately a check on the
Markdown itself rather than on ruff's E501 over build/examples:
ruff never sees fragment blocks, and it silently exempts any line
whose overflow comes from a trailing pragma comment.

One exemption is sanctioned here too: a line whose code fits the
limit and only overflows because of a trailing `# type: ignore`
pragma. The pragma is addressed to the type checker, not the
reader, and restructuring a line to fit one would hurt more than
the overflow does. Everything else counts, markers included: a
`#:` marker wider than the limit means the program's own output
needs shortening, not the marker.

There is no --fix. Shortening a line is a judgment call: wrap the
statement, move a comment to its own line (or into the prose), or
change what the program prints.
"""
import argparse
from collections.abc import Iterator
from typing import Final

from tools_markdown import Document
from tools_pycode import scan_line
from tools_report import Check, Finding, report
from tools_repo import add_paths_arg, md_files

WIDTH_LIMIT: Final[int] = 60
PRAGMA: Final[str] = "# type: ignore"


def _effective_width(block: list[str], index: int,
                     triples: list[str | None]) -> int:
    """The line's width, with a trailing type-ignore pragma excluded.

    `triples` carries the in-progress triple-quote state at the top
    of each block line, so a `#` inside a multiline string is never
    mistaken for a comment.
    """
    line = block[index].rstrip()
    hash_i, _ = scan_line(line, triples[index])
    if hash_i != -1 and line[hash_i:].startswith(PRAGMA):
        code = line[:hash_i].rstrip()
        if code:
            return len(code)
    return len(line)


def _triple_states(block: list[str]) -> list[str | None]:
    """Triple-quote state entering each line of the block."""
    states: list[str | None] = []
    triple: str | None = None
    for line in block:
        states.append(triple)
        _, triple = scan_line(line, triple)
    return states


def find(doc: Document) -> Iterator[Finding]:
    """Every listing line wider than WIDTH_LIMIT, pragmas excluded."""
    for block in doc.python_blocks():
        triples = _triple_states(block.lines)
        for i in range(len(block.lines)):
            width = _effective_width(block.lines, i, triples)
            if width > WIDTH_LIMIT:
                yield Finding(
                    doc.path, block.line_number(i),
                    f"listing line is {width} chars "
                    f"(limit {WIDTH_LIMIT})",
                )


CHECK = Check(
    name="widths",
    doc=f"listing lines fit {WIDTH_LIMIT} chars "
        "(trailing type-ignore pragmas exempt)",
    run=find,
    clean="Listing widths OK.",
    problem="{n} listing line(s) too wide. Wrap the statement, "
            "move the comment, or shorten the printed text.",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    args = ap.parse_args(argv)
    docs = [Document.parse(p) for p in md_files(args.paths)]
    findings = (f for doc in docs for f in find(doc))
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
