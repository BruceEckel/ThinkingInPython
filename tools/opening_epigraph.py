#!/usr/bin/env python
"""Fail if a numbered chapter does not open with its epigraph.

Chapters 02 onward open with a two-sentence statement of the chapter's
problem and its answer, written as a blockquote directly under the
`#` heading. The site, EPUB, and PDF builds find it with
`build_site.split_epigraph()`, which matches only a blockquote that
starts the body, and style it as the chapter's epigraph. A chapter
whose opener loses its `>` markers, or gains a paragraph above them,
builds without complaint and simply shows no epigraph; this check
turns that into a gate failure.

The rule: line 1 is the `#` heading, line 2 is blank, and lines 3
onward are a blockquote of two to four lines (Semantic Line Breaks
put each sentence, and each long clause, on its own line), followed
by a blank line. Chapter 01 and the appendices open with an ordinary
paragraph and are not checked, nor is any file outside a numbered
chapter's name, such as a Solutions file checked by mistake.

Usage:
    python -m tools.opening_epigraph                # all of Chapters/
    python -m tools.opening_epigraph Chapters/30_Patterns--Observer.md
"""

import argparse
import re
from collections.abc import Iterator
from tools.markdown import Document
from tools.repo import add_paths_arg, md_files
from tools.report import Check, Finding, report

CHAPTER = re.compile(r"^(\d{2})_")
FIRST_CHAPTER = 2
MIN_LINES = 2
MAX_LINES = 4


def applies(doc: Document) -> bool:
    """True for a numbered chapter from FIRST_CHAPTER on."""
    if doc.path.parent.name == "Solutions":
        return False
    m = CHAPTER.match(doc.path.name)
    return m is not None and int(m.group(1)) >= FIRST_CHAPTER


def find(doc: Document) -> Iterator[Finding]:
    """A finding if the chapter's opening blockquote is missing or malformed."""
    if not applies(doc):
        return
    lines = doc.lines
    if not lines or not lines[0].startswith("# "):
        yield Finding(doc.path, 1, "line 1 is not the chapter's # heading")
        return
    if len(lines) < 2 or lines[1].strip():
        yield Finding(doc.path, 2,
                      "the # heading must be followed by a blank line")
        return
    count = 0
    while 2 + count < len(lines) and lines[2 + count].startswith(">"):
        count += 1
    if count == 0:
        yield Finding(doc.path, 3,
                      "the chapter does not open with its epigraph: "
                      "a `>` blockquote directly under the heading")
    elif not MIN_LINES <= count <= MAX_LINES:
        yield Finding(doc.path, 3,
                      f"the opening epigraph is {count} line(s); "
                      f"expected {MIN_LINES} to {MAX_LINES}")
    elif 2 + count < len(lines) and lines[2 + count].strip():
        yield Finding(doc.path, 3 + count,
                      "the opening epigraph must end with a blank line")


CHECK = Check(
    name="epigraph",
    doc="chapters 02 on open with a 2-4 line `>` epigraph "
        "under the heading",
    run=find,
    clean="Every chapter opens with its epigraph.",
    problem="{n} chapter(s) without a well-formed opening epigraph. "
            "Put the two-sentence opener in a `>` blockquote directly "
            "under the # heading.",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_paths_arg(ap)
    args = ap.parse_args(argv)
    findings = [
        f for p in md_files(args.paths) for f in find(Document.parse(p))
    ]
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
