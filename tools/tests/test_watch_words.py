"""Tests for tools/watch_words.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.stranded_prepositions import (
    display,
    load_baseline,
    write_baseline,
)
from tools.watch_words import find, key, main

def hits(text: str) -> list[tuple[int, int, str, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(line, tier, word, clause)
            for _, line, tier, word, clause in find(doc)]


def test_tier_3_hit() -> None:
    assert hits("The library ships with a parser.") == [
        (1, 3, "ships", "The library ships with a parser")]


def test_tier_2_hit() -> None:
    assert hits("The value is already set.") == [
        (1, 2, "already", "The value is already set")]


def test_phrase_hit_is_case_insensitive() -> None:
    assert [h[2] for h in hits("Near-miss bugs. The Way Out.")] == [
        "near-miss", "the way out"]


@pytest.mark.parametrize("text", [
    "The `ships` field is a count.",
    "Call [it](https://example.com/ships/landing).",
    "An even number is divisible by two.",
    "Odd and even integers differ.",
    "Odd or even values both work.",
    "The numbers divide evenly.",
    "The relationship is a membership with ownership.",
    "A landscape is a view.",
    "Install the pre-commit hook.",
    "A git hook runs before the commit.",
    "A SessionStart hook prints the tags.",
    "The Claude Code hook runs a script.",
    "The hooks module registers each callback.",
])
def test_not_a_hit(text: str) -> None:
    assert hits(text) == []


def test_even_intensifier_and_plain_hook_hit() -> None:
    assert [h[2] for h in hits("Even a decorator works.")] == ["even"]
    assert [h[2] for h in hits("A hook lets a plugin react.")] == ["hook"]


def test_land_and_ship_whole_words() -> None:
    assert [h[2] for h in hits("The check lands early.")] == ["lands"]
    assert [h[2] for h in hits("The ship sails.")] == ["ship"]


def test_skips_heading_quote_table_html_and_fence() -> None:
    text = "\n".join([
        "# It never ships",
        "",
        "> It never ships.",
        "",
        "| never ships |",
        "",
        "<summary>never ships</summary>",
        "",
        "```python",
        "# never ships.",
        "```",
        "",
        "#: never ships",
    ])
    assert hits(text) == []


def test_line_is_the_words_line() -> None:
    text = "One sentence.\nThe tool\nnever stops."
    assert hits(text) == [(3, 2, "never", "The tool never stops")]


CLAUSE = "The library ships with a parser"


@pytest.fixture
def book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A one-hit Markdown file and an isolated baseline path."""
    root = tmp_path.resolve()
    monkeypatch.setattr("tools.stranded_prepositions.ROOT", root)
    monkeypatch.setattr("tools.watch_words.ROOT", root)
    monkeypatch.setattr("tools.watch_words.BASELINE", root / "base.txt")
    (root / "Chapters").mkdir()
    (root / "Solutions").mkdir()
    path = root / "Chapters" / "a.md"
    path.write_text(f"{CLAUSE}.\n", encoding="utf-8")
    return path


def entry(path: Path, clause: str = CLAUSE, word: str = "ships") -> str:
    return key(display(path), word, clause)


def baseline_of(path: Path) -> Path:
    return path.parent.parent / "base.txt"


def test_new_hit_is_marked_and_summarized(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([str(book)]) == 0
    out = capsys.readouterr().out
    assert "NEW" in out and "[T3] ships" in out
    assert "1 new (1 T3, 0 T2), 0 accepted" in out


def test_baselined_hit_is_hidden_then_listed_with_all(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_baseline({entry(book)}, baseline_of(book))
    assert main([str(book), "--fail"]) == 0
    out = capsys.readouterr().out
    assert CLAUSE not in out
    assert "0 new (0 T3, 0 T2), 1 accepted" in out
    assert main([str(book), "--all"]) == 0
    out = capsys.readouterr().out
    assert "accepted" in out and CLAUSE in out


def test_stale_entry_is_listed(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_baseline({entry(book, "The tool ships")}, baseline_of(book))
    assert main([str(book)]) == 0
    out = capsys.readouterr().out
    assert "1 new (1 T3, 0 T2), 0 accepted, 1 stale" in out
    assert "stale" in out


def test_accept_adds_new_and_drops_stale(book: Path) -> None:
    gone = entry(book, "The tool ships")
    write_baseline({gone}, baseline_of(book))
    assert main(["--accept"]) == 0
    assert load_baseline(baseline_of(book)) == {entry(book)}
    assert main([]) == 0


def test_accept_refuses_paths(book: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(book), "--accept"])


def test_fail_only_on_tier_3(tmp_path: Path) -> None:
    low = tmp_path / "low.md"
    low.write_text("The value is already set.\n", encoding="utf-8")
    high = tmp_path / "high.md"
    high.write_text(f"{CLAUSE}.\n", encoding="utf-8")
    assert main([str(low), "--fail"]) == 0
    assert main([str(high), "--fail"]) == 1


def test_tier_filter(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("It already ships.\n", encoding="utf-8")
    assert main([str(path), "--tier", "3"]) == 0
    out = capsys.readouterr().out
    assert "[T3]" in out and "[T2]" not in out
