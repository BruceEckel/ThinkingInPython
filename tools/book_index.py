#!/usr/bin/env python
"""The book's index: a term file, a matcher, and three renderers.

The index is data plus code, never markers in `Chapters/` (INDEXING.md
has the survey and Bruce's decisions of 2026-09-29). The data is
`tools/data/index_terms.toml`, one `[[entry]]` table per entry:

    [[entry]]
    term = "closure"            # the heading as the index shows it
    kind = "concept"            # concept, pattern, python, or pep
    match = ["closure", "closures", "re:enclosing\\s+scope"]
    under = "functions"         # optional: a subentry of that entry
    see = []                    # optional: entry names
    see_also = ["nonlocal"]     # optional: entry names
    code = false                # true sets the heading in code font

A `match` item is a plain string, matched case-insensitively on word
boundaries (a space matches any run of whitespace), or a regular
expression when it starts with `re:`. A `python` entry's items match
case-sensitively, since `Enum` and `enum` name different things. An entry with an empty `match`
and a `see` is a cross-reference alone. The file's top-level `stop`
list names italic spans that are emphasis, not terms ("is", "not");
`tools/index_seed.py` wrote the first version of the file.

Where a match counts depends on the kind:

- `python`: inside inline code spans, in prose and headings, and in
  the lines of Python listings (Decision 2: a listing that uses
  `functools.cache` is a fair locator).
- `pattern`: inside an italic span, since the book italicizes a
  pattern name on every mention (*State*), or in a heading, where the
  name is plain. Either way the match must start with a capital: the
  lowercase word keeps its ordinary sense, so *decorator* in italics
  is Python's construct, not the pattern. A phrase from the `!` lines
  of `tools/data/pattern_names.txt` ("State Machines") never counts.
- `concept` and `pep`: in prose and headings, with code spans, link
  destinations, and HTML tags masked out.

Fenced listings never count for the other three kinds.

Locators follow Decision 2. A chapter is a sequence of paragraphs
(`paragraphs()`): a heading, a run of prose lines, one list item, a
block quote, a table, a figure, or a fenced block. A section is the
text under one `##` or `###` heading, or the chapter's opening text.
An entry gets one locator per section however often the section
mentions it. The locator is principal when the section's own heading
contains the term, or when the section holds a defining occurrence
(a `concept` match that fills an italic span, *closure*). Principal
locators come first and are set bold; the rest follow in book order.
An entry with more than eight locators is a warning.

A locator names the chapter, the section anchor, and the paragraph's
index within the chapter. `BookIndex.inject_anchors()` adds an empty
span, `[]{#ix-12-34}` (chapter 12, paragraph 34), at the start of each
located paragraph, or wraps a located listing or table in a fenced div
carrying that id, since a span cannot sit inside a code block. A
heading needs nothing injected: its own id is the anchor. The
injection runs on the in-memory text inside the builds; `Chapters/`
is never edited. The id comes from the chapter and the paragraph's
position, so it is the same on every build of the same text.

The builds call it from two places: `build_epub.book_markdown()`, the
assembly the EPUB and the PDF share, and `build_site.write_page()`.
Both read a chapter through `build_site.load_chapter()`, and so does
this module, so the paragraph numbers agree. The renderers are here
too: `render_html()` for the site's `book-index.html`,
`render_markdown()` for the EPUB's index chapter and for
`build/index/index.md`, and `render_typst()` for the PDF, whose page
numbers come from typst's `counter(page).at(label)`.

Usage:
    python -m tools.book_index                  # print the counts
    python -m tools.book_index --markdown FILE  # also write the index
    python -m tools.book_index --report         # the term file's health

`--report` lists italic terms with no entry, entries that match
nothing, `see`/`see_also`/`under` targets that name no entry, entries
that differ only by case or plural, and entries over eight locators.
It always exits 0 (Decision 5: reported, not gated).
"""

import argparse
import html
import re
import tomllib
import unicodedata
from bisect import bisect_right
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from tools.config import DATA_DIR, ROOT
from tools.heading_links import ATTR_BLOCK, EXPLICIT_ID, pandoc_anchor
from tools.markdown import Document
from tools.repo import write_text_lf

TERMS_FILE = DATA_DIR / "index_terms.toml"
KINDS = ("concept", "pattern", "python", "pep")
ENTRY_KEYS = frozenset(
    {"term", "match", "under", "see", "see_also", "kind", "code"})
TOP_KEYS = frozenset({"entry", "stop"})
# More locators than this and an entry needs subentries or a tighter
# pattern (INDEXING.md, Decision 2).
MAX_LOCATORS = 8

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)(.*)$")
QUOTE_LEAD = re.compile(r"^((?:\s*>)+ ?)")
TABLE = re.compile(r"^\s*\|")
INDENTED = re.compile(r"^(\t| {4,})\S")
FOOTNOTE_DEF = re.compile(r"^\[\^[^\]]+\]:")
FIGURE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?\s*\\?\s*$")
COMMENT_OPEN = re.compile(r"^\s*<!--")
COMMENT_CLOSE = re.compile(r"-->")
# Masked out of the prose channel: code spans, link destinations,
# attribute blocks, footnote markers, and HTML tags.
CODE_SPAN = re.compile(r"``[^`]*``|`[^`]*`")
WORD = re.compile(r"\w+")
PROSE_MASK = re.compile(
    r"``[^`]*``|`[^`]*`|\]\([^)]*\)|\{[#.][^}]*\}"
    r"|\[\^[^\]]+\]|<[^>]+>")
# One `*italic*` span, never `**bold**`. Group 1 is the text inside.
ITALIC = re.compile(
    r"(?<![*\w\\])\*(?![\s*])(.+?)(?<![\s*\\])\*(?![*\w])")

