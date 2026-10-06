"""Tests for tools/stranded_prepositions.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.stranded_prepositions import (
    display,
    find,
    key,
    load_baseline,
    main,
    write_baseline,
)

def hits(text: str) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(f.line, f.message) for f in find(doc)]


@pytest.mark.parametrize("text", [
    "Name the field they sit on.",
    "Say what it is for.",
    "This is the tool you look at.",
    "The type checker has nothing to compare `Beetle` against, "
    "so it passes.",
    "The namespace `type` builds it from.",
    "With no registration to choose among, the call fails.",
    "A default cannot come before one without.",
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
    "Then turn it on.",
    "The wrapper passes `x` through.",
    "Carry them along.",
    "The caller passes it by.",
    "You may have seen something like it before.",
    "Run it as many times as you like.",
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
    assert "1 new, 0 accepted" in capsys.readouterr().out
    assert main([str(path), "--fail"]) == 1


CLAUSE = "Name the field they sit on"


@pytest.fixture
def book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A one-hit Markdown file and an isolated baseline path."""
    root = tmp_path.resolve()
    monkeypatch.setattr("tools.stranded_prepositions.ROOT", root)
    monkeypatch.setattr(
        "tools.stranded_prepositions.BASELINE", root / "baseline.txt")
    (root / "Chapters").mkdir()
    (root / "Solutions").mkdir()
    path = root / "Chapters" / "a.md"
    path.write_text(f"{CLAUSE}.\n", encoding="utf-8")
    return path


def entry(path: Path, clause: str = CLAUSE) -> str:
    return key(display(path), clause)


def test_key_ignores_line_and_whitespace(tmp_path: Path) -> None:
    path = tmp_path / "a.md"
    assert key("a.md", "Name  the\tfield") == key("a.md", "Name the field")
    assert "\t" in key("a.md", "x") and ":" not in key("a.md", "x")
    path.write_text(f"Intro.\n\n{CLAUSE}.\n", encoding="utf-8")
    moved = [(f.line, key(display(f.path), f.message))
             for f in find(Document.parse(path))]
    path.write_text(f"{CLAUSE}.\n", encoding="utf-8")
    first = [(f.line, key(display(f.path), f.message))
             for f in find(Document.parse(path))]
    assert moved[0][0] != first[0][0]
    assert moved[0][1] == first[0][1]


def test_new_hit_is_marked(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([str(book), "--fail"]) == 1
    out = capsys.readouterr().out
    assert "NEW" in out
    assert "1 new, 0 accepted" in out


def test_baselined_hit_is_hidden_then_listed_with_all(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_baseline({entry(book)})
    assert main([str(book), "--fail"]) == 0
    out = capsys.readouterr().out
    assert CLAUSE not in out
    assert "0 new, 1 accepted" in out
    assert main([str(book), "--all"]) == 0
    out = capsys.readouterr().out
    assert "accepted" in out and CLAUSE in out


def test_edited_clause_is_new_again(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_baseline({entry(book, "Name the field they stand on")})
    assert main([str(book)]) == 0
    out = capsys.readouterr().out
    assert "1 new, 0 accepted, 1 stale" in out
    assert "stale" in out


def test_accept_adds_new_and_drops_stale(book: Path) -> None:
    gone = entry(book, "Name the field they stand on")
    write_baseline({gone})
    assert main(["--accept"]) == 0
    assert load_baseline() == {entry(book)}
    assert main([]) == 0
