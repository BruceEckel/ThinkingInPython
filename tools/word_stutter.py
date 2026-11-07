#!/usr/bin/env python
"""Survey word stutters in prose: a word beside its own code-span form,
and a stem recurring within a few tokens of itself.

Bruce (chapter 45, 2026-11-07) read "The next `next()` links that frame
back into the call stack" and called it awkward: the adjective "next"
and the function `next()` sit side by side, the font is the only thing
separating them, and read aloud the phrase stutters. The scan he then
asked for found two more in the chapter: "`close()` returns the value
the generator returned ... and the call returns", one verb said of
three different things in one sentence, and a paragraph that wrote
"`job`" (the loop variable) in one sentence and "job" (the generator)
in the next. The book-wide sweep that day read 1,311 candidates in 93
files and reworded 56, so the shape is rare and most hits are keeps.
This check is the `stutter` pass's mechanical prefilter
(`.claude/skills/stutter/SKILL.md`), the tenth pass of `super-prose`.

Two shapes, four labels:

- `[CODE!]` and `[CODE]`: a prose word whose stem equals an identifier
  in a code span within WINDOW tokens of it ("the next `next()`", "a
  function that finishes without a `return` returns `None`", "an empty
  set is `set()`"). `[CODE!]` means adjacent or one token apart, the
  strongest form. A code span counts when it is a single identifier,
  a dotted path, or a call (`next()`, `copy.deepcopy()`, `Shape.registry`);
  an expression span (`x + 1`, `yield from`) is skipped, since its
  words are code, not the prose word's double.
- `[STEM~]` and `[STEM=]`: a content word whose stem recurs within
  WINDOW tokens in the same sentence. `~` is two inflections ("returns
  ... returned", "resumes ... resuming"), the shape most often worth
  rewording; `=` is the same form twice ("the generator ... the
  generator"), usually the topic noun named again, which the author's
  antecedents rule prefers to a pronoun.

The scan is mechanical. A sentence boundary stops the window, a link's
text is hidden (its words repeat the target heading on purpose), and a
pair joined by "and", "or", "to", "but", "than", or a preposition is
dropped before it prints ("the yield channel and the return channel",
"one by one"). Stopwords and words under three letters never pair. The
stemmer is a light suffix stripper (plural, -ed, -ing, a doubled final
consonant, a trailing "e"), so "closed" pairs with `close()` and
"hashing" with "hashes"; it does not pair "driver" with "drive".

What the reader decides, from the pass's test: reword when the two
occurrences do different jobs and the repeat makes the reader re-sort
them (a word beside its identifier in another role, one verb with two
subjects, a prose noun and a code variable of one spelling naming
different things); keep a deliberate parallel, the topic noun named
again, a function whose name is the verb it performs in subject
position ("`tg.cancel()` cancels every task"), a definition ("an empty
set is `set()`"), a plural beside its singular doing the distributive
job, and quoted or generated text. The repair uses words the passage
already has: the thing's role ("The call that resumes the generator"),
a second clause, a deletion, or one form, prose or code, for a thing
the paragraph named both ways. Never a synonym for a technical term.

It reads `Chapters/*.md` and `Solutions/*/README.md` prose: fenced
listings, headings, block quotes (the generated exercise quotes),
tables, HTML, link and footnote definitions, and `#:` lines are
skipped; list items, `Hint:` paragraphs, and `Done when:` criteria are
read, since three of the sweep's rewrites were criteria. It keeps no
baseline and is not part of `tip prose`: each hit is a judgment the
pass makes, and a baseline of 1,200 keeps would hide the next real one
behind a re-keying on every edit.

A line reads `survey   path:line: [TAG] word / word: context`, and the
run ends with `N stutter candidates (C code, S stem)`. A run given
paths reads only those files. `--window N` widens the gap: the
`close()` sentence above has four tokens between its "returns" and
"returned", which the default of three misses and `--window 4` lists,
at about a third more candidates over the book.

    uv run python -m tools.word_stutter                  # the book
    uv run python -m tools.word_stutter Chapters/45_*.md
    uv run python -m tools.word_stutter --calibrate      # built-in examples
    uv run tip stutter CH=45
"""

import argparse
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final, NamedTuple
from tools.config import ROOT
from tools.markdown import Document
from tools.prose import (
    BLOCKQUOTE,
    HEADING,
    HTML,
    HTML_COMMENT_CLOSE,
    HTML_COMMENT_OPEN,
    INDENTED_CODE,
    LIST_ITEM,
    TABLE,
)
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.stranded_prepositions import display

WINDOW: Final = 3
"""Tokens allowed between the two members of a pair."""

LINK: Final = re.compile(r"\[([^\]]*)\]\([^)]*\)")
IMAGE: Final = re.compile(r"!\[[^\]]*\]\([^)]*\)")
ATTRS: Final = re.compile(r"\{#[^}]*\}")
FOOTNOTE_REF: Final = re.compile(r"\[\^[^\]]+\]")
FOOTNOTE_DEF: Final = re.compile(r"^\[\^[^\]]+\]:\s*")
LINK_DEF: Final = re.compile(r"^\s*\[[^\]]+\]:\s")
OUTPUT_MARKER: Final = re.compile(r"^\s*#:")
TOKEN: Final = re.compile(
    r"``[^`]+``|`[^`]+`|[A-Za-z][A-Za-z'’-]*|[.!?](?=[\s\"’”)]|$)")
