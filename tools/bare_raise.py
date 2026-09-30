"""Find "raise" used without an object in prose.

The style rule: never write "raise" or "raises" by itself to mean
raising an exception, in any form ("will raise", "raised", "raising").
Write "raises an exception", name the exception ("raises a
`NameError`"), or give the verb some other object ("raising it",
"raising that failure").

A word counts as bare when nothing that could be its object follows it:
the sentence or clause ends ("the call raises."), or the next word is a
preposition or conjunction ("raises when", "raised inside"). Anything
else after it is taken as an object, which lets "raise the limit"
through along with "raise the exception"; the check hunts the missing
object, not the non-exception sense. "raised" after an article is an
adjective ("a raised failure") and is skipped, and so is a verb whose
object comes first ("the exception it raises", "what they raise"),
which `FRONTED` recognizes by the words just before it.

Code spans and fenced listings are never searched. Sentences are joined
across Semantic Line Breaks first, so "raises" at a line end followed by
"a `KeyError`" on the next line is not a hit; the report names the line
the word is on.

Report-only: it prints the hits and exits 0, and no gate runs it.

    uv run python -m tools.bare_raise              # Chapters/ and Solutions/
    uv run python -m tools.bare_raise Chapters/42_Functional--Error_Handling.md
"""

import re
import sys
from collections.abc import Iterator
from pathlib import Path

from tools.check_self_reference import sentences
from tools.config import CHAPTERS_DIR, ROOT
from tools.markdown import Document
from tools.repo import md_files

WORD = re.compile(r"\b(?:re-)?rais(?:e|es|ed|ing)\b", re.IGNORECASE)
CODE_SPAN = re.compile(r"`[^`]+`")
LINK_TARGET = re.compile(r"\]\([^)]*\)|\{#[^}]*\}")
NOT_AN_OBJECT = frozenset("""
    about after again against along at because before but by during
    for from here if in inside instead into on or once so than
    then there through to too under unless until when whenever
    where whether which while with within without and
""".split())
ARTICLES = frozenset({"a", "an", "the"})
FRONTED = frozenset({"exception", "exceptions", "error", "errors",
                     "failure", "failures", "what", "whatever", "`code`"})
"""Words that, within `LOOKBACK` words before the verb, are its object
moved ahead of it: "the exception that call raises", "what they
raise", "every `RuntimeError` an action method might raise"."""
LOOKBACK = 8


def masked(sentence: str) -> str:
    """The sentence with code spans as `CODE` and link targets removed."""
    return CODE_SPAN.sub("`CODE`", LINK_TARGET.sub("]", sentence))


def fronted(before: list[str], word: str) -> bool:
    """Does an object come ahead of the verb in these preceding words?

    Two shapes count. A relative clause sits between the object and the
    verb, with no preposition or conjunction in it ("the exception it
    raises", "what they raise"). Or "raised" follows its noun directly,
    as a participle ("a `TypeError` raised inside"). A code span right
    before any other form is the verb's subject ("`handle()` raises"),
    and "`None` rather than raising" has a conjunction in between.
    """
    words = [w.lower().strip("*_,.;:()") for w in before]
    for i, w in enumerate(words):
        if w not in FRONTED:
            continue
        between = words[i + 1:]
        if not between:
            if word.endswith("raised"):
                return True
        elif not any(b in NOT_AN_OBJECT for b in between):
            return True
    return False


def bare(text: str, m: re.Match[str]) -> bool:
    """Is the raise word at `m` in `text` missing its object?"""
    before = text[:m.start()].split()
    if before and before[-1].lower().strip("*_") in ARTICLES:
        return False
    if fronted(before[-LOOKBACK:], m.group(0).lower()):
        return False
    rest = text[m.end():]
    if not rest.strip() or rest.lstrip()[0] in ".,;:!?)":
        return True
    following = rest.split()[0].lower().strip("*_,.;:")
    return following in NOT_AN_OBJECT


def hits(path: Path) -> Iterator[tuple[int, str]]:
    """(line, text around the word) for each bare raise word in a file."""
    doc = Document.parse(path)
    for first, sentence in sentences(doc):
        text = masked(sentence)
        for m in WORD.finditer(text):
            if bare(text, m):
                around = text[max(0, m.start() - 70):m.end() + 40]
                yield locate(doc, first, m.group(0)), around


def locate(doc: Document, first: int, word: str) -> int:
    """The 1-based line, from `first` on, where `word` appears."""
    for n in range(first, min(first + 20, len(doc.lines) + 1)):
        if re.search(rf"\b{re.escape(word)}\b", doc.lines[n - 1]):
            return n
    return first


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    paths = ([Path(a) for a in args] if args
             else md_files([CHAPTERS_DIR, ROOT / "Solutions"]))
    total = 0
    for path in paths:
        for line, around in hits(path):
            total += 1
            shown = path.resolve().relative_to(ROOT).as_posix()
            print(f"{shown}:{line}: ...{' '.join(around.split())}...")
    print(f"\n{total} bare raise word(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
