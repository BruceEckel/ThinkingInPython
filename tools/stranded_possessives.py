#!/usr/bin/env python
"""Report prose clauses that hold a stranded possessive.

The style rule (Bruce, 2026-10-14): a possessive needs its head noun.
A *stranded possessive* leaves the noun out, the possessive cousin of
the stranded preposition: "a call on a subclass has the subclass's
type, not the base's", "The catalog above is GoF's", "The engine is
the chapter's". Restore the noun ("not the base's type") or restate
the sentence without the possessive.

The check reads each paragraph's prose, joins its lines (the chapters
use Semantic Line Breaks, the Solutions are hand-wrapped), and finds
every possessive token: a word ending in `'s` or `s'`. Contractions
(`CONTRACTIONS`: "it's", "that's", "let's") are not possessives. A
possessive is a hit when the text after it, past any closing emphasis
marks or quotes, is clause punctuation (`. , ; : ) ! ? ]`), the end
of the paragraph, or a function word from `FUNCTION_WORDS` that cannot
be a head noun ("not the base's, to", "GoF's and", "the chapter's is").
A line break between a possessive and its noun is no stranding: the
joined text puts the next line's first word after it.

Skipped input: fenced listings, headings, block quotes, tables, HTML
lines and comments, link definitions, and `#:` lines, the same skips
`tools/stranded_prepositions.py` makes (this module reuses its
paragraph reader). Inline code spans become the placeholder `CODE`, so
a code span after a possessive counts as the head noun ("the
wrapper's `__dict__`") and a possessive code span (`CODE's`) is still
seen. Links keep their text and lose their targets.

Report-only: it prints the hits and exits 0, because the heuristic is
literal and no gate runs it. `--fail` exits 1 when a NEW hit is found.
It runs inside `tip prose` and alone as `tip possessives`.

A hit prints as `path:line: clause`, with the line holding the
possessive and the clause cut at `.`, `,`, `;`, `:`, `?`, and `!` as
`stranded_prepositions` cuts it. Every hit was read once by a human,
and the ones judged false positives live in
`tools/data/stranded_possessives_baseline.txt`, so a run prints only
what is new. An entry is `path<TAB>clause`: the clause text with its
whitespace normalized and no line number, so a reflow or an edit
elsewhere in the file leaves the entry alone, while an edit to the
clause itself retires it and the rewritten clause reports as NEW. An
entry is a judged false positive, not an exemption from the rule. The
default run prints each NEW hit and a summary (`N new, M accepted`),
and lists a `stale` entry that matches no hit any more. `--all` prints
every hit, marked NEW or accepted. `--accept` appends every NEW hit to
the baseline and drops the stale entries, keeping the file sorted and
free of duplicates. A run given paths compares against those files'
entries alone, and refuses `--accept`.

Known false-positive shapes, all left in the report for a human: a
coordinated possessive whose noun follows the second one ("the
player's and opponent's class names"), a hyphenated compound that
starts with a function word ("the base's do-nothing version"), and a
possessive before a code span the masking lost.

    uv run python -m tools.stranded_possessives          # new hits
    uv run python -m tools.stranded_possessives --all    # every hit
    uv run python -m tools.stranded_possessives --accept # judged false
    uv run python -m tools.stranded_possessives Chapters/30_*.md
    uv run tip possessives CH=30
    uv run tip possessives-accept
"""

import argparse
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.stranded_prepositions import (
    TERMINATOR,
    display,
    joined,
    paragraphs,
)

CONTRACTIONS: Final[frozenset[str]] = frozenset("""
    it's that's let's there's what's here's he's she's who's where's
    how's one's when's why's everything's something's nothing's
""".split())
"""Words ending in `'s` that are not possessives."""
FUNCTION_WORDS: Final[frozenset[str]] = frozenset("""
    to and or than not alone too as but is are was were does do did
    has have because since if so then which that rather instead either
    neither nor when where while with without in on at for from by of
    until once again anyway here there now
""".split())
"""Words after a possessive that cannot be its head noun."""
BASELINE: Final = DATA_DIR / "stranded_possessives_baseline.txt"
HEADER: Final = (
    "# Stranded-possessive hits a human read and judged false\n"
    "# positives: a coordinated possessive whose noun follows the\n"
    "# second one, a hyphenated compound that starts with a function\n"
    "# word. An entry is not an exemption from the rule.\n"
    "# path<TAB>clause, with the clause's whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the clause retires it. Rewritten by `tip possessives-accept`;\n"
    "# read the delta with `tip possessives` before accepting.\n"
    "# See tools/stranded_possessives.py.\n"
)

POSSESSIVE = re.compile(r"(?<![\w`])[A-Za-z][\w-]*(?:'s|s')")
CLOSERS: Final = "*_\"'”’"
PUNCTUATION: Final = ".,;:)!?]"
NEXT_WORD = re.compile(r"[A-Za-z]+")


def stranded(text: str, end: int) -> bool:
    """Does the possessive ending at `end` in `text` lack its noun?"""
    after = text[end:].lstrip(CLOSERS).lstrip()
    if not after or after[0] in PUNCTUATION:
        return True
    word = NEXT_WORD.match(after)
    return word is not None and word.group().lower() in FUNCTION_WORDS


def spans(text: str) -> Iterator[tuple[int, int]]:
    """The (start, end) of each clause, cut as the stranded check cuts."""
    start = 0
    for m in TERMINATOR.finditer(text):
        yield start, m.start()
        start = m.end()
    if text[start:].strip():
        yield start, len(text)


def find(doc: Document) -> Iterator[Finding]:
    """A finding per clause that holds a stranded possessive."""
    for paragraph in paragraphs(doc):
        text, lines = joined(paragraph)
        clause_spans = list(spans(text))
        for m in POSSESSIVE.finditer(text):
            if m.group().lower() in CONTRACTIONS:
                continue
            if not stranded(text, m.end()):
                continue
            for start, stop in clause_spans:
                if start <= m.start() < max(stop, start + 1):
                    clause = " ".join(text[start:stop].split())
                    yield Finding(doc.path, lines[m.end() - 1], clause)
                    break


def key(shown: str, clause: str) -> str:
    """The baseline line for a hit: path and clause, no line number."""
    return f"{shown}\t{' '.join(clause.split())}"


def load_baseline(path: Path | None = None) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    path = path or BASELINE
    if not path.exists():
        return set()
    return {
        line for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    path = path or BASELINE
    body = "".join(f"{entry}\n" for entry in sorted(entries))
    path.write_text(HEADER + body, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW clause is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    found = sorted(
        {(display(f.path), f.line, f.message)
         for p in paths for f in find(Document.parse(p))}
    )
    baseline = load_baseline()
    scope = {e for e in baseline if e.split("\t", 1)[0] in shown_paths}
    current = {key(shown, clause) for shown, _, clause in found}
    new = [(s, n, c) for s, n, c in found if key(s, c) not in baseline]
    stale = sorted(scope - current)
    if args.accept:
        added = {key(s, c) for s, _, c in new}
        write_baseline((baseline - set(stale)) | added)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    for shown, line, clause in found:
        accepted = key(shown, clause) in baseline
        if accepted and not args.all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {shown}:{line}: {clause}")
    for entry in stale:
        shown, clause = entry.split("\t", 1)
        print(f"stale    {shown}: {clause}")
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and new else 0


if __name__ == "__main__":
    raise SystemExit(main())
