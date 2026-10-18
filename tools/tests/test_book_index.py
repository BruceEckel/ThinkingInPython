"""Tests for tools/book_index.py (the term file, matcher, and renderers).

The index is computed on every build and checked by no gate, so a
matcher rule that drifts shows up only as a worse index: a section
listed twice, a principal locator buried, a listing counted for a
concept, or an `#ix-` id that moves between builds and breaks a
link in a published EPUB. The rules are pinned here on a synthetic
chapter, along with the term file's load errors and one smoke test
per output. The seeded regex search (2026-10-18) must return what
`finditer()` returns, so its walk is pinned on the shapes the term
file uses and its matches are compared with the scan's.
"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tools import book_index
from tools.book_index import (
    ChapterSource,
    Channel,
    Term,
    TermFile,
    TermFileError,
    book_href,
    build_index,
    letter,
    paragraphs,
    parse_terms,
    render_html,
    render_markdown,
    render_typst,
    seed_words,
    sort_key,
)

BODY = """\
The opening names a closure in passing.

## Closures

A *closure* keeps the variables it uses.
Here is a second closure on the same paragraph.

Another paragraph about closures.

## Defining Elsewhere

Before the definition, a closure.

This is where a *closure* gets its italic.

## Listings

- A list item that names a closure.

```python
# demo.py
from functools import cache
closure = cache
```

## Patterns

