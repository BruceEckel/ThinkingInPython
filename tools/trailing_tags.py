#!/usr/bin/env python
"""Report prose clauses with a trailing participle tag or a transactional connective.

Two sentence shapes Bruce marked in chapter 31 on 2026-10-18, now
rules R32 and R35 in `bruce_edit_db.md`. Each hit carries its rule
label at the start of the printed clause.

`[R32]`, the trailing participle tag: a clause ends with a comma, a
past participle, and a measure or a place ("belongs in that state's
row, written once"; "the loop that iterates over the data, written
once"). The final comma-separated segment of the clause is a hit when
it starts with a past participle (a regular `-ed` word or one of
`IRREGULAR`) followed by at most `MAX_TAIL` words that contain a word
or phrase from `MEASURES` ("once", "alone", "in advance", "by hand"),
when it is the single word "unchanged", or when it is "the same" plus
up to `MAX_SAME` words ("the same rule any duplicate dictionary key
follows"), the noun-phrase cousin of the tag.

`[R35]`, the transactional connective: anywhere in a clause, "in
return", "in exchange", "trade-off" (also "tradeoff" and "trade
off"), "what you get back", "on the plus side", "on the minus side",
"the upside", "the downside", "the catch is", "the flip side", "the
price of", and "the cost of" (`CONNECTIVES`). Case-insensitive. Every
"the price of" and "the cost of" is reported, and the baseline holds
the measured ones.

The check reads each paragraph's prose, joins its lines (the chapters
use Semantic Line Breaks, the Solutions are hand-wrapped), and splits
the text into clauses at `.`, `;`, `:`, `?`, and `!` (commas stay
inside a clause, since the R32 test reads the segment after the last
one). Skipped input: fenced listings, headings, block quotes, tables,
HTML lines and comments, link definitions, footnote definitions, and
`#:` lines, the same skips `tools/stranded_prepositions.py` makes (this
module reuses its paragraph reader). Inline code spans become the
placeholder `CODE`, and links keep their text and lose their targets.

Report-only: it prints the hits and exits 0, because the heuristic is
literal and no gate runs it. `--fail` exits 1 when a NEW hit is found.
It runs inside `tip prose` and alone as `tip trailing`.

A hit prints as `path:line: [Rnn] clause`, with the line holding the
end of the matched text. Every hit is read once by a human, and the
ones judged keeps live in `tools/data/trailing_tags_baseline.txt`, so
a run prints only what is new. An entry is `path<TAB>[Rnn] clause`:
the clause text with its whitespace normalized and no line number, so
a reflow or an edit elsewhere in the file leaves the entry alone,
while an edit to the clause itself retires it and the rewritten clause
reports as NEW. An entry is a judged keep, not an exemption from the
rule. The default run prints each NEW hit and a summary (`N new, M
accepted`), and lists a `stale` entry that matches no hit any more.
`--all` prints every hit, marked NEW or accepted. `--accept` appends
every NEW hit to the baseline and drops the stale entries, keeping the
file sorted and free of duplicates. A run given paths compares against
those files' entries alone, and refuses `--accept`.

Known false-positive shapes, all left in the report for a human: a
participle that describes the noun it follows ("a `logged` instance,
stored as a class attribute"), a regular `-ed` noun or adjective that
starts a final segment ("a need, embedded once"), a measured "cost of"
or "price of", and "trade-off" naming the expression problem.

    uv run python -m tools.trailing_tags          # new hits
    uv run python -m tools.trailing_tags --all    # every hit
    uv run python -m tools.trailing_tags --accept # judged keeps
    uv run python -m tools.trailing_tags Chapters/31_*.md
    uv run tip trailing CH=31
    uv run tip trailing-accept
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
    display,
    joined,
    paragraphs,
)

IRREGULAR: Final[frozenset[str]] = frozenset("""
    written kept held built bound read run set made done left spread
    split sent put cut hit let lost won drawn known shown given taken
    seen thrown grown begun bought brought caught taught found fed led
    met paid said sold told understood
