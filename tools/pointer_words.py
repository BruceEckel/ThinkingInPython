#!/usr/bin/env python
"""Report each sentence that opens with a pronoun pointer.

The author's style rule: name the noun when a generic word could point
two ways. A pronoun is a pointer, and it is fine when the reader can
name its target from its own sentence and the paragraph's topic. When a
reader could pick a different target, or must reread the previous
sentence to find one, the sentence writes the noun. The `antecedents`
skill (`.claude/skills/antecedents/SKILL.md`) is the pass that reads
for this; this check is its mechanical prefilter. It lists the
sentences that open with a pronoun and says what the pronoun could
point at, so the pass starts from a short list.

It reads the dependency parse that `tools/parsed_prose.py` caches under
`build/parses/` (spaCy, run in a throwaway Python 3.12 environment; see
that module). A sentence opens with a pointer when its first non-punct
token, or the first token after a sentence-initial adverb or
coordinating conjunction (dep `advmod` or `cc`, or "then", "so", "but",
"and", "here", "now", "also", "still"), is one of "this", "that",
"these", "those", "it", or "they", used as a pronoun: its dep is
`nsubj` or `nsubjpass`. "This technique" has "This" as a determiner and
is not a hit, and the cleft "It is X that" has an `expl` and is left
for a later rule.

Two labels. `[THIS]`: the opening pronoun is a demonstrative. It is
always a hit, since a sentence-opening demonstrative pronoun gets its
noun. `[IT]`: the opening pronoun is "it" or "they". It is a hit when
the previous sentence of the same paragraph holds two or more candidate
antecedents whose number matches (singular for "it", plural for
"they"), or when the pronoun opens the paragraph, so that its
antecedent sits in the paragraph before.

A candidate antecedent is a token of pos `NOUN` or `PROPN` whose dep is
`nsubj`, `nsubjpass`, `dobj`, `attr`, `pobj`, `appos`, or `conj` (a
noun coordinated with one of those). Singular means a morph with
`Number=Sing`, the placeholder `CODE`, or a `PROPN`; plural means
`Number=Plur`. Distinct lowercase texts count once.

A hit prints as `path:line: [THIS] This: <sentence>` or `path:line:
[IT] it -> proxy, level: <sentence>`; a paragraph-opening "it" prints
`it -> (opens paragraph)`. The line holds the sentence's first
character.

The shared reading rules: a paragraph whose text starts with `Hint:` or
`Done when:` (the Solutions labels) is skipped; the paragraph reader is
the one `tools/stranded_prepositions.py` uses, so listings, headings,
block quotes, tables, and `#:` lines are skipped and inline code spans
arrive as the placeholder `CODE`. When the parser cannot start, the
check says so and exits 0.

A survey rule, with no baseline. The calibration against
`tools/data/edit_pairs.json` (72 pairs of the author's rewrites, each
with its previous sentence) shows the check does not separate his
originals from his rewrites: `[THIS]` fires on 1 pair before only, 0 on
both, and 2 after only; `[IT]` 1, 0, and 1. One of the after-only pairs
is the author writing "This governs" himself. Every hit is therefore a
judgment the antecedents pass makes, and nothing is accepted or
remembered. The check prints every hit and exits 0 (`--fail` exits 1
when there is any hit, for scripting). It is not part of `tip prose`.

The intended use is `tip pointers CH=NN` at the start of an
antecedents pass. Read each line as a mechanical candidate, with the
candidate list as the reader's aid, and not as a fault by itself: a
pronoun whose target the sentence and the paragraph's topic make clear
stays.

A line reads `survey   path:line: message`, and the run ends with `N
pointer sentences (T [THIS], U [IT])`. A run given paths reads only
those files.

`--calibrate` prints, against `tools/data/edit_pairs.json`, per label
the pairs where the check fires on the before text only, on both, and
on the after text only, with ids and texts. Each record's `previous`
sentence is put in front of the before and after text, so the
previous-sentence test has its context, and only hits in the edited
text count. Then it prints the built-in examples with the result each
should give.

    uv run python -m tools.pointer_words           # every hit
    uv run python -m tools.pointer_words --calibrate
    uv run python -m tools.pointer_words Chapters/31_*.md
    uv run tip pointers CH=31
"""

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Final, NamedTuple
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.parsed_prose import (
    Paragraph,
    Parser,
    ParserUnavailable,
    Sentence,
    Token,
    children,
    parse,
    parsed,
)
from tools.passive_voice import first_line
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.sentence_shapes import sentence_text, skipped
from tools.stranded_prepositions import display

