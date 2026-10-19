#!/usr/bin/env python
"""Report sentences with an imperative-plus-consequence, a split-worthy "and", or a colon-led clause.

Three sentence shapes from the author's style rules, found with the
dependency parse that `tools/parsed_prose.py` caches under
`build/parses/` (spaCy, run in a throwaway Python 3.12 environment; see
that module). Each hit carries its rule label at the start of the
printed sentence.

`[IMP]`, imperative plus consequence: the sentence root is a bare
imperative verb (tag `VB`, no subject, not an infinitive after "to")
and a verb coordinated with it through "and" has a subject of its own.
"Remove CODE and the pattern fails" commands the reader and then
reports what happens; the repair is the condition, "If you remove
CODE, the pattern fails". The second clause's subject may be anything,
"you" included, but it must be a plain `nsubj` or `nsubjpass`. Two
imperatives ("Try the operation and handle the exception") and an
exercise ("Run CODE and read the error it reports") are not hits,
since the second verb has no subject. Two exclusions keep exercise
sentences out: a coordinated verb with a wh-word child (tag `WP`,
`WDT`, or `WRB`) or a `mark` child ("that", "whether") is a wh-clause
or that-clause, not a consequence ("Explain both failures, and why an
intermediate kick avoids them"); and the `csubj` fallback below fires
only when the "and" joins the imperative to the finite root.

`[AND]`, an "and" that joins two clauses with different subjects: the
root is a finite verb with a subject, a verb coordinated with it
through "and" is finite and has its own subject, that second subject
is not a bare pronoun (it, they, he, she, this, that, which, who,
these, those), and its text differs from the first. The test is
substitution: if "but", "so", "while", or "whereas" fits where the
"and" sits, the "and" is not additive, and the sentence splits. Only
the root clause is examined, and a sentence is reported once.

`[COLON]`, a colon followed by an independent clause: after a ":" in
the sentence, a subject whose head is a finite verb that also follows
the colon. A colon is a pointer to what the lead-in announced (a list,
an example, a restatement), so a clause after it is often a reason or a
claim of its own, and the colon stands in for "because" or a period.
`[COLON+AND]` is the stronger label for the same shape when that
clause's verb is coordinated through "and" with a second verb that has
its own subject: a colon delivers one thing, and the first claim takes
a period. A sentence earns one of the two labels. A spaCy sentence
that ends on a colon is merged with the sentence after it in the same
paragraph before the rule applies, since the parser splits there. The
style rules keep a colon after a count or a demonstrative that names
what follows ("three parts:", "this shape:"), so a colon is skipped
when a non-punctuation word before it is a number (pos `NUM`) or one of
`COUNT_WORDS` ("both", "two", "several", "pair"), or when the last such
word is one of `POINTER_WORDS` ("this", "these", "following", "here").
A bare noun lead-in ("The prediction:") stays a hit.

Two rules run by default, `RULES`: `[IMP]` and `[COLON+AND]`, judged
against a baseline. Two are survey rules, `SURVEY_RULES`: `[AND]` and
plain `[COLON]`. The calibration shows why. `[AND]` fired on 7 before
only, 1 both, and 6 after only of the 72 rewritten pairs, so the
author's own rewrites carry the shape: it is a judgment made per
sentence in an editing pass, not a fault, and the whole book yields
hundreds of hits. `[COLON]` is the same, since most colons restate in
other words. `[IMP]` fired on 2 before only, 0 both, and 1 after only,
and the after-only one was an exercise sentence the parser misread.
Survey rules print only under `--survey`, each line marked `survey`
instead of NEW or accepted, after the default rules' lines. They never
enter the baseline and never count toward `N new`. The intended use is
`tip sentence-shapes CH=31 ARGS=--survey` at the start of a chapter
pass.

The shared reading rules: a paragraph whose text starts with `Hint:` or
`Done when:` (the Solutions labels) is skipped; the paragraph reader is
the one `tools/stranded_prepositions.py` uses, so listings, headings,
block quotes, tables, and `#:` lines are skipped and inline code spans
arrive as the placeholder `CODE`. When the parser cannot start, the
check says so and exits 0.

Report-only: it prints the hits and exits 0, because the parser is a
statistical model and no gate runs it. `--fail` exits 1 when a NEW hit
is found. It runs inside `tip prose` and alone as `tip sentence-shapes`.

A hit prints as `path:line: [RULE] sentence`, the line holding the
sentence's first character. Every hit is read once by a human, and the
ones judged keeps live in `tools/data/sentence_shapes_baseline.txt`, so
a run prints only what is new. An entry is `path<TAB>[RULE] sentence`
with whitespace normalized and no line number, so a reflow or an edit
elsewhere in the file leaves the entry alone, while an edit to the
sentence retires it and the rewritten sentence reports as NEW. An
entry is a judged keep, not an exemption. The default run prints each
NEW hit and a summary (`N new, M accepted`), and lists a `stale` entry
that matches no hit any more. `--all` prints every hit, marked NEW or
accepted. `--accept` appends every NEW hit to the baseline and drops
the stale entries. A run given paths compares against those files'
entries alone, and refuses `--accept`.

`--calibrate` checks all four rules against `tools/data/edit_pairs.json`
(the sentences the author rewrote, 72 records of `before`, `after`, and
`fault`): each before and after text is parsed as a one-paragraph
document, and each rule reports the pairs where it fires on the before
text only (the hoped-for result), on the after text only, and on both,
with the ids and texts. The built-in `CALIBRATION_EXAMPLES` (the style
rules' own examples and their repairs) print in the same run, marked
ok or MISS. Calibration writes no cache.

Known false negatives, from the 2026-10-18 calibration on the small
English model. Of the rule examples, "Remove CODE and the pattern
fails" parses as an imperative root. "Forget the new argument at a call
and CODE reports a CODE" does not: the parser makes "Forget" the
clausal subject (`csubj`) of "reports", so `clausal_imperative()`
reads that one misparse. "CODE returns a new function, and the old one
stays registered" is missed by `[AND]`, because the parser tags "stays"
as a plural noun. Sentence-initial imperatives that the parser tags as
nouns ("Print", "Run") are missed by `[IMP]`; there is no fallback
for them. Known false-positive shapes, all left in the report for a
human: an exercise instruction with a long second clause ("Write a
test in which the first listener fails and the second still records
its notification"), an additive "and" whose clauses name different
subjects but belong together, and a colon that restates in other words
or introduces a list whose items hold relative clauses.

    uv run python -m tools.sentence_shapes           # new hits
    uv run python -m tools.sentence_shapes --all     # every hit
    uv run python -m tools.sentence_shapes --accept  # judged keeps
    uv run python -m tools.sentence_shapes --survey  # + AND, COLON
    uv run python -m tools.sentence_shapes --calibrate
    uv run python -m tools.sentence_shapes Chapters/31_*.md
    uv run tip sentence-shapes CH=31
    uv run tip sentence-shapes-accept
"""

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Final
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.parsed_prose import (
    Paragraph,
    Parser,
    ParserUnavailable,
    Sentence,
    Token,
    children,
    conj_verbs,
    coordinator,
    finite,
    parse,
    parsed,
    subject_of,
    subtree,
)
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.stranded_prepositions import clean, display

