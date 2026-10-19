#!/usr/bin/env python
"""Report each expletive frame in the prose: "there is", "it is ... that".

The author's style guide asks for the active register: a real actor in
the subject, the action in the verb, no "there is", no empty "it is"
frame. Vale's write-good `ThereIs` rule (run by `tip prose`) matches
"There is/are" by word pattern. This check reads the dependency parse
that `tools/parsed_prose.py` caches under `build/parses/` (spaCy, run in
a throwaway Python 3.12 environment; see that module) and is meant to
replace or confirm Vale's list. `--calibrate` compares the two.

Two labels, one finding per construction.

`[THERE]`: the existential "there", a token with dep `expl` and
lowercase text "there", in any position ("there is", "there are",
"there remains", "if there were", "Without a guard, there is a race").
The head verb must have no subject of its own (no child with dep
`nsubj`, `nsubjpass`, or `csubj` besides the "there"), because an
existential "there" stands in the subject's place. The parser labels a
place adverb `expl` too ("Caching there is one way", "a comprehension
there cannot read"), and that adverb always has a real subject beside
it. The message names the head verb: `[THERE] there is: <sentence>`. A
negated existential ("there is no X") is still the shape and still hits.

`[IT-IS]`: the extraposed "it is ADJ to/that" frame. The token "it" has
dep `nsubj` or `expl` and a form of "be" for its head, and the verb has
an `acomp` child (an adjective: "easy", "true", "possible", "worth")
together with a clausal complement: an `xcomp` (an infinitive, "to add")
or a `ccomp` (a "that" clause), a child of the verb or of the adjective.
"It is a record" (an `attr`, no clause) is not a hit. "It is easy to add
a state" and "It is true that the loop stops" are. The message is
`[IT-IS] <it + auxiliaries + be> <adjective>: <sentence>`, with the
auxiliaries of the verb group in sentence order ("it might have been
better", "it is easy").

There is no cleft rule. The parse cannot tell the "it is X that" cleft
from "it is a NOUN that ..." with an antecedent ("It is a factory that
presets one argument"): all 14 hits of a cleft rule on 2026-10-19 had a
real antecedent. `tools/pointer_words.py` lists the sentence-opening
"It" for the antecedents pass.

A hit prints as `path:line: [LABEL] ...: <sentence>`, the line holding
the sentence's first character. A sentence with two constructions
reports both.

Skips: a construction inside double quotes (an odd number of `"`
before the token, within the paragraph), and a paragraph whose text
starts with `Hint:` or `Done when:` (the Solutions labels). The
paragraph reader is the one `tools/stranded_prepositions.py` uses, so
listings, headings, block quotes, tables, and `#:` lines are skipped and
inline code spans arrive as the placeholder `CODE`. When the parser
cannot start, the check says so and exits 0.

Known keeps, which the baseline holds (judged in the 2026-10-19 read):
an `[IT-IS]` hit where "it" has an antecedent and the adjective's
infinitive lacks its object ("the validation ... so it is easy to
change", "a pure function ... so it is safe to run in parallel"), since
the parse cannot tell that from true extraposition ("It is easy to add a
state"); a quotation the quote count missed; and a place adverb the
parser mislabeled that still has no subject beside it.

Vale's `write-good.ThereIs` reported zero alerts over the book on
2026-10-19: it matches sentence-initial "There is/are" only, and none is
left. It stays on as the cheap guard, and this check adds the
mid-sentence existentials.

Report-only: it prints the hits and exits 0, because the parser is a
statistical model and no gate runs it. `--fail` exits 1 when a NEW hit
is found. It runs inside `tip prose` and alone as `tip expletives`.
Judged keeps live in `tools/data/expletives_baseline.txt`. An entry is
`path<TAB>[LABEL] message` with whitespace normalized and no line
number, so a reflow leaves it alone and an edit to the sentence retires
it. The default run prints each NEW hit, lists a `stale` entry that
matches no hit any more, and ends with a summary (`N new, M accepted`).
`--all` prints every hit, marked NEW or accepted. `--accept` appends
every NEW hit to the baseline and drops the stale entries. A run given
paths compares against those files' entries alone, and refuses
`--accept`.

`--calibrate` prints three things. First, against
`tools/data/edit_pairs.json` (the sentences the author rewrote): per
label, the pairs where the check fires on the before text only (the
hoped-for result), on both, and on the after text only, with ids and
texts. Each record's `previous` sentence is put in front of the text,
and only hits in the edited text count. Second, the built-in examples,
each marked ok or MISS. Third, a comparison with Vale: it runs `vale
--output=JSON Chapters Solutions`, keeps the `write-good.ThereIs`
alerts, and matches them to the `[THERE]` hits by line (an alert
matches a hit when its line falls within the hit sentence's lines; Vale
matches only `[THERE]`-shaped sentences, so only `[THERE]` takes part). It prints CONFIRMED
(both), VALE-ONLY (Vale's match text and the sentence), and PARSE-ONLY,
then a summary. When `vale` is missing, that comparison prints one line
and stops.

    uv run python -m tools.expletives           # new hits
    uv run python -m tools.expletives --all     # every hit
    uv run python -m tools.expletives --accept  # judged keeps
    uv run python -m tools.expletives --calibrate
    uv run python -m tools.expletives Chapters/31_*.md
    uv run tip expletives CH=31
    uv run tip expletives-accept
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
from tools.passive_voice import Unit, first_line, last_line, vale_alerts
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.sentence_shapes import sentence_text, skipped
from tools.stranded_prepositions import display

BASELINE: Final = DATA_DIR / "expletives_baseline.txt"
EDIT_PAIRS: Final = DATA_DIR / "edit_pairs.json"
HEADER: Final = (
    "# Expletive frames a human read and judged keeps: a quotation\n"
    "# the quote count missed, a place adverb the parser mislabeled,\n"
    '# an "it" with a real antecedent. An entry is not an exemption\n'
    "# from the rule.\n"
    "# path<TAB>[LABEL] message, with whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the sentence retires it. Rewritten by `tip expletives-accept`;\n"
    "# read the delta with `tip expletives` before accepting.\n"
    "# See tools/expletives.py.\n"
)
LABELS: Final = {
    "THERE": "existential there",
    "IT-IS": "extraposed it is ADJ to/that",
}
IT_DEPS: Final = frozenset({"nsubj", "expl"})
CLAUSE_DEPS: Final = frozenset({"xcomp", "ccomp"})
SUBJECT_DEPS: Final = frozenset({"nsubj", "nsubjpass", "csubj"})
VALE_CHECK: Final = "write-good.ThereIs"


class Hit(NamedTuple):
    label: str
    pronoun: Token
    verb: Token
    detail: str
    sentence: Sentence
    index: int
    """The sentence's position in its paragraph."""


