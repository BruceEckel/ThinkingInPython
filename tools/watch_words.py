#!/usr/bin/env python
"""Report the author's "words and phrases to watch" in prose.

The global style guide keeps three lists of words that are usually a
defect. Tier 3 ("Don't use") is metaphor standing in for a literal
statement: `ships`, `lands`, `fuse`, `load-bearing`, `part ways`,
`rides on`, `near-miss`, `the way out`, `in the first place`, `wants`,
`spelling`, `pays off`, `pays for itself` (a cost figure; write
"beneficial", "justified", "a better choice", or the gain, "saves
time"; "worth its cost" keeps the figure). Tier 2 ("Avoid if possible") is a word that must earn its
place: `already`, `even`, `honest`, `buy`, `hooks`, `never`, `anyway`,
`at all`, `promise`. Tier 1 ("Consider rewriting") is a word with
legitimate uses that the author checks every time: `happen`, `is what`,
`and nothing else`, `nothing more`, `nothing but`, `does it`, `ever`,
`only`, `exactly`, `has to` (with `have to` and `had to`), `actually`,
`itself`, `was to`, `used to`, `fix` (every form; the repair sense,
the hyphenated compounds, and "fixed point" stay, the hold-constant
sense goes, adjective included). A Tier 3 hit is a defect to fix unless a
human reads it as literal ("a person wants a refund"); a Tier 2 hit is
kept where the word changes the meaning; a Tier 1 hit is a prompt to
try a rewrite, and most stay.

The check reuses the prose walk of `tools.stranded_prepositions`:
fenced listings, headings, block quotes, tables, HTML lines, link
definitions, and `#:` lines are skipped, inline code spans become the
placeholder `CODE`, and links lose their targets. It matches whole
words and phrases, case-insensitively, so `relationship` is not
`ship` and `landscape` is not `land`. `ever` matches as a word of its
own, so `never`, `every`, `however`, and `forever` do not count. Two
words carry a literal sense that is not flagged: `even` in the
arithmetic sense ("even number",
"odd and even", "even integer"), and `hook` within four words of
`pre-commit`, `git`, `SessionStart`, `Claude`, or `hooks.py`, or
before `module`.

A hit reports as `path:line: [T3|T2] word: clause`, with the clause
(split at `.`, `,`, `;`, `:`, `?`, `!`) that holds the word and the
line of the word. Report-only: it prints and exits 0. `--fail` exits 1
when a NEW Tier 3 hit is found; Tier 2 alone never fails. `--tier 3`
prints only Tier 3.

Tier 1 is advisory. Its hits are numerous and mostly fine, so a
default run never prints them, and they never count toward `new` or
`--fail`. `--all` prints them marked `[T1]`, `--tier 1` prints them
alone, and either adds a `c T1` count to the summary. `--accept`
leaves them out of the baseline; `--accept --tier 1` baselines only
the Tier 1 hits.

Every hit a human judges a keep lives in
`tools/data/watch_words_baseline.txt`, so a run prints only what is
new. An entry is `path<TAB>word: clause`, whitespace normalized and no
line number, so a reflow leaves it alone and an edit to the clause
retires it. An entry is a judged keep, not an exemption from the rule.
The default run prints each NEW hit, a `stale` entry that matches no
hit any more, and a summary (`N new (a T3, b T2), M accepted`; with
Tier 1 shown, `N new (a T3, b T2, c T1), M accepted`).
`--all` prints every hit, marked NEW or accepted. `--accept` appends
every NEW Tier 2 and Tier 3 hit to the baseline and drops the stale
entries. A run
given paths compares against those files' entries alone, and refuses
`--accept`.

    uv run python -m tools.watch_words          # new hits
    uv run python -m tools.watch_words --all    # every hit
    uv run python -m tools.watch_words --tier 3 # Tier 3 only
    uv run python -m tools.watch_words --tier 1 # advisory Tier 1
    uv run python -m tools.watch_words --accept # judged keeps
    uv run tip watch-words CH=30
    uv run tip watch-words-accept
"""

import argparse
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.repo import add_paths_arg, md_files
from tools.stranded_prepositions import (
    TERMINATOR,
    display,
    joined,
    load_baseline,
    paragraphs,
    write_baseline,
)

BASELINE: Final = DATA_DIR / "watch_words_baseline.txt"
HEADER: Final = (
    "# Watch-word hits a human read and judged a keep: a literal\n"
    "# sense, or a word that earns its place. An entry is not an\n"
    "# exemption from the rule.\n"
    "# path<TAB>word: clause, with the clause's whitespace normalized\n"
    "# and no line number, so a reflow leaves an entry alone and an\n"
    "# edit to the clause retires it. Rewritten by\n"
    "# `tip watch-words-accept`; read the delta with `tip watch-words`\n"
    "# before accepting. See tools/watch_words.py.\n"
)
RULES: Final[tuple[tuple[int, re.Pattern[str]], ...]] = tuple(
    (tier, re.compile(rf"\b(?:{pattern})\b", re.IGNORECASE))
    for tier, pattern in [
        (1, r"happen(?:s|ed|ing)?"),
        (1, r"is what"),
        (1, r"and nothing else"),
        (1, r"nothing more"),
        (1, r"nothing but"),
        (1, r"does it"),
        (1, r"ever"),
        (1, r"only"),
        (1, r"exactly"),
        (1, r"(?:has|have|had) to"),
        (1, r"actually"),
        (1, r"itself"),
        (1, r"was to"),
        (1, r"used to"),
        (1, r"fix(?:es|ed|ing)?"),
        (3, r"in the first place"),
        (3, r"ships?|shipped|shipping"),
        (3, r"lands?|landed|landing"),
        (3, r"fuses?|fused|fusing"),
        (3, r"load[- ]bearing"),
        (3, r"part(?:s|ed)? ways"),
        (3, r"rides? on|rode on"),
        (3, r"near[- ]miss"),
        (3, r"the way out"),
        (3, r"pays? off|paid off|paying off"),
        (3, r"pays? for (?:it|them)sel(?:f|ves)|paid for itself"),
        (3, r"wants?"),
        (3, r"spellings?"),
        (2, r"already"),
        (2, r"even"),
        (2, r"honest(?:ly)?"),
        (2, r"buys?|bought"),
        (2, r"hooks?"),
        (2, r"never"),
        (2, r"anyway"),
        (2, r"at all"),
        (2, r"promis(?:e|es|ed|ing)"),
    ]
)
EVEN_AFTER: Final = re.compile(
    r"-?\s*(?:numbers?|numbered|integers?|and\s+odd|or\s+odd"
    r"|parity)\b", re.IGNORECASE)
