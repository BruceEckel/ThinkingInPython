#!/usr/bin/env python
"""Survey the reading level of the book's prose, per file and per section.

Three published formulas read the same counts of words, sentences,
syllables, letters, and polysyllables (words of three or more
syllables):

- Flesch-Kincaid grade: `0.39 * W/S + 11.8 * Y/W - 15.59`, the US school
  grade a reader needs, driven by sentence length and syllables per word.
- SMOG: `1.0430 * sqrt(P * 30 / S) + 3.1291`, driven by the density of
  polysyllables, so a run of long technical words moves it most.
- Coleman-Liau: `0.0588 * L - 0.296 * S' - 15.8`, with L the letters per
  100 words and S' the sentences per 100 words. It counts letters, not
  syllables, so it needs no syllable counter and checks the other two.

The tool reports and gates nothing and keeps no baseline. It is not part
of `tip prose`.

What it reads. `tools.word_stutter.paragraphs()` supplies the prose:
fenced listings, headings, block quotes (the generated exercise
statements), tables, HTML, link definitions, and `#:` lines are
skipped, and list items, `Hint:` paragraphs, and footnote definitions
are read, each list item as its own paragraph. A reader reads link text,
so `[text](url)` counts as `text`; images, footnote references, and
`{#id}` attributes count as nothing. A paragraph's lines are joined with
single spaces and split by `tools.reflow_prose.split_sentences()`, the
repo's own splitter. A paragraph's last piece is a sentence with or
without end punctuation, so a fragment list item is one sentence, and a
piece with no word is dropped.

What a word is. A prose word matches `[A-Za-z]+(?:['’-][A-Za-z]+)*`
after the `*` characters go, so "don't" and "keyword-only" are one word
each and a number such as 3.15 or 2026 is none. An em-dash written
`--`, `---`, or `—` separates words.

What a code span is. `--code words` (the default) reads each identifier
in a span (`[A-Za-z_][A-Za-z0-9_]*`) as one word. Its letters are its
ASCII letters. Its syllables are the sum over its parts, split on
underscores, on digits, and at a lower-to-upper boundary, so
`StopIteration` is Stop + Iteration, `validate_output` is validate +
output, and `__post_init__` is post + init. A run of capitals before a
capitalized word is its own part: `HTTPServer` is HTTP + Server. A span
with no identifier (`[1]`, `42`, `#:`) is no word. `--code it` reads
every span as the one word "it", one syllable and two letters, the
lower bound that treats every name as a word the reader knows. Code
spans are cut out before the word pattern runs, so nothing inside a
span counts twice.

Sections. A line starting `## `, outside a fence, opens a section that
runs to the next such line, so `###` and deeper headings stay inside
their section. Prose before the first one is `(opening)`. A paragraph
belongs to the section its first line is in. The label is the heading
without a trailing `{#id}` or backticks, and a section with no
sentence prints no row.

Syllables. `syllables(word)` looks a lowercase form up in `HAND` (a
small table in this module for technical words no dictionary has), then
in `tools/data/syllable_overrides.txt` (generated), then falls back to
`heuristic()`, a vowel-group counter with a silent-e rule. A hyphenated
word is looked up whole and, when absent, summed over its parts. The
generated table holds each word of the book where the heuristic and the
CMU Pronouncing Dictionary's first pronunciation disagree, with the
dictionary's count. The dictionary is a separate program,
`tools/syllable_dict.py`, run in a throwaway environment with `uv run
--no-project --python 3.12 --with cmudict` (`DICT_CMD`), because the
project adds no dependency for a survey. It is needed only by
`--calibrate`; an ordinary run reads the table.

Output. Per file: a table with one row for the whole file and one for
each section (words, sentences, words per sentence, syllables per word,
and the three scores), then the longest sentences of the file. With more
than one file a summary table follows, hardest first, and a last line
gives the Flesch-Kincaid grade over all of them.

Flags:

- `--code {words,it}`: how a code span counts (default `words`).
- `--longest N`: sentences listed per file (default 10; 0 prints none).
- `--summary`: print only the summary table and its last line.
- `--target GRADE`: mark every row whose Flesch-Kincaid grade is above
  GRADE with ` >`, and end with `K of M sections above grade G`.
- `--fail`: with `--target`, exit 1 when a whole-file grade is above it.
- `--calibrate`: compare the syllable counter with the dictionary over
  the words in the paths: agreement and bias before and after `HAND` and
  the table, the words the table lacks, its stale entries, and the words
  the dictionary lacks, so you can add a `HAND` entry for a miscounted
  technical word. `--calibrate --write` updates the table: the words of
  the paths join the words it holds, and an entry the heuristic now
  gets right is dropped, so a run over one chapter keeps the rest of
  the book's entries. When the dictionary cannot start, calibration
  says so on stderr and exits 0.

    uv run python -m tools.reading_level HighLevel.md
    uv run python -m tools.reading_level --summary
    uv run python -m tools.reading_level --calibrate --write
    uv run tip reading-level CH=44 ARGS="--target 8"
"""