# The paragraph kinds. A heading carries its own id; these take an
# injected span at the start of their first line; these are wrapped
# in a fenced div; and these are never located.
SPAN_KINDS = frozenset({"prose", "item", "quote", "cont"})
DIV_KINDS = frozenset({"listing", "table"})
SILENT_KINDS = frozenset({"figure", "footnote", "skip"})


class TermFileError(ValueError):
    """The term file cannot be read as an index."""


# --------------------------------------------------------------------------- #
# The term file
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Term:
    """One `[[entry]]` table from the term file."""

    term: str
    kind: str
    match: tuple[str, ...] = ()
    under: str | None = None
    see: tuple[str, ...] = ()
    see_also: tuple[str, ...] = ()
    code: bool = False

    def patterns(self) -> list[re.Pattern[str]]:
        return [compile_match(m, self.kind != "python")
                for m in self.match]


@dataclass(frozen=True)
class TermFile:
    entries: tuple[Term, ...]
    stop: frozenset[str] = frozenset()


@cache
def compile_match(item: str, fold: bool = True) -> re.Pattern[str]:
    """One `match` item as a regular expression.

    A plain string matches on word boundaries, with each space standing
    for any run of whitespace, since prose lines are joined before
    matching. `re:` hands the rest to `re` as written. Both ignore case
    unless `fold` is false, which `python` entries pass: `Enum` and
    `enum` are different names.
    """
    flags = re.IGNORECASE if fold else 0
    if item.startswith("re:"):
        return re.compile(item[3:], flags)
    words = r"\s+".join(re.escape(w) for w in item.split())
    return re.compile(rf"(?<!\w){words}(?!\w)", flags)


def _strings(value: object, where: str, key: str) -> tuple[str, ...]:
    """`value` as a tuple of strings; a lone string is a list of one."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not all(
            isinstance(v, str) and v for v in value):
        raise TermFileError(
            f"{where}: `{key}` must be a list of non-empty strings")
    return tuple(value)


def parse_terms(text: str, source: str = "index_terms.toml") -> TermFile:
    """Read the term file's TOML, raising `TermFileError` on any fault.

    The faults: TOML that does not parse, an unknown key, a missing or
    duplicate `term`, an unknown `kind`, a `match` or `see` that is not
    a list of strings, a `code` that is not a boolean, and a `re:`
    pattern that does not compile. Each message names the entry.
    """
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise TermFileError(f"{source}: {e}") from e
    extra = set(data) - TOP_KEYS
    if extra:
        raise TermFileError(
            f"{source}: unknown top-level key(s): {', '.join(sorted(extra))}")
    stop = _strings(data.get("stop", []), source, "stop")
    tables = data.get("entry", [])
    if not isinstance(tables, list):
        raise TermFileError(f"{source}: `entry` must be [[entry]] tables")
    entries: list[Term] = []
    seen: set[str] = set()
    for n, table in enumerate(tables, 1):
        where = f"{source}: entry {n}"
        if not isinstance(table, dict):
            raise TermFileError(f"{where}: not a table")
        name = table.get("term")
        if not isinstance(name, str) or not name.strip():
            raise TermFileError(f"{where}: missing `term`")
        where = f"{source}: entry {n} ({name!r})"
        unknown = set(table) - ENTRY_KEYS
        if unknown:
            raise TermFileError(
                f"{where}: unknown key(s): {', '.join(sorted(unknown))}")
        if name in seen:
            raise TermFileError(f"{where}: duplicate term")
        seen.add(name)
        kind = table.get("kind", "concept")
        if kind not in KINDS:
            raise TermFileError(
                f"{where}: kind must be one of {', '.join(KINDS)}, "
                f"not {kind!r}")
        code = table.get("code", False)
        if not isinstance(code, bool):
            raise TermFileError(f"{where}: `code` must be true or false")
        under = table.get("under")
        if under is not None and not (isinstance(under, str) and under):
            raise TermFileError(f"{where}: `under` must be an entry name")
        match = _strings(table.get("match", []), where, "match")
        for item in match:
            if item.startswith("re:"):
                try:
                    re.compile(item[3:])
                except re.error as e:
                    raise TermFileError(
                        f"{where}: bad regex {item!r}: {e}") from e
        entries.append(Term(
            term=name, kind=kind, match=match, under=under,
            see=_strings(table.get("see", []), where, "see"),
            see_also=_strings(table.get("see_also", []), where,
                              "see_also"),
            code=code))
    return TermFile(tuple(entries), frozenset(s.lower() for s in stop))


def load_terms(path: Path | None = None) -> TermFile:
    """The term file at `path`, `TERMS_FILE` by default."""
    path = TERMS_FILE if path is None else path
    if not path.exists():
        raise TermFileError(f"{path}: no term file")
    return parse_terms(path.read_text(encoding="utf-8"), path.name)


# --------------------------------------------------------------------------- #
# Paragraphs
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Unit:
    """One paragraph of a chapter: lines `first` through `last`."""

    index: int
    kind: str
    first: int
    last: int
    level: int = 0      # a heading's level, 0 for everything else
    anchor: str = ""    # a heading's id, as pandoc assigns it
    title: str = ""     # a heading's text, attribute block removed
    python: bool = False  # a listing fenced as Python


def paragraphs(text: str) -> list[Unit]:
    """The chapter body's paragraphs, in order.

    A heading is one paragraph, and so is a fenced block, a table, a
    figure, a block quote, and each list item; any other run of
    non-blank lines is a prose paragraph. An indented run following a
    list item continues it (`cont`). One following a footnote
    definition belongs to the footnote, which is never located: a
    footnote prints where its marker is, so a locator inside one names
    the wrong place. An indented run following anything else is
    indented code (`skip`), never located either, like an HTML comment.
    Heading ids follow pandoc, numbered within the chapter as
    `build_epub.heading_ids()` numbers them.
    """
    lines = text.split("\n")
    doc = Document.from_text(text)
    opens = {b.open_at: b for b in doc.blocks}
    units: list[Unit] = []
    counts: dict[str, int] = {}
    # What an indented run continues: "item", "footnote", or "".
    context = ""
    i, n = 0, len(lines)

    def add(kind: str, first: int, last: int, **extra) -> None:
        units.append(Unit(len(units), kind, first, last, **extra))

    while i < n:
        line = lines[i]
        if i in opens:
            block = opens[i]
            last = min(block.end, n - 1)
            nested = bool(context) and line[:1].isspace()
            if nested and context == "footnote":
                add("footnote", i, last)
            else:
                add("listing", i, last, python=block.is_python)
            context = context if nested else ""
            i = last + 1
            continue
        if not line.strip():
            i += 1
            continue
        m = HEADING.match(line)
        if m:
            raw = m.group(2)
            explicit = EXPLICIT_ID.search(raw)
            title = ATTR_BLOCK.sub("", raw).rstrip()
            if explicit:
                anchor = explicit.group(1)
            else:
                base = pandoc_anchor(title)
                k = counts.get(base, 0)
                if base:
                    counts[base] = k + 1
                anchor = base if k == 0 or not base else f"{base}-{k}"
            add("heading", i, i, level=len(m.group(1)), anchor=anchor,
                title=title)
            context = ""
            i += 1
            continue
        if COMMENT_OPEN.match(line):
            j = i
            while j < n - 1 and not COMMENT_CLOSE.search(lines[j]):
                j += 1
            add("skip", i, j)
            i = j + 1
            continue
        table = bool(TABLE.match(line))
        j = i + 1
        while (j < n and lines[j].strip() and j not in opens
               and not HEADING.match(lines[j])
               and (table or not LIST_ITEM.match(lines[j]))):
            j += 1
        if FOOTNOTE_DEF.match(line):
            kind = "footnote"
        elif LIST_ITEM.match(line):
            kind = "item"
        elif QUOTE_LEAD.match(line):
            kind = "quote"
        elif table:
            kind = "table"
        elif j == i + 1 and FIGURE.match(line):
            kind = "figure"
        elif INDENTED.match(line):
            kind = {"item": "cont", "footnote": "footnote"}.get(
                context, "skip")
        else:
            kind = "prose"
        add(kind, i, j - 1)
        if kind in ("item", "footnote"):
            context = kind
        elif kind != "cont":
            context = ""
        i = j
    return units


def unit_channels(unit: Unit, lines: list[str]) -> tuple[str, str]:
    """(prose, code): the text each kind of entry is matched against.

    The prose channel is the paragraph's lines joined with spaces, with
    code spans and other markup blanked to spaces of the same width, so
    offsets stay put. The code channel keeps only the code spans'
    contents, or a Python listing's lines.
    """
    if unit.kind == "listing":
        if not unit.python:
            return "", ""
        return "", "\n".join(lines[unit.first + 1:unit.last])
    if unit.kind in SILENT_KINDS:
        return "", ""
    if unit.kind == "heading":
        raw = unit.title
    else:
        raw = " ".join(lines[unit.first:unit.last + 1])
    prose = PROSE_MASK.sub(lambda m: " " * len(m.group(0)), raw)
    code = [" "] * len(raw)
    for m in CODE_SPAN.finditer(raw):
        ticks = 2 if m.group(0).startswith("``") else 1
        start, end = m.start() + ticks, m.end() - ticks
        code[start:end] = raw[start:end]
    return prose, "".join(code)


# --------------------------------------------------------------------------- #
# The book as text the matcher searches
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ChapterSource:
    """A chapter as the builds read it: `load_chapter()`'s body."""

    stem: str
    number: str
    title: str
    body: str