def it_is_adjective(verb: Token, sentence: Sentence) -> str | None:
    """The adjective if the verb has an `acomp` and a clause, else None."""
    kids = children(verb, sentence)
    clause = any(k.dep in CLAUSE_DEPS for k in kids)
    for kid in kids:
        if kid.dep != "acomp":
            continue
        if clause or any(g.dep in CLAUSE_DEPS
                         for g in children(kid, sentence)):
            return kid.text
    return None


def has_subject(verb: Token, sentence: Sentence, expl: Token) -> bool:
    """Does the verb have a subject other than the "there" token?"""
    return any(c.dep in SUBJECT_DEPS and c.i != expl.i
               for c in children(verb, sentence))


def verb_group(verb: Token, sentence: Sentence) -> str:
    """The auxiliaries in sentence order, then the head verb's text."""
    parts = [c for c in children(verb, sentence)
             if c.dep == "aux" and c.i < verb.i]
    return " ".join(t.text.lower() for t in (*parts, verb))


def quoted(text: str, token: Token) -> bool:
    """Is the token inside double quotes: an odd `"` count before it?"""
    return text[:token.idx].count('"') % 2 == 1


def frames(paragraph: Paragraph, sentence: Sentence,
           index: int) -> Iterator[Hit]:
    """Each expletive frame of one sentence."""
    for tok in sentence.tokens:
        word = tok.text.lower()
        if word == "there" and tok.dep == "expl":
            head = sentence.tokens[tok.head]
            if (not quoted(paragraph.text, tok)
                    and not has_subject(head, sentence, tok)):
                yield Hit("THERE", tok, head, head.text, sentence, index)
            continue
        if word != "it" or tok.dep not in IT_DEPS:
            continue
        verb = sentence.tokens[tok.head]
        if verb.lemma != "be" or quoted(paragraph.text, tok):
            continue
        adjective = it_is_adjective(verb, sentence)
        if adjective is not None:
            yield Hit("IT-IS", tok, verb, adjective, sentence, index)


def hits(paragraph: Paragraph) -> Iterator[Hit]:
    """Each expletive frame in one paragraph."""
    if skipped(paragraph):
        return
    for index, sentence in enumerate(paragraph.sentences):
        yield from frames(paragraph, sentence, index)


def message(paragraph: Paragraph, hit: Hit) -> str:
    """`[LABEL] ...: sentence`, whitespace normalized."""
    text = sentence_text(paragraph, hit.sentence)
    if hit.label == "THERE":
        return f"[THERE] there {hit.detail}: {text}"
    group = verb_group(hit.verb, hit.sentence)
    return f"[IT-IS] it {group} {hit.detail}: {text}"


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per expletive frame."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            for hit in hits(paragraph):
                yield Finding(doc.path, first_line(paragraph, hit.sentence),
                              message(paragraph, hit))


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


EXAMPLES: Final[tuple[tuple[str, str | None], ...]] = (
    ("There is a simpler design.", "THERE"),
    ("A simpler design exists.", None),
    ("There are three parts.", "THERE"),
    ("Caching there is one way to build a Singleton.", None),
    ("It is easy to add a state.", "IT-IS"),
    ("Adding a state is easy.", None),
    ("It is a record.", None),
    ("It is true that the loop stops.", "IT-IS"),
    ("Put the file there.", None),
)
"""Calibration sentences and the label each should give (None: no hit)."""