The *State* pattern, and the *state* an object holds.
The *State Machines* chapter title is not a mention.
"""


def chapter(body: str = BODY, stem: str = "07_Test",
            number: str = "07") -> ChapterSource:
    return ChapterSource(stem, number, "Test", body)


def terms(*entries: Term) -> TermFile:
    return TermFile(tuple(entries))


CLOSURE = Term("closure", "concept", ("closure", "closures"))
CACHE_CONCEPT = Term("cache", "concept", ("cache",))
CACHE_PYTHON = Term("cache", "python", ("cache",), code=True)


def index_of(*entries: Term, body: str = BODY):
    return build_index([chapter(body)], terms(*entries),
                       excluded=["State Machines"])


# ── locators ────────────────────────────────────────────────────────────────

def test_one_locator_per_section() -> None:
    entry = index_of(CLOSURE).by_term["closure"]
    sections = [loc.section for loc in entry.locators]
    # The opening, then four sections; "Closures" mentions it four
    # times and still yields one locator.
    assert sorted(sections) == sorted(
        ["", "closures", "defining-elsewhere", "listings"])
    assert len(sections) == len(set(sections))


def test_heading_and_definition_are_principal_and_first() -> None:
    entry = index_of(CLOSURE).by_term["closure"]
    principal = [loc.section for loc in entry.locators if loc.principal]
    assert principal == ["closures", "defining-elsewhere"]
    assert [loc.principal for loc in entry.locators] == [
        True, True, False, False]
    # The heading's locator points at the heading itself; the
    # definition's at the italic paragraph, not the earlier mention.
    heading, defining = entry.locators[:2]
    assert heading.heading_anchor == "closures"
    units = paragraphs(BODY)
    assert "*closure* gets" in BODY.split("\n")[units[defining.paragraph].first]


def test_listing_counts_only_for_python_names() -> None:
    index = index_of(CACHE_CONCEPT, body=BODY)
    assert index.by_term["cache"].locators == []
    index = index_of(CACHE_PYTHON, body=BODY)
    [loc] = index.by_term["cache"].locators
    assert loc.section == "listings"
    assert paragraphs(BODY)[loc.paragraph].kind == "listing"


def test_prose_is_preferred_to_a_listing_in_the_same_section() -> None:
    entry = index_of(CLOSURE).by_term["closure"]
    [listings] = [loc for loc in entry.locators
                  if loc.section == "listings"]
    assert paragraphs(BODY)[listings.paragraph].kind == "item"


def test_pattern_needs_a_capitalized_italic() -> None:
    entry = index_of(Term("State", "pattern", ("State",))).by_term["State"]
    [loc] = entry.locators
    assert loc.section == "patterns"
    # Only one mention counts: *state* is lowercase and *State
    # Machines* is excluded, so dropping the real one leaves nothing.
    body = BODY.replace("The *State* pattern", "The pattern")
    assert index_of(Term("State", "pattern", ("State",)),
                    body=body).by_term["State"].locators == []


def test_over_eight_locators_is_a_warning() -> None:
    body = "\n".join(f"## Part {n}\n\nA widget here.\n" for n in range(9))
    index = index_of(Term("widget", "concept", ("widget",)), body=body)
    assert len(index.by_term["widget"].locators) == 9
    assert len(index.warnings) == 1 and "widget" in index.warnings[0]
    body = "\n".join(f"## Part {n}\n\nA widget here.\n" for n in range(8))
    assert index_of(Term("widget", "concept", ("widget",)),
                    body=body).warnings == []


def test_subentries_nest_under_their_parent() -> None:
    child = Term("closure cells", "concept", ("closure",), under="closure")
    index = index_of(CLOSURE, child)
    assert [e.term.term for e in index.entries] == ["closure"]
    assert [c.term.term for c in index.entries[0].children] == [
        "closure cells"]


# ── injected ids ────────────────────────────────────────────────────────────

def test_ix_ids_are_stable_and_unique() -> None:
    first = index_of(CLOSURE, CACHE_PYTHON).located
    second = index_of(CLOSURE, CACHE_PYTHON).located
    assert first == second
    ids = [ix for paras in first.values() for ix in paras.values()]
    assert len(ids) == len(set(ids))
    assert all(ix.startswith("ix-07-") for ix in ids)


def test_inject_anchors_places_spans_and_divs() -> None:
    index = index_of(CLOSURE, CACHE_PYTHON)
    text = index.inject_anchors(BODY, "07_Test")
    lines = text.split("\n")
    assert lines[0].startswith("[]{#ix-07-0}The opening")
    item = next(line for line in lines if "list item" in line)
    assert item.startswith("- []{#ix-07-")
    fence = lines.index("```python")
    assert lines[fence - 2].startswith("::: {#ix-07-")
    assert "\n:::\n" in text
    # Headings get nothing: their own id is the anchor.
    assert "## Closures" in lines
    # The same text twice gives the same ids.
    assert index.inject_anchors(BODY, "07_Test") == text


def test_inject_anchors_refuses_a_different_text() -> None:
    index = index_of(CLOSURE)
    with pytest.raises(ValueError, match="paragraphs"):
        index.inject_anchors(BODY + "\nOne more paragraph.\n", "07_Test")
    # A chapter the index never located is returned unchanged.
    assert index.inject_anchors("Other text.", "99_Other") == "Other text."


def test_footnote_continuations_are_never_located() -> None:
    body = ("- An item.\n\n"
            "[^n]: A footnote about a closure.\n\n"
            "    Its second paragraph names a closure too.\n")
    index = index_of(CLOSURE, body=body)
    assert index.by_term["closure"].locators == []
    assert [u.kind for u in paragraphs(body)] == [
        "item", "footnote", "footnote"]


def test_exercises_sections_are_never_located() -> None:
    body = ("## Closures\n\n"
            "A *closure* keeps variables.\n\n"
            "## Exercises\n\n"
            "1. Write a closure that counts, then a *lambda*.\n\n"
            "Another closure here.\n")
    index = index_of(CLOSURE, body=body)
    [loc] = index.by_term["closure"].locators
    assert loc.section == "closures"
    lam = Term("lambda", "concept", ("lambda",))
    index = index_of(CLOSURE, lam, body=body)
    assert index.by_term["lambda"].locators == []
    assert "lambda" not in book_index.untracked_italics(index)
    other = index_of(CLOSURE, body=body.replace("Exercises", "Practice"))
    assert "lambda" in book_index.untracked_italics(other)


# ── the term file ───────────────────────────────────────────────────────────

GOOD = """\
stop = ["is"]

[[entry]]
term = "closure"
match = ["closure", "re:closures?"]
see_also = ["nonlocal"]

