#!/usr/bin/env python
"""Rank paragraphs by how many negatives the reader must cancel.

The author's style rule: prefer the positive statement. A negative makes
the reader build the positive picture and then cancel it, and the whole
family counts, not just "not": no, never, nothing, un-/non-/-less,
"without" plus a gerund, verbs that mean "did not" (omit, lack, fail,
skip), and the restrictive "only". The `positive` skill
(`.claude/skills/positive/SKILL.md`) is the pass that restates a
paragraph; this tool is its prefilter. It lists the paragraphs with the
most negatives first, so the pass reads the dense ones before the rest.

It reads the dependency parse that `tools/parsed_prose.py` caches under
`build/parses/` (spaCy, run in a throwaway Python 3.12 environment; see
that module). Each token of a paragraph counts once, by the first test
it passes:

- dep `neg` (not, n't, never as spaCy labels them);
- a negating word: no, none, nothing, nobody, nowhere, neither, nor,
  without, unless, never, cannot;
- a verb (pos VERB) with the lemma omit, lack, fail, skip, avoid,
  refuse, forbid, prevent, or miss;
- a prefix word, `un` or `non` plus four or more letters, or `non-x`,
  or a bare "non" (spaCy splits "non-empty" into "non", "-", "empty"),
  except the words and stems in `PREFIX_STOP` (under, union, unit,
  unique, universal, until, unpack, and the like);
- a suffix word, three or more letters plus `less`, except "unless"
  (counted above as a negating word) and the words in `SUFFIX_STOP`;
- the restrictive "only" (pos ADV or ADJ), counted apart as `only`.

"regardless", "nevertheless", and "nonetheless" are concessive
connectives, not a negation the reader cancels, so they do not count.
The library name "Stateless" (capitalized) does not count; the
lowercase adjective does.

A paragraph is listed when its count without `only` reaches THRESHOLD
(default 3, `--threshold N`). A line reads `survey   path:line:
[NEG n +k only] word, word x2: <first 90 characters>`: the matched
words in order of first appearance, lowercased, a repeat shown as
"not x3", and `+k only` present only when k is above 0. The line is
the paragraph's first. A paragraph that starts with `Hint:` or `Done
when:` (the Solutions labels) is skipped; the paragraph reader is the
one `tools/stranded_prepositions.py` uses, so listings, headings, block
quotes, tables, and `#:` lines are skipped and inline code spans arrive
as the placeholder `CODE`. When the parser cannot start, the tool says
so and exits 0.

After the hits comes a per-file table (file, paragraphs, paragraphs at
or above the threshold, negatives per 1000 words with `only` counted),
densest file first, and the line `N paragraphs at >= THRESHOLD in F
files`. `--top N` prints only the N densest paragraphs (by count, then
by count per token) before the table.

A survey tool with no baseline, outside `tip prose`. Whether a negation
is the claim, half of a real contrast, or an accident with a positive
form is the `positive` skill's judgment, so a listed paragraph is a
candidate and not a fault. `--fail` exits 1 when any paragraph is
listed, for scripting.

`--calibrate` counts the markers (without `only`) in the `before` and
`after` text of each pair in `tools/data/edit_pairs.json`, prints the
pairs in three groups (FEWER, SAME, MORE negatives after the author's
rewrite), and ends with the three counts and the two totals. Then it
prints the style rule's own examples with the count each side should
give.

    uv run python -m tools.negation_density            # every paragraph
    uv run python -m tools.negation_density --top 20
    uv run python -m tools.negation_density --calibrate
    uv run tip negatives CH=31
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Final, NamedTuple
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.parsed_prose import (
    Paragraph,
    Parser,
    ParserUnavailable,
    parse,
    parsed,
)
from tools.repo import add_paths_arg, md_files
from tools.sentence_shapes import skipped
from tools.stranded_prepositions import display

EDIT_PAIRS: Final = DATA_DIR / "edit_pairs.json"
DEFAULT_THRESHOLD: Final = 3
PREVIEW: Final = 90
NEG_WORDS: Final = frozenset({
    "no", "none", "nothing", "nobody", "nowhere", "neither", "nor",
    "without", "unless", "never", "cannot"})
NEG_VERBS: Final = frozenset({
    "omit", "lack", "fail", "skip", "avoid", "refuse", "forbid",
    "prevent", "miss"})
PREFIX_RE: Final = re.compile(r"^(un|non)[a-z]{4,}$|^non-[a-z]+$")
SUFFIX_RE: Final = re.compile(r"^[a-z]{3,}less$")
PREFIX_STOP: Final = (
    "under", "unic", "unif", "unio", "unit", "uniq", "univ", "unix",
    "unar", "unpack", "unpick", "until", "uncle", "unwrap", "unwind", "unbind",
    "unregister", "unsubscribe", "unpublish", "unlock", "unzip",
    "unroll", "unset", "unmount", "undo", "unfold", "unmarshal",
    "nonlocal", "nonce", "nonetheless")
"""Words and stems that start with `un` or `non` without negating."""
SUFFIX_STOP: Final = frozenset({
    "unless", "regardless", "nevertheless", "nonetheless"})
CASED_STOP: Final = frozenset({"Stateless"})
"""The library's name, which the suffix test would count."""