EDIT_PAIRS: Final = DATA_DIR / "edit_pairs.json"
LABELS: Final = {
    "THIS": "sentence opens with a demonstrative pronoun",
    "IT": "sentence opens with it/they and the target is ambiguous",
}
DEMONSTRATIVES: Final = frozenset({"this", "that", "these", "those"})
POINTERS: Final = DEMONSTRATIVES | {"it", "they"}
LEADERS: Final = frozenset(
    {"then", "so", "but", "and", "here", "now", "also", "still"})
LEADER_DEPS: Final = frozenset({"advmod", "cc"})
PRONOUN_DEPS: Final = frozenset({"nsubj", "nsubjpass"})
CANDIDATE_DEPS: Final = frozenset(
    {"nsubj", "nsubjpass", "dobj", "attr", "pobj", "appos"})
OPENS: Final = "(opens paragraph)"


class Hit(NamedTuple):
    label: str
    pronoun: Token
    candidates: tuple[str, ...]
    opens: bool
    sentence: Sentence
    index: int
    """The sentence's position in its paragraph."""


def opening_pronoun(sentence: Sentence) -> Token | None:
    """The pointer that opens the sentence, or None."""
    for tok in sentence.tokens:
        if tok.punct:
            continue
        if tok.text.lower() in POINTERS and tok.dep in PRONOUN_DEPS:
            return None if is_cleft(tok, sentence) else tok
        if tok.dep in LEADER_DEPS or tok.text.lower() in LEADERS:
            continue
        return None
    return None


def is_cleft(pronoun: Token, sentence: Sentence) -> bool:
    """Is this the "It is X that ..." cleft, which the parser reads as
    `nsubj` instead of `expl`: "it" with a form of "be" for its head
    and a noun complement that carries a relative clause?"""
    if pronoun.text.lower() != "it":
        return False
    verb = sentence.tokens[pronoun.head]
    if verb.lemma != "be":
        return False
    return any(
        c.dep in ("attr", "acomp") and any(
            g.dep == "relcl" for g in children(c, sentence))
        for c in children(verb, sentence))


def counts_as_candidate(tok: Token, sentence: Sentence) -> bool:
    """Is this noun a subject, object, or the like, or conjoined to one?

    A noun the small model reads as a `compound` of a verb ("The proxy
    stores"), which a noun cannot modify, is a misread subject and counts.
    """
    if tok.dep == "compound":
        return sentence.tokens[tok.head].pos == "VERB"
    seen: set[int] = set()
    while tok.dep == "conj" and tok.i not in seen:
        seen.add(tok.i)
        tok = sentence.tokens[tok.head]
    return tok.dep in CANDIDATE_DEPS


def candidates(sentence: Sentence, plural: bool) -> list[str]:
    """The distinct lowercase nouns of one sentence that "it"/"they" fit."""
    found: list[str] = []
    for tok in sentence.tokens:
        if tok.pos not in ("NOUN", "PROPN"):
            continue
        if not counts_as_candidate(tok, sentence):
            continue
        if plural:
            fits = "Number=Plur" in tok.morph
        else:
            fits = ("Number=Sing" in tok.morph or tok.text == "CODE"
                    or tok.pos == "PROPN")
        name = tok.text.lower() if tok.text != "CODE" else "CODE"
        if fits and name not in found:
            found.append(name)
    return found


def hits(paragraph: Paragraph) -> Iterator[Hit]:
    """Each sentence of one paragraph that opens with a pointer."""
    if skipped(paragraph):
        return
    sentences = paragraph.sentences
    for index, sentence in enumerate(sentences):
        pronoun = opening_pronoun(sentence)
        if pronoun is None:
            continue
        word = pronoun.text.lower()
        if word in DEMONSTRATIVES:
            yield Hit("THIS", pronoun, (), False, sentence, index)
            continue
        if index == 0:
            yield Hit("IT", pronoun, (), True, sentence, index)
            continue
        found = candidates(sentences[index - 1], word == "they")
        if len(found) >= 2:
            yield Hit("IT", pronoun, tuple(found), False, sentence, index)


def message(paragraph: Paragraph, hit: Hit) -> str:
    """`[THIS] This: sentence` or `[IT] it -> a, b: sentence`."""
    text = sentence_text(paragraph, hit.sentence)
    if hit.label == "THIS":
        return f"[THIS] {hit.pronoun.text}: {text}"
    shown = OPENS if hit.opens else ", ".join(hit.candidates)
    return f"[IT] {hit.pronoun.text.lower()} -> {shown}: {text}"


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per sentence that opens with a pointer."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            for hit in hits(paragraph):
                yield Finding(doc.path, first_line(paragraph, hit.sentence),
                              message(paragraph, hit))


