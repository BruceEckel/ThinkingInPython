"""Tests for tools/opening_epigraph.py: chapters open with an epigraph."""
from pathlib import Path
from tools.markdown import Document
from tools.opening_epigraph import find

GOOD = "# Title\n\n> One sentence.\n> Another.\n\nBody.\n"


def lines(name: str, text: str) -> list[int]:
    doc = Document.from_text(text, Path("Chapters") / name)
    return [f.line for f in find(doc)]


def test_two_line_blockquote_under_heading_is_clean() -> None:
    assert lines("30_Patterns--Observer.md", GOOD) == []


def test_missing_blockquote_is_reported() -> None:
    text = "# Title\n\nOne sentence.\nAnother.\n\nBody.\n"
    assert lines("30_Patterns--Observer.md", text) == [3]


def test_one_line_and_five_line_blockquotes_are_reported() -> None:
    one = "# Title\n\n> Only one.\n\nBody.\n"
    five = "# Title\n\n" + "> Line.\n" * 5 + "\nBody.\n"
    assert lines("30_P.md", one) == [3]
    assert lines("30_P.md", five) == [3]


def test_paragraph_run_on_after_blockquote_is_reported() -> None:
    text = "# Title\n\n> One.\n> Two.\nLazy continuation.\n"
    assert lines("30_P.md", text) == [5]


def test_missing_blank_after_heading_is_reported() -> None:
    assert lines("30_P.md", "# Title\n> One.\n> Two.\n") == [2]


def test_chapter_01_appendices_and_solutions_are_skipped() -> None:
    text = "# Title\n\nAn ordinary paragraph.\n"
    assert lines("01_Introduction.md", text) == []
    assert lines("A_Effect_Tracking.md", text) == []
    doc = Document.from_text(text, Path("Solutions") / "30_P.md")
    assert list(find(doc)) == []
