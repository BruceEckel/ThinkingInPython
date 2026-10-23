#!/usr/bin/env python
"""Report sentences whose subject is held open from its verb.

The shape Bruce marked in chapter 31 on 2026-10-18: "an action that must
run on every entry into that state appears once". The subject head
("action") carries a postmodifier, here a relative clause, and the
finite verb ("appears") comes nine words later, so the reader holds
the subject open until the verb arrives. The `straighten` skill calls
it "the subject held open" and puts the threshold at about ten words,
or any parenthetical in the gap. The same shape comes with a
participle ("A program coded in the most straightforward way, without
concern for performance, can..."), a "such as" phrase, a prepositional
chain, or an appositive. The repair moves the modifier after the verb
("as X does"), turns it into a when-clause, or gives it a sentence of
its own; commit 0fc6e04d has 37 examples.

A hit is a nominal subject whose head verb follows it with at least
`GAP` (9) non-punctuation words between, nearly all of them inside
the subject's own subtree. The dependency parse is spaCy's, shared
with the other parse-based checks: `tools/parsed_prose.py` runs
`tools/spacy_parse.py` in a throwaway Python 3.12 environment (the book
pins a Python that spaCy has no wheel for) and caches the result under
`build/parses/`, and this module applies its rule to the token table in
pure Python. When the parser cannot start (no network on a first run,
no `uv`), the check says so and exits 0, since it is report-only. The
baseline file, the report, and the command line are
`tools/parse_check.py`'s, shared with the other parse-based checks.

The check reads each paragraph's prose through the same reader as
`tools/stranded_prepositions.py`: fenced listings, headings, block
quotes, tables, HTML, link and footnote definitions, and `#:` lines
are skipped, inline code spans become the placeholder `CODE` (which
the parser reads as a noun), and links keep their text. Chapters use
Semantic Line Breaks and the Solutions are hand-wrapped, so a
paragraph's lines are joined before parsing.

Report-only: it prints the hits and exits 0, because the parser is a
statistical model and no gate runs it. `--fail` exits 1 when a NEW hit
is found. It runs inside `tip prose` and alone as `tip subject-gap`.

A hit prints as `path:line: [kinds] subject .. verb: sentence`, the
line holding the subject head, and `kinds` the dependency labels of
the subject's postmodifiers (`relcl` a relative clause, `acl` a
participle or infinitive, `prep` a prepositional phrase, `appos` an
appositive, `conj` a coordinated subject). Every hit is read once by a
human, and the ones judged keeps live in
`tools/data/subject_gap_baseline.txt`, so a run prints only what is
new. An entry is `path<TAB>[kinds] subject .. verb: sentence` with
whitespace normalized and no line number, so a reflow or an edit
elsewhere in the file leaves the entry alone, while an edit to the
sentence retires it and the rewritten sentence reports as NEW. An
entry is a judged keep, not an exemption. The default run prints each
NEW hit and a summary (`N new, M accepted`), and lists a `stale` entry
that matches no hit any more. `--all` prints every hit, marked NEW or
accepted. `--accept` appends every NEW hit to the baseline and drops
the stale entries, keeping the file sorted and free of duplicates. A
run given paths compares against those files' entries alone, and `--accept`
with paths adds and drops entries for those files and keeps
every other file's entries. `--gap N` changes the threshold for one run.

Known false-positive shapes, all left in the report for a human: two
coordinated subjects ("A module or a package with the same name"), a
short appositive that names the subject, a relative clause of nine or
ten words that is the sentence's claim and reads once ("A method that
needs the class rather than an instance can be a `classmethod`"), a
"Done when:" criterion of several coordinated clauses that the parser
hangs off one subject, and a verb the parser mistakes for a noun
("records" in "A sampling profiler records which line..."). The
2026-10-18 sweep read 181 hits over the book: 37 were the shape and
read badly, and the rest seeded the baseline.

    uv run python -m tools.subject_gap           # new hits
    uv run python -m tools.subject_gap --all     # every hit
    uv run python -m tools.subject_gap --accept  # judged keeps
    uv run python -m tools.subject_gap Chapters/31_*.md
    uv run tip subject-gap CH=31
    uv run tip subject-gap-accept
"""

