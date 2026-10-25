#!/usr/bin/env python
"""A cached dependency parse of the book's prose, shared by the checks.

Several report-only checks need a parser (`tools/subject_gap.py`,
`tools/sentence_shapes.py`, and five more), and a whole-book parse takes about 24
seconds, so they share one. `parsed()` reads each document's
paragraphs through the same reader as `tools/stranded_prepositions.py`
(fenced listings, headings, block quotes, tables, HTML, link and
footnote definitions, and `#:` lines are skipped; inline code spans
become the placeholder `CODE`; links keep their text; a paragraph's
lines are joined), parses them, and returns the sentences as typed
records.

The parser is spaCy, run in a throwaway environment: the book pins a
Python that spaCy has no wheel for, so `parse()` writes the paragraph
texts to JSON and starts `tools/spacy_parse.py` under `uv run
--no-project --python 3.12 --with spacy ...` (`PARSER_CMD`). uv caches
that environment, so the first run downloads an interpreter, spaCy, and
the small English model (a minute or so) and later runs start in a few
seconds. When the parser cannot start (no network on a first run, no
`uv`), `parse()` raises `ParserUnavailable` and each check says so and
exits 0, since they are report-only.

The cache is `build/parses/<path with "/" as "__">.json` per document,
holding `{"hash": ..., "paragraphs": [...]}`, where the hash covers the
document's joined paragraph texts. A document whose hash matches is
not parsed again; every paragraph of every other document goes to one
`parse()` call, so a run with a stale cache starts one subprocess. The
cache lives under `build/`, which is derived and gitignored, so
deleting it is always safe. A spaCy or model upgrade does not
invalidate it: delete `build/parses/` after one.

The helpers at the end (`finite()`, `children()`, `subtree()`,
`subject_of()`, `conj_verbs()`, `coordinator()`) read a `Sentence`'s
token table and are shared by the rules.
"""

import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final, NamedTuple
from tools.config import ROOT
from tools.markdown import Document
from tools.stranded_prepositions import display, joined, paragraphs

SPACY_PARSE: Final = Path(__file__).with_name("spacy_parse.py")
SPACY_MODEL: Final = (
    "https://github.com/explosion/spacy-models/releases/download/"
    "en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
)
PARSER_CMD: Final[tuple[str, ...]] = (
    "uv", "run", "--no-project", "--python", "3.12",
    "--with", "spacy>=3.8,<3.9", "--with", "preshed<3.0.14",
    "--with", SPACY_MODEL,
    "python", str(SPACY_PARSE),
)
"""The throwaway environment the spaCy half runs in.

`preshed` is pinned because 3.0.14 (resolved on 2026-10-24) makes
spaCy 3.8.16 fail to load any model on Windows with `OverflowError:
Python int too large to convert to C ssize_t` in
`Tokenizer._flush_specials`; 3.0.13 loads it. The failure reached the
checks as `parser unavailable ...; nothing checked`, an exit 0, so
every spaCy check was silently off. Lift the pin when a `preshed`
release loads the model again.
"""
CACHE_DIR: Path = ROOT / "build" / "parses"
"""Where each document's parse is kept; tests point this at a tmp dir."""

FINITE_TAGS: Final = frozenset({"VBZ", "VBP", "VBD"})
SUBJECT_DEPS: Final = frozenset(
    {"nsubj", "nsubjpass", "csubj", "csubjpass", "expl"})

RawSentence = list[dict[str, Any]]
Parser = Callable[[list[str]], list[list[RawSentence]]]
"""Texts in; per text, its sentences, each a list of token dicts."""


class ParserUnavailable(Exception):
    """The spaCy environment could not start or did not answer."""


class Token(NamedTuple):
    i: int
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    head: int
    idx: int
    punct: bool
    morph: str


class Sentence(NamedTuple):
    tokens: tuple[Token, ...]
    start: int
    end: int
    """Character offsets of the sentence within its paragraph."""


class Paragraph(NamedTuple):
    path: Path
    text: str
    lines: list[int]
    """The 1-based source line of every character of `text`."""
    sentences: tuple[Sentence, ...]


def parse(texts: list[str]) -> list[list[RawSentence]]:
    """Run the spaCy half on these paragraphs; sentences per text."""
    request = json.dumps({"texts": texts})
    try:
        done = subprocess.run(
            list(PARSER_CMD), input=request, capture_output=True,
            text=True, encoding="utf-8", cwd=ROOT, check=False,
        )
    except FileNotFoundError as exc:
        raise ParserUnavailable(f"{PARSER_CMD[0]}: command not found") from exc
    if done.returncode:
        tail = done.stderr.strip().splitlines()[-1:] or ["no output"]
        raise ParserUnavailable(f"exit {done.returncode}: {tail[0]}")
    return json.loads(done.stdout)