[[entry]]
term = "nonlocal"
kind = "python"
match = ["nonlocal"]
code = true
"""


def test_parse_terms_reads_entries_and_the_stop_list() -> None:
    parsed = parse_terms(GOOD)
    assert [t.term for t in parsed.entries] == ["closure", "nonlocal"]
    assert parsed.entries[0].kind == "concept"
    assert parsed.entries[0].see_also == ("nonlocal",)
    assert parsed.entries[1].code is True
    assert parsed.stop == frozenset({"is"})


@pytest.mark.parametrize(("text", "message"), [
    ("[[entry]\nterm = 'x'", "index_terms.toml"),
    ("[[entry]]\nmatch = ['x']", "missing `term`"),
    ("[[entry]]\nterm = 'x'\ncolour = 'red'", "unknown key"),
    ("[[entry]]\nterm = 'x'\n[[entry]]\nterm = 'x'", "duplicate"),
    ("[[entry]]\nterm = 'x'\nkind = 'idea'", "kind must be"),
    ("[[entry]]\nterm = 'x'\nmatch = [1]", "list of non-empty strings"),
    ("[[entry]]\nterm = 'x'\ncode = 'yes'", "true or false"),
    ("[[entry]]\nterm = 'x'\nmatch = ['re:(']", "bad regex"),
    ("extra = 1", "unknown top-level"),
])
def test_parse_terms_rejects_a_bad_file(text: str, message: str) -> None:
    with pytest.raises(TermFileError, match=message):
        parse_terms(text)


def test_python_names_match_case_sensitively() -> None:
    body = "Use `Enum` here.\n\nThe `enum` module there.\n"
    index = index_of(Term("Enum", "python", ("Enum",)), body=body)
    [loc] = index.by_term["Enum"].locators
    assert loc.paragraph == 0


# ── sorting ─────────────────────────────────────────────────────────────────

def test_sort_ignores_underscores_parentheses_and_case() -> None:
    names = ["__init__()", "@dataclass", "Iterator", "id()", "PEP 484",
             "PEP 8", "abc"]
    assert sorted(names, key=sort_key) == [
        "abc", "@dataclass", "id()", "__init__()", "Iterator", "PEP 8",
        "PEP 484"]
    assert letter("__init__()") == "I"
    assert letter("@dataclass") == "D"
    assert letter("Façade") == "F"


# ── rendering, one smoke test per output ────────────────────────────────────

TWO = """\
## Closures

A *closure* keeps its variables.

## Caching