import argparse
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Final
from tools import parse_check
from tools.config import DATA_DIR
from tools.markdown import Document
from tools.parse_check import build_arg_parser, key, parse_args, run
from tools.parsed_prose import (
    Paragraph,
    Parser,
    ParserUnavailable,  # noqa: F401
    Sentence,
    children,
    parse,
    parsed,
    subtree,
)
from tools.report import Finding
from tools.stranded_prepositions import display  # noqa: F401

GAP: Final = 9
"""Fewest words between the subject head and its verb for a hit."""
PUNCT_SLACK: Final = 1
"""Tokens in the gap allowed to lie outside the subject's subtree."""
BASELINE: Final = DATA_DIR / "subject_gap_baseline.txt"
HEADER: Final = (
    "# Subject-gap hits a human read and judged keeps: coordinated\n"
    "# subjects, a short appositive, a relative clause that is the\n"
    "# claim and reads once, a parser error. An entry is not an\n"
    "# exemption from the rule.\n"
    "# path<TAB>[kinds] subject .. verb: sentence, with whitespace\n"
    "# normalized and no line number, so a reflow leaves an entry\n"
    "# alone and an edit to the sentence retires it. Rewritten by\n"
    "# `tip subject-gap-accept`; read the delta with `tip subject-gap`\n"
    "# before accepting.\n"
    "# See tools/subject_gap.py.\n"
)

Hit = dict[str, Any]


def message(hit: Hit) -> str:
    """`[kinds] subject .. verb: sentence`, the printed and keyed form."""
    kinds = ",".join(hit["kinds"]) or "-"
    return (f"[{kinds}] {hit['subject']} .. {hit['verb']}: "
            f"{' '.join(hit['sentence'].split())}")


def hits(paragraph: Paragraph, sentence: Sentence,
         gap: int = GAP) -> Iterator[Hit]:
    """The held-open subjects of one sentence, as hit dicts."""
    tokens = sentence.tokens
    for tok in tokens:
        if tok.dep not in ("nsubj", "nsubjpass"):
            continue
        verb = tokens[tok.head]
        if verb.i <= tok.i:
            continue
        words = [t for t in tokens
                 if tok.i < t.i < verb.i and not t.punct]
        if len(words) < gap:
            continue
        owned = subtree(tok, sentence)
        if sum(t.i not in owned for t in words) > PUNCT_SLACK:
            continue
        kinds = sorted({c.dep for c in children(tok, sentence)
                        if c.i > tok.i and not c.punct})
        yield {
            "offset": tok.idx,
            "subject": tok.text,
            "verb": verb.text,
            "gap": len(words),
            "kinds": kinds,
            "sentence": paragraph.text[sentence.start:sentence.end],
        }


def find(docs: list[Document], parser: Parser = parse,
         gap: int = GAP) -> Iterator[Finding]:
    """A finding per held-open subject across these documents."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            for sentence in paragraph.sentences:
                for hit in hits(paragraph, sentence, gap):
                    lines = paragraph.lines
                    line = lines[min(hit["offset"], len(lines) - 1)]
                    yield Finding(doc.path, line, message(hit))


def load_baseline(path: Path | None = None) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    return parse_check.load_baseline(path or BASELINE)


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    parse_check.write_baseline(entries, path or BASELINE, HEADER)


def add_gap_arg(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--gap", type=int, default=GAP,
                    help=f"fewest words between subject and verb "
                         f"(default {GAP})")


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = build_arg_parser(
        __doc__, fail_help="exit 1 when any NEW sentence is found",
        leading=add_gap_arg)
    args = parse_args(ap, argv)
    return run("subject_gap", args,
               lambda docs: find(docs, parser, args.gap),
               baseline=BASELINE, header=HEADER)


if __name__ == "__main__":
    raise SystemExit(main())