SIMPLE_CODE: Final = re.compile(r"^[A-Za-z_][\w.]*(\(\))?$")
IDENT: Final = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
LINK_TOKEN: Final = "LINKTEXT"

STOP: Final = frozenset("""
the a an of to in on at by for with and or but nor is are was were be been
being it its that this these those as from than then so if not no do does
did has have had which who whom whose what when where why how into onto out
up down over under one two three each every all any some same other another
you your yours we our ours i me my they them their he him his she her can
will would could should may might must shall also both either neither only
more most less least such very there here own just too yet still even ever
about after before between through during without within because while
until once since though although whether per via off like unlike
""".split())
"""Function words and the quantifiers that never form a pair."""

CONNECTIVES: Final = frozenset({
    "and", "or", "to", "by", "than", "versus", "from", "into", "after",
    "before", "but", "nor", "then", "per", "over", "upon", "on", "in",
    "for", "with", "against", "of",
})
"""A word between the members that marks a deliberate pair."""


class Token(NamedTuple):
    kind: str
    """"word", "code", "break" (sentence end), or "link"."""
    text: str
    stems: tuple[str, ...]
    line: int


def stem(word: str) -> str:
    """A light stem: plural, -ed, -ing, and a doubled final consonant."""
    w = word.lower().replace("’", "'")
    w = w.removesuffix("'s").strip("'-")
    if len(w) <= 3:
        return w
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("es") and len(w) > 4 and (
            w[-3] in "sxz" or w[-4:-2] in ("ch", "sh")):
        w = w[:-2]
    elif w.endswith("s") and not w.endswith(("ss", "us")):
        w = w[:-1]
    for suffix in ("ing", "ed"):
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            w = w[:-len(suffix)]
            if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "lsz":
                w = w[:-1]
            break
    return w


def same_stem(a: str, b: str) -> bool:
    """Equal stems, or stems that differ by a trailing "e" (close/clos)."""
    if a == b:
        return True
    return min(len(a), len(b)) >= 4 and (a + "e" == b or b + "e" == a)


def code_idents(span: str) -> tuple[str, ...]:
    """The identifiers in a simple code span, lowercased, dunders stripped."""
    body = span.strip("`").strip()
    if not SIMPLE_CODE.match(body):
        return ()
    return tuple(ident for m in IDENT.finditer(body)
                 if (ident := m.group(0).strip("_").lower()))


def clean(line: str) -> str:
    """One prose line with images gone, links as LINK_TOKEN, attrs gone."""
    line = IMAGE.sub("", line)
    line = LINK.sub(f" {LINK_TOKEN} ", line)
    line = FOOTNOTE_REF.sub("", line)
    return ATTRS.sub("", line)


def paragraphs(doc: Document) -> Iterator[list[tuple[int, str]]]:
    """Each prose paragraph as (1-based line, cleaned text) pairs.

    The reader `tools/stranded_prepositions.py` uses, except that code
    spans stay in the text, since their identifiers are what the
    `[CODE]` shape compares against.
    """
    fenced = doc.in_fence()
    current: list[tuple[int, str]] = []
    in_comment = False
    in_list = False
    for index, line in enumerate(doc.lines):
        number = index + 1
        text: str | None = line
        if fenced[index]:
            text = None
        elif in_comment:
            in_comment = HTML_COMMENT_CLOSE.search(line) is None
            text = None
        elif HTML_COMMENT_OPEN.match(line):
            in_comment = HTML_COMMENT_CLOSE.search(line) is None
            text = None
        elif not line.strip():
            in_list = False
            text = None
        elif (HEADING.match(line) or BLOCKQUOTE.match(line)
              or TABLE.match(line) or HTML.match(line)
              or LINK_DEF.match(line) or OUTPUT_MARKER.match(line)):
            text = None
        elif m := LIST_ITEM.match(line):
            if current:
                yield current
                current = []
            in_list = True
            text = m.group(4)
        elif INDENTED_CODE.match(line) and not (current or in_list):
            text = None
        else:
            text = FOOTNOTE_DEF.sub("", line)
        if text is None:
            if current:
                yield current
                current = []
            continue
        current.append((number, clean(text.strip())))
    if current:
        yield current


def tokens(paragraph: list[tuple[int, str]]) -> list[Token]:
    out: list[Token] = []
    for number, text in paragraph:
        for m in TOKEN.finditer(text):
            t = m.group(0)
            if t in ".!?":
                out.append(Token("break", t, (), number))
            elif t == LINK_TOKEN:
                out.append(Token("link", t, (), number))
            elif t.startswith("`"):
                out.append(Token("code", t, code_idents(t), number))
            else:
                out.append(Token("word", t, (stem(t),), number))
    return out