class Marker(NamedTuple):
    word: str
    only: bool


class Stat(NamedTuple):
    """One paragraph's count."""

    path: Path
    line: int
    words: tuple[str, ...]
    """Matched words in order, `only` excluded."""
    only: int
    tokens: int
    text: str

    @property
    def total(self) -> int:
        return len(self.words)

    @property
    def rate(self) -> float:
        return self.total / self.tokens if self.tokens else 0.0


def classify(text: str, lemma: str, pos: str, dep: str) -> str | None:
    """`"neg"`, `"only"`, or None for one token."""
    lower = text.lower()
    if dep == "neg" or lower in NEG_WORDS:
        return "neg"
    if pos == "VERB" and lemma in NEG_VERBS:
        return "neg"
    if lower == "non":
        return "neg"
    if PREFIX_RE.match(lower) and not lower.startswith(PREFIX_STOP):
        return "neg"
    if (SUFFIX_RE.match(lower) and lower not in SUFFIX_STOP
            and text not in CASED_STOP):
        return "neg"
    if lower == "only" and pos in ("ADV", "ADJ"):
        return "only"
    return None


def markers(paragraph: Paragraph) -> list[Marker]:
    """Each negation marker of one paragraph, in token order."""
    found: list[Marker] = []
    for sentence in paragraph.sentences:
        for tok in sentence.tokens:
            if tok.punct:
                continue
            kind = classify(tok.text, tok.lemma, tok.pos, tok.dep)
            if kind is not None:
                found.append(Marker(tok.text.lower(), kind == "only"))
    return found


def token_count(paragraph: Paragraph) -> int:
    return sum(1 for s in paragraph.sentences for t in s.tokens
               if not t.punct)


def stat(path: Path, paragraph: Paragraph) -> Stat:
    found = markers(paragraph)
    return Stat(
        path, paragraph.lines[0] if paragraph.lines else 1,
        tuple(m.word for m in found if not m.only),
        sum(1 for m in found if m.only),
        token_count(paragraph), " ".join(paragraph.text.split()))


def word_list(words: tuple[str, ...]) -> str:
    """Words in order of first appearance, repeats as `not x3`."""
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return ", ".join(w if n == 1 else f"{w} x{n}"
                     for w, n in counts.items())


def message(s: Stat) -> str:
    """`[NEG n +k only] word, word x2: text`."""
    extra = f" +{s.only} only" if s.only else ""
    return (f"[NEG {s.total}{extra}] {word_list(s.words)}: "
            f"{s.text[:PREVIEW]}")


def survey(docs: list[Document], parser: Parser = parse,
           ) -> list[list[Stat]]:
    """Per document, a Stat for each paragraph that is not skipped."""
    result: list[list[Stat]] = []
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        result.append([stat(doc.path, p) for p in paras
                       if not skipped(p)])
    return result


def table(per_file: list[list[Stat]], threshold: int) -> list[str]:
    """Rows of (file, paragraphs, listed, per 1000 words), densest first."""
    rows: list[tuple[float, str, int, int]] = []
    for stats in per_file:
        if not stats:
            continue
        negatives = sum(s.total + s.only for s in stats)
        tokens = sum(s.tokens for s in stats)
        rate = negatives / tokens * 1000 if tokens else 0.0
        listed = sum(1 for s in stats if s.total >= threshold)
        rows.append((rate, display(stats[0].path), len(stats), listed))
    rows.sort(key=lambda r: (-r[0], r[1]))
    lines = [f"{'file':<60} {'paras':>6} {'listed':>6} {'per1000':>8}"]
    lines += [f"{name:<60} {n:>6} {listed:>6} {rate:>8.1f}"
              for rate, name, n, listed in rows]
    return lines


