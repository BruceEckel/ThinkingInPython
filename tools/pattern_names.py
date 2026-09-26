#!/usr/bin/env python
"""Every naming of a design pattern is capitalized and italic: *Strategy*.

Some pattern names are ordinary words (State, Command, Bridge, Proxy),
so a bare "state" or even "State" does not read as the pattern. The
book's rule is therefore that a pattern name, wherever it names the
pattern, is written capitalized and in italics, on every mention and
not only the first: *State*, *Chain of Responsibility*, and inside
link text, [*Template Method*](25_Patterns--Template_Method.md).
Headings stay plain (they are already title case), and code spans are
class names, not pattern names. The lowercase word keeps its ordinary
sense: "an observer registers interest", "a flyweight is immutable",
"the template method" (the method), "mutable state".

The names come from `tools/data/pattern_names.txt`, one per line. A
line starting with ``!`` is a phrase that contains a name without
naming the pattern, ``!State Machines`` (the chapter title), and is
skipped wherever it appears.

What is reported, and what `--fix` rewrites:

- ``plain``: the capitalized name outside italics, "the Observer
  pattern" or "[Observer](30_...)". Fixed by wrapping it: *Observer*.
- ``bold``: **Observer**. Fixed to *Observer*.
- ``lower-pattern``: the lowercase name directly before "pattern",
  "the null object pattern", which can only mean the pattern. Fixed to
  *Null Object* pattern.
- ``sentence-start``: a name that is also a common verb or noun (State,
  Command, Bridge) at the start of a line, where "State the rule" and
  "*State* appears beside *Proxy*" cannot be told apart by shape. Never
  rewritten, and listed only with ``--sentence-start``, since the three
  verbs the book opens sentences with would otherwise keep the gate red.
  Run that listing after writing new prose about *State* or *Command*.

Headings are skipped, and so is an indented code block outside a fence
(a line indented four spaces that is not continuing a list item).

A name already inside an italic span (an odd number of ``*`` before it
on the line) is taken as italic, so "*the Strategy pattern*" is not
double-wrapped. Plurals ("two Singletons") and possessives on the
plain form are not matched; the book reads those as objects.

Usage:
    python -m tools.pattern_names               # check Chapters/
    python -m tools.pattern_names --fix         # rewrite what it can
    python -m tools.pattern_names Solutions/    # another tree
"""

import argparse
import re
from collections.abc import Iterator
from functools import cache
from pathlib import Path

from tools.config import DATA_DIR
from tools.markdown import Document
from tools.prose import HEADING, INDENTED_CODE, LIST
from tools.repo import add_paths_arg, md_files, write_text_lf
from tools.report import Check, Finding, report

NAMES_FILE = DATA_DIR / "pattern_names.txt"
# Names that are also everyday verbs or nouns, so a capital at the start
# of a line proves nothing.
AMBIGUOUS_AT_START = frozenset({"State", "Command", "Bridge"})

_PUA = 0xE000
# Masked before matching: inline code, a link's destination (which holds
# the chapter filename, "26_Patterns--Surrogate.md#state"), a reference
# footnote marker, and an explicit heading id.
_MASKED = re.compile(
    r"``[^`]*``|`[^`]*`|\]\([^)]*\)|\[\^[^\]]+\]|\{#[^}]*\}")
_BOLD = re.compile(r"\*\*(?P<name>[^*]+)\*\*")
# A line's leading list marker, table pipe, or quote marker, so "the
# start of a line" means the start of its text.
_LEAD = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+|\|\s*|>\s*)*")


def load_names(path: Path = NAMES_FILE) -> tuple[str, ...]:
    """The names, then the ``!`` exclusions, each in file order."""
    if not path.exists():
        return ()
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            names.append(stripped)
    return tuple(names)


@cache
def default_names() -> tuple[str, ...]:
    return load_names()


def split_names(names: tuple[str, ...]) -> tuple[list[str], list[str]]:
    """(pattern names longest first, excluded phrases).

    Longest first so "Factory Method" is seen before "Factory", whatever
    order the caller passed them in.
    """
    plain = sorted((n for n in names if not n.startswith("!")),
                   key=len, reverse=True)
    excluded = [n[1:].strip() for n in names if n.startswith("!")]
    return plain, excluded


def mask(text: str) -> tuple[str, list[str]]:
    store: list[str] = []

    def repl(m: re.Match[str]) -> str:
        store.append(m.group(0))
        return chr(_PUA + len(store) - 1)

    return _MASKED.sub(repl, text), store


def unmask(text: str, store: list[str]) -> str:
    """Restore the masked spans, latest first.

    A span masked later can hold placeholders masked earlier (a bold span
    holding a code span), so those must be restored after it is.
    """
    for i in range(len(store) - 1, -1, -1):
        text = text.replace(chr(_PUA + i), store[i])
    return text


def _pattern(name: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![\w*])({re.escape(name)})(?![\w*])")


