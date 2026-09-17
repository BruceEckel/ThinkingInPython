#!/usr/bin/env python
"""Fail if a footnote label is defined more than once across a tree.

Markdown reference footnotes are written `text[^label]` at the reference
and `[^label]: note` at the definition. A label only has to be unique
within one Markdown document, and the site renders each chapter as its
own page, so two chapters can define the same label and the site shows
both notes correctly. The EPUB and PDF concatenate every chapter into
one document before pandoc sees it. There, pandoc keeps the first
definition of a label and drops the rest with a warning, so the second
chapter's reference silently shows the first chapter's note. Chapter 17
carried chapter 11's `parametrize` footnote through release 0.5.9 that
way; the only sign was one line in the release's build output.

This check reads every `[^label]:` definition in the directory the
checked file sits in (its siblings are the files a book build
concatenates) and reports a definition whose label another file, or an
earlier line of the same file, also defines. Definitions inside fenced
code are ignored. References are not checked: one note may be cited
many times, and a reference to an undefined label is pandoc's own
warning on every build, site included.

Usage:
    python -m tools.footnote_labels                # all of Chapters/
    python -m tools.footnote_labels Chapters/17_Techniques--Metaprogramming.md
"""

import argparse
import re
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from tools.markdown import Document
from tools.repo import add_paths_arg, md_files
from tools.report import Check, Finding, report

DEFINITION = re.compile(r"^\[\^([^\]\s]+)\]:")


def definitions(doc: Document) -> Iterator[tuple[int, str]]:
    """(line, label) for each footnote definition outside fenced code."""
    for lineno, line in doc.outside_fences():
        m = DEFINITION.match(line)
        if m:
            yield lineno, m.group(1)


@cache
def _tree_definitions(directory: Path) -> dict[str, list[tuple[Path, int]]]:
    """Every definition in the directory's *.md files, keyed by label."""
    found: dict[str, list[tuple[Path, int]]] = {}
    for path in md_files([directory]):
        for lineno, label in definitions(Document.parse(path)):
            found.setdefault(label, []).append((path, lineno))
    return found


def find(doc: Document) -> Iterator[Finding]:
    """A finding per definition in `doc` whose label is defined elsewhere.

    "Elsewhere" is another file in the same directory, or an earlier
    line of this file. A document parsed from text with no real path has
    no siblings, so only its own duplicates are reported.
    """
    seen: dict[str, int] = {}
    tree = (_tree_definitions(doc.path.parent.resolve())
            if doc.path.is_file() else {})
    for lineno, label in definitions(doc):
        others = [f"{p.name}:{n}" for p, n in tree.get(label, [])
                  if p.resolve() != doc.path.resolve()]
        if label in seen:
            others.insert(0, f"line {seen[label]}")
        seen.setdefault(label, lineno)
        if others:
            yield Finding(
                doc.path, lineno,
                f"footnote label [^{label}] is also defined at "
                f"{', '.join(others)}; a label must be unique across the "
                "book, since the EPUB and PDF concatenate the chapters")


CHECK = Check(
    name="footnotes",
    doc="footnote labels are unique across the tree "
        "(the EPUB and PDF concatenate the chapters)",
    run=find,
    clean="Footnote labels are unique.",
    problem="{n} footnote label(s) defined more than once. Rename one "
            "of each pair at both its reference and its definition.",
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