BASELINE: Final = DATA_DIR / "sentence_shapes_baseline.txt"
EDIT_PAIRS: Final = DATA_DIR / "edit_pairs.json"
HEADER: Final = (
    "# Sentence-shape hits a human read and judged keeps: a colon\n"
    "# that restates in other words, an \"and\" that is additive, an\n"
    "# imperative the parser misread. An entry is not an exemption\n"
    "# from the rule.\n"
    "# path<TAB>[RULE] sentence, with whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the sentence retires it. Rewritten by\n"
    "# `tip sentence-shapes-accept`; read the delta with\n"
    "# `tip sentence-shapes` before accepting.\n"
    "# See tools/sentence_shapes.py.\n"
)
SKIPPED_LABELS: Final = ("Hint:", "Done when:")
BARE_PRONOUNS: Final = frozenset(
    "it they he she this that which who these those".split())
SUBJECT_DEPS: Final = ("nsubj", "nsubjpass")
CLOSERS: Final = frozenset("\"'”’)]*_")
RULES: Final = {
    "IMP": "imperative plus consequence",
    "COLON+AND": "colon, then a clause with an and-joined clause",
}
"""The default rules: judged against the baseline."""
SURVEY_RULES: Final = {
    "AND": "an and joining clauses with different subjects",
    "COLON": "colon, then an independent clause",
}
"""Printed only under `--survey`; never baselined."""
ALL_RULES: Final = tuple(RULES) + tuple(SURVEY_RULES)
COUNT_WORDS: Final = frozenset(
    "both several twice two three four five six seven eight nine ten "
    "pair couple".split())
