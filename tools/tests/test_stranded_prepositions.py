"""Tests for tools/stranded_prepositions.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.stranded_prepositions import find, main

def hits(text: str) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(f.line, f.message) for f in find(doc)]


@pytest.mark.parametrize("text", [
    "Name the field they sit on.",
    "Say what it is for.",
    "This is the tool you look at.",
])
def test_hit(text: str) -> None:
    assert len(hits(text)) == 1


@pytest.mark.parametrize("text", [
    "Name the field on which they sit.",
    "You can pass it around.",
    "Turn it on.",
    "The class refers to `x`.",
    "A code span ends `up with`.",
    "Look at it.",
])
def test_not_a_hit(text: str) -> None:
    assert hits(text) == []


def test_reports_clause_text() -> None:
    assert hits("Name the field they sit on.") == [
        (1, "Name the field they sit on")]


def test_skips_block_quote_heading_table_and_html() -> None:
    text = "\n".join([
        "# The field they sit on",
        "",
        "> Name the field they sit on.",
        "",
        "| the field they sit on |",
        "",
        "<summary>the field they sit on</summary>",
        "",
        "[ref]: the field they sit on",
        "",
        "```python",
        "# the field they sit on.",
        "```",
        "",
        "#: the field they sit on.",
    ])
    assert hits(text) == []


def test_multiline_paragraph_reports_the_prepositions_line() -> None:
    text = "\n".join([
        "The sentence starts here.",
        "Name the field",
        "they sit on.",
        "It ends cleanly.",
    ])
    assert hits(text) == [(3, "Name the field they sit on")]


def test_clause_split_at_comma() -> None:
    assert hits("Pick the object you work with, and then stop.") == [
        (1, "Pick the object you work with")]


def test_list_item_is_read() -> None:
    assert len(hits("- Name the field they sit on.")) == 1


def test_main_report_only_unless_fail(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("Name the field they sit on.\n", encoding="utf-8")
    assert main([str(path)]) == 0
    assert "1 stranded prepositions in 1 files" in capsys.readouterr().out
    assert main([str(path), "--fail"]) == 1