EVEN_BEFORE: Final = re.compile(
    r"\bodd\s+(?:and|or)\s+$", re.IGNORECASE)
HOOK_NEAR: Final = ("pre-commit", "git", "sessionstart", "claude",
                    "hooks.py")
HOOK_WINDOW: Final = 4
HOOK_MODULE: Final = re.compile(r"\s+module\b", re.IGNORECASE)


def literal_even(text: str, m: re.Match[str]) -> bool:
    """Is this `even` the arithmetic sense, not the intensifier?"""
    return bool(EVEN_AFTER.match(text, m.end())
                or EVEN_BEFORE.search(text[:m.start()]))


def literal_hook(text: str, m: re.Match[str]) -> bool:
    """Is this `hook` a pre-commit, git, or Claude Code hook?"""
    if HOOK_MODULE.match(text, m.end()):
        return True
    before = text[:m.start()].split()[-HOOK_WINDOW:]
    after = text[m.end():].split()[:HOOK_WINDOW]
    near = " ".join(before + after).lower()
    return any(term in near for term in HOOK_NEAR)


def literal(word: str, text: str, m: re.Match[str]) -> bool:
    """Does this match carry a sense the style guide does not flag?"""
    if word == "even":
        return literal_even(text, m)
    if word in ("hook", "hooks"):
        return literal_hook(text, m)
    return False


def bounds(text: str) -> list[tuple[int, int]]:
    """The (start, end) of every clause in `text`."""
    spans: list[tuple[int, int]] = []
    start = 0
    for m in TERMINATOR.finditer(text):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(text)))
    return spans


def find(doc: Document) -> Iterator[tuple[Path, int, int, str, str]]:
    """(path, line, tier, word, clause) per watch word in a document."""
    for paragraph in paragraphs(doc):
        text, lines = joined(paragraph)
        spans = bounds(text)
        for tier, rule in RULES:
            for m in rule.finditer(text):
                word = " ".join(m.group().lower().split())
                if literal(word, text, m):
                    continue
                begin, end = next(
                    (s, e) for s, e in spans if m.start() <= max(e, s))
                clause = " ".join(text[begin:end].split())
                yield doc.path, lines[m.start()], tier, word, clause


def key(shown: str, word: str, clause: str) -> str:
    """The baseline line for a hit: path, word, clause, no line."""
    return f"{shown}\t{word}: {' '.join(clause.split())}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW Tier 3 hit is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--tier", type=int, choices=(1, 2, 3),
                    help="print only this tier (1 is advisory)")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW Tier 2 and 3 hits (with --tier "
                         "1, the Tier 1 hits) to the baseline and "
                         "drop stale entries")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    if args.accept and args.tier in (2, 3):
        ap.error("--accept covers Tiers 2 and 3; give no --tier, "
                 "or --tier 1")
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    found = sorted(
        (display(p), line, tier, word, clause)
        for path in paths
        for p, line, tier, word, clause in find(Document.parse(path))
    )
    baseline = load_baseline(BASELINE)
    scope = {e for e in baseline if e.split("\t", 1)[0] in shown_paths}
    current = {key(s, w, c) for s, _, _, w, c in found}
    stale = sorted(scope - current)
    if args.accept:
        added = {key(s, w, c) for s, _, t, w, c in found
                 if (t == 1) == (args.tier == 1)
                 and key(s, w, c) not in baseline}
        write_baseline((baseline - set(stale)) | added, BASELINE)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    show_t1 = args.all or args.tier == 1
    shown = [h for h in found
             if (h[2] == args.tier if args.tier
                 else show_t1 or h[2] != 1)]
    new = [h for h in shown if key(h[0], h[3], h[4]) not in baseline]
    for path, line, tier, word, clause in shown:
        accepted = key(path, word, clause) in baseline
        if accepted and not args.all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {path}:{line}: [T{tier}] {word}: {clause}")
    for entry in stale:
        path, rest = entry.split("\t", 1)
        print(f"stale    {path}: {rest}")
    count = {t: sum(1 for h in new if h[2] == t) for t in (1, 2, 3)}
    t3 = count[3]
    tiers = f"{t3} T3, {count[2]} T2"
    if show_t1:
        tiers += f", {count[1]} T1"
    print(f"{len(new)} new ({tiers}), "
          f"{len(shown) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and t3 else 0


if __name__ == "__main__":
    raise SystemExit(main())
