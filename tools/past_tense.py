#!/usr/bin/env python
"""Report each past-tense verb in the prose and the headings.

The author's style rule: present tense for standing behavior. Write
what code, a pattern, or a tool does, not what it did earlier in the
text the reader is reading ("In every case the observer is a callable,"
not "was"). The past creeps into headings and closing sections, where
the writing turns retrospective: "What Stayed Constant" is "What Stays
Constant," and "One design served three jobs in this chapter" is
"serves." The past stays for an event the text can point at: a release
that added a feature, a measurement taken on a date, a run whose output
is on the page.

This check reads the dependency parse that `tools/parsed_prose.py`
caches under `build/parses/` (spaCy, run in a throwaway Python 3.12
environment; see that module). A past-tense verb is either (a) a token
tagged `VBD` whose dep is not `aux` or `auxpass` ("served", "stayed",
and "was" as a copula), or (b) a `VBN` or `VBG` token with a child of
dep `aux` or `auxpass` tagged `VBD`: a past passive ("was built"), a
past progressive ("was running"), or a past perfect ("had loaded"). A
present perfect ("has loaded") is not a hit, since its auxiliary is
`VBZ` or `VBP`. A hit in form (b) is named with its auxiliary. A
sentence with two past verbs reports both.

Three labels. `[PAST]`: the past verb is the verb of a main clause
(its dep is `ROOT`, or `conj` with a head chain that reaches `ROOT`
through `conj` links alone; for a past passive or progressive, its main
verb). `[PAST-SUB]`: every other past verb (dep `relcl`, `acl`, `advcl`,
`ccomp`, `xcomp`, `pcomp`, `csubj`, or a `conj` under one of those).
`[PAST-HEADING]`: a heading, which the paragraph reader skips, so this
check reads the document's heading lines itself (outside fenced
blocks), strips the `#`s and any `{#id}` attribute, and parses the
heading as its own text. A heading hit has this one label whatever the
clause. The parser sees the headings in one call that skips the cache,
since headings are short.

`[PAST]` and `[PAST-HEADING]` are the default rules, held to a baseline.
`[PAST-SUB]` is a survey rule: it prints only under `--survey`, each
line marked `survey` after the default lines, is never baselined, and
is not counted in `N new`. The first run (2026-10-19) found 1283 hits,
and the session's read found nearly all of them subordinate ("the
function the caller passed", "the case that failed"): an anterior
reference inside present narration, not the drift the rule describes.
The drift is a main-clause past ("One design served three jobs in this
chapter"). `tip past-tense CH=NN ARGS=--survey` feeds an activate pass.
A hit prints as `path:line: [PAST] <verb>: <sentence>`, the line holding
the sentence's first character or the heading's line. A verb in form
(b) is named with its auxiliary.

Four skips, per sentence, that print nothing. A sentence is a dated
event when it holds a year (a token matching 19xx or 20xx), a version
number (text matching `\\d+\\.\\d+`), or "PEP" followed by a number. A
sentence with a modal "would", "could", "might", or "should" is a
conditional or hypothetical, a different rule. A verb inside double
quotes (an odd number of `"` characters before it in the sentence) is
quoted speech or output. A paragraph starting `Hint:` or `Done when:` is
skipped whole. Two more skips: a `[PAST]` verb whose subject is "I" or
"we" is the author's own narrative ("I began adding material"), and a
"were" in a sentence that opens with "If" or "When" is a subjunctive;
the second applies to `[PAST-SUB]` too, since a subjunctive is never
drift.

Known keeps, which the baseline holds: a narrated run whose output is
on the page ("the gate rewrote the marker"), a measurement ("the first
run took 0.3 s"), history without a year ("the design patterns movement
was an important step"), an exercise asking the reader what happened in
a run, a reported past in a quotation the `"` count missed (single or
curly quotes), and the subjunctive "were" ("if the list were empty").
The check does not read "did" plus a bare verb ("did not load") and does
not skip a "that was" plus a time word.

The shared reading rules: the paragraph reader is the one
`tools/stranded_prepositions.py` uses, so listings, headings, block
quotes, tables, and `#:` lines are skipped and inline code spans arrive
as the placeholder `CODE`. When the parser cannot start, the check says
so and exits 0.

Report-only: it prints the hits and exits 0, because the parser is a
statistical model and no gate runs it. `--fail` exits 1 when a NEW hit
is found. It runs inside `tip prose` and alone as `tip past-tense`.
The baseline file, the report, the command line, and the edit-pairs half
of `--calibrate` are `tools/parse_check.py`'s, shared with the other
parse-based checks.
Judged keeps live in `tools/data/past_tense_baseline.txt`. An entry is
`path<TAB>[LABEL] message` with whitespace normalized and no line
number, so a reflow leaves it alone and an edit to the sentence retires
it. The default run prints each NEW hit, lists a `stale` entry that
matches no hit any more, and ends with a summary (`N new, M accepted`).
`--all` prints every hit, marked NEW or accepted. `--accept` appends
every NEW hit to the baseline and drops the stale entries. A run given
paths compares against those files' entries alone, and refuses
`--accept`.

`--calibrate` compares the check with `tools/data/edit_pairs.json` (the
sentences the author rewrote): per label, the pairs where it fires on
the before text only (the hoped-for result), on both, and on the after
text only, with ids and texts. The unsplit rule gave 1 before-only, 1
both, and 1 after-only, of 72 pairs; the split gives `[PAST]` 1, 0, 0
and `[PAST-SUB]` 0, 1, 1, so the main-clause rule fires only on an
original. Each record's `previous` sentence is put
in front of the before and after text, and only hits in the edited text
count. The edit pairs hold no headings, so `[PAST-HEADING]` shows zeros
there. Then it prints the built-in examples, each marked ok or MISS.

    uv run python -m tools.past_tense           # new hits
    uv run python -m tools.past_tense --all     # every hit
    uv run python -m tools.past_tense --accept  # judged keeps
    uv run python -m tools.past_tense --calibrate
    uv run python -m tools.past_tense Chapters/31_*.md
    uv run tip past-tense CH=31
    uv run tip past-tense-accept
"""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final, NamedTuple
from tools import parse_check
from tools.config import DATA_DIR
from tools.markdown import Document
from tools.parse_check import (
    build_arg_parser,
    calibrate_edit_pairs,
    first_line,
    inside_quotes,
    key,  # noqa: F401
    parse_args,
    run,
    run_calibrate,
    sentence_text,
    skipped,
)
from tools.parsed_prose import (
    Paragraph,
    Parser,
    ParserUnavailable,
    Sentence,
    Token,
    children,
    parse,
    parsed,
    sentence_of,
)
from tools.prose import HEADING
from tools.report import Finding
from tools.stranded_prepositions import clean, display  # noqa: F401