def cache_file(path: Path) -> Path:
    """The cache file for a document: its shown path, flattened."""
    flat = re.sub(r"[/:]", "__", display(path).replace("\\", "/"))
    return CACHE_DIR / f"{flat}.json"


def digest(texts: list[str]) -> str:
    """One sha256 over a document's joined paragraph texts."""
    h = hashlib.sha256()
    for text in texts:
        h.update(text.encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def load_cache(path: Path, want: str) -> list[list[RawSentence]] | None:
    """The cached parse when its hash matches, else None."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("hash") != want:
        return None
    return data.get("paragraphs")


def sentence_of(raw: RawSentence) -> Sentence:
    """A typed sentence from the parser's token dicts."""
    tokens = tuple(Token(**tok) for tok in raw)
    if not tokens:
        return Sentence(tokens, 0, 0)
    last = tokens[-1]
    return Sentence(tokens, tokens[0].idx, last.idx + len(last.text))


def parsed(docs: list[Document], parser: Parser = parse,
           use_cache: bool = True) -> list[list[Paragraph]]:
    """Each document's paragraphs with their parsed sentences.

    All uncached paragraphs, across every document, go to one
    `parser` call. `use_cache=False` neither reads nor writes the
    cache, for texts that are not files of the book.
    """
    plans = []
    for doc in docs:
        items = [joined(p) for p in paragraphs(doc)]
        texts = [text for text, _ in items]
        want = digest(texts)
        raw = load_cache(cache_file(doc.path), want) if use_cache else None
        if raw is not None and len(raw) != len(texts):
            raw = None
        plans.append((doc, items, want, raw))
    pending = [text for _, items, _, raw in plans if raw is None
               for text, _ in items]
    answers = parser(pending) if pending else []
    if len(answers) != len(pending):
        raise ParserUnavailable("parser returned the wrong number of texts")
    position = 0
    result: list[list[Paragraph]] = []
    for doc, items, want, raw in plans:
        if raw is None:
            raw = answers[position:position + len(items)]
            position += len(items)
            if use_cache:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache_file(doc.path).write_text(
                    json.dumps({"hash": want, "paragraphs": raw}),
                    encoding="utf-8")
        result.append([
            Paragraph(doc.path, text, lines,
                      tuple(sentence_of(s) for s in sentences))
            for (text, lines), sentences in zip(items, raw, strict=True)
        ])
    return result


def finite(tok: Token, sentence: Sentence) -> bool:
    """Is this token a finite verb, alone or through a finite auxiliary?"""
    if tok.tag in FINITE_TAGS:
        return True
    return any(
        c.dep in ("aux", "auxpass")
        and (c.tag == "MD" or c.tag in FINITE_TAGS)
        for c in children(tok, sentence)
    )


def children(tok: Token, sentence: Sentence) -> list[Token]:
    """The tokens whose head is `tok`, in sentence order."""
    return [t for t in sentence.tokens if t.head == tok.i and t.i != tok.i]


def subtree(tok: Token, sentence: Sentence) -> set[int]:
    """The indexes of `tok` and everything below it."""
    seen = {tok.i}
    todo = [tok]
    while todo:
        for child in children(todo.pop(), sentence):
            if child.i not in seen:
                seen.add(child.i)
                todo.append(child)
    return seen


def subject_of(verb: Token, sentence: Sentence) -> Token | None:
    """The verb's own subject (a clausal or expletive one too), or None."""
    for child in children(verb, sentence):
        if child.dep in SUBJECT_DEPS:
            return child
    return None


def conj_verbs(verb: Token, sentence: Sentence) -> list[Token]:
    """Verbs coordinated with `verb`, following the conj chain."""
    found: list[Token] = []
    todo = [verb]
    while todo:
        for child in children(todo.pop(), sentence):
            if child.dep == "conj" and child.pos in ("VERB", "AUX"):
                found.append(child)
                todo.append(child)
    return found


def coordinator(conj_tok: Token, sentence: Sentence) -> str | None:
    """The lowercase `cc` word joining this conjunct to its head.

    The `cc` normally hangs off the first conjunct, so the search
    walks up the conj chain until it finds one between head and conj.
    """
    tok = conj_tok
    while tok.dep == "conj" and tok.head != tok.i:
        head = sentence.tokens[tok.head]
        for child in children(head, sentence):
            if child.dep == "cc" and head.i < child.i < conj_tok.i:
                return child.text.lower()
        tok = head
    return None