def calibrate_pairs(parser: Parser) -> None:
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
    totals: dict[str, tuple[int, int, int]] = {}
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
        totals[label] = (len(before_only), len(both), len(after_only))
        print(f"{label}: before-only {len(before_only)}, "
              f"both {len(both)}, after-only {len(after_only)}, "
              f"of {len(pairs)} pairs\n")
    summary = "; ".join(f"{label} {b}/{n}/{a}"
                        for label, (b, n, a) in totals.items())
    print(f"Summary (before-only/both/after-only, of {len(pairs)} "
          f"pairs): {summary}\n")


def calibrate_examples(parser: Parser) -> None:
    """The built-in examples, each marked ok or MISS."""
    print("== built-in examples ==")
    docs = [Document.from_text(text, Path(f"calibrate/ex{n}.md"))
            for n, (text, _) in enumerate(EXAMPLES)]
    answers = parsed(docs, parser, use_cache=False)
    for (text, expected), paras in zip(EXAMPLES, answers, strict=True):
        got = [h.label for p in paras for h in hits(p)]
        ok = got == ([expected] if expected else [])
        print(f"{'ok' if ok else 'MISS':4} expected "
              f"{expected or 'no hit'}, got {got or 'no hit'}: {text}")
    print()


def calibrate_vale(parser: Parser) -> None:
    """CONFIRMED, VALE-ONLY, and PARSE-ONLY against write-good.ThereIs."""
    alerts = vale_alerts()
    if alerts is None:
        return
    names = {a["Check"] for found in alerts.values() for a in found}
    kept = {path: [a for a in found if a["Check"] == VALE_CHECK]
            for path, found in alerts.items()}
    if not any(kept.values()):
        print(f"vale: no {VALE_CHECK} alerts; checks seen: "
              f"{sorted(names)}")
        return
    paths = md_files([ROOT / "Chapters", ROOT / "Solutions"])
    docs = [Document.parse(p) for p in paths]
    mine: dict[str, list[Unit]] = {}
    sentences: dict[str, list[Unit]] = {}
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        shown = display(doc.path).replace("\\", "/")
        for paragraph in paras:
            for sentence in paragraph.sentences:
                sentences.setdefault(shown, []).append(Unit(
                    first_line(paragraph, sentence),
                    last_line(paragraph, sentence),
                    sentence_text(paragraph, sentence)))
            for hit in hits(paragraph):
                if hit.label != "THERE":
                    continue
                mine.setdefault(shown, []).append(Unit(
                    first_line(paragraph, hit.sentence),
                    last_line(paragraph, hit.sentence),
                    message(paragraph, hit)))
    confirmed: list[str] = []
    vale_only: list[str] = []
    parse_only: list[str] = []
    matched: set[tuple[str, int, int, str]] = set()
    for path, found in kept.items():
        units = mine.get(path, [])
        for alert in found:
            line = alert["Line"]
            hit_units = [u for u in units if u.first <= line <= u.last]
            if hit_units:
                matched.update((path, u.first, u.last, u.text)
                               for u in hit_units)
                confirmed.append(f"{path}:{line}: {alert['Match']!r}: "
                                 f"{hit_units[0].text}")
                continue
            near = [u for u in sentences.get(path, [])
                    if u.first <= line <= u.last]
            text = near[0].text if near else "(sentence not found)"
            vale_only.append(f"{path}:{line}: {alert['Match']!r}: {text}")
    for path, units in mine.items():
        for u in units:
            if (path, u.first, u.last, u.text) not in matched:
                parse_only.append(f"{path}:{u.first}: {u.text}")
    for title, items in (("CONFIRMED", confirmed), ("VALE-ONLY", vale_only),
                         ("PARSE-ONLY", parse_only)):
        print(f"== {title} ({len(items)}) ==")
        for item in items:
            print(item)
        print()
    total = sum(len(u) for u in mine.values())
    print(f"Vale {sum(len(v) for v in kept.values())} alerts, parse "
          f"{total} [THERE] hits: {len(confirmed)} confirmed alerts, "
          f"{len(vale_only)} vale-only, {len(parse_only)} parse-only")


def calibrate(parser: Parser = parse) -> None:
    """All three comparisons: edit pairs, examples, then Vale."""
    calibrate_pairs(parser)
    calibrate_examples(parser)
    calibrate_vale(parser)


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW expletive is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    ap.add_argument("--calibrate", action="store_true",
                    help="compare with tools/data/edit_pairs.json, run "
                         "the built-in examples, and compare with Vale's "
                         "write-good.ThereIs")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    if args.calibrate:
        try:
            calibrate(parser)
        except ParserUnavailable as exc:
            print(f"expletives: parser unavailable ({exc}); "
                  f"nothing checked", file=sys.stderr)
        return 0
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    try:
        findings = list(find([Document.parse(p) for p in paths], parser))
    except ParserUnavailable as exc:
        print(f"expletives: parser unavailable ({exc}); "
              f"nothing checked", file=sys.stderr)
        return 0
    found = sorted(
        {(display(f.path), f.line, f.message) for f in findings})
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