@dataclass(frozen=True)
class Place:
    """Where one paragraph sits: its chapter, section, and itself."""

    chapter: int     # index into Corpus.chapters
    unit: Unit
    section: Unit | None  # the H2/H3 heading over it, None if none


class Channel:
    """Every paragraph's text in one channel, joined for fast search.

    A plain `match` item is found through a word index rather than a
    scan: its first word's occurrences are the only places it can
    start, so the pattern is tried there alone. A regex that opens with
    a lookbehind defeats the `re` module's literal-prefix search, and
    one scan of the whole book per entry made the matcher take tens of
    seconds.
    """

    def __init__(self, texts: list[str]) -> None:
        self.starts: list[int] = []
        parts: list[str] = []
        pos = 0
        for text in texts:
            self.starts.append(pos)
            parts.append(text)
            pos += len(text) + 1
        self.text = "\n".join(parts)
        self._words: dict[str, list[int]] | None = None

    def at(self, pos: int) -> int:
        """The paragraph holding offset `pos`."""
        return bisect_right(self.starts, pos) - 1

    def words(self) -> dict[str, list[int]]:
        """Each word's start offsets, keyed by the word in lowercase."""
        if self._words is None:
            found: dict[str, list[int]] = defaultdict(list)
            for m in WORD.finditer(self.text):
                found[m.group(0).lower()].append(m.start())
            self._words = dict(found)
        return self._words

    def finditer(self, item: str,
                 pattern: re.Pattern[str]) -> Iterator[re.Match[str]]:
        """The matches of `pattern`, compiled from `match` item `item`."""
        first = WORD.match(item)
        if item.startswith("re:") or first is None:
            yield from pattern.finditer(self.text)
            return
        for pos in self.words().get(first.group(0).lower(), ()):
            m = pattern.match(self.text, pos)
            if m is not None:
                yield m