The `cache` decorator from `functools`, and a closure again.
"""


def two_entry_index():
    return index_of(CLOSURE, CACHE_PYTHON, body=TWO)


def test_render_html_links_the_site_pages() -> None:
    page = render_html(two_entry_index())
    assert 'class="ix-letters"' in page
    assert '<a href="#ix-letter-c">C</a>' in page
    assert "<code>cache</code>" in page
    assert ('<strong><a href="07_Test.html#closures">07 Test, '
            "<em>Closures</em></a></strong>") in page
    assert 'href="07_Test.html#ix-07-' in page


def test_render_markdown_is_an_epub_chapter() -> None:
    text = render_markdown(two_entry_index(),
                           heading="# Index {#book-index epub:type=index}")
    assert text.startswith("# Index {#book-index epub:type=index}")
    assert "## C {#ix-letter-c .unlisted}" in text
    assert "- `cache`: [07 Test, *Caching*](#ix-07-" in text
    assert "**[07 Test, *Closures*](#ch07-closures)**" in text


def test_render_typst_writes_page_lookups_in_columns() -> None:
    text = render_typst(two_entry_index())
    assert text.startswith("# Index {#book-index}")
    assert "#columns(2, gutter: 1.8em)[" in text
    assert "counter(page).at(l)" in text
    assert '#ixentry(0, "closure", false, (label("ch07-closures"), true)' \
        in text
    assert '#ixentry(0, "cache", true, (label("ix-07-' in text
    assert render_typst(two_entry_index(), columns=1).count(
        "#columns(1") == 1


def test_book_href_namespaces_headings_only() -> None:
    entry = two_entry_index().by_term["closure"]
    assert book_href(entry.locators[0]) == "#ch07-closures"
    assert book_href(entry.locators[1]).startswith("#ix-07-")


@pytest.mark.skipif(shutil.which("pandoc") is None
                    or shutil.which("typst") is None,
                    reason="needs pandoc and typst")
def test_typst_index_compiles_with_page_numbers(tmp_path: Path) -> None:
    # The real path in small: the injected chapter and the index
    # chapter through pandoc's typst writer, then typst itself, which
    # rejects a label that does not exist and an unknown function.
    index = two_entry_index()
    body = index.inject_anchors(TWO, "07_Test").replace(
        "## Closures", "## Closures {#ch07-closures}").replace(
        "## Caching", "## Caching {#ch07-caching}")
    src = tmp_path / "book.md"
    src.write_text(f"# Test {{#ch07}}\n\n{body}\n{render_typst(index)}",
                   encoding="utf-8")
    pdf = tmp_path / "book.pdf"
    proc = subprocess.run(
        ["pandoc", str(src), "--pdf-engine", "typst", "-o", str(pdf)],
        capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    assert pdf.stat().st_size > 0


def test_book_markdown_adds_the_index_chapter(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tools.build_epub import book_markdown
    from tools.build_site import Chapter
    terms_file = tmp_path / "terms.toml"
    terms_file.write_text(
        '[[entry]]\nterm = "closure"\nmatch = ["closure"]\n',
        encoding="utf-8")
    monkeypatch.setattr(book_index, "TERMS_FILE", terms_file)
    md = tmp_path / "07_Test.md"
    md.write_text("# Test\n\nA closure here.\n", encoding="utf-8")
    chapters = [Chapter(md, "07_Test.html", "07", "Test", "Chapter 7")]
    epub = book_markdown(chapters, set(), set(), index_form="epub")
    assert "[]{#ix-07-0}A closure here." in epub
    assert "# Index {#book-index epub:type=index}" in epub
    assert "](#ix-07-0)" in epub
    typst = book_markdown(chapters, set(), set(), hang_code=False,
                          index_form="typst")
    assert '(label("ix-07-0"), false)' in typst
    assert "Index" not in book_markdown(chapters, set(), set())


# --------------------------------------------------------------------------- #
# The seeded regex search
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("regex, flags, groups", [
    # A word after lookarounds alone: bounded at 0.
    (r"(?<!\[\*)\bProxy\b(?!\*)", re.I, ({"Proxy": 0},)),
    # An optional dotted prefix makes the distance unbounded; nothing
    # can match a newline, so the line bounds the search.
    (r"(?<=[ \n] )(?:\w+\.)*Path(?!\w)", 0, ({"Path": None},)),
    # `\s+` can match a newline, so only the bounded first word serves.
    (r"A\s+data\s+class", re.I, ({"A": 0},)),
    # Nothing bounded and a newline possible: the full scan.
    (r"\s+can carry the row", re.I, ()),
    # Two orderings of the same words: each word in both alternatives,
    # with the larger distance.
    (r"(?:isinstance\([^\n]{0,40}?\)[^\n]{0,20}?Protocol"
     r"|Protocol[^\n]{0,20}?isinstance\()", 0,
     ({"isinstance": 28, "Protocol": 72},)),
    # Unrelated alternatives: one group per alternative.
    (r"(?:A plugin writes|plugins or other packages)", re.I,
     ({"A": 0, "plugin": 2, "writes": 9},
      {"plugins": 0, "or": 8, "other": 11, "packages": 17})),
    # A word in every alternative of a title list, after an unbounded
    # line prefix.
    (r"(?m)^(?=[^\n]{0,100}$)[^\n]*?(?:Self Registration|Hazards of Self)",
     re.I, ({"Self": None},)),
    # A word under a local `(?i:...)` is dropped: the pattern's flags
    # would search for one casing of it.
    (r"(?i:x)abc", 0, ({"abc": 1},)),
    # A backreference is not modeled.
    (r"(?P<n>ab)(?P=n)", 0, ()),
])
def test_seed_words_follow_the_parse_tree(regex: str, flags: int,
                                          groups: tuple) -> None:
    assert seed_words(re.compile(regex, flags)) == groups


SEED_TEXT = [
    "nap the cat sat down nap",
    "A plugin writes a line.  plugins or other packages read it",
    "    isinstance(x, Proxy)  # a *Proxy* here,  pathlib.Path there",
    "Proxies and a proxy and PROXY; A  data\nclass",
    "Self Registration",
    "the Hazards of Self",
]


@pytest.mark.parametrize("regex, flags", [
    (r"(?<!\[\*)\bProxy\b(?!\*)", re.I),
    (r"(?<=[ \n] )(?:\w+\.)*Path(?!\w)", 0),
    (r"A\s+data\s+class", re.I),
    (r"(?:A plugin writes|plugins or other packages)", re.I),
    (r"(?m)^(?=[^\n]{0,100}$)[^\n]*?(?:Self Registration|Hazards of Self)",
     re.I),
    # The group-two match starts before a failed group-one occurrence.
    (r"(?:cat nap|the cat sat down)", 0),
])
def test_seeded_search_matches_the_scan(regex: str, flags: int) -> None:
    channel = Channel(SEED_TEXT)
    pattern = re.compile(regex, flags)
    expected = [m.span() for m in pattern.finditer(channel.text)]
    assert expected, "the fixture must exercise the pattern"
    assert [m.span() for m in channel.seeded(pattern)] == expected


@pytest.mark.book
def test_seeded_search_matches_the_scan_on_a_chapter() -> None:
    """Every `re:` item of the term file, against one real chapter."""
    from tools.pattern_names import default_names, split_names
    chapters = [c for c in book_index.book_chapters()
                if c.stem.startswith("30_")]
    corpus = book_index.Corpus(chapters, split_names(default_names())[1])
    seeded = 0
    for term in book_index.load_terms().entries:
        channel = corpus.code if term.kind == "python" else corpus.prose
        for item, pattern in zip(term.match, term.patterns()):
            if not item.startswith("re:"):
                continue
            seeded += bool(seed_words(pattern))
            assert ([m.span() for m in channel.seeded(pattern)]
                    == [m.span() for m in pattern.finditer(channel.text)]), item
    assert seeded > 500