def _lower_pattern(name: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w)({re.escape(name.lower())}) pattern\b")


def _inside_italics(text: str, pos: int) -> bool:
    return text.count("*", 0, pos) % 2 == 1


def rewrite_line(line: str, names: tuple[str, ...],
                 ) -> tuple[str, list[tuple[str, str]]]:
    """(fixed line, [(code, what)]) for one prose line.

    The line comes back unchanged when nothing is wrong. The list holds
    every problem, including the ``sentence-start`` ones the fix leaves.
    """
    plain, excluded = split_names(names)
    text, store = mask(line)
    found: list[tuple[str, str]] = []
    for phrase in excluded:
        def hide(m: re.Match[str]) -> str:
            store.append(m.group(0))
            return chr(_PUA + len(store) - 1)
        text = re.sub(rf"(?<!\w){re.escape(phrase)}(?!\w)", hide, text)

    # Bold first. A span that is only a name becomes italic. Any other
    # bold span keeps its text, so a name inside it is still wrapped, but
    # its ``**`` markers are masked so they cannot throw off the italic
    # count below.
    def unbold(m: re.Match[str]) -> str:
        inner = m.group("name")
        if inner in plain:
            found.append(("bold", inner))
            return f"*{inner}*"
        store.append("**")
        marker = chr(_PUA + len(store) - 1)
        return f"{marker}{inner}{marker}"
    text = _BOLD.sub(unbold, text)
    lead = _LEAD.match(text)
    start = lead.end() if lead else 0
    for name in plain:
        def wrap(m: re.Match[str]) -> str:
            if _inside_italics(text, m.start()):
                return m.group(0)
            if m.start() == start and name in AMBIGUOUS_AT_START:
                found.append(("sentence-start", name))
                return m.group(0)
            found.append(("plain", name))
            return f"*{name}*"
        text = _pattern(name).sub(wrap, text)

        def lower(m: re.Match[str]) -> str:
            if _inside_italics(text, m.start()):
                return m.group(0)
            found.append(("lower-pattern", m.group(1)))
            return f"*{name}* pattern"
        text = _lower_pattern(name).sub(lower, text)
    return unmask(text, store), found


def _lines(doc: Document) -> Iterator[tuple[int, str]]:
    """Every line outside code fences that is not a heading or code.

    An indented line continues a list item when a list is open (a list
    item started it and no unindented text has closed it since), and is
    an indented code block otherwise, which is skipped like a fence.
    """
    in_list = False
    for lineno, line in doc.outside_fences():
        if HEADING.match(line):
            in_list = False
            continue
        if LIST.match(line):
            in_list = True
        elif line.strip() and not INDENTED_CODE.match(line):
            in_list = False
        if INDENTED_CODE.match(line) and not in_list:
            continue
        yield lineno, line


def scan(doc: Document, names: tuple[str, ...],
         sentence_start: bool = False) -> Iterator[Finding]:
    for lineno, line in _lines(doc):
        _, found = rewrite_line(line, names)
        for code, what in found:
            if code == "sentence-start" and not sentence_start:
                continue
            if code == "sentence-start":
                msg = (f'"{what}" starts the line: the pattern (write '
                       f"*{what}*) or the word? Check by hand")
            elif code == "lower-pattern":
                msg = f'"{what} pattern" names the pattern: write *{what.title()}* pattern'
            elif code == "bold":
                msg = f"**{what}** should be italic: *{what}*"
            else:
                msg = f'pattern name "{what}" should be italic: *{what}*'
            yield Finding(doc.path, lineno, msg, code=code)


def find(doc: Document) -> Iterator[Finding]:
    return scan(doc, default_names())


def fixed(doc: Document) -> str | None:
    names = default_names()
    lines = list(doc.lines)
    changed = False
    for lineno, line in _lines(doc):
        new, _ = rewrite_line(line, names)
        if new != line:
            lines[lineno - 1] = new
            changed = True
    return doc.rendered(lines) if changed else None


CHECK = Check(
    name="pattern-names",
    doc="every naming of a design pattern is capitalized and italic (*Strategy*)",
    run=find,
    clean="Pattern names are capitalized and italic.",
    problem="{n} pattern name(s) not written as *Name*. "
            "`tip fix-pattern-names` rewrites them.",
    fixer=fixed,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the fixable findings in place")
    ap.add_argument("--sentence-start", action="store_true",
                    help="also list State/Command/Bridge at a line start, "
                         "for a human to judge")
    args = ap.parse_args(argv)
    paths = md_files(args.paths)
    if args.fix:
        changed = 0
        for p in paths:
            new = fixed(Document.parse(p))
            if new is not None:
                write_text_lf(p, new)
                changed += 1
        print(f"{changed} file(s) rewritten.")
        return 0
    findings = (
        f for p in paths
        for f in scan(Document.parse(p), default_names(),
                      sentence_start=args.sentence_start))
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
