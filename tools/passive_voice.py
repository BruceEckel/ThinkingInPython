#!/usr/bin/env python
"""Report each passive clause in the prose.

The author's style guide asks for the active register: a real actor in
the subject, the action in the verb. Vale's write-good `Passive` rule
(run by `tip prose`) matches by word pattern, so it flags an adjective
after "be" ("is unchanged"). This check reads the dependency parse that
`tools/parsed_prose.py` caches under `build/parses/` (spaCy, run in a
throwaway Python 3.12 environment; see that module) and is meant to
replace or confirm Vale's list. `--calibrate` compares the two.

A passive clause is a verb with a child of dep `auxpass` (the be-passive
or get-passive auxiliary) and a child of dep `nsubjpass` or `csubjpass`.
A relative clause counts too: in "a value that is written once",
`written` has the auxiliary `is` and the subject `that`. The small
model often reads a get-passive ("The file got overwritten") with the
participle as an `acomp` of "got"; a form of "get" with a subject and a
`VBN` `acomp` or `xcomp` counts as a passive too. A bare
participle with no auxiliary ("a value stored in the class", dep `acl`
or `amod`) and an adjective after "be" (`acomp`, "is unchanged", "is
available") are not hits, since neither has an `auxpass`.

Two labels, by whether the actor is written out. `[PASSIVE]`: no actor.
`[PASSIVE+BY]`: the verb has a child with dep `agent`, or a `prep` child
"by" with an object, so the "by" phrase names an actor that the sentence
could make its subject. That one is the form most often worth turning
around. A sentence with two passive clauses reports both. A hit prints
as `path:line: [LABEL] <auxiliary> <participle>: <sentence>`, the line
holding the sentence's first character.

Known keeps, which the baseline holds: a passive whose actor is unknown
or irrelevant ("Python was released in 1991"), a passive in quoted
output or a quoted diagnostic that `clean()` did not mask, a naming
convention ("is called X", "is said to"), and a passive inside a
code-like phrase.

The shared reading rules: a paragraph whose text starts with `Hint:` or
`Done when:` (the Solutions labels) is skipped; the paragraph reader is
the one `tools/stranded_prepositions.py` uses, so listings, headings,
block quotes, tables, and `#:` lines are skipped and inline code spans
arrive as the placeholder `CODE`. When the parser cannot start, the
check says so and exits 0.

Report-only: it prints the hits and exits 0, because the parser is a
statistical model and no gate runs it. `--fail` exits 1 when a NEW hit
is found. It runs inside `tip prose` and alone as `tip passive`.
Judged keeps live in `tools/data/passive_voice_baseline.txt`. An entry
is `path<TAB>[LABEL] message` with whitespace normalized and no line
number, so a reflow leaves it alone and an edit to the sentence retires
it. The default run prints each NEW hit, lists a `stale` entry that
matches no hit any more, and ends with a summary (`N new, M accepted`).
`--all` prints every hit, marked NEW or accepted. `--accept` appends
every NEW hit to the baseline and drops the stale entries. A run given
paths compares against those files' entries alone, and `--accept`
with paths adds and drops entries for those files and keeps
every other file's entries. The baseline file, the report, the command line, and the
edit-pairs and Vale comparisons are `tools/parse_check.py`'s, shared
with the other parse-based checks.

`--calibrate` prints two comparisons. First, against
`tools/data/edit_pairs.json` (the sentences the author rewrote): per
label, the pairs where the check fires on the before text only (the
hoped-for result), on both, and on the after text only, with ids and
texts. Second, against Vale: it runs `vale --output=JSON Chapters
Solutions`, keeps the `write-good.Passive` alerts, and matches them to
this check's hits by line (an alert matches a hit when its line falls
within the hit sentence's lines). It prints CONFIRMED (both), VALE-ONLY
(Vale's match text and the sentence), and PARSE-ONLY, then a summary.
When `vale` is missing, the second comparison prints one line and stops.

    uv run python -m tools.passive_voice           # new hits
    uv run python -m tools.passive_voice --all     # every hit
    uv run python -m tools.passive_voice --accept  # judged keeps
    uv run python -m tools.passive_voice --calibrate
    uv run python -m tools.passive_voice Chapters/31_*.md
    uv run tip passive CH=31
    uv run tip passive-accept
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Final, NamedTuple
from tools import parse_check
from tools.config import DATA_DIR
from tools.markdown import Document
from tools.parse_check import (
    build_arg_parser,
    calibrate_edit_pairs,
    calibrate_vale,
    first_line,
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
    Sentence,
    Token,
    children,
    parse,
    parsed,
)
from tools.report import Finding
from tools.stranded_prepositions import display  # noqa: F401

BASELINE: Final = DATA_DIR / "passive_voice_baseline.txt"
HEADER: Final = (
    "# Passive clauses a human read and judged keeps: an actor that\n"
    "# is unknown or irrelevant, a quoted diagnostic, a naming\n"
    "# convention. An entry is not an exemption from the rule.\n"
    "# path<TAB>[LABEL] message, with whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the sentence retires it. Rewritten by `tip passive-accept`;\n"
    "# read the delta with `tip passive` before accepting.\n"
    "# See tools/passive_voice.py.\n"
)
LABELS: Final = {
    "PASSIVE": "passive clause with no actor written out",
    "PASSIVE+BY": "passive clause with a by-phrase actor",
}
SUBJECT_DEPS: Final = ("nsubjpass", "csubjpass")
VALE_CHECK: Final = "write-good.Passive"


class Hit(NamedTuple):
    label: str
    auxiliary: Token
    verb: Token
    sentence: Sentence


def has_agent(verb: Token, sentence: Sentence) -> bool:
    """Is the actor written out: an `agent` child or a "by" with an object."""
    for child in children(verb, sentence):
        if child.dep == "agent":
            return True
        if child.dep == "prep" and child.text.lower() == "by" and any(
                g.dep == "pobj" for g in children(child, sentence)):
            return True
    return False


def get_passive(verb: Token, sentence: Sentence) -> Token | None:
    """The participle of a get-passive the parser read as `acomp`.

    "The file got overwritten": the small model makes "got" the head,
    with the participle (tag `VBN`) as its `acomp` or `xcomp`, instead
    of the `auxpass` reading. The head must be a form of "get" with a
    subject of its own.
    """
    if verb.lemma != "get":
        return None
    kids = children(verb, sentence)
    if not any(c.dep in ("nsubj", "nsubjpass") for c in kids):
        return None
    for child in kids:
        if child.dep in ("acomp", "xcomp") and child.tag == "VBN":
            return child
    return None


def passives(sentence: Sentence) -> Iterator[Hit]:
    """Each passive clause of one sentence."""
    for verb in sentence.tokens:
        kids = children(verb, sentence)
        aux = [c for c in kids if c.dep == "auxpass"]
        if aux and any(c.dep in SUBJECT_DEPS for c in kids):
            label = "PASSIVE+BY" if has_agent(verb, sentence) else "PASSIVE"
            yield Hit(label, aux[-1], verb, sentence)
            continue
        participle = get_passive(verb, sentence)
        if participle is not None:
            label = ("PASSIVE+BY" if has_agent(participle, sentence)
                     or has_agent(verb, sentence) else "PASSIVE")
            yield Hit(label, verb, participle, sentence)


def hits(paragraph: Paragraph) -> Iterator[Hit]:
    """Each passive clause in one paragraph."""
    if skipped(paragraph):
        return
    for sentence in paragraph.sentences:
        yield from passives(sentence)


def message(paragraph: Paragraph, hit: Hit) -> str:
    """`[LABEL] aux verb: sentence`, whitespace normalized."""
    return (f"[{hit.label}] {hit.auxiliary.text} {hit.verb.text}: "
            + sentence_text(paragraph, hit.sentence))


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per passive clause."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            for hit in hits(paragraph):
                yield Finding(doc.path, first_line(paragraph, hit.sentence),
                              message(paragraph, hit))


def label_of(text: str) -> str:
    """The label in a message's leading `[LABEL]`."""
    return text[1:text.index("]")]


