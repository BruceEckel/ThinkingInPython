#!/usr/bin/env python
"""Fail the build if any banned phrase appears in the book.

Reads phrases from `tools/data/banned_phrases.txt` (one per line) and searches every
`Chapters/*.md` file, prose and code alike, for each as a literal,
case-sensitive substring. Every occurrence is reported as `path:line:col`, and
a non-zero exit makes it a gate. Use it to retire constructs the book has moved
past, such as `from __future__ import annotations` (unnecessary on Python 3.14).

In the phrases file, blank lines and lines starting with `#` are ignored, so you
can group and explain the entries.

Usage:
    python tools/banned_phrases.py                 # scan Chapters/
    python tools/banned_phrases.py path ...        # scan specific files/dirs
    python tools/banned_phrases.py --phrases FILE  # use another phrases file
"""
import argparse
from collections.abc import Iterable, Iterator
from functools import cache
from pathlib import Path

from tools_config import DATA_DIR
from tools_markdown import Document
from tools_repo import add_paths_arg, md_files
from tools_report import Check, Finding, report

PHRASES_FILE = DATA_DIR / "banned_phrases.txt"


def load_phrases(path: Path) -> list[str]:
    if not path.exists():
        return []
    phrases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            phrases.append(stripped)
    return phrases


def scan(doc: Document, phrases: Iterable[str]) -> Iterator[Finding]:
    """Every occurrence of every phrase, as a literal substring.

    Prose and code alike: a phrase the book has retired should not
    survive inside a listing either.
    """
    for lineno, line in enumerate(doc.lines, 1):
        for phrase in phrases:
            col = line.find(phrase)
            while col != -1:
                yield Finding(
                    doc.path, lineno, f'banned phrase: "{phrase}"',
                    col=col + 1,
                )
                col = line.find(phrase, col + 1)


@cache
def default_phrases() -> tuple[str, ...]:
    """The configured phrases, read once per process."""
    return tuple(load_phrases(PHRASES_FILE))


def find(doc: Document) -> Iterator[Finding]:
    """The check as the runner calls it, against the configured phrases."""
    return scan(doc, default_phrases())


CHECK = Check(
    name="banned",
    doc="no phrase from tools/data/banned_phrases.txt appears in the book",
    run=find,
    clean="No banned phrases found.",
    problem="{n} banned phrase occurrence(s). "
            "Remove them or edit tools/data/banned_phrases.txt.",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--phrases", type=Path, default=PHRASES_FILE,
                    help=f"phrases file (default: {PHRASES_FILE.name})")
    args = ap.parse_args(argv)

    phrases = load_phrases(args.phrases)
    if not phrases:
        print(f"No banned phrases configured in {args.phrases}.")
        return 0

    findings = (
        f for p in md_files(args.paths)
        for f in scan(Document.parse(p), phrases)
    )
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
