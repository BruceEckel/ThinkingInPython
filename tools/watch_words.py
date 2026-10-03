#!/usr/bin/env python
"""Report the author's "words and phrases to watch" in prose.

The global style guide keeps two lists of words that are usually a
defect. Tier 3 ("Don't use") is metaphor standing in for a literal
statement: `ships`, `lands`, `fuse`, `load-bearing`, `part ways`,
`rides on`, `near-miss`, `the way out`, `in the first place`, `wants`,
`spelling`. Tier 2 ("Avoid if possible") is a word that must earn its
place: `already`, `even`, `honest`, `buy`, `hooks`, `never`, `anyway`,
`at all`, `promise`. A Tier 3 hit is a defect to fix unless a human
reads it as literal ("a person wants a refund"); a Tier 2 hit is kept
where the word changes the meaning.

The check reuses the prose walk of `tools.stranded_prepositions`:
fenced listings, headings, block quotes, tables, HTML lines, link
definitions, and `#:` lines are skipped, inline code spans become the
placeholder `CODE`, and links lose their targets. It matches whole
words and phrases, case-insensitively, so `relationship` is not
`ship` and `landscape` is not `land`. Two words carry a literal sense
that is not flagged: `even` in the arithmetic sense ("even number",
"odd and even", "even integer"), and `hook` within four words of
`pre-commit`, `git`, `SessionStart`, `Claude`, or `hooks.py`, or
before `module`.

A hit reports as `path:line: [T3|T2] word: clause`, with the clause
(split at `.`, `,`, `;`, `:`, `?`, `!`) that holds the word and the
line of the word. Report-only: it prints and exits 0. `--fail` exits 1
when a NEW Tier 3 hit is found; Tier 2 alone never fails. `--tier 3`
prints only Tier 3.

Every hit a human judges a keep lives in
`tools/data/watch_words_baseline.txt`, so a run prints only what is
new. An entry is `path<TAB>word: clause`, whitespace normalized and no
line number, so a reflow leaves it alone and an edit to the clause
retires it. An entry is a judged keep, not an exemption from the rule.
The default run prints each NEW hit, a `stale` entry that matches no
hit any more, and a summary (`N new (a T3, b T2), M accepted`).
`--all` prints every hit, marked NEW or accepted. `--accept` appends
every NEW hit to the baseline and drops the stale entries. A run
given paths compares against those files' entries alone, and refuses
`--accept`.

    uv run python -m tools.watch_words          # new hits
    uv run python -m tools.watch_words --all    # every hit
    uv run python -m tools.watch_words --tier 3 # Tier 3 only
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
        (3, r"in the first place"),
        (3, r"ships?|shipped|shipping"),
        (3, r"lands?|landed|landing"),
        (3, r"fuses?|fused|fusing"),
        (3, r"load[- ]bearing"),
        (3, r"part(?:s|ed)? ways"),
        (3, r"rides? on|rode on"),
        (3, r"near[- ]miss"),
        (3, r"the way out"),
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
    ap.add_argument("--tier", type=int, choices=(2, 3),
                    help="print only this tier")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    if args.tier and args.accept:
        ap.error("--accept covers both tiers; give no --tier")
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
        added = {key(s, w, c) for s, _, _, w, c in found
                 if key(s, w, c) not in baseline}
        write_baseline((baseline - set(stale)) | added, BASELINE)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    shown = [h for h in found if not args.tier or h[2] == args.tier]
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
    t3 = sum(1 for h in new if h[2] == 3)
    print(f"{len(new)} new ({t3} T3, {len(new) - t3} T2), "
          f"{len(shown) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and t3 else 0


if __name__ == "__main__":
    raise SystemExit(main())
