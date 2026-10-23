#!/usr/bin/env python
"""Report italics that emphasize instead of introducing a term.

The style rule: italics introduce a new term, concept, or language
element, once, and are never used for emphasis. Design-pattern names
are the exception, italic on every mention (`tools/pattern_names.py`
checks those). The 2026-10-23 sweep removed 38 emphasis italics by
hand (commit cd9c4045); this check finds the same three shapes.

`[EMPHASIS]`: every word of the span is a function word from
`FUNCTION_WORDS` ("*is*", "*every*", "*whether*", "defers *how*"). A
function word never names a term, so the italics can only be stress.

`[REPEAT]`: the span's term was italicized earlier in the same file.
The first italic introduced it; this one repeats the introduction.

`[EARLIER]`: the span's term already appeared, without italics,
earlier in the file's prose ("the event loop ... the *event loop*").
A term the reader has already met is not being introduced. The test
compares lowercased text and also tries the term with a trailing "s"
or "es" added or removed. A "-ies" plural ("*proxies*" after "proxy")
goes unmatched and is left for a human.

Spans skipped by `REPEAT` and `EARLIER`: a pattern name from
`tools/data/pattern_names.txt`, a span of two or more words that are
all capitalized (a book title, *Design Patterns*), and a span shorter
than three letters. `EMPHASIS` checks every span but pattern names.

The check reads paragraphs with `tools/stranded_prepositions.py`'s
reader, so it skips the same input: fenced listings, headings, block
quotes (the Solutions exercise quotes among them), tables, HTML lines
and comments, link and footnote definitions, and `#:` lines. Code spans
become `CODE` and links keep their text, so an italic pattern name in
link text is still read. "Earlier" means earlier paragraphs of the same
file, plus the text before the span in its own paragraph. An italic
span is `*text*` with no space inside either star and no star or word
character outside them, so bold and `**` never match.

Calibration: run over the 15 chapters as they stood before commit
cd9c4045, it flags 32 of the 38 lines that commit changed. The six it
misses are a verb or an adjective stressed at its first use
("*suppresses*", "*enable*", "*infinite*", "*exact*"), which no word
list separates from a term being introduced.

Report-only: it prints the hits and exits 0. `--fail` exits 1 when a
NEW hit is found. It runs inside `tip prose` and alone as `tip italics`.

A hit prints as `path:line: [RULE] *term* :: clause`. The judged keeps
(a term the earlier prose used loosely and this sentence defines, an
italic that sets off a word as a word) live in
`tools/data/italics_baseline.txt`, keyed by path and message with no
line number, so a reflow leaves an entry alone and an edit to the
clause retires it. `--all` prints every hit, marked NEW or accepted.
`--accept` appends every NEW hit and drops the stale entries; with
paths it touches only those files' entries.

    uv run python -m tools.italics          # new hits
    uv run python -m tools.italics --all    # every hit
    uv run python -m tools.italics --accept # judged keeps
    uv run tip italics CH=45
    uv run tip italics-accept CH=45
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
from tools.stranded_prepositions import display, joined, paragraphs
from tools.trailing_tags import clauses

FUNCTION_WORDS: Final[frozenset[str]] = frozenset("""
    a an the is are was were be been being am do does did done has have
    had not no nor never always only also even still just very too
    all any both each every either neither none some same other
    and or but if whether because so than then
    what how which why when where who whom whose
    this that these those it its one
    can cannot could may might must shall should will would
    before after during inside outside within without into onto
    in on at of to from by for with about over under up down out off
    more most less least much many few
    first last once now here there