import argparse
import bisect
import json
import math
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Final, NamedTuple
from tools.config import ROOT
from tools.markdown import Document
from tools.reflow_prose import split_sentences
from tools.repo import add_paths_arg, md_files, write_text_lf
from tools.stranded_prepositions import display
from tools.word_stutter import ATTRS, FOOTNOTE_REF, IMAGE, LINK, paragraphs

DICT_CMD: Final = (
    "uv", "run", "--no-project", "--python", "3.12", "--with", "cmudict",
    "python", str(ROOT / "tools" / "syllable_dict.py"),
)
"""The throwaway environment the dictionary half runs in."""
OVERRIDES: Path = ROOT / "tools" / "data" / "syllable_overrides.txt"
"""The generated table of dictionary counts; tests point this at a tmp file."""
OPENING: Final = "(opening)"
LABEL_WIDTH: Final = 44

WORD: Final = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]+(?:['’-][A-Za-z]+)*")
CODE_SPAN: Final = re.compile(r"(``[^`]+``|`[^`]+`)")
IDENT: Final = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*")
IDENT_PART: Final = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+")
SECTION: Final = re.compile(r"^## +(.*?)\s*$")

HAND: Final[dict[str, int]] = {
    # Spoken by ear. An acronym read letter by letter gets one syllable
    # per letter; one read as a word gets that word's count.
    "asyncio": 4, "cpython": 3, "expr": 2, "getattr": 3, "gof": 3,
    "json": 2, "mro": 3, "namespace": 2, "placeholder": 3,
    "setattr": 3, "traceback": 2, "zio": 2,
}
"""Technical words no dictionary has, counted by ear (see `--calibrate`)."""

VOWEL_GROUP: Final = re.compile(r"[aeiouy]+")
CONSONANT_LE: Final = re.compile(r"[^aeiouy]le$")
SIBILANT_ES: Final = ("ses", "zes", "ces", "ges", "xes", "ches", "shes")
CONSONANT_LES: Final = re.compile(r"[^aeiouy]les$")
SYLLABIC_LED: Final = re.compile(r"[^aeiouyl]led$")
HIATUS_UA: Final = re.compile(r"(?<![qg])ua[lt]")
SYLLABIC_M: Final = re.compile(r"(?:thm|ism|asm)s?$")


class DictionaryUnavailable(Exception):
    """The cmudict environment could not start or did not answer."""


Lookup = Callable[[list[str]], dict[str, int]]
"""Forms in; the dictionary's syllable count for each form it has."""


def heuristic(word: str) -> int:
    """Vowel groups, less a silent final e, -ed, or -es."""
    w = word.lower()
    if len(w) <= 3:
        return 1
    count = len(VOWEL_GROUP.findall(w))
    if w.endswith("e"):
        # -ue sounds its e after a vowel group: value, continue.
        if not (w.endswith(("ee", "ye")) or CONSONANT_LE.search(w)
                or w.endswith("ue") and not w.endswith("que")):
            count -= 1
    elif w.endswith("ed") and not w.endswith(("ted", "ded")):
        # -led after one consonant and -ied are syllables: handled,
        # bundled; supplied, copied.
        if not (SYLLABIC_LED.search(w) or w.endswith("ied")):
            count -= 1
    elif w.endswith("es") and not w.endswith(SIBILANT_ES):
        # -ies and -les are syllables: carries, copies; handles, tables.
        if not (w.endswith("ies") or CONSONANT_LES.search(w)):
            count -= 1
    # The u and a split into two syllables: actual, evaluate.
    count += len(HIATUS_UA.findall(w))
    # A final m after a consonant takes its own syllable: algorithm, prism.
    count += bool(SYLLABIC_M.search(w))
    return max(count, 1)


def plain_heuristic(form: str) -> int:
    """`heuristic()` of a form with its apostrophe removed ("don't")."""
    return heuristic(form.replace("'", ""))


@cache
def load_table(path: Path) -> dict[str, int]:
    """The generated `word count` table; empty when the file is missing."""
    table: dict[str, int] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return table
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        word, _, count = line.partition(" ")
        if count.strip().isdigit():
            table[word] = int(count)
    return table


def table() -> dict[str, int]:
    return load_table(OVERRIDES)


def form_syllables(form: str) -> int:
    """One lowercase form: `HAND`, then the table, then the heuristic."""
    if form in HAND:
        return HAND[form]
    known = table()
    if form in known:
        return known[form]
    return plain_heuristic(form)


def normalize(word: str) -> str:
    """Lowercase, straight apostrophe, no possessive "'s"."""
    w = word.lower().replace("’", "'").removesuffix("'s")
    return w.strip("'-")


def single_forms(word: str) -> tuple[str, ...]:
    """The forms the syllable counter looks up for a prose word."""
    w = normalize(word)
    if "-" in w:
        return tuple(p for p in w.split("-") if p)
    return (w,) if w else ()


def syllables(word: str) -> int:
    """Syllables of a prose word, a hyphenated or apostrophe form too."""
    w = normalize(word)
    if not w:
        return 0
    if "-" in w:
        if w in HAND:
            return HAND[w]
        if w in table():
            return table()[w]
        return sum(form_syllables(p) for p in w.split("-") if p)
    return form_syllables(w)


class Unit(NamedTuple):
    """One counted word: its letters, syllables, and single forms."""

    letters: int
    syllables: int
    parts: tuple[str, ...]


def prose_unit(word: str) -> Unit:
    return Unit(sum(c.isalpha() for c in word), syllables(word),
                single_forms(word))


def code_units(span: str, mode: str) -> list[Unit]:
    """The words one code span contributes."""
    if mode == "it":
        return [Unit(2, 1, ("it",))]
    units: list[Unit] = []
    for ident in IDENT.finditer(span.strip("`")):
        parts = tuple(
            m.group(0).lower()
            for chunk in re.split(r"[_0-9]+", ident.group(0))
            for m in IDENT_PART.finditer(chunk))
        if parts:
            units.append(Unit(sum(len(p) for p in parts),
                              sum(form_syllables(p) for p in parts), parts))
    return units


def units_of(text: str, mode: str) -> list[Unit]:
    """Every counted word of one sentence, in order."""
    units: list[Unit] = []
    for index, piece in enumerate(CODE_SPAN.split(text)):
        if index % 2:
            units.extend(code_units(piece, mode))
        else:
            units.extend(prose_unit(m.group(0))
                         for m in WORD.finditer(piece.replace("*", "")))
    return units


@dataclass(frozen=True)
class Counts:
    words: int = 0
    sentences: int = 0
    syllables: int = 0
    letters: int = 0
    polysyllables: int = 0

    def __add__(self, other: "Counts") -> "Counts":
        return Counts(
            self.words + other.words, self.sentences + other.sentences,
            self.syllables + other.syllables, self.letters + other.letters,
            self.polysyllables + other.polysyllables)


def total(counts: Iterable[Counts]) -> Counts:
    return sum(counts, Counts())


def flesch_kincaid(c: Counts) -> float:
    if not c.words or not c.sentences:
        return 0.0
    return (0.39 * c.words / c.sentences
            + 11.8 * c.syllables / c.words - 15.59)


def smog(c: Counts) -> float:
    if not c.sentences:
        return 0.0
    return 1.0430 * math.sqrt(c.polysyllables * 30 / c.sentences) + 3.1291


def coleman_liau(c: Counts) -> float:
    if not c.words:
        return 0.0
    return (0.0588 * (c.letters / c.words * 100)
            - 0.296 * (c.sentences / c.words * 100) - 15.8)


class Sentence(NamedTuple):
    line: int
    text: str
    section: str
    units: tuple[Unit, ...]

    @property
    def counts(self) -> Counts:
        return Counts(
            len(self.units), 1, sum(u.syllables for u in self.units),
            sum(u.letters for u in self.units),
            sum(1 for u in self.units if u.syllables >= 3))


def clean(line: str) -> str:
    """Images, footnote references, and attributes gone; link text kept."""
    line = IMAGE.sub("", line)
    line = LINK.sub(r"\1", line)
    line = FOOTNOTE_REF.sub("", line)
    return ATTRS.sub("", line)


def heading_label(text: str) -> str:
    return ATTRS.sub("", text).replace("`", "").strip() or OPENING


def section_labels(doc: Document) -> list[str]:
    """Per line, the label of the `##` section the line is in."""
    fenced = doc.in_fence()
    labels: list[str] = []
    current = OPENING
    for index, line in enumerate(doc.lines):
        if not fenced[index] and (m := SECTION.match(line)):
            current = heading_label(m.group(1))
        labels.append(current)
    return labels


def paragraph_sentences(
    paragraph: list[tuple[int, str]],
) -> list[tuple[int, str]]:
    """(start line, text) of each sentence in one paragraph."""
    pieces = [(n, t) for n, t in paragraph if t.strip()]
    if not pieces:
        return []
    starts: list[int] = []
    joined = ""
    for _, text in pieces:
        if joined:
            joined += " "
        starts.append(len(joined))
        joined += text
    found: list[tuple[int, str]] = []
    position = 0
    line = pieces[0][0]
    for sentence in split_sentences(joined):
        at = joined.find(sentence, position)
        if at >= 0:
            position = at + len(sentence)
            line = pieces[bisect.bisect_right(starts, at) - 1][0]
        found.append((line, sentence))
    return found


def read(doc: Document, mode: str) -> list[Sentence]:
    """Every counted sentence of one document."""
    labels = section_labels(doc)
    sentences: list[Sentence] = []
    for paragraph in paragraphs(doc, clean):
        section = labels[paragraph[0][0] - 1]
        for line, text in paragraph_sentences(paragraph):
            units = tuple(units_of(text, mode))
            if units:
                sentences.append(Sentence(line, text, section, units))
    return sentences


@dataclass(frozen=True)
class FileReport:
    path: Path
    sentences: list[Sentence]
    sections: dict[str, Counts]
    whole: Counts


def report(doc: Document, mode: str) -> FileReport:
    sentences = read(doc, mode)
    sections: dict[str, Counts] = {}
    for s in sentences:
        sections[s.section] = sections.get(s.section, Counts()) + s.counts
    return FileReport(doc.path, sentences, sections,
                      total(sections.values()))


HEADER_COLUMNS: Final = (
    f"{'words':>7}{'sent':>7}{'w/sent':>8}{'syl/w':>7}"
    f"{'FK':>7}{'SMOG':>7}{'C-L':>7}")


def clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[:width - 3] + "..."


def row(label: str, c: Counts, target: float | None,
        width: int = LABEL_WIDTH) -> str:
    fk = flesch_kincaid(c)
    line = (f"  {clip(label, width):<{width}}"
            f"{c.words:>7}{c.sentences:>7}"
            f"{c.words / c.sentences:>8.1f}{c.syllables / c.words:>7.2f}"
            f"{fk:>7.1f}{smog(c):>7.1f}{coleman_liau(c):>7.1f}")
    if target is not None and fk > target:
        line += " >"
    return line


def header(label: str, width: int = LABEL_WIDTH) -> str:
    return f"  {label:<{width}}{HEADER_COLUMNS}"


def file_block(r: FileReport, longest: int, target: float | None) -> list[str]:
    shown = display(r.path)
    if not r.sentences:
        return [shown, "  no prose"]
    out = [shown, header("section"), row("(whole file)", r.whole, target)]
    out.extend(row(label, c, target) for label, c in r.sections.items())
    if longest > 0:
        ranked = sorted(r.sentences, key=lambda s: (-len(s.units), s.line))
        out.append("  longest sentences")
        for s in ranked[:longest]:
            out.append(f"  {len(s.units):>6}  {shown}:{s.line}: "
                       f"{clip(s.text, 100)}")
    return out


def summary_block(
    reports: Sequence[FileReport], target: float | None,
) -> list[str]:
    rows = sorted((r for r in reports if r.sentences),
                  key=lambda r: (-flesch_kincaid(r.whole), display(r.path)))
    if not rows:
        return []
    # A path is the row's whole identity, so the column fits the longest.
    width = max(len(display(r.path)) for r in rows)
    out = [header("file", width)]
    out.extend(row(display(r.path), r.whole, target, width) for r in rows)
    everything = total(r.whole for r in rows)
    out.append(f"{len(rows)} files, {everything.words} words, "
               f"{everything.sentences} sentences; Flesch-Kincaid "
               f"{flesch_kincaid(everything):.1f} over all of them")
    return out


def dictionary(words: list[str]) -> dict[str, int]:
    """Ask the cmudict helper for each word's syllable count."""
    request = json.dumps({"words": words})
    try:
        done = subprocess.run(
            list(DICT_CMD), input=request, capture_output=True, text=True,
            encoding="utf-8", cwd=ROOT, check=False)
    except FileNotFoundError as exc:
        raise DictionaryUnavailable(
            f"{DICT_CMD[0]}: command not found") from exc
    if done.returncode:
        tail = done.stderr.strip().splitlines()[-1:] or ["no output"]
        raise DictionaryUnavailable(f"exit {done.returncode}: {tail[0]}")
    try:
        counts: dict[str, int] = json.loads(done.stdout)["counts"]
    except (ValueError, KeyError, TypeError) as exc:
        raise DictionaryUnavailable(f"unreadable answer: {exc}") from exc
    return counts


TABLE_HEADER: Final = """\
# Syllable counts for words in the book's prose where the heuristic in
# tools/reading_level.py and the CMU Pronouncing Dictionary's first
# pronunciation disagree. Each line is `word count`, the dictionary's
# count.
#
# Source: CMUdict, Carnegie Mellon University (BSD-style license), read
# through the `cmudict` package by tools/syllable_dict.py.
#
# Generated; edit `HAND` in tools/reading_level.py, not this file.
# Update it over the book with:
#   uv run python -m tools.reading_level --calibrate --write
# A run over other paths adds their words and keeps these.
"""


def percent(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}%" if whole else "0.0%"


def agreement(
    counts: Counter[str], known: dict[str, int],
    count: Callable[[str], int],
) -> str:
    words = [w for w in counts if w in known]
    tokens = sum(counts[w] for w in words)
    same_words = sum(1 for w in words if count(w) == known[w])
    same_tokens = sum(counts[w] for w in words if count(w) == known[w])
    bias = (sum(counts[w] * (count(w) - known[w]) for w in words) / tokens
            if tokens else 0.0)
    return (f"{percent(same_words, len(words))} of those words, "
            f"{percent(same_tokens, tokens)} of their tokens; "
            f"net bias {bias:+.4f} syllables per word")


def calibrate(
    paths: list[Path], mode: str, lookup: Lookup, write: bool,
) -> int:
    counts: Counter[str] = Counter()
    for path in paths:
        for s in read(Document.parse(path), mode):
            for unit in s.units:
                counts.update(unit.parts)
    try:
        known = lookup(sorted(set(counts) | set(table())))
    except DictionaryUnavailable as exc:
        print(f"reading_level: dictionary unavailable ({exc}); "
              f"nothing calibrated", file=sys.stderr)
        return 0
    tokens = sum(counts.values())
    have = [w for w in counts if w in known]
    have_tokens = sum(counts[w] for w in have)
    if write:
        # The words of these paths join the words the table holds, so a
        # run over one chapter cannot drop the rest of the book's
        # entries. An entry the heuristic now gets right is left out.
        candidates = set(have) | {w for w in table() if w in known}
        entries = {w: known[w] for w in candidates
                   if w not in HAND and plain_heuristic(w) != known[w]}
        body = TABLE_HEADER
        body += "".join(f"{w} {n}\n" for w, n in sorted(entries.items()))
        write_text_lf(OVERRIDES, body)
        load_table.cache_clear()
        print(f"wrote {len(entries)} entries to {display(OVERRIDES)}")
        return 0
    print(f"{len(counts)} distinct words, {tokens} tokens in "
          f"{len(paths)} files")
    print(f"the dictionary has {len(have)} of them "
          f"({percent(have_tokens, tokens)} of tokens)")
    print("heuristic alone: " + agreement(counts, known, plain_heuristic))
    print("with HAND and the table: "
          + agreement(counts, known, form_syllables))
    by_use = sorted(counts, key=lambda w: (-counts[w], w))
    missing = [w for w in by_use if w in known and w not in HAND
               and form_syllables(w) != known[w]]
    print(f"missing from the table: {len(missing)}")
    for w in missing[:40]:
        print(f"  {counts[w]:>6}  {w}  heuristic {plain_heuristic(w)}, "
              f"dictionary {known[w]}")
    stale = [w for w, n in sorted(table().items())
             if w in known and w not in HAND
             and (n == plain_heuristic(w) or n != known[w])]
    print(f"stale in the table: {len(stale)}")
    for w in stale[:40]:
        print(f"  {w}  table {table()[w]}, heuristic {plain_heuristic(w)}, "
              f"dictionary {known[w]}")
    print("not in the dictionary, most frequent first:")
    unknown = [w for w in by_use
               if w not in known and w not in HAND and len(w) > 2]
    for w in unknown[:60]:
        print(f"  {counts[w]:>6}  {w}  {form_syllables(w)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--code", choices=("words", "it"), default="words",
                    help="how a code span counts (default words)")
    ap.add_argument("--longest", type=int, default=10,
                    help="longest sentences listed per file (default 10)")
    ap.add_argument("--summary", action="store_true",
                    help="print only the summary table")
    ap.add_argument("--target", type=float, default=None,
                    help="mark rows whose Flesch-Kincaid grade is above it")
    ap.add_argument("--fail", action="store_true",
                    help="with --target, exit 1 when a file is above it")
    ap.add_argument("--calibrate", action="store_true",
                    help="compare the syllable counter with CMUdict")
    ap.add_argument("--write", action="store_true",
                    help="with --calibrate, rewrite the syllable table")
    return ap


def main(argv: list[str] | None = None, lookup: Lookup = dictionary) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.write and not args.calibrate:
        ap.error("--write needs --calibrate")
    named: list[str | Path] = list(args.paths) or [
        ROOT / "Chapters", ROOT / "Solutions"]
    paths = md_files(named)
    if args.calibrate:
        return calibrate(paths, args.code, lookup, args.write)
    reports = [report(Document.parse(p), args.code) for p in paths]
    target: float | None = args.target
    out: list[str] = []
    if not args.summary:
        for r in reports:
            out.extend(file_block(r, args.longest, target))
            out.append("")
    if args.summary or len(reports) > 1:
        out.extend(summary_block(reports, target))
    for line in out:
        print(line)
    if target is not None:
        sections = [c for r in reports for c in r.sections.values()]
        above = sum(1 for c in sections if flesch_kincaid(c) > target)
        print(f"{above} of {len(sections)} sections above grade {target:g}")
        if args.fail and any(
                r.sentences and flesch_kincaid(r.whole) > target
                for r in reports):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