BASELINE: Final = DATA_DIR / "past_tense_baseline.txt"
HEADER: Final = (
    "# Past-tense verbs a human read and judged keeps: a narrated run\n"
    "# whose output is on the page, a measurement, history without a\n"
    "# year, a subjunctive. An entry is not an exemption from the rule.\n"
    "# path<TAB>[LABEL] message, with whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the sentence retires it. Rewritten by `tip past-tense-accept`;\n"
    "# read the delta with `tip past-tense` before accepting.\n"
    "# See tools/past_tense.py.\n"
)
LABELS: Final = {
    "PAST": "past-tense verb of a main clause",
    "PAST-HEADING": "past-tense verb in a heading",
    "PAST-SUB": "past-tense verb of a subordinate clause (survey)",
}
SURVEY_LABELS: Final = frozenset({"PAST-SUB"})
"""Printed only under `--survey`; never baselined."""
FIRST_PERSON: Final = frozenset({"i", "we"})
OPENERS: Final = frozenset({"if", "when"})
AUX_DEPS: Final = frozenset({"aux", "auxpass"})
PARTICIPLE_TAGS: Final = frozenset({"VBN", "VBG"})
MODALS: Final = frozenset({"would", "could", "might", "should"})
YEAR: Final = re.compile(r"(?:19|20)\d\d")
VERSION: Final = re.compile(r"\d+\.\d+")
PEP: Final = re.compile(r"\bPEP\s*\d+")


class Hit(NamedTuple):
    label: str
    verb: Token
    shown: str
    """The verb, with its past auxiliary in front for form (b)."""
    sentence: Sentence


def dated(sentence: Sentence, text: str) -> bool:
    """Does the sentence hold a year, a version number, or a PEP number?"""
    if any(YEAR.fullmatch(tok.text) for tok in sentence.tokens):
        return True
    return bool(VERSION.search(text) or PEP.search(text))