def _spans_in(spans: list[tuple[int, int]], starts: list[int],
              lo: int, hi: int) -> tuple[int, int] | None:
    """The span in `spans` (sorted, disjoint) that holds lo..hi."""
    k = bisect_right(starts, lo) - 1
    if k >= 0 and spans[k][0] <= lo and hi <= spans[k][1]:
        return spans[k]
    return None


class Corpus:
    """The chapters, split into paragraphs and joined into channels."""

    def __init__(self, chapters: Iterable[ChapterSource],
                 excluded: Iterable[str] = ()) -> None:
        self.chapters = list(chapters)
        self.places: list[Place] = []
        self.units: dict[str, list[Unit]] = {}
        prose: list[str] = []
        code: list[str] = []
        for c, ch in enumerate(self.chapters):
            lines = ch.body.split("\n")
            units = paragraphs(ch.body)
            self.units[ch.stem] = units
            section: Unit | None = None
            for unit in units:
                if unit.kind == "heading" and unit.level <= 3:
                    section = unit
                self.places.append(Place(c, unit, section))
                p, k = unit_channels(unit, lines)
                prose.append(p)
                code.append(k)
        self.prose = Channel(prose)
        self.code = Channel(code)
        # Italic spans (the text inside the asterisks, trimmed) and the
        # excluded pattern phrases, both as offsets into the prose.
        self.italics: list[tuple[int, int]] = []
        for m in ITALIC.finditer(self.prose.text):
            inner = m.group(1)
            lead = len(inner) - len(inner.lstrip())
            self.italics.append(
                (m.start(1) + lead, m.start(1) + len(inner.rstrip())))
        self.italic_starts = [s for s, _ in self.italics]
        blocked: list[tuple[int, int]] = []
        for phrase in excluded:
            words = r"\s+".join(re.escape(w) for w in phrase.split())
            blocked += [(m.start(), m.end()) for m in
                        re.finditer(words, self.prose.text)]
        self.blocked = sorted(blocked)
        self.blocked_starts = [s for s, _ in self.blocked]

    def italic_at(self, lo: int, hi: int) -> tuple[int, int] | None:
        return _spans_in(self.italics, self.italic_starts, lo, hi)

    def is_blocked(self, lo: int, hi: int) -> bool:
        return _spans_in(self.blocked, self.blocked_starts, lo, hi) \
            is not None


# --------------------------------------------------------------------------- #
# Locators
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Locator:
    """One section where an entry is found."""

    stem: str
    number: str
    chapter_title: str
    section: str          # the section's anchor, "" for the opening
    section_title: str    # its heading text, "" for the opening
    paragraph: int        # the located paragraph's index in the chapter
    principal: bool
    heading_anchor: str = ""  # set when the paragraph is a heading

    @property
    def ix(self) -> str:
        """The injected id: chapter and paragraph, `ix-12-34`."""
        return f"ix-{self.number}-{self.paragraph}"

    @property
    def anchor(self) -> str:
        """The id a link to this locator targets within its chapter:
        the heading's own id, or the injected one."""
        return self.heading_anchor or self.ix


@dataclass
class Entry:
    term: Term
    locators: list[Locator] = field(default_factory=list)
    children: list[Entry] = field(default_factory=list)

    @property
    def code(self) -> bool:
        return self.term.code or self.term.kind == "python"


@dataclass(frozen=True)
class Mention:
    place: int
    defining: bool


def find_mentions(term: Term, corpus: Corpus) -> list[Mention]:
    """Every paragraph that mentions `term`, by the kind's rules."""
    channel = corpus.code if term.kind == "python" else corpus.prose
    found: dict[int, bool] = {}
    for item, pattern in zip(term.match, term.patterns()):
        for m in channel.finditer(item, pattern):
            if m.end() == m.start():
                continue
            place = channel.at(m.start())
            unit = corpus.places[place].unit
            defining = False
            if term.kind == "pattern":
                if (corpus.is_blocked(m.start(), m.end())
                        or not m.group(0)[:1].isupper()):
                    continue
                if (unit.kind != "heading"
                        and corpus.italic_at(m.start(), m.end()) is None):
                    continue
            elif term.kind == "concept":
                span = corpus.italic_at(m.start(), m.end())
                defining = span == (m.start(), m.end())
            found[place] = found.get(place, False) or defining
    return [Mention(p, d) for p, d in sorted(found.items())]


def locate(term: Term, corpus: Corpus) -> list[Locator]:
    """The entry's locators: one per section, principal ones first."""
    by_section: dict[tuple[int, int], list[Mention]] = defaultdict(list)
    for mention in find_mentions(term, corpus):
        place = corpus.places[mention.place]
        key = (place.chapter,
               -1 if place.section is None else place.section.index)
        by_section[key].append(mention)
    principal: list[Locator] = []
    rest: list[Locator] = []
    for (c, _), mentions in sorted(by_section.items()):
        ch = corpus.chapters[c]
        places = [corpus.places[m.place] for m in mentions]
        section = places[0].section
        heading = next((p for p in places
                        if section is not None and p.unit is section),
                       None)
        defining = next((p for m, p in zip(mentions, places)
                         if m.defining), None)
        if heading is not None:
            chosen, is_principal = heading, True
        elif defining is not None:
            chosen, is_principal = defining, True
        else:
            chosen = next((p for p in places
                           if p.unit.kind != "listing"), places[0])
            is_principal = False
        locator = Locator(
            stem=ch.stem, number=ch.number, chapter_title=ch.title,
            section="" if section is None else section.anchor,
            section_title="" if section is None else section.title,
            paragraph=chosen.unit.index, principal=is_principal,
            heading_anchor=(chosen.unit.anchor
                            if chosen.unit.kind == "heading" else ""))
        (principal if is_principal else rest).append(locator)
    return principal + rest