"""Words that make a colon lead-in a count ("three parts:")."""
POINTER_WORDS: Final = frozenset(
    "this these that those following so here".split())
"""Last words that make a colon lead-in a demonstrative ("this shape:")."""
WH_TAGS: Final = frozenset({"WP", "WDT", "WRB"})

CALIBRATION_EXAMPLES: Final[tuple[tuple[str, str, bool], ...]] = (
    # (rule, text, should it fire)
    ("IMP", "Remove `frozen=True` and the pattern fails.", True),
    ("IMP", "If you remove `frozen=True`, the pattern fails.", False),
    ("IMP", "Forget the new argument at a call and `ty` reports "
            "a `missing-argument`.", True),
    ("IMP", "If you forget the new argument at a call, `ty` reports "
            "a `missing-argument`.", False),
    ("IMP", "Run `ty` and read the error it reports.", False),
    ("IMP", "Try the operation and handle the exception.", False),
    ("AND", "`wraps()` returns a new function, and the old one "
            "stays registered.", True),
    ("AND", "`wraps()` returns a new function. The old one stays "
            "registered.", False),
    ("COLON+AND",
     "Python supplies `self` only when the lookup finds the function "
     "on the class: a function stored there is a descriptor, and "
     "reading it through an instance binds that instance.", True),
    ("COLON+AND",
     "Python supplies `self` only when the lookup finds the function "
     "on the class. A function stored there is a descriptor, and "
     "reading it through an instance binds that instance.", False),
)
"""The style rules' own examples: (rule, text, should it fire)."""


def root_of(sentence: Sentence) -> Token | None:
    """The token that is its own head, None for an empty sentence."""
    for tok in sentence.tokens:
        if tok.head == tok.i:
            return tok
    return None


def phrase(tok: Token, sentence: Sentence) -> str:
    """The lowercase text of a token and everything below it."""
    keep = subtree(tok, sentence)
    return " ".join(t.text for t in sentence.tokens if t.i in keep).lower()


def absorbed_subject(head: Token, sentence: Sentence) -> bool:
    """Is the subject of `head` hanging off an earlier noun as a conj?

    "Forget X at a call and CODE reports Y": the parser coordinates
    "call" and "CODE", so "reports" has no subject and the "and" is a
    child of "call".
    """
    return own_subject(head, sentence) is None and any(
        t.dep == "conj" and t.pos in ("NOUN", "PROPN", "PRON")
        and t.i < head.i and sentence.tokens[t.head].pos in (
            "NOUN", "PROPN", "PRON")
        for t in sentence.tokens)


def clausal_imperative(sentence: Sentence) -> bool:
    """The parser's misreading of "Forget X and CODE reports Y".

    The sentence-initial bare verb becomes the clausal subject (`csubj`)
    of the verb after the "and", which is then the root. The shape is a
    hit when that head is finite, the bare verb has no coordinated verb
    of its own (else the "and" joins two imperatives), and an "and"
    lies between them that joins the imperative to the root: it hangs
    off the bare verb or the root, or off a noun whose coordinated
    partner is the root's absorbed subject. An "and" inside a relative
    clause ("in which the first responder fails and the second ...")
    hangs off a verb and is no hit.
    """
    tokens = sentence.tokens
    first = tokens[0] if tokens else None
    if first is None or first.tag != "VB" or first.dep != "csubj":
        return False
    head = tokens[first.head]
    if not finite(head, sentence) or any(
            c.dep == "conj" for c in children(first, sentence)):
        return False
    ands = [t for t in tokens if t.dep == "cc" and t.text.lower() == "and"
            and first.i < t.i < head.i]
    return any(t.head in (first.i, head.i) for t in ands) or (
        bool(ands) and absorbed_subject(head, sentence))


def own_subject(verb: Token, sentence: Sentence) -> Token | None:
    """The verb's `nsubj` or `nsubjpass` child, None otherwise."""
    for child in children(verb, sentence):
        if child.dep in SUBJECT_DEPS:
            return child
    return None