def hypothetical(sentence: Sentence) -> bool:
    """Does the sentence hold a modal "would", "could", "might", "should"?"""
    return any(tok.tag == "MD" and tok.text.lower() in MODALS
               for tok in sentence.tokens)


def quoted(sentence: Sentence, text: str, verb: Token) -> bool:
    """Is the verb inside double quotes: an odd `"` count before it?"""
    return inside_quotes(text, verb.idx, sentence.start)


def past_verbs(sentence: Sentence) -> Iterator[tuple[Token, str]]:
    """(verb, shown) for each past-tense verb of one sentence."""
    for tok in sentence.tokens:
        if tok.tag == "VBD" and tok.dep not in AUX_DEPS:
            yield tok, tok.text
        elif tok.tag in PARTICIPLE_TAGS:
            past = [c for c in children(tok, sentence)
                    if c.dep in AUX_DEPS and c.tag == "VBD"]
            if past:
                yield tok, f"{past[0].text} {tok.text}"


def is_main(verb: Token, sentence: Sentence) -> bool:
    """Is the verb the root, or conjoined to it through `conj` links?"""
    seen: set[int] = set()
    while verb.dep == "conj" and verb.i not in seen:
        seen.add(verb.i)
        verb = sentence.tokens[verb.head]
    return verb.dep == "ROOT"


def first_person(verb: Token, sentence: Sentence) -> bool:
    """Is the subject "I" or "we"? A conjunct borrows its head's."""
    seen: set[int] = set()
    while verb.i not in seen:
        seen.add(verb.i)
        for child in children(verb, sentence):
            if child.dep in ("nsubj", "nsubjpass"):
                return child.text.lower() in FIRST_PERSON
        if verb.dep != "conj":
            return False
        verb = sentence.tokens[verb.head]
    return False


def subjunctive(verb: Token, sentence: Sentence) -> bool:
    """Is this "were" in a sentence that opens with "If" or "When"?"""
    if verb.text.lower() != "were":
        return False
    first = next((t for t in sentence.tokens if not t.punct), None)
    return first is not None and first.text.lower() in OPENERS


def hits(paragraph: Paragraph, label: str | None = None) -> Iterator[Hit]:
    """Each past-tense verb in one paragraph.

    `label` forces one label (the heading scan); otherwise a main-clause
    verb is `PAST` and any other is `PAST-SUB`.
    """
    if skipped(paragraph):
        return
    for sentence in paragraph.sentences:
        text = paragraph.text
        if dated(sentence, text[sentence.start:sentence.end]):
            continue
        if hypothetical(sentence):
            continue
        for verb, shown in past_verbs(sentence):
            if quoted(sentence, text, verb):
                continue
            if subjunctive(verb, sentence):
                continue
            main = is_main(verb, sentence)
            if label is None and main and first_person(verb, sentence):
                continue
            kind = label or ("PAST" if main else "PAST-SUB")
            yield Hit(kind, verb, shown, sentence)


def message(paragraph: Paragraph, hit: Hit) -> str:
    """`[LABEL] verb: sentence`, whitespace normalized."""
    return (f"[{hit.label}] {hit.shown}: "
            + sentence_text(paragraph, hit.sentence))


def heading_lines(doc: Document) -> list[tuple[int, str]]:
    """(1-based line, cleaned text) of each heading outside a fence."""
    fenced = doc.in_fence()
    found: list[tuple[int, str]] = []
    for index, line in enumerate(doc.lines):
        if fenced[index] or not HEADING.match(line):
            continue
        text = clean(line.strip().lstrip("#").strip()).strip()
        if text:
            found.append((index + 1, text))
    return found


def heading_paragraphs(docs: list[Document],
                       parser: Parser) -> list[tuple[Path, Paragraph]]:
    """Each heading parsed as its own one-line paragraph, in one call."""
    items = [(doc.path, number, text) for doc in docs
             for number, text in heading_lines(doc)]
    if not items:
        return []
    answers = parser([text for _, _, text in items])
    if len(answers) != len(items):
        raise ParserUnavailable("parser returned the wrong number of texts")
    return [
        (path, Paragraph(path, text, [number] * len(text),
                         tuple(sentence_of(s) for s in sentences)))
        for (path, number, text), sentences in zip(items, answers,
                                                   strict=True)
    ]


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per past-tense verb, in sentences and in headings."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            for hit in hits(paragraph):
                yield Finding(doc.path, first_line(paragraph, hit.sentence),
                              message(paragraph, hit))
    for path, paragraph in heading_paragraphs(docs, parser):
        for hit in hits(paragraph, "PAST-HEADING"):
            yield Finding(path, first_line(paragraph, hit.sentence),
                          message(paragraph, hit))