# --------------------------------------------------------------------------- #
# The index
# --------------------------------------------------------------------------- #
def bare_name(term: str) -> str:
    """The text a heading sorts by: no `()`, no leading `_`, `@`, `*`,
    or `.`, so `__init__()` files under I and `@dataclass` under D."""
    bare = term.strip("`").strip()
    bare = bare.removesuffix("()")
    return bare.lstrip("_@*.~ ") or bare


def sort_key(term: str) -> tuple[tuple[int, int, str], ...]:
    """Case-insensitive, accent-blind, numbers in numeric order (PEP 8
    before PEP 484)."""
    folded = unicodedata.normalize("NFKD", bare_name(term))
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    parts = re.findall(r"\d+|\D+", folded.lower())
    key = tuple((0, int(p), "") if p.isdigit() else (1, 0, p)
                for p in parts)
    return (*key, (2, 0, term))


def letter(term: str) -> str:
    """The letter group: A to Z, or `#` for anything else."""
    first = sort_key(term)[0]
    ch = first[2][:1].upper() if first[0] == 1 else ""
    return ch if "A" <= ch <= "Z" else "#"


@dataclass
class BookIndex:
    """The computed index: entries with locators, and what was found."""

    entries: list[Entry]                # top level, sorted
    by_term: dict[str, Entry]
    stop: frozenset[str]
    corpus: Corpus
    warnings: list[str] = field(default_factory=list)
    # Per chapter stem, paragraph index to the id injected there.
    located: dict[str, dict[int, str]] = field(default_factory=dict)

    def all_entries(self) -> list[Entry]:
        out: list[Entry] = []

        def walk(entries: list[Entry]) -> None:
            for e in entries:
                out.append(e)
                walk(e.children)
        walk(self.entries)
        return out

    def inject_anchors(self, text: str, chapter: str) -> str:
        """`text` (chapter stem `chapter`) with an id at each located
        paragraph.

        A prose paragraph, list item, or block quote gets an empty span
        at the start of its text; a listing or table is wrapped in a
        fenced div with the id, since pandoc drops ids on code blocks
        in the typst writer and a span cannot sit inside one. `text`
        must be the body this index was built from (`load_chapter()`'s),
        or the paragraph numbers would point at other paragraphs, so a
        different paragraph count raises a `ValueError`.
        """
        want = self.located.get(chapter)
        if not want:
            return text
        units = paragraphs(text)
        expected = self.corpus.units.get(chapter, [])
        if len(units) != len(expected):
            raise ValueError(
                f"{chapter}: {len(units)} paragraphs, but the index was "
                f"built from {len(expected)}")
        lines = text.split("\n")
        starts = {u.first: u for u in units if u.index in want}
        out: list[str] = []
        i = 0
        while i < len(lines):
            unit = starts.get(i)
            if unit is None:
                out.append(lines[i])
                i += 1
                continue
            ix = want[unit.index]
            line = lines[i]
            if unit.kind in DIV_KINDS:
                indent = line[:len(line) - len(line.lstrip())]
                out += ["", f"{indent}::: {{#{ix}}}", ""]
                out += lines[unit.first:unit.last + 1]
                out += ["", f"{indent}:::", ""]
                i = unit.last + 1
                continue
            span = f"[]{{#{ix}}}"
            if unit.kind == "item" and (m := LIST_ITEM.match(line)):
                line = (m.group(1) + m.group(2) + m.group(3)
                        + span + m.group(4))
            elif unit.kind == "quote" and (m := QUOTE_LEAD.match(line)):
                line = m.group(1) + span + line[m.end():]
            else:
                stripped = line.lstrip()
                line = line[:len(line) - len(stripped)] + span + stripped
            out.append(line)
            i += 1
        return "\n".join(out)


def build_index(chapters: Iterable[ChapterSource],
                terms: TermFile | None = None,
                excluded: Iterable[str] | None = None) -> BookIndex:
    """Match every entry against the chapters and nest the subentries.

    `excluded` defaults to the `!` phrases of pattern_names.txt.
    """
    if terms is None:
        terms = load_terms()
    if excluded is None:
        from tools.pattern_names import default_names, split_names
        excluded = split_names(default_names())[1]
    corpus = Corpus(chapters, excluded)
    by_term: dict[str, Entry] = {}
    for term in terms.entries:
        by_term[term.term] = Entry(term, locate(term, corpus))
    top: list[Entry] = []
    for entry in by_term.values():
        parent = by_term.get(entry.term.under or "")
        if parent is None or parent is entry:
            top.append(entry)
        else:
            parent.children.append(entry)
    for entry in by_term.values():
        entry.children.sort(key=lambda e: sort_key(e.term.term))
    top.sort(key=lambda e: sort_key(e.term.term))
    index = BookIndex(top, by_term, terms.stop, corpus)
    for entry in by_term.values():
        if len(entry.locators) > MAX_LOCATORS:
            index.warnings.append(
                f"{entry.term.term}: {len(entry.locators)} locators "
                f"(over {MAX_LOCATORS}; add subentries or tighten "
                "`match`)")
        for loc in entry.locators:
            if not loc.heading_anchor:
                index.located.setdefault(loc.stem, {})[loc.paragraph] = \
                    loc.ix
    return index


def book_chapters(chapters: Iterable | None = None
                  ) -> list[ChapterSource]:
    """The book's chapters as `build_site.load_chapter()` reads them.

    `chapters` is `build_site.discover()`'s list, found here when not
    given. Imported late: build_site imports this module.
    """
    from tools import build_site
    found = build_site.discover() if chapters is None else chapters
    out: list[ChapterSource] = []
    for ch in found:
        _, body = build_site.load_chapter(ch.md)
        title = ATTR_BLOCK.sub("", ch.title).rstrip()
        out.append(ChapterSource(ch.md.stem, ch.number, title, body))
    return out