def consequence_clause(verb: Token, sentence: Sentence) -> bool:
    """A plain clause with its own subject, not a wh- or that-clause."""
    if own_subject(verb, sentence) is None:
        return False
    return not any(c.tag in WH_TAGS or c.dep == "mark"
                   for c in children(verb, sentence))


def imperative_consequence(sentence: Sentence) -> bool:
    """A bare imperative root with an "and" verb that has a subject."""
    root = root_of(sentence)
    if root is None or root.pos not in ("VERB", "AUX") or root.tag != "VB":
        return clausal_imperative(sentence)
    if subject_of(root, sentence) is not None:
        return False
    if root.i > 0 and sentence.tokens[root.i - 1].text.lower() == "to":
        return False
    return any(
        consequence_clause(c, sentence)
        and coordinator(c, sentence) == "and"
        for c in conj_verbs(root, sentence)
    )


def and_joins_subjects(sentence: Sentence) -> bool:
    """A finite root and a finite "and" verb with different subjects."""
    root = root_of(sentence)
    if root is None or not finite(root, sentence):
        return False
    first = subject_of(root, sentence)
    if first is None or first.dep not in SUBJECT_DEPS:
        return False
    for conj in conj_verbs(root, sentence):
        second = subject_of(conj, sentence)
        if (second is None or not finite(conj, sentence)
                or coordinator(conj, sentence) != "and"):
            continue
        said = phrase(second, sentence)
        if said not in BARE_PRONOUNS and said != phrase(first, sentence):
            return True
    return False


def ends_on_colon(sentence: Sentence) -> bool:
    """Does the sentence's last word-like token equal ':'?"""
    tail = [t for t in sentence.tokens
            if t.pos != "SPACE" and t.text not in CLOSERS]
    return bool(tail) and tail[-1].text == ":"


def merge(first: Sentence, second: Sentence) -> Sentence:
    """Two sentences as one, the second's indexes moved past the first."""
    shift = len(first.tokens)
    moved = tuple(t._replace(i=t.i + shift, head=t.head + shift)
                  for t in second.tokens)
    return Sentence(first.tokens + moved, first.start, second.end)


def colon_units(paragraph: Paragraph) -> list[Sentence]:
    """The paragraph's sentences, each colon-ended one joined to the next."""
    units: list[Sentence] = []
    pending: Sentence | None = None
    for sentence in paragraph.sentences:
        if pending is not None:
            sentence = merge(pending, sentence)
            pending = None
        if ends_on_colon(sentence):
            pending = sentence
        else:
            units.append(sentence)
    if pending is not None:
        units.append(pending)
    return units


def counted_lead_in(sentence: Sentence, colon: Token) -> bool:
    """Does a count or demonstrative before this colon name what follows?"""
    words = [t for t in sentence.tokens[:colon.i] if not t.punct]
    if not words:
        return False
    return (any(t.pos == "NUM" or t.text.lower() in COUNT_WORDS
                for t in words)
            or words[-1].text.lower() in POINTER_WORDS)


def colon_clause(sentence: Sentence) -> str | None:
    """COLON, COLON+AND, or None for a clause after a colon."""
    found: str | None = None
    tokens = sentence.tokens
    for colon in tokens:
        if colon.text != ":" or counted_lead_in(sentence, colon):
            continue
        for subject in tokens:
            if subject.i <= colon.i or subject.dep not in (
                    "nsubj", "nsubjpass", "expl"):
                continue
            verb = tokens[subject.head]
            if verb.i <= colon.i or not finite(verb, sentence):
                continue
            found = found or "COLON"
            if any(subject_of(c, sentence) is not None
                   and coordinator(c, sentence) == "and"
                   for c in conj_verbs(verb, sentence)):
                return "COLON+AND"
    return found


def skipped(paragraph: Paragraph) -> bool:
    """Is this a Solutions label paragraph (Hint: or Done when:)?"""
    return paragraph.text.startswith(SKIPPED_LABELS)


def shapes(paragraph: Paragraph) -> Iterator[tuple[str, Sentence]]:
    """(rule, sentence) for each hit in one paragraph."""
    if skipped(paragraph):
        return
    for sentence in paragraph.sentences:
        if imperative_consequence(sentence):
            yield "IMP", sentence
        if and_joins_subjects(sentence):
            yield "AND", sentence
    for sentence in colon_units(paragraph):
        label = colon_clause(sentence)
        if label:
            yield label, sentence