def label_of(text: str) -> str:
    """The label in a message's leading `[LABEL]`."""
    return text[1:text.index("]")]


def load_baseline(path: Path | None = None) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    return parse_check.load_baseline(path or BASELINE)


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    parse_check.write_baseline(entries, path or BASELINE, HEADER)


EXAMPLES: Final[tuple[tuple[str, str, str | None], ...]] = (
    ("One design served three jobs in this chapter.", "PAST", "served"),
    ("One design serves three jobs in this chapter.", "PAST", None),
    ("In every case the observer was a callable.", "PAST", "was"),
    ("Python 3.12 added the type statement.", "PAST", None),
    ("The 1994 book carried it into the mainstream.", "PAST", None),
    ("If the list were empty, the loop would stop.", "PAST", None),
    ("If the list were empty, it stops.", "PAST", None),
    ("The marker was rewritten by the gate.", "PAST", "was rewritten"),
    ("The gate has rewritten the marker.", "PAST", None),
    ("I began adding material.", "PAST", None),
    ("The function the caller passed runs.", "PAST-SUB", "passed"),
    ("What Stayed Constant", "PAST-HEADING", "Stayed"),
    ("What Stays Constant", "PAST-HEADING", None),
)
"""Calibration texts: (text, label, the verb that must fire or None)."""


def labels_of(paras: list[Paragraph], skip: int = 0) -> set[str]:
    """The labels earned by sentences after the first `skip`.

    Each sentence is judged as a paragraph of its own, so the leading
    `previous` sentence of an edit pair never counts.
    """
    found: set[str] = set()
    for p in paras:
        for seen, sentence in enumerate(p.sentences):
            if seen >= skip:
                one = Paragraph(p.path, p.text, p.lines, (sentence,))
                found.update(h.label for h in hits(one))
    return found


def calibrate_examples(parser: Parser) -> None:
    """The built-in examples, each marked ok or MISS."""
    print("== built-in examples ==")
    body = [(n, ex) for n, ex in enumerate(EXAMPLES)
            if ex[1] != "PAST-HEADING"]
    head = [(n, ex) for n, ex in enumerate(EXAMPLES)
            if ex[1] == "PAST-HEADING"]
    got: dict[int, list[Hit]] = {}
    docs = [Document.from_text(ex[0], Path(f"calibrate/ex{n}.md"))
            for n, ex in body]
    for (n, _), paras in zip(body, parsed(docs, parser, use_cache=False),
                             strict=True):
        got[n] = [h for p in paras for h in hits(p)]
    if head:
        hdocs = [Document.from_text(f"# {ex[0]}", Path(f"calibrate/ex{n}.md"))
                 for n, ex in head]
        found = heading_paragraphs(hdocs, parser)
        for (n, _), (_, para) in zip(head, found, strict=True):
            got[n] = list(hits(para, "PAST-HEADING"))
    for n, (text, label, want) in enumerate(EXAMPLES):
        shown = [f"[{h.label}] {h.shown}" for h in got[n]]
        if want is None:
            good = not shown
        else:
            good = any(h.label == label and h.shown == want
                       for h in got[n])
        print(f"{'ok  ' if good else 'MISS'} [{label}] "
              f"expect {want or 'no hit'}: {text}")
        print(f"     got {', '.join(shown) if shown else 'no hit'}")


def calibrate(parser: Parser = parse) -> None:
    """Edit pairs, then the built-in examples."""
    calibrate_edit_pairs(parser, LABELS, labels_of, previous=True)
    calibrate_examples(parser)


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = build_arg_parser(
        __doc__, fail_help="exit 1 when any NEW past-tense verb is found",
        survey_help="also print the subordinate-clause pasts "
                    "(PAST-SUB), never baselined",
        calibrate_help="compare with tools/data/edit_pairs.json and "
                       "run the built-in examples")
    args = parse_args(ap, argv)
    if args.calibrate:
        return run_calibrate("past_tense", calibrate, parser)
    return run("past_tense", args, lambda docs: find(docs, parser),
               baseline=BASELINE, header=HEADER, survey_last=True,
               is_survey=lambda message: label_of(message) in SURVEY_LABELS)


if __name__ == "__main__":
    raise SystemExit(main())
