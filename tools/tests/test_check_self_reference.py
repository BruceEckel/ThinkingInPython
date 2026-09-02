"""Tests for tools/check_self_reference.py.

Each rule is pinned by the real error that motivated it, so a later
tightening cannot quietly stop catching the thing it was built for. The
two false-positive shapes that cost the first draft its precision (a bare
"later" modifying a noun, and a type name that is also an English word)
are pinned the same way.
"""
from pathlib import Path

import pytest

from check_self_reference import (
    GATE_CODES,
    Chapter,
    load,
    scan,
    searchable,
    sentences,
)
from tools_markdown import Document

NO_WAIVERS: frozenset[str] = frozenset()


def codes(doc: Document) -> list[str]:
    return [f.code for f in scan(doc, NO_WAIVERS)]


def messages(doc: Document) -> str:
    return "\n".join(f.message for f in scan(doc, NO_WAIVERS))


@pytest.fixture
def book(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Build a tiny two-chapter corpus the rules can be run against."""
    def make(files: dict[str, str]) -> dict[str, Chapter]:
        written = {}
        for name, text in files.items():
            path = tmp_path / name
            path.write_text(text, encoding="utf-8")
            written[name] = load(path)
        monkeypatch.setattr(
            "check_self_reference.corpus", lambda: written)
        return written
    return make


# ── searchable ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(("span", "expected"), [
    ("slots=True", "slots"),
    ("cached_property", "cached_property"),
    ("__dict__", "__dict__"),
    ("dict[str, int]", None),          # `dict` is too common to be evidence
    ("int", None),
    ("x", None),
    ("a_package/module4.py", "a_package/module4.py"),
])
def test_searchable_reduces_a_span_to_what_is_worth_grepping(
    span: str, expected: str | None,
) -> None:
    assert searchable(span) == expected


# ── sentence assembly ─────────────────────────────────────────────────────────

def test_a_sentence_spans_semantic_line_breaks() -> None:
    """The `slots=True` error needed the link and the term joined."""
    doc = Document.from_text(
        "A class declared with `slots=True`\n"
        "([Rethinking Objects](20_A--B.md) uses it)\n"
        "has no `__dict__`.\n"
    )
    (line, text), = sentences(doc)
    assert line == 1
    assert "`slots=True`" in text and "20_A--B.md" in text


def test_a_table_row_is_its_own_sentence() -> None:
    """Joining a table pooled every row's vocabulary into one claim."""
    doc = Document.from_text(
        "| `a` | first |\n"
        "| `b` | second |\n"
    )
    assert [t for _, t in sentences(doc)] == [
        "| `a` | first |", "| `b` | second |"]


def test_fenced_code_is_not_prose() -> None:
    doc = Document.from_text("Prose.\n\n```python\nx = `not prose`\n```\n")
    assert [t for _, t in sentences(doc)] == ["Prose."]


# ── absence (SR001), which gates ──────────────────────────────────────────────

def test_absence_catches_a_term_the_book_does_use(book) -> None:
    """Chapter 08 said `bytes` appears nowhere else. It is in five."""
    written = book({
        "08_A--B.md": (
            "| `bytes`, `complex` | the built-ins "
            "(`bytes` and `complex` do not appear elsewhere in this book) |\n"
        ),
        "18_C--D.md": "Slicing a large `bytes` view avoids a copy.\n",
    })
    doc = Document.parse(written["08_A--B.md"].path)
    assert codes(doc) == ["SR001"]
    assert "`bytes`" in messages(doc)


def test_absence_reports_each_term_once(book) -> None:
    """A row naming a term in two columns is still one claim."""
    written = book({
        "08_A--B.md": (
            "| `bytes` | `bytes` does not appear elsewhere in this book |\n"),
        "18_C--D.md": "A `bytes` slice.\n",
    })
    assert codes(Document.parse(written["08_A--B.md"].path)) == ["SR001"]


def test_absence_ignores_the_english_word(book) -> None:
    """`complex` in "a more complex design" is not the type."""
    written = book({
        "08_A--B.md": "`complex` does not appear elsewhere in this book.\n",
        "18_C--D.md": "A more complex design returns the factory.\n",
    })
    assert codes(Document.parse(written["08_A--B.md"].path)) == []


# ── direction (SR003), which gates ────────────────────────────────────────────

def test_direction_catches_an_earlier_chapter_that_is_later(book) -> None:
    written = book({
        "14_A--B.md": (
            "Several decorators from earlier chapters, such as "
            "[Performance](18_C--D.md), use this mechanism.\n"),
        "18_C--D.md": "Caching.\n",
    })
    findings = list(scan(Document.parse(written["14_A--B.md"].path),
                         NO_WAIVERS))
    assert [f.code for f in findings] == ["SR003"]
    assert "points forward" in findings[0].message


def test_direction_ignores_later_modifying_a_noun(book) -> None:
    """"every later construction" is not a claim about the link."""
    written = book({
        "24_A--B.md": (
            "[Metaprogramming](17_C--D.md) shows that singleton: its "
            "override skips `__init__()` on every later construction.\n"),
        "17_C--D.md": "Metaclasses and `__init__()`.\n",
    })
    assert "SR003" not in codes(Document.parse(written["24_A--B.md"].path))


def test_direction_needs_the_phrase_near_the_link(book) -> None:
    """Distance is what makes the ordering word evidence about the link."""
    filler = "and " * 40
    written = book({
        "24_A--B.md": (
            f"An earlier chapter said so, {filler}"
            "which [Metaprogramming](17_C--D.md) repeats.\n"),
        "17_C--D.md": "Metaclasses.\n",
    })
    assert "SR003" not in codes(Document.parse(written["24_A--B.md"].path))


# ── grounding (SR002), which reports ──────────────────────────────────────────

def test_grounding_catches_a_chapter_that_shares_no_vocabulary(book) -> None:
    """The flagship: chapter 20 contains no `slots`, `__dict__`, or
    `cached_property`, and the sentence attributed all three to it."""
    written = book({
        "07_A--B.md": (
            "A class declared with `slots=True`\n"
            "([Rethinking Objects](20_C--D.md) uses it)\n"
            "has no `__dict__`, so `cached_property` has nowhere to store.\n"),
        "20_C--D.md": "Composition and protocols.\n",
    })
    findings = list(scan(Document.parse(written["07_A--B.md"].path),
                         NO_WAIVERS))
    assert [f.code for f in findings] == ["SR002"]
    assert "`slots`" in findings[0].message


def test_grounding_stays_quiet_when_one_term_lands(book) -> None:
    """One shared word is enough: the sentence is about that chapter."""
    written = book({
        "07_A--B.md": (
            "A class declared with `slots=True`\n"
            "([Performance](18_C--D.md) uses it) has no `__dict__`.\n"),
        "18_C--D.md": "`@dataclass(slots=True)` shrinks instances.\n",
    })
    assert codes(Document.parse(written["07_A--B.md"].path)) == []


def test_grounding_is_not_a_gating_rule() -> None:
    assert "SR002" not in GATE_CODES
    assert {"SR001", "SR003"} == set(GATE_CODES)