def sentence_text(paragraph: Paragraph, sentence: Sentence) -> str:
    """The sentence's text from the paragraph, whitespace normalized."""
    return " ".join(paragraph.text[sentence.start:sentence.end].split())


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per rule per sentence, the message led by `[RULE]`."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            lines = paragraph.lines
            for rule, sentence in shapes(paragraph):
                line = lines[min(sentence.start, len(lines) - 1)]
                yield Finding(doc.path, line, f"[{rule}] "
                              + sentence_text(paragraph, sentence))


def rule_of(message: str) -> str:
    """The label in a message's leading `[RULE]`."""
    return message[1:message.index("]")]


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


def labels_of(paras: list[Paragraph]) -> set[str]:
    """The rule labels any paragraph of a text earns."""
    return {rule for p in paras for rule, _ in shapes(p)}


def calibrate(parser: Parser = parse) -> None:
    """Run the rules over the recorded edit pairs and the examples."""
    pairs: dict[str, dict[str, str]] = json.loads(
        EDIT_PAIRS.read_text(encoding="utf-8"))
    docs: list[Document] = []
    for ident, record in pairs.items():
        for side in ("before", "after"):
            docs.append(Document.from_text(
                record[side], Path(f"calibrate/{ident}.{side}.md")))
    for number, (_, text, _) in enumerate(CALIBRATION_EXAMPLES):
        docs.append(Document.from_text(
            clean(text), Path(f"calibrate/example{number}.md")))
    results = parsed(docs, parser, use_cache=False)
    sides = {doc.path.name: labels_of(paras)
             for doc, paras in zip(docs, results, strict=True)}
    for rule in ALL_RULES:
        before_only: list[str] = []
        after_only: list[str] = []
        both: list[str] = []
        for ident in pairs:
            b = rule in sides[f"{ident}.before.md"]
            a = rule in sides[f"{ident}.after.md"]
            if b and a:
                both.append(ident)
            elif b:
                before_only.append(ident)
            elif a:
                after_only.append(ident)
        print(f"== {rule} ==")
        for title, ids in (("before only", before_only),
                           ("both", both), ("after only", after_only)):
            for ident in ids:
                print(f"{title}: {ident}")
                print(f"  before: {pairs[ident]['before']}")
                print(f"  after:  {pairs[ident]['after']}")
        print(f"{rule}: before-only {len(before_only)}, "
              f"both {len(both)}, after-only {len(after_only)}, "
              f"of {len(pairs)} pairs\n")
    print("== built-in examples ==")
    for number, (rule, text, should) in enumerate(CALIBRATION_EXAMPLES):
        fired = rule in sides[f"example{number}.md"]
        verdict = "ok  " if fired == should else "MISS"
        want = "fires" if should else "quiet"
        print(f"{verdict} [{rule}] {want}: {text}")


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW sentence is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    ap.add_argument("--survey", action="store_true",
                    help="also print the survey rules (AND, COLON), "
                         "never baselined or counted")
    ap.add_argument("--calibrate", action="store_true",
                    help="run the rules over tools/data/edit_pairs.json "
                         "and the built-in examples")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    if args.calibrate:
        try:
            calibrate(parser)
        except ParserUnavailable as exc:
            print(f"sentence_shapes: parser unavailable ({exc}); "
                  f"nothing checked", file=sys.stderr)
        return 0
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    try:
        findings = list(find([Document.parse(p) for p in paths], parser))
    except ParserUnavailable as exc:
        print(f"sentence_shapes: parser unavailable ({exc}); "
              f"nothing checked", file=sys.stderr)
        return 0
    everything = sorted(
        {(display(f.path), f.line, f.message) for f in findings})
    survey = [h for h in everything if rule_of(h[2]) in SURVEY_RULES]
    found = [h for h in everything if rule_of(h[2]) in RULES]
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
    if args.survey:
        for shown, line, text in survey:
            print(f"survey   {shown}:{line}: {text}")
        print(f"{len(survey)} survey")
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and new else 0


if __name__ == "__main__":
    raise SystemExit(main())
