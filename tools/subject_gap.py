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
the subject's own subtree. The dependency parse comes from spaCy, run
in a throwaway environment: the book pins a Python that spaCy has no
wheel for, so this module writes the paragraphs to JSON and starts
`tools/subject_gap_parse.py` under `uv run --no-project --python 3.12
--with spacy ...` (`PARSER_CMD`). uv caches that environment, so the
first run downloads an interpreter, spaCy, and the small English model
(a minute or so) and later runs start in a few seconds. When the
parser cannot start (no network on a first run, no `uv`), the check
says so and exits 0, since it is report-only.

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
run given paths compares against those files' entries alone, and
refuses `--accept`. `--gap N` changes the threshold for one run.

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
import json
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, Final
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.stranded_prepositions import (
    display,
    joined,
    paragraphs,
)

GAP: Final = 9
"""Fewest words between the subject head and its verb for a hit."""
PARSER: Final = Path(__file__).with_name("subject_gap_parse.py")
SPACY_MODEL: Final = (
    "https://github.com/explosion/spacy-models/releases/download/"
    "en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
)
PARSER_CMD: Final[tuple[str, ...]] = (
    "uv", "run", "--no-project", "--python", "3.12",
    "--with", "spacy>=3.8,<3.9", "--with", SPACY_MODEL,
    "python", str(PARSER),
)
"""The throwaway environment the spaCy half runs in."""
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
Parser = Callable[[list[str], int], list[list[Hit]]]


class ParserUnavailable(Exception):
    """The spaCy environment could not start or did not answer."""


def parse(texts: list[str], gap: int) -> list[list[Hit]]:
    """Run the spaCy half on these paragraphs; one hit list per text."""
    request = json.dumps({"gap": gap, "texts": texts})
    try:
        done = subprocess.run(
            list(PARSER_CMD), input=request, capture_output=True,
            text=True, encoding="utf-8", cwd=ROOT, check=False,
        )
    except FileNotFoundError as exc:
        raise ParserUnavailable(f"{PARSER_CMD[0]}: command not found") from exc
    if done.returncode:
        tail = done.stderr.strip().splitlines()[-1:] or ["no output"]
        raise ParserUnavailable(f"exit {done.returncode}: {tail[0]}")
    return json.loads(done.stdout)


def message(hit: Hit) -> str:
    """`[kinds] subject .. verb: sentence`, the printed and keyed form."""
    kinds = ",".join(hit["kinds"]) or "-"
    return (f"[{kinds}] {hit['subject']} .. {hit['verb']}: "
            f"{' '.join(hit['sentence'].split())}")


def find(docs: list[Document], parser: Parser = parse,
         gap: int = GAP) -> Iterator[Finding]:
    """A finding per held-open subject across these documents."""
    texts: list[str] = []
    places: list[tuple[Path, list[int]]] = []
    for doc in docs:
        for paragraph in paragraphs(doc):
            text, lines = joined(paragraph)
            texts.append(text)
            places.append((doc.path, lines))
    if not texts:
        return
    for (path, lines), hits in zip(places, parser(texts, gap), strict=True):
        for hit in hits:
            line = lines[min(hit["offset"], len(lines) - 1)]
            yield Finding(path, line, message(hit))


def key(shown: str, text: str) -> str:
    """The baseline line for a hit: path and message, no line number."""
    return f"{shown}\t{' '.join(text.split())}"


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


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--gap", type=int, default=GAP,
                    help=f"fewest words between subject and verb "
                         f"(default {GAP})")
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW sentence is found")
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
    try:
        findings = list(find([Document.parse(p) for p in paths],
                             parser, args.gap))
    except ParserUnavailable as exc:
        print(f"subject_gap: parser unavailable ({exc}); nothing checked",
              file=sys.stderr)
        return 0
    found = sorted({(display(f.path), f.line, f.message) for f in findings})
    baseline = load_baseline()
    scope = {e for e in baseline if e.split("\t", 1)[0] in shown_paths}
    current = {key(shown, text) for shown, _, text in found}
    new = [(s, n, t) for s, n, t in found if key(s, t) not in baseline]
    stale = sorted(scope - current)
    if args.accept:
        added = {key(s, t) for s, _, t in new}
        write_baseline((baseline - set(stale)) | added)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    for shown, line, text in found:
        accepted = key(shown, text) in baseline
        if accepted and not args.all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {shown}:{line}: {text}")
    for entry in stale:
        shown, text = entry.split("\t", 1)
        print(f"stale    {shown}: {text}")
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and new else 0


if __name__ == "__main__":
    raise SystemExit(main())