def book_index(chapters: Iterable | None = None) -> BookIndex:
    """The index of `Chapters/` from the committed term file."""
    return build_index(book_chapters(chapters))


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
# A function from a locator to the link that reaches it in one output.
type Href = Callable[[Locator], str]


def chapter_label(loc: Locator) -> str:
    """"12 Data Classes as Types", as the contents page numbers it."""
    return f"{loc.number} {loc.chapter_title}"


def site_href(loc: Locator) -> str:
    """The site: one page per chapter, ids as the page carries them."""
    return f"{loc.stem}.html#{loc.anchor}"


def book_href(loc: Locator) -> str:
    """The EPUB and PDF: one document, every heading id namespaced by
    chapter (`build_epub.namespace_headings()`); the injected ids carry
    the chapter already."""
    if loc.heading_anchor:
        return f"#ch{loc.number}-{loc.heading_anchor}"
    return f"#{loc.ix}"


def source_href(loc: Locator) -> str:
    """`build/index/index.md`: the chapter file and section, since the
    injected ids exist only inside the builds."""
    target = f"../../Chapters/{loc.stem}.md"
    return f"{target}#{loc.section}" if loc.section else target


def _see_targets(index: BookIndex, names: tuple[str, ...]
                 ) -> list[tuple[str, bool]]:
    out = []
    for name in names:
        entry = index.by_term.get(name)
        out.append((name, entry.code if entry else False))
    return out


def letters(index: BookIndex) -> list[tuple[str, list[Entry]]]:
    groups: dict[str, list[Entry]] = defaultdict(list)
    for entry in index.entries:
        groups[letter(entry.term.term)].append(entry)
    order = sorted(groups, key=lambda g: (g != "#", g))
    return [(g, groups[g]) for g in order]


def _letter_id(group: str) -> str:
    return "ix-letter-" + ("symbols" if group == "#" else group.lower())


# ---- Site ----------------------------------------------------------------- #
INLINE_CODE_HTML = re.compile(r"`([^`]*)`")
MD_LINK_TEXT = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def inline_html(md: str) -> str:
    """A heading's Markdown as HTML: code spans kept, links and
    emphasis reduced to their text."""
    md = MD_LINK_TEXT.sub(r"\1", md)
    parts = INLINE_CODE_HTML.split(md)
    out = []
    for k, part in enumerate(parts):
        if k % 2:
            out.append(f"<code>{html.escape(part)}</code>")
        else:
            out.append(html.escape(part.replace("*", "")))
    return "".join(out)


def _term_html(name: str, code: bool) -> str:
    text = html.escape(name)
    return f"<code>{text}</code>" if code else text


def _entry_html(entry: Entry, index: BookIndex, href: Href,
                depth: int) -> list[str]:
    links = []
    for loc in entry.locators:
        label = html.escape(chapter_label(loc))
        if loc.section_title:
            label += f", <em>{inline_html(loc.section_title)}</em>"
        link = f'<a href="{html.escape(href(loc))}">{label}</a>'
        links.append(f"<strong>{link}</strong>" if loc.principal else link)
    body = _term_html(entry.term.term, entry.code)
    if links:
        body += ": " + "; ".join(links)
    for word, names in (("see", entry.term.see),
                        ("see also", entry.term.see_also)):
        if names:
            targets = ", ".join(_term_html(n, c) for n, c in
                                _see_targets(index, names))
            body += f"; <em>{word}</em> {targets}"
    out = [f'<li class="ix-entry ix-depth-{depth}">{body}</li>']
    for child in entry.children:
        out += _entry_html(child, index, href, depth + 1)
    return out


INDEX_PAGE_CSS = """\
.ix-letters { display: flex; flex-wrap: wrap; gap: 0.3rem 0.7rem;
  margin: 1.5rem 0 2rem; font-family: 'Cormorant SC', serif;
  font-size: 1.05rem; letter-spacing: 0.08em; }
.ix-letters a { color: var(--ink); text-decoration: none; }
.ix-letters a:hover { color: var(--accent); }
.ix-group { margin-top: 2rem; }
.ix-group h2 { font-family: 'Cormorant SC', serif; font-size: 1.5rem;
  letter-spacing: 0.12em; color: var(--accent);
  border-bottom: 1px solid var(--rule); margin-bottom: 0.6rem; }
.ix-list { list-style: none; padding: 0; margin: 0; }
.ix-entry { padding-left: 1.5rem; text-indent: -1.5rem;
  line-height: 1.5; margin: 0.25rem 0; }
.ix-entry.ix-depth-1 { padding-left: 3rem; }
.ix-entry.ix-depth-2 { padding-left: 4.5rem; }
.ix-entry a { color: var(--ink); text-decoration: none;
  border-bottom: 1px solid var(--rule); }
.ix-entry a:hover { color: var(--accent); border-color: var(--accent); }
.ix-entry code { font-size: 0.85em; }
"""


def render_html(index: BookIndex, href: Href = site_href) -> str:
    """The site's index page body: a letter bar, then one list per
    letter. Raw HTML, which build_site.py hands to pandoc in a raw
    block so the template supplies the page around it."""
    groups = letters(index)
    bar = " ".join(f'<a href="#{_letter_id(g)}">{html.escape(g)}</a>'
                   for g, _ in groups)
    out = [f"<style>\n{INDEX_PAGE_CSS}</style>",
           f'<nav class="ix-letters" aria-label="Index letters">{bar}</nav>']
    for group, entries in groups:
        out.append(f'<section class="ix-group" id="{_letter_id(group)}">')
        out.append(f"<h2>{html.escape(group)}</h2>")
        out.append('<ul class="ix-list">')
        for entry in entries:
            out += _entry_html(entry, index, href, 0)
        out.append("</ul>")
        out.append("</section>")
    return "\n".join(out)