""".split())
"""Past participles that do not end in `-ed`."""
MEASURES: Final[tuple[str, ...]] = (
    "once", "twice", "again", "alone", "together", "apart", "elsewhere",
    "here", "there", "separately", "differently", "first", "last",
    "later", "earlier", "in advance", "by hand", "in place",
    "in one place", "in order", "at once",
)
"""Measures and places that make a participle segment a tag."""
MAX_TAIL: Final = 5
"""Most words allowed after the participle."""
MAX_SAME: Final = 6
"""Most words allowed after "the same"."""
CONNECTIVES: Final[tuple[str, ...]] = (
    r"in return", r"in exchange", r"trade[- ]?offs?", r"what you get back",
    r"on the plus side", r"on the minus side", r"the upside",
    r"the downside", r"the catch is", r"the flip side",
    r"the price of", r"the cost of",
)
"""R35 phrases, as regular expressions."""
BASELINE: Final = DATA_DIR / "trailing_tags_baseline.txt"
HEADER: Final = (
    "# Trailing-tag and transactional-connective hits a human read\n"
    "# and judged keeps: a participle that describes the noun it\n"
    "# follows, a measured cost or price, a named trade-off. An\n"
    "# entry is not an exemption from the rule.\n"
    "# path<TAB>[Rnn] clause, with the clause's whitespace normalized\n"
    "# and no line number, so a reflow leaves an entry alone and an\n"
    "# edit to the clause retires it. Rewritten by\n"
    "# `tip trailing-accept`; read the delta with `tip trailing`\n"
    "# before accepting.\n"
    "# See tools/trailing_tags.py.\n"
)

SENTENCE_END = re.compile(r"[.;:?!]+[\"')\]*_”’]*(?=\s|$)")
CLOSERS: Final = "*_\"'”’)] "
EDGE = re.compile(r"^[^A-Za-z]+|[^A-Za-z]+$")
CONNECTIVE = re.compile(
    r"\b(?:" + "|".join(CONNECTIVES) + r")\b", re.IGNORECASE)
MEASURE = re.compile(
    r"\b(?:" + "|".join(re.escape(m) for m in MEASURES) + r")\b")


def word_of(token: str) -> str:
    """A token lowercased, without edge punctuation or emphasis marks."""
    return EDGE.sub("", token).lower()


def participle(word: str) -> bool:
    """Is this word a past participle by the regular or irregular test?"""
    return word in IRREGULAR or (len(word) > 4 and word.endswith("ed"))


def tag(segment: str) -> bool:
    """Is this final comma segment a participle tag or a "same" tag?"""
    words = [word_of(w) for w in segment.split()]
    words = [w for w in words if w]
    if not words:
        return False
    if words == ["unchanged"]:
        return True
    if words[:2] == ["the", "same"]:
        return len(words) - 2 <= MAX_SAME
    if not participle(words[0]):
        return False
    tail = words[1:]
    return (0 < len(tail) <= MAX_TAIL
            and MEASURE.search(" ".join(tail)) is not None)


def rules(clause: str) -> list[str]:
    """The rule labels this clause earns, R32 before R35."""
    found: list[str] = []
    if "," in clause:
        final = clause.rsplit(",", 1)[1].strip(CLOSERS)
        if tag(final):
            found.append("R32")
    if CONNECTIVE.search(clause):
        found.append("R35")
    return found


def clauses(text: str) -> Iterator[tuple[str, int]]:
    """(clause, index of its last character) per sentence-level clause."""
    start = 0
    for m in SENTENCE_END.finditer(text):
        yield text[start:m.start()], m.start() - 1
        start = m.end()
    tail = text[start:].rstrip()
    if tail:
        yield tail, start + len(tail) - 1


def find(doc: Document) -> Iterator[Finding]:
    """A finding per rule per clause, the message led by `[Rnn]`."""
    for paragraph in paragraphs(doc):
        text, lines = joined(paragraph)
        for clause, last in clauses(text):
            shown = " ".join(clause.split())
            for rule in rules(clause):
                yield Finding(doc.path, lines[max(last, 0)],
                              f"[{rule}] {shown}")


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
