#!/usr/bin/env python
"""Report prose clauses that bound a set with a count or exclusivity word.

An overclaim candidate is a clause that says "one restriction", "the
only way", "nothing else", "all it does", or "the rest is" about a set
whose other members the text then contradicts. Chapter 45 said "PEP
255's generator is a coroutine with one restriction" while the same
paragraph called the send channel "the other half". The test a reader
applies: can you point at the second member? If so, the bound is
false and the sentence needs rewording. If not, the count is true and
the hit is a keep.

`[BOUND]` is the one rule. A clause earns it from any pattern in
`PATTERNS`: "the one/only/sole/single X", a count word ("one", "a
single", "two", "three", "four") before a noun from `NOUNS`, "one and
only", "nothing else", "no other", "all it does", "that is all", "the
rest is", "everything else", and "alone". `RULES` maps a label to its
regular expression, so a second rule can join later.

The check reads each paragraph's prose, joins its lines, and splits
the text into clauses at `.`, `;`, `:`, `?`, and `!`, the way
`tools/trailing_tags.py` does. It reuses
`tools/stranded_prepositions.py`'s paragraph reader, so fenced
listings, headings, block quotes, tables, HTML, link definitions,
footnote definitions, and `#:` lines are skipped. Matching is
case-insensitive.

Report-only: it prints the hits and exits 0. `--fail` exits 1 when a
NEW hit is found. It runs inside `tip prose` and alone as `tip
overclaims`. A hit prints as `path:line: [BOUND] clause`. An entry in
`tools/data/overclaims_baseline.txt` is `path<TAB>[BOUND] clause`
with the clause's whitespace normalized and no line number, a judged
keep. The default run prints each NEW hit and `N new, M accepted`;
`--all` prints every hit; `--accept` adds the NEW hits and drops stale
entries, for the given files alone when paths are given.

    uv run python -m tools.overclaims          # new hits
    uv run python -m tools.overclaims --all    # every hit
    uv run tip overclaims CH=45
    uv run tip overclaims-accept CH=45
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

NOUNS: Final = (
    r"restrictions?|differences?|jobs?|rules?|ways?|exceptions?|changes?|"
    r"limitations?|reasons?|places?|requirements?|constraints?|catch|"
    r"drawbacks?|caveats?|problems?|conditions?|details?|things?|"
    r"purposes?|costs?|points?|steps?|lines?|calls?|sources?|kinds?|"
    r"shapes?|moves?|tasks?|responsibilit(?:y|ies)|decisions?|choices?|"
    r"options?|parts?|pieces?|cases?|uses?|effects?|edits?|"
    r"consequences?|benefits?|advantages?|gains?|losses?|tradeoffs?|"
    r"trade-offs?|obligations?|guarantees?|promises?|hooks?|knobs?|"
    r"flags?|arguments?|parameters?|fields?|methods?|functions?|"
    r"classes?|statements?|expressions?|operations?|branches?|paths?|"
    r"channels?|holes?|gaps?"
)
"""Nouns that name a member of a set."""
PATTERNS: Final[tuple[str, ...]] = (
    r"\bthe (?:one|only|sole|single)\s+\w+",
    r"\b(?:one|a single|exactly one|only one|just one|two|three|four)"
    rf"\s+(?:{NOUNS})\b",
    r"\bone and only\b",
    r"\bnothing else\b",
    r"\bno other\b",
    r"\ball it (?:does|takes|needs|asks|requires)\b",
    r"\b(?:that|this|which) is (?:all|the whole|the only)\b",
    r"\bthe rest (?:is|stays|are)\b",
    r"\beverything else\b",
    r"\balone\b",
)
"""Bounding words and phrases, as regular expressions."""
RULES: Final[dict[str, re.Pattern[str]]] = {
    "BOUND": re.compile("|".join(f"(?:{p})" for p in PATTERNS),
                        re.IGNORECASE),
}
"""Rule label to its pattern."""
BASELINE: Final = DATA_DIR / "overclaims_baseline.txt"
HEADER: Final = (
    "# Overclaim candidates a human read and judged keeps: the count\n"
    "# or exclusivity word is true, and no second member can be\n"
    "# pointed at. An entry is not an exemption from the rule.\n"
    "# path<TAB>[BOUND] clause, with the clause's whitespace normalized\n"
    "# and no line number, so a reflow leaves an entry alone and an\n"
    "# edit to the clause retires it. Rewritten by\n"
    "# `tip overclaims-accept`; read the delta with `tip overclaims`\n"
    "# before accepting.\n"
    "# See tools/overclaims.py.\n"
)

SENTENCE_END = re.compile(r"[.;:?!]+[\"')\]*_”’]*(?=\s|$)")


def rules(clause: str) -> list[str]:
    """The rule labels this clause earns."""
    return [label for label, rx in RULES.items() if rx.search(clause)]


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
    """A finding per rule per clause, the message led by `[LABEL]`."""
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