# ---- Markdown (EPUB, and build/index/index.md) ---------------------------- #
MD_SPECIAL = re.compile(r"([\\`*_\[\]<>#])")


def _term_md(name: str, code: bool) -> str:
    if code:
        fence = "``" if "`" in name else "`"
        return f"{fence}{name}{fence}"
    return MD_SPECIAL.sub(r"\\\1", name)


def _section_md(title: str) -> str:
    """A heading's Markdown inside link text set in italics: links
    and emphasis reduced to text, code spans kept."""
    title = MD_LINK_TEXT.sub(r"\1", title)
    parts = re.split(r"(`[^`]*`)", title)
    return "".join(p if k % 2 else p.replace("*", "")
                   for k, p in enumerate(parts))


def _entry_md(entry: Entry, index: BookIndex, href: Href,
              depth: int) -> list[str]:
    links = []
    for loc in entry.locators:
        label = chapter_label(loc)
        if loc.section_title:
            label += f", *{_section_md(loc.section_title)}*"
        link = f"[{label}]({href(loc)})"
        links.append(f"**{link}**" if loc.principal else link)
    body = _term_md(entry.term.term, entry.code)
    if links:
        body += ": " + "; ".join(links)
    for word, names in (("see", entry.term.see),
                        ("see also", entry.term.see_also)):
        if names:
            targets = ", ".join(_term_md(n, c) for n, c in
                                _see_targets(index, names))
            body += f"; *{word}* {targets}"
    out = [f"{'  ' * depth}- {body}"]
    for child in entry.children:
        out += _entry_md(child, index, href, depth + 1)
    return out


def render_markdown(index: BookIndex, href: Href = book_href,
                    heading: str = "# Index {#book-index}") -> str:
    """The index as a Markdown chapter: `heading`, a letter bar, then
    one unlisted section per letter, each a nested list of entries.

    The EPUB passes a heading with `epub:type=index` and the default
    `href`; `tip index` passes `source_href`, whose links reach the
    chapter files.
    """
    groups = letters(index)
    bar = " · ".join(f"[{'\\#' if g == '#' else g}](#{_letter_id(g)})"
                     for g, _ in groups)
    out = [heading, "", "::: {.book-index}", "", bar, ""]
    for group, entries in groups:
        name = "\\#" if group == "#" else group
        out += [f"## {name} {{#{_letter_id(group)} .unlisted}}", ""]
        for entry in entries:
            out += _entry_md(entry, index, href, 0)
        out.append("")
    out += [":::", ""]
    return "\n".join(out)


# ---- Typst (PDF) ---------------------------------------------------------- #
# The PDF's index chapter: raw typst after a level-1 "Index" heading.
# `ixpages` looks up each locator's page with counter(page).at(label),
# the lookup INDEXING.md's survey tested, then sorts the pages, keeps
# one per page (bold wins), and joins a run of consecutive non-bold
# pages into a range, "212–214", linked to its first page.
TYPST_PREAMBLE = """\
#let ixpages(..locs) = context {
  let found = (:)
  for (l, b) in locs.pos() {
    let p = counter(page).at(l).first()
    let k = str(p)
    if k in found {
      if b { found.insert(k, (l, true, p)) }
    } else { found.insert(k, (l, b, p)) }
  }
  let items = found.values().sorted(key: it => it.at(2))
  let out = ()
  let i = 0
  while i < items.len() {
    let (l, b, p) = items.at(i)
    let j = i
    if not b {
      while (j + 1 < items.len() and not items.at(j + 1).at(1)
             and items.at(j + 1).at(2) == items.at(j).at(2) + 1) {
        j += 1
      }
    }
    let shown = if j > i {
      str(p) + "–" + str(items.at(j).at(2))
    } else { str(p) }
    out.push(link(l, if b { strong(shown) } else { shown }))
    i = j + 1
  }
  out.join(", ")
}
#let ixname(t, code) = if code { raw(t) } else { t }
#let ixsee(word, names) = if names.len() > 0 {
  [; #emph(word) ]
  names.map(((t, c)) => ixname(t, c)).join(", ")
}
#let ixentry(depth, t, code, see: (), also: (), ..locs) = block(
  above: 0.45em, below: 0.45em, breakable: true,
  pad(left: depth * 1em, par(hanging-indent: 1.2em, justify: false)[
    #ixname(t, code)#if locs.pos().len() > 0 [, #ixpages(..locs)]#ixsee("see", see)#ixsee("see also", also)
  ]))
#let ixletter(l) = block(above: 1.2em, below: 0.6em, sticky: true,
  text(weight: "bold", size: 1.15em, l))
"""


def typst_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _see_typst(index: BookIndex, names: tuple[str, ...]) -> str:
    pairs = [f"({typst_string(n)}, {'true' if c else 'false'})"
             for n, c in _see_targets(index, names)]
    if not pairs:
        return "()"
    return "(" + ", ".join(pairs) + ("," if len(pairs) == 1 else "") + ")"


def _entry_typst(entry: Entry, index: BookIndex, depth: int) -> list[str]:
    args = [str(depth), typst_string(entry.term.term),
            "true" if entry.code else "false"]
    if entry.term.see:
        args.append(f"see: {_see_typst(index, entry.term.see)}")
    if entry.term.see_also:
        args.append(f"also: {_see_typst(index, entry.term.see_also)}")
    for loc in entry.locators:
        label = book_href(loc).removeprefix("#")
        args.append(f"(label({typst_string(label)}), "
                    f"{'true' if loc.principal else 'false'})")
    out = [f"#ixentry({', '.join(args)})"]
    for child in entry.children:
        out += _entry_typst(child, index, depth + 1)
    return out


