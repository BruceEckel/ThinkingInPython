"""Settle `check_self_reference.py`'s grounding findings with a model.

The grounding rule's search settles one fact: the linked chapter
contains none of the code names in the sentence. It cannot tell a
sentence that *attributes* those names to the linked chapter (a real
error, like chapter 07's old "[Rethinking Objects] does with
`slots=True`") from one that credits the linked chapter with an idea
while the names belong to the current chapter's own example ("`DONE` is
a [sentinel]"). That is a reading question, so this tool asks TypeSafe
a Choice question about each finding and stores the answer in
`tools/data/grounding_verdicts.json`, which the gate reads offline:
`check_self_reference.py` turns a verdict at or above `MISATTRIBUTED`
into SR004, which gates, and drops a finding judged to credit an idea.

Only findings with no stored verdict are sent, so a run after a small
edit costs a question or two. A verdict whose sentence no longer
produces a finding is pruned. `--dry-run` lists what would be asked.

Calibration, 2026-09-27: the 41 real findings, which a reader judged
all to credit an idea, scored 0.00-0.11 for attribution; the five
planted misattributions in `CALIBRATION` scored 0.66-0.93. `--calibrate`
re-asks those five and the stored real ones, for a model or wording
change.

    tip grounding-triage                  # ask about new findings
    tip grounding-triage ARGS=--dry-run
    tip grounding-triage ARGS=--calibrate
"""

import argparse
import datetime
import sys
from typing import Any

from tools import judgments
from tools.check_self_reference import (
    MISATTRIBUTED, VERDICTS_FILE, Site, corpus, default_waivers,
    grounding_sites)
from tools.config import CHAPTERS_DIR
from tools.markdown import Document
from tools.repo import md_files

QUESTION = {
    "instructions": [
        "The sentence in `sentence` links to another chapter of the "
        "same book; `link.label` is the link text and "
        "`link.target_title` is the linked chapter's title.",
        "`terms` lists code names that appear in the sentence. A search "
        "has confirmed that the linked chapter contains none of them.",
        "Decide what the sentence says the linked chapter contains, "
        "shows, or defines.",
    ],
    "criteria": {
        "terms_to_target": (
            "The sentence says or implies that the linked chapter "
            "contains, shows, defines, or uses at least one name in "
            "`terms`, for example 'the `Tile` class from [Chapter X]' "
            "or '[Chapter X] uses `slots=True`'."),
        "idea_to_target": (
            "The sentence credits the linked chapter only with a "
            "concept, technique, or general topic. Every name in "
            "`terms` belongs to the code under discussion in the "
            "current chapter, not to the linked chapter."),
    },
}

# Misattributions to check the question against, since the book has
# none today: chapter 07's historical sentence, and four real sentences
# reworded to attribute a code name to the linked chapter.
# (file, target, label, terms, sentence)
CALIBRATION = [
    ("07_Foundations--Classes.md", "20_Patterns--Rethinking_Objects.md",
     "Rethinking Objects", ["slots", "cached_property"],
     "The stored value lives in the instance's `__dict__`, so a class "
     "that suppresses that dictionary, as [Rethinking Objects]"
     "(20_Patterns--Rethinking_Objects.md) does with `slots=True`, "
     "cannot use `cached_property`."),
    ("35_Patterns--Flyweight.md", "20_Patterns--Rethinking_Objects.md",
     "Rethinking Objects", ["Tile"],
     "The `Tile` record from [Rethinking Objects](20_Patterns--"
     "Rethinking_Objects.md#the-immutability-solution) holds a `list`, "
     "so every cell that shares the tile shares that list."),
    ("23_Patterns--Iterators.md", "05_Foundations--Functions.md",
     "Functions", ["DONE"],
     "This listing reuses the `DONE` sentinel that [Functions]"
     "(05_Foundations--Functions.md#sentinel-values) defines."),
    ("31_Patterns--State_Machines.md", "13_Techniques--Pattern_Matching.md",
     "Pattern Matching", ["APPEARS"],
     "As in the `APPEARS` example in [Pattern Matching](13_Techniques--"
     "Pattern_Matching.md#a-bare-name-captures-a-dotted-name-compares), "
     "a dotted name compares the event with that member."),
    ("28_Patterns--Function_Objects.md", "18_Techniques--Performance.md",
     "record", ["Repeat"],
     "`Repeat` first appears in [Performance](18_Techniques--"
     "Performance.md#record), where it becomes a record."),
]


