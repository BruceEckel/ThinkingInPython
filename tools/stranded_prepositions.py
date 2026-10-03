#!/usr/bin/env python
"""Report prose clauses that end on a stranded preposition.

The style rule: do not end a sentence on a preposition whose object was
moved or omitted ("the field they sit on", "what it is for"). Front the
preposition ("the field on which they sit"), restructure the sentence,
or swap in a transitive verb. A phrasal verb with its object already
present ("pass it around", "carry it along") is not stranding.

The check reads each paragraph's prose, joins its lines (the chapters
use Semantic Line Breaks, the Solutions are hand-wrapped), and splits
the text into clauses at `.`, `,`, `;`, `:`, `?`, and `!`. A clause
whose last word is a preposition from `PREPOSITIONS` is a hit, reported
as `path:line: clause` with the line holding that final word. A clause
is skipped when it has fewer than three words, when the word before
the final preposition is a pronoun object (`PRONOUNS`: "turn it on",
"carry them along", and the `CODE` placeholder: "passes `x` through"),
or when the last two words are an adverbial idiom (`IDIOMS`: "and so
on", "as before", "left behind", "built in").

Skipped input: fenced listings, headings, block quotes, tables, HTML
lines and comments, link definitions, and `#:` lines. Inline code spans
become the placeholder `CODE` before matching, so "refers to `x`" is
not a hit and a code span ending a clause is not read as prose. Links
keep their text and lose their targets.

Report-only: it prints the hits and exits 0, because the heuristic is
literal and no gate runs it. `--fail` exits 1 when anything is found.
It runs inside `tip prose` and alone as `tip stranded`.

Known false-positive shapes, all left in the report for a human:
an infinitive marker closing a clause ("the thing you want to"), a
clause that continues after a comma the splitter cut at ("the set of
objects, in"), a preposition that is a particle of a phrasal verb with
no pronoun ("a function to look up"), the quoted word itself
("the word 'for'"), a heading-like label ending a list item, and a
fronted relative clause whose object is far ahead ("the tool with
which you work on").

    uv run python -m tools.stranded_prepositions          # whole book
    uv run python -m tools.stranded_prepositions Chapters/30_*.md
    uv run tip stranded CH=30
"""

import argparse
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final
from tools.config import ROOT
from tools.markdown import Document
from tools.prose import (
    BLOCKQUOTE,
    HEADING,
    HTML,
    HTML_COMMENT_CLOSE,
    HTML_COMMENT_OPEN,
    INDENTED_CODE,
    LIST_ITEM,
    TABLE,
)
from tools.repo import add_paths_arg, md_files
from tools.report import Finding

PREPOSITIONS: Final[frozenset[str]] = frozenset("""
    to on for from into with about at in of by through over under after
    before between against toward towards onto upon within without
    around across along behind beyond during like
""".split())
PRONOUNS: Final[frozenset[str]] = frozenset(
    "it them this that one you me us code".split())
"""Object words before a particle that make a phrasal verb, not a
stranding: "turn it on", "carry them along". `code` is the placeholder
a code span becomes, so "passes `x` through" is a phrasal verb too."""
IDIOMS: Final[frozenset[str]] = frozenset("""
    so-on then-on early-on later-on as-before left-behind left-over
    built-in in-between outside-in inside-out back-in all-along
    twice-over and-over over-and-over fall-through falls-through
    fell-through moves-on move-on moved-on live-on lives-on carries-over
    carry-over carried-over passed-in compiled-in baked-in locked-in
    logged-in signed-in opted-in checked-in cleanup-after here-on
    and-after everything-after far-along
""".split())
"""Trailing bigrams (hyphen-joined) in which the final word is an
adverb or a fixed idiom, not a preposition missing its object."""
MIN_WORDS: Final = 3

CODE_SPAN = re.compile(r"``[^`]*``|`[^`]*`")
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
ATTRS = re.compile(r"\{#[^}]*\}")
LINK_DEF = re.compile(r"^\s*\[[^\]]+\]:\s")
FOOTNOTE_DEF = re.compile(r"^\s*\[\^[^\]]+\]:\s*")
OUTPUT_MARKER = re.compile(r"^\s*#:")
# Clause-ending punctuation, optional closing quotes and brackets, then
# a space or the end of the text (so "3.5" and "e.g.," mid-word hold).
TERMINATOR = re.compile(r"[.,;:?!]+[\"')\]*_”’]*(?=\s|$)")
EDGE = re.compile(r"^[^A-Za-z]+|[^A-Za-z]+$")