def counts(texts: list[str], parser: Parser) -> list[tuple[int, str]]:
    """(negatives without `only`, word list) for each text."""
    docs = [Document.from_text(t, Path(f"calibrate/{n}.md"))
            for n, t in enumerate(texts)]
    out: list[tuple[int, str]] = []
    for paras in parsed(docs, parser, use_cache=False):
        words = tuple(m.word for p in paras for m in markers(p)
                      if not m.only)
        out.append((len(words), word_list(words)))
    return out


EXAMPLES: Final[tuple[tuple[str, str, int, int], ...]] = (
    ("does not remember", "forgets", 1, 0),
    ("reads its argument without changing it",
     "reads its argument and leaves it as it was", 1, 0),
    ("answers Need[Console] and not Need[Clock]",
     "answers Need[Console] and leaves Need[Clock] open", 1, 0),
)
"""The style rule's own pairs: text, repair, expected counts."""
DENSE: Final = ("Nothing objects: not the annotation, not the type "
                "checker, not the running program. Without a guard, "
                "no caller can tell.")


def calibrate(parser: Parser = parse) -> None:
    """Group the edit pairs by whether the rewrite cut negatives."""
    pairs: dict[str, dict[str, str]] = json.loads(
        EDIT_PAIRS.read_text(encoding="utf-8"))
    idents = list(pairs)
    texts = [pairs[i][side] for i in idents for side in ("before", "after")]
    got = counts(texts, parser)
    groups: dict[str, list[str]] = {"FEWER": [], "SAME": [], "MORE": []}
    total_before = total_after = 0
    shown: dict[str, tuple[int, str, int, str]] = {}
    for n, ident in enumerate(idents):
        (b, bw), (a, aw) = got[2 * n], got[2 * n + 1]
        total_before += b
        total_after += a
        shown[ident] = (b, bw, a, aw)
        groups["FEWER" if a < b else "MORE" if a > b else "SAME"].append(
            ident)
    for name, ids in groups.items():
        print(f"== {name} ==")
        for ident in ids:
            b, bw, a, aw = shown[ident]
            print(f"{name}: {ident}")
            print(f"  before ({b}; {bw}): {pairs[ident]['before']}")
            print(f"  after  ({a}; {aw}): {pairs[ident]['after']}")
        print()
    print(f"FEWER {len(groups['FEWER'])}, SAME {len(groups['SAME'])}, "
          f"MORE {len(groups['MORE'])}, of {len(pairs)} pairs; "
          f"negatives before {total_before}, after {total_after}\n")
    print("== built-in examples ==")
    example = counts([t for e in EXAMPLES for t in e[:2]] + [DENSE], parser)
    for n, (text, repair, want_b, want_a) in enumerate(EXAMPLES):
        (b, bw), (a, aw) = example[2 * n], example[2 * n + 1]
        print(f"before {b} (expected {want_b}; {bw or 'none'}): {text}")
        print(f"after  {a} (expected {want_a}; {aw or 'none'}): {repair}")
    n, words = example[-1]
    print(f"dense paragraph: {n} negatives ({words}); lists at the "
          f"default threshold {DEFAULT_THRESHOLD}: "
          f"{n >= DEFAULT_THRESHOLD}")


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                    help="list paragraphs with at least this many "
                         "negatives, without `only` (default 3)")
    ap.add_argument("--top", type=int, default=0, metavar="N",
                    help="print only the N densest paragraphs")
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any paragraph is listed")
    ap.add_argument("--calibrate", action="store_true",
                    help="compare with tools/data/edit_pairs.json and "
                         "run the built-in examples")
    args = ap.parse_args(argv)
    if args.calibrate:
        try:
            calibrate(parser)
        except ParserUnavailable as exc:
            print(f"negation_density: parser unavailable ({exc}); "
                  f"nothing checked", file=sys.stderr)
        return 0
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    try:
        per_file = survey([Document.parse(p) for p in paths], parser)
    except ParserUnavailable as exc:
        print(f"negation_density: parser unavailable ({exc}); "
              f"nothing checked", file=sys.stderr)
        return 0
    listed = [s for stats in per_file for s in stats
              if s.total >= args.threshold]
    if args.top:
        listed.sort(key=lambda s: (-s.total, -s.rate))
        shown = listed[:args.top]
    else:
        shown = sorted(listed, key=lambda s: (display(s.path), s.line))
    for s in shown:
        print(f"survey   {display(s.path)}:{s.line}: {message(s)}")
    print()
    print("\n".join(table(per_file, args.threshold)))
    print()
    files = len({s.path for s in listed})
    print(f"{len(listed)} paragraphs at >= {args.threshold} "
          f"in {files} files")
    return 1 if args.fail and listed else 0


if __name__ == "__main__":
    raise SystemExit(main())