EXAMPLES: Final[tuple[tuple[str, str], ...]] = (
    ("The proxy stores the level. It never consults the "
     "implementation again.", "IT: proxy, level"),
    ("The proxy stores the level. The proxy never consults the "
     "implementation again.", "no hit"),
    ("The handler checks the key. This is the fast path.", "THIS"),
    ("The handler checks the key. This check is the fast path.",
     "no hit"),
    ("It is the loop that calls the method.", "no hit"),
    ("The function runs. It returns quickly.", "no hit"),
    ("The function returns a wrapper. It keeps the name.",
     "IT: function, wrapper"),
)
"""Calibration sentences and the result each should give."""


def calibrate(parser: Parser = parse) -> None:
    """Per label, the edit pairs where it fires before, after, or both."""
    pairs: dict[str, dict[str, str]] = json.loads(
        EDIT_PAIRS.read_text(encoding="utf-8"))
    docs: list[Document] = []
    for ident, record in pairs.items():
        previous = record.get("previous", "").strip()
        docs.append(Document.from_text(
            previous or "x", Path(f"calibrate/{ident}.prev.md")))
        for side in ("before", "after"):
            text = f"{previous} {record[side]}" if previous else record[side]
            docs.append(Document.from_text(
                text, Path(f"calibrate/{ident}.{side}.md")))
    results = parsed(docs, parser, use_cache=False)
    skip: dict[str, int] = {}
    sides: dict[str, set[str]] = {}
    for doc, paras in zip(docs, results, strict=True):
        name = doc.path.name
        if name.endswith(".prev.md"):
            ident = name.removesuffix(".prev.md")
            has_previous = bool(pairs[ident].get("previous", "").strip())
            skip[ident] = (sum(len(p.sentences) for p in paras)
                           if has_previous else 0)
    for doc, paras in zip(docs, results, strict=True):
        name = doc.path.name
        if name.endswith(".prev.md"):
            continue
        ident = name.rsplit(".", 2)[0]
        sides[name] = {h.label for p in paras for h in hits(p)
                       if h.index >= skip[ident]}
    for label, meaning in LABELS.items():
        before_only: list[str] = []
        after_only: list[str] = []
        both: list[str] = []
        for ident in pairs:
            b = label in sides[f"{ident}.before.md"]
            a = label in sides[f"{ident}.after.md"]
            if b and a:
                both.append(ident)
            elif b:
                before_only.append(ident)
            elif a:
                after_only.append(ident)
        print(f"== {label}: {meaning} ==")
        for title, ids in (("before only", before_only),
                           ("both", both), ("after only", after_only)):
            for ident in ids:
                print(f"{title}: {ident}")
                print(f"  previous: {pairs[ident].get('previous', '')}")
                print(f"  before:   {pairs[ident]['before']}")
                print(f"  after:    {pairs[ident]['after']}")
        print(f"{label}: before-only {len(before_only)}, "
              f"both {len(both)}, after-only {len(after_only)}, "
              f"of {len(pairs)} pairs\n")
    print("== built-in examples ==")
    example_docs = [Document.from_text(text, Path(f"calibrate/ex{n}.md"))
                    for n, (text, _) in enumerate(EXAMPLES)]
    answers = parsed(example_docs, parser, use_cache=False)
    for (text, expected), paras in zip(EXAMPLES, answers, strict=True):
        got = [message(p, h) for p in paras for h in hits(p)]
        print(f"expected {expected}: {text}")
        for line in got:
            print(f"  hit {line}")
        if not got:
            print("  no hit")


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any pointer sentence is found")
    ap.add_argument("--calibrate", action="store_true",
                    help="compare with tools/data/edit_pairs.json and "
                         "run the built-in examples")
    args = ap.parse_args(argv)
    if args.calibrate:
        try:
            calibrate(parser)
        except ParserUnavailable as exc:
            print(f"pointer_words: parser unavailable ({exc}); "
                  f"nothing checked", file=sys.stderr)
        return 0
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    try:
        findings = list(find([Document.parse(p) for p in paths], parser))
    except ParserUnavailable as exc:
        print(f"pointer_words: parser unavailable ({exc}); "
              f"nothing checked", file=sys.stderr)
        return 0
    found = sorted(
        {(display(f.path), f.line, f.message) for f in findings})
    for shown, line, text in found:
        print(f"survey   {shown}:{line}: {text}")
    these = sum(1 for _, _, t in found if t.startswith("[THIS]"))
    print(f"{len(found)} pointer sentences ({these} [THIS], "
          f"{len(found) - these} [IT])")
    return 1 if args.fail and found else 0


if __name__ == "__main__":
    raise SystemExit(main())
