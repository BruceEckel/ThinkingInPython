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
paths compares against those files' entries alone, and refuses
`--accept`.

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

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Final, NamedTuple
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
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.sentence_shapes import sentence_text, skipped
from tools.stranded_prepositions import display

BASELINE: Final = DATA_DIR / "passive_voice_baseline.txt"
EDIT_PAIRS: Final = DATA_DIR / "edit_pairs.json"
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


def first_line(paragraph: Paragraph, sentence: Sentence) -> int:
    lines = paragraph.lines
    return lines[min(sentence.start, len(lines) - 1)]


def last_line(paragraph: Paragraph, sentence: Sentence) -> int:
    lines = paragraph.lines
    return lines[min(max(sentence.end - 1, 0), len(lines) - 1)]


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


def calibrate_pairs(parser: Parser) -> None:
    """Per label, the edit pairs where it fires before, after, or both."""
    pairs: dict[str, dict[str, str]] = json.loads(
        EDIT_PAIRS.read_text(encoding="utf-8"))
    docs = [Document.from_text(record[side],
                               Path(f"calibrate/{ident}.{side}.md"))
            for ident, record in pairs.items()
            for side in ("before", "after")]
    results = parsed(docs, parser, use_cache=False)
    sides = {doc.path.name: {h.label for p in paras for h in hits(p)}
             for doc, paras in zip(docs, results, strict=True)}
    for label in LABELS:
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
        print(f"== {label} ==")
        for title, ids in (("before only", before_only),
                           ("both", both), ("after only", after_only)):
            for ident in ids:
                print(f"{title}: {ident}")
                print(f"  before: {pairs[ident]['before']}")
                print(f"  after:  {pairs[ident]['after']}")
        print(f"{label}: before-only {len(before_only)}, "
              f"both {len(both)}, after-only {len(after_only)}, "
              f"of {len(pairs)} pairs\n")


def vale_alerts() -> dict[str, list[dict[str, Any]]] | None:
    """Vale's JSON for the book, or None (after saying why)."""
    if shutil.which("vale") is None:
        print("vale: not on PATH; skipping the Vale comparison")
        return None
    done = subprocess.run(
        ["vale", "--output=JSON", "Chapters", "Solutions"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        check=False)
    try:
        data = json.loads(done.stdout)
    except ValueError:
        print(f"vale: no JSON (exit {done.returncode}); skipping the "
              f"Vale comparison")
        return None
    return {str(k).replace("\\", "/"): v for k, v in data.items()}


class Unit(NamedTuple):
    first: int
    last: int
    text: str


def calibrate_vale(parser: Parser) -> None:
    """CONFIRMED, VALE-ONLY, and PARSE-ONLY against write-good.Passive."""
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
          f"{total} hits: {len(confirmed)} confirmed alerts, "
          f"{len(vale_only)} vale-only, {len(parse_only)} parse-only")


def calibrate(parser: Parser = parse) -> None:
    """Both comparisons: edit pairs, then Vale."""
    calibrate_pairs(parser)
    calibrate_vale(parser)


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW passive is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    ap.add_argument("--calibrate", action="store_true",
                    help="compare with tools/data/edit_pairs.json and "
                         "with Vale's write-good.Passive")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    if args.calibrate:
        try:
            calibrate(parser)
        except ParserUnavailable as exc:
            print(f"passive_voice: parser unavailable ({exc}); "
                  f"nothing checked", file=sys.stderr)
        return 0
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    try:
        findings = list(find([Document.parse(p) for p in paths], parser))
    except ParserUnavailable as exc:
        print(f"passive_voice: parser unavailable ({exc}); "
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