""".split())
"""Words whose italics can only be stress, never a term."""
PATTERN_NAMES: Final = DATA_DIR / "pattern_names.txt"
BASELINE: Final = DATA_DIR / "italics_baseline.txt"
HEADER: Final = (
    "# Italic spans a human read and judged keeps: a term the earlier\n"
    "# prose used loosely and this sentence defines, a word set off as\n"
    "# a word. An entry is not an exemption from the rule.\n"
    "# path<TAB>[RULE] *term* :: clause, with whitespace normalized and\n"
    "# no line number, so a reflow leaves an entry alone and an edit to\n"
    "# the clause retires it. Rewritten by `tip italics-accept`; read\n"
    "# the delta with `tip italics` before accepting.\n"
    "# See tools/italics.py.\n"
)

ITALIC = re.compile(r"(?<![*\w])\*(?![*\s])([^*\n]+?)(?<!\s)\*(?![*\w])")


def pattern_names(path: Path = PATTERN_NAMES) -> frozenset[str]:
    """The pattern names, lowercased, without comments or exclusions."""
    return frozenset(
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith(("#", "!")))


def unitalic(text: str) -> str:
    """The text with its italic stars removed and the words kept."""
    return ITALIC.sub(r"\1", text)


def forms(term: str) -> re.Pattern[str]:
    """The term, singular or plural by a trailing s or es, as words."""
    variants = {term, term + "s"}
    if term.endswith("s"):
        variants.add(term[:-1])
    if term.endswith("es"):
        variants.add(term[:-2])
    alternatives = "|".join(re.escape(v) for v in sorted(variants))
    return re.compile(rf"\b(?:{alternatives})\b")


def title(term: str) -> bool:
    """Is this span two or more capitalized words, like a book title?"""
    words = term.split()
    return len(words) > 1 and all(w[:1].isupper() for w in words)


def emphasis(term: str) -> bool:
    """Is every word of the span a function word?"""
    return all(w in FUNCTION_WORDS for w in term.lower().split())


def clause_at(text: str, index: int) -> tuple[str, int]:
    """(the clause holding `index`, the index of its last character)."""
    for clause, last in clauses(text):
        if index <= last:
            return clause, last
    return text, len(text) - 1


def find(doc: Document,
         names: frozenset[str] | None = None) -> Iterator[Finding]:
    """A finding per italic span that emphasizes or re-introduces."""
    names = pattern_names() if names is None else names
    italicized: set[str] = set()
    seen = ""
    for paragraph in paragraphs(doc):
        text, lines = joined(paragraph)
        for m in ITALIC.finditer(text):
            term = " ".join(m.group(1).split())
            lowered = term.lower()
            if lowered in names:
                continue
            rule = None
            if emphasis(term):
                rule = "EMPHASIS"
            elif len(lowered) >= 3 and not title(term):
                before = seen + unitalic(text[:m.start()]).lower()
                if lowered in italicized:
                    rule = "REPEAT"
                elif forms(lowered).search(before):
                    rule = "EARLIER"
                italicized.add(lowered)
            if rule:
                clause, _ = clause_at(text, m.start())
                shown = " ".join(clause.split())
                yield Finding(doc.path, lines[m.start()],
                              f"[{rule}] *{term}* :: {shown}")
        seen += unitalic(text).lower() + "\n"


def key(shown: str, message: str) -> str:
    """The baseline line for a hit: path and message, no line number."""
    return f"{shown}\t{' '.join(message.split())}"


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
                    help="exit 1 when any NEW hit is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    args = ap.parse_args(argv)
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    names = pattern_names()
    found = sorted(
        (display(f.path), f.line, f.message)
        for p in paths for f in find(Document.parse(p), names)
    )
    baseline = load_baseline()
    scope = {e for e in baseline if e.split("\t", 1)[0] in shown_paths}
    current = {key(shown, message) for shown, _, message in found}
    new = [(s, n, t) for s, n, t in found if key(s, t) not in baseline]
    stale = sorted(scope - current)
    if args.accept:
        added = {key(s, t) for s, _, t in new}
        write_baseline((baseline - set(stale)) | added)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    for shown, line, message in found:
        accepted = key(shown, message) in baseline
        if accepted and not args.all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {shown}:{line}: {message}")
    for entry in stale:
        shown, message = entry.split("\t", 1)
        print(f"stale    {shown}: {message}")
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and new else 0


if __name__ == "__main__":
    raise SystemExit(main())