def state(file: str, site: Site) -> dict[str, Any]:
    book = corpus()
    return {
        "current_chapter_title": judgments.title(book[file].text),
        "previous_sentence": site.previous,
        "sentence": site.sentence,
        "link": {"label": site.label,
                 "target_title": judgments.title(book[site.target].text)},
        "terms": site.terms,
    }


def findings() -> list[tuple[str, Site]]:
    waivers = default_waivers()
    return [(path.name, site)
            for path in md_files([CHAPTERS_DIR])
            for site in grounding_sites(Document.parse(path), waivers)]


def p_terms(answer: dict[str, dict[str, Any]]) -> float:
    return answer["attribution"]["probabilities"]["terms_to_target"]


def progress(done: int, total: int) -> None:
    print(f"\r  {done}/{total}", end="", file=sys.stderr, flush=True)
    if done == total:
        print(file=sys.stderr)


def calibrate(store: dict[str, dict[str, Any]]) -> int:
    planted = [(f, Site(0, s, "", t, "", label, terms))
               for f, t, label, terms, s in CALIBRATION]
    real = [(f, s) for f, s in findings() if s.key in store]
    cases = planted + real
    answers = judgments.ask(
        [(state(f, s), {"attribution": QUESTION}) for f, s in cases],
        progress)
    wrong = 0
    for (f, s), a in zip(cases, answers):
        p = p_terms(a)
        expected = s.line == 0
        mark = " " if (p >= MISATTRIBUTED) == expected else "X"
        wrong += mark == "X"
        where = "planted" if s.line == 0 else f"line {s.line}"
        print(f"{mark} {p:.2f}  {f[:2]} {where:9} -> {s.target[:2]}")
    print(f"{len(cases) - wrong}/{len(cases)} on the expected side of "
          f"{MISATTRIBUTED}")
    return 1 if wrong else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="list the findings that would be asked about")
    ap.add_argument("--calibrate", action="store_true",
                    help="re-ask the planted and stored cases; store "
                         "nothing")
    args = ap.parse_args(argv)

    store = judgments.load(VERDICTS_FILE)
    if args.calibrate:
        return calibrate(store)

    current = findings()
    live = {s.key for _, s in current}
    stale = [k for k in store if k not in live]
    new = [(f, s) for f, s in current if s.key not in store]
    if args.dry_run:
        for f, s in new:
            print(f"{CHAPTERS_DIR.name}/{f}:{s.line}: -> {s.target}")
        print(f"{len(new)} to ask, {len(stale)} stale, "
              f"{len(current) - len(new)} settled")
        return 0

    for k in stale:
        del store[k]
    if new:
        answers = judgments.ask(
            [(state(f, s), {"attribution": QUESTION}) for f, s in new],
            progress)
        today = datetime.date.today().isoformat()
        for (f, s), a in zip(new, answers):
            p = p_terms(a)
            store[s.key] = {
                "file": f, "line": s.line, "target": s.target,
                "terms": s.terms, "sentence": s.sentence,
                "p_terms": p, "asked": today,
            }
            if p >= MISATTRIBUTED:
                print(f"{CHAPTERS_DIR.name}/{f}:{s.line}: SR004 "
                      f"attributes {s.terms} to {s.target} (p={p:.2f})")
    # Line numbers move with every edit above a sentence; refresh them
    # so the stored file stays readable, without re-asking.
    for f, s in current:
        store[s.key]["line"] = s.line
    judgments.save(VERDICTS_FILE, store)
    print(f"{len(new)} asked, {len(stale)} pruned, "
          f"{len(store)} verdicts in {VERDICTS_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