def labels_of(paras: list[Paragraph], skip: int = 0) -> set[str]:
    """The labels any paragraph of a text earns."""
    return {h.label for p in paras for h in hits(p)}


def load_baseline(path: Path | None = None) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    return parse_check.load_baseline(path or BASELINE)


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    parse_check.write_baseline(entries, path or BASELINE, HEADER)


def vale_hits(paragraph: Paragraph) -> Iterator[tuple[Sentence, str]]:
    """(sentence, message) for each hit, for the Vale comparison."""
    for hit in hits(paragraph):
        yield hit.sentence, message(paragraph, hit)


def calibrate(parser: Parser = parse) -> None:
    """Both comparisons: edit pairs, then Vale."""
    calibrate_edit_pairs(parser, LABELS, labels_of,
                         previous=False, meanings=False)
    calibrate_vale(parser, VALE_CHECK, vale_hits)


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = build_arg_parser(
        __doc__, fail_help="exit 1 when any NEW passive is found",
        calibrate_help="compare with tools/data/edit_pairs.json and "
                       "with Vale's write-good.Passive")
    args = parse_args(ap, argv)
    if args.calibrate:
        return run_calibrate("passive_voice", calibrate, parser)
    return run("passive_voice", args, lambda docs: find(docs, parser),
               baseline=BASELINE, header=HEADER)


if __name__ == "__main__":
    raise SystemExit(main())