def render_typst(index: BookIndex, columns: int = 2) -> str:
    """The index chapter for the PDF: a level-1 heading, then raw
    typst, one `#ixentry` line per entry inside `#columns`."""
    body: list[str] = []
    for group, entries in letters(index):
        body.append(f"#ixletter({typst_string(group)})")
        for entry in entries:
            body += _entry_typst(entry, index, 0)
    return "\n".join([
        "# Index {#book-index}", "", "```{=typst}", TYPST_PREAMBLE,
        "#set text(size: 0.85em)",
        f"#columns({columns}, gutter: 1.8em)[", *body, "]", "```", ""])


# --------------------------------------------------------------------------- #
# Counts and the report
# --------------------------------------------------------------------------- #
def counts(index: BookIndex) -> dict[str, int]:
    entries = index.all_entries()
    out: dict[str, int] = {f"entries ({kind})": 0 for kind in KINDS}
    for e in entries:
        out[f"entries ({e.term.kind})"] += 1
    out["entries"] = len(entries)
    out["entries with locators"] = sum(1 for e in entries if e.locators)
    out["locators"] = sum(len(e.locators) for e in entries)
    out["principal locators"] = sum(
        1 for e in entries for loc in e.locators if loc.principal)
    out["injected anchors"] = sum(len(v) for v in index.located.values())
    out[f"entries over {MAX_LOCATORS} locators"] = len(index.warnings)
    return out


def _singular_forms(name: str) -> set[str]:
    k = bare_name(name).lower()
    forms = {k, k + "s", k + "es"}
    if k.endswith("y"):
        forms.add(k[:-1] + "ies")
    return forms


def untracked_italics(index: BookIndex,
                      pattern_names: Iterable[str] = ()
                      ) -> dict[str, list[str]]:
    """Italic spans no entry matches, by text, with their chapters.

    A span counts as tracked when a `concept` or `pattern` entry's
    match falls inside it. Stop words and pattern names are skipped.
    """
    corpus = index.corpus
    tracked: set[tuple[int, int]] = set()
    for entry in index.all_entries():
        if entry.term.kind not in ("concept", "pattern"):
            continue
        for item, pattern in zip(entry.term.match,
                                 entry.term.patterns()):
            for m in corpus.prose.finditer(item, pattern):
                span = corpus.italic_at(m.start(), m.end())
                if span is not None:
                    tracked.add(span)
    names = {n.lower() for n in pattern_names}
    names |= {n + "s" for n in names}
    found: dict[str, list[str]] = defaultdict(list)
    for span in corpus.italics:
        if span in tracked:
            continue
        text = " ".join(corpus.prose.text[span[0]:span[1]].split())
        key = text.lower()
        if not text or key in index.stop or key in names:
            continue
        place = corpus.places[corpus.prose.at(span[0])]
        number = corpus.chapters[place.chapter].number
        if number not in found[text]:
            found[text].append(number)
    return dict(sorted(found.items(), key=lambda kv: sort_key(kv[0])))


def report(index: BookIndex, pattern_names: Iterable[str] = ()) -> str:
    """The term file's health, as text: five lists, each with a count."""
    entries = index.all_entries()
    sections: list[tuple[str, list[str]]] = []

    italics = untracked_italics(index, pattern_names)
    sections.append(("Italic terms with no entry", [
        f"{text}  ({', '.join(chs)})" for text, chs in italics.items()]))

    sections.append(("Entries whose patterns match nothing", [
        e.term.term for e in entries
        if not e.locators and (e.term.match or not (
            e.term.see or e.term.see_also or e.children))]))

    missing = []
    for e in entries:
        for key, names in (("see", e.term.see),
                           ("see_also", e.term.see_also),
                           ("under", (e.term.under,) if e.term.under
                            else ())):
            missing += [f"{e.term.term}: {key} {n!r}" for n in names
                        if n not in index.by_term]
    sections.append(("Cross-references naming no entry", missing))

    forms: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        forms[bare_name(e.term.term).lower()].append(e.term.term)
    pairs = []
    for e in entries:
        for form in sorted(_singular_forms(e.term.term)):
            for other in forms.get(form, []):
                if other != e.term.term and (other, e.term.term) not in pairs:
                    pairs.append((e.term.term, other))
    sections.append(("Entries differing only by case or plural",
                     [f"{a}  /  {b}" for a, b in pairs]))

    sections.append((f"Entries over {MAX_LOCATORS} locators",
                     list(index.warnings)))

    out: list[str] = []
    for title, rows in sections:
        out.append(f"{title}: {len(rows)}")
        out += [f"  {row}" for row in rows]
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--markdown", type=Path, metavar="FILE",
                    help="write the index as Markdown to FILE")
    ap.add_argument("--report", action="store_true",
                    help="report on the term file instead (exit 0)")
    ap.add_argument("--terms", type=Path, default=TERMS_FILE,
                    help=f"the term file (default: {TERMS_FILE.name})")
    args = ap.parse_args(argv)
    try:
        terms = load_terms(args.terms)
    except TermFileError as e:
        print(f"error: {e}")
        return 0 if args.report else 1
    from tools.pattern_names import default_names, split_names
    names, excluded = split_names(default_names())
    index = build_index(book_chapters(), terms, excluded)
    if args.report:
        print(report(index, names))
        return 0
    if args.markdown is not None:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(args.markdown,
                      render_markdown(index, source_href))
        shown = (args.markdown.resolve().relative_to(ROOT)
                 if args.markdown.resolve().is_relative_to(ROOT)
                 else args.markdown)
        print(f"Wrote {shown.as_posix()}")
    width = max(len(k) for k in counts(index))
    for key, value in counts(index).items():
        print(f"{key:<{width}}  {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