def context(toks: list[Token], i: int, j: int) -> str:
    lo, hi = max(0, i - 4), min(len(toks), j + 5)
    return " ".join(t.text for t in toks[lo:hi])


def surface(word: str) -> str:
    return word.lower().replace("’", "'").removesuffix("'s")


def pair(toks: list[Token], i: int, j: int) -> str | None:
    """The label for tokens i and j, or None when they do not pair."""
    a, b = toks[i], toks[j]
    if a.kind == "word" and b.kind == "word":
        sa, sb = a.stems[0], b.stems[0]
        if sa in STOP or sb in STOP or len(sa) < 3:
            return None
        if a.text.lower() in STOP or b.text.lower() in STOP:
            return None
        if {t.text.lower() for t in toks[i + 1:j]} & CONNECTIVES:
            return None
        if not same_stem(sa, sb):
            return None
        return "STEM=" if surface(a.text) == surface(b.text) else "STEM~"
    word, code = (a, b) if a.kind == "word" else (b, a)
    if word.kind != "word" or code.kind != "code" or not code.stems:
        return None
    if word.text.lower() in STOP:
        return None
    wstem = word.stems[0]
    for ident in code.stems:
        if same_stem(wstem, ident) or same_stem(wstem, stem(ident)):
            return "CODE!" if j - i <= 2 else "CODE"
    return None


def find(doc: Document, window: int = WINDOW) -> Iterator[Finding]:
    """Every stutter candidate in `doc`, as `[TAG] a / b: context`."""
    for para in paragraphs(doc):
        toks = tokens(para)
        for i, tok in enumerate(toks):
            if tok.kind in ("break", "link"):
                continue
            for j in range(i + 1, min(len(toks), i + window + 2)):
                other = toks[j]
                if other.kind == "break":
                    break
                if other.kind == "link" or (
                        tok.kind == "code" and other.kind == "code"):
                    continue
                label = pair(toks, i, j)
                if label is None:
                    continue
                yield Finding(
                    doc.path, tok.line,
                    f"[{label}] {tok.text} / {other.text}: "
                    f"{context(toks, i, j)}")
                break


EXAMPLES: Final[tuple[tuple[str, bool, int], ...]] = (
    ("The next `next()` links that frame back into the call stack.",
     True, WINDOW),
    ("`close()` returns the value the generator returned while handling "
     "`GeneratorExit`.", False, WINDOW),
    ("`close()` returns the value the generator returned while handling "
     "`GeneratorExit`.", True, 4),
    ("A function that finishes without a `return` returns `None`.",
     True, WINDOW),
    ("The `for` loop primes each `job` and pairs it with its first "
     "request. When a `job` finishes, its `send()` raises "
     "`StopIteration`.", False, WINDOW),
    ("The call that resumes the generator links that frame back into "
     "the call stack.", False, WINDOW),
    ("The yield channel and the return channel end in different places.",
     False, WINDOW),
    ("Calling a generator function creates the generator. The generator "
     "body runs later.", True, WINDOW),
    ("The rat moves one cell at a time, one step per turn.", False, WINDOW),
    ("[Iterators](22_Patterns--Iterators.md) covers iterators in full.",
     False, WINDOW),
)
"""(text, fires, window): the chapter 45 sentences and the keeps.

The `close()` sentence has four tokens between "returns" and
"returned", so the default window misses it and `--window 4` finds it;
the sweep's brief carried it as a worked example instead. The `job`
paragraph does not fire because the two spellings sit in different
sentences; that shape is the pass's to read. The topic-noun example
fires as `[STEM=]`, the tier the pass mostly keeps.
"""


def calibrate() -> int:
    bad = 0
    for text, fires, window in EXAMPLES:
        doc = Document.from_text(text, Path("example.md"))
        hits = [f.message for f in find(doc, window)]
        ok = bool(hits) == fires
        bad += not ok
        mark = "ok  " if ok else "FAIL"
        print(f"{mark} {'fires' if fires else 'quiet'} (window {window}): "
              f"{text}")
        for h in hits:
            print(f"       {h}")
    print(f"{len(EXAMPLES) - bad} of {len(EXAMPLES)} examples as expected")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--window", type=int, default=WINDOW,
                    help=f"tokens allowed between the pair "
                         f"(default {WINDOW})")
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any candidate is found")
    ap.add_argument("--calibrate", action="store_true",
                    help="run the built-in examples")
    args = ap.parse_args(argv)
    if args.calibrate:
        return calibrate()
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    found = sorted(
        {(display(f.path), f.line, f.message)
         for p in paths for f in find(Document.parse(p), args.window)})
    for shown, line, text in found:
        print(f"survey   {shown}:{line}: {text}")
    code = sum(1 for _, _, t in found if t.startswith("[CODE"))
    print(f"{len(found)} stutter candidates ({code} code, "
          f"{len(found) - code} stem)")
    return 1 if args.fail and found else 0


if __name__ == "__main__":
    raise SystemExit(main())