def clean(line: str) -> str:
    """One line's prose: code spans as `CODE`, links as their text."""
    line = CODE_SPAN.sub("CODE", line)
    line = IMAGE.sub("", line)
    line = LINK.sub(r"\1", line)
    return ATTRS.sub("", line)


def paragraphs(doc: Document) -> Iterator[list[tuple[int, str]]]:
    """Each paragraph as (1-based line number, cleaned text) pairs."""
    fenced = doc.in_fence()
    current: list[tuple[int, str]] = []
    in_comment = False
    in_list = False
    for index, line in enumerate(doc.lines):
        number = index + 1
        text: str | None = line
        if fenced[index]:
            text = None
        elif in_comment:
            in_comment = HTML_COMMENT_CLOSE.search(line) is None
            text = None
        elif HTML_COMMENT_OPEN.match(line):
            in_comment = HTML_COMMENT_CLOSE.search(line) is None
            text = None
        elif not line.strip():
            in_list = False
            text = None
        elif (HEADING.match(line) or BLOCKQUOTE.match(line)
              or TABLE.match(line) or HTML.match(line)
              or LINK_DEF.match(line) or OUTPUT_MARKER.match(line)):
            text = None
        elif m := LIST_ITEM.match(line):
            if current:
                yield current
                current = []
            in_list = True
            text = m.group(4)
        elif INDENTED_CODE.match(line) and not (current or in_list):
            text = None
        else:
            text = FOOTNOTE_DEF.sub("", line)
        if text is None:
            if current:
                yield current
                current = []
            continue
        current.append((number, clean(text.strip())))
    if current:
        yield current


def joined(paragraph: list[tuple[int, str]]) -> tuple[str, list[int]]:
    """The paragraph as one string, plus the line of every character."""
    chars: list[str] = []
    lines: list[int] = []
    for number, text in paragraph:
        if chars:
            chars.append(" ")
            lines.append(number)
        chars.extend(text)
        lines.extend([number] * len(text))
    return "".join(chars), lines


def word_of(token: str) -> str:
    """A token lowercased, without edge punctuation or emphasis marks."""
    return EDGE.sub("", token).lower()


def stranded(clause: str) -> bool:
    """Does this clause end on a stranded preposition?"""
    words = clause.split()
    if len(words) < MIN_WORDS:
        return False
    if word_of(words[-1]) not in PREPOSITIONS:
        return False
    if f"{word_of(words[-2])}-{word_of(words[-1])}" in IDIOMS:
        return False
    return word_of(words[-2]) not in PRONOUNS


def clauses(text: str) -> Iterator[tuple[str, int]]:
    """(clause, index of its last character) for each clause in `text`."""
    start = 0
    for m in TERMINATOR.finditer(text):
        yield text[start:m.start()], m.start() - 1
        start = m.end()
    tail = text[start:].rstrip()
    if tail:
        yield tail, start + len(tail) - 1


def find(doc: Document) -> Iterator[Finding]:
    """A finding per stranded-preposition clause in one document."""
    for paragraph in paragraphs(doc):
        text, lines = joined(paragraph)
        for clause, last in clauses(text):
            if stranded(clause):
                shown = " ".join(clause.split())
                yield Finding(doc.path, lines[max(last, 0)], shown)


def display(path: Path) -> str:
    """The path relative to the repo root when it lies under it."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any clause is found")
    args = ap.parse_args(argv)
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    found = sorted(
        (display(f.path), f.line, f.message)
        for p in paths for f in find(Document.parse(p))
    )
    for shown, line, clause in found:
        print(f"{shown}:{line}: {clause}")
    files = len({shown for shown, _, _ in found})
    print(f"{len(found)} stranded prepositions in {files} files")
    return 1 if args.fail and found else 0


if __name__ == "__main__":
    raise SystemExit(main())
