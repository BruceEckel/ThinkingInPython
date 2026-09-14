"""Tests for tools/check_quoted_diagnostics.py.

A quoted `ty` diagnostic is prose: nothing runs it, so a listing edit
that moves a quoted line goes unnoticed. The check compares each
quote's gutter lines with the extracted listing, and these tests pin
what counts as a match and what is reported.
"""
from pathlib import Path

from tools import check_quoted_diagnostics as cqd
from tools.markdown import Document


def test_gutter_line_matches_ignore_span_bar_indent_and_ignores() -> None:
    assert cqd.gutter_matches("x = f(1)", "x = f(1)")
    assert cqd.gutter_matches("|     Need[A], str", "    Need[A], str")
    assert cqd.gutter_matches("x = f(1)", "x = f(1)  # type: ignore")
    assert cqd.gutter_matches("x = f(1)", "x = f(1)  # type: ignore[arg]")
    assert cqd.gutter_matches("x = f(1)", "# x = f(1)")
    assert not cqd.gutter_matches("x = f(2)", "x = f(1)")


def quoted(md: Path, listing_dir: Path, text: str) -> list[str]:
    md.write_text(text, encoding="utf-8")
    cqd.TREES[md.parent.name] = listing_dir.parent
    try:
        return [f.message for f in cqd.find(Document.parse(md))]
    finally:
        del cqd.TREES[md.parent.name]


def test_matching_quote_is_silent_and_moved_line_is_reported(
        tmp_path: Path) -> None:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    tree = tmp_path / "examples" / "05_F"
    tree.mkdir(parents=True)
    (tree / "area.py").write_text(
        "# area.py\n\ndef area(w: int) -> int:\n    return w\n"
        'print(area("3"))\n', encoding="utf-8")
    block = (
        "# text\n\n```text\n"
        "error[invalid-argument-type]: Argument is incorrect\n"
        " --> area.py:{n}:12\n"
        "  |\n"
        '{n} | print(area("3"))\n'
        "  |            ^^^ Expected `int`\n"
        "```\n")
    md = chapters / "05_F.md"
    assert quoted(md, tree, block.format(n=5)) == []
    hits = quoted(md, tree, block.format(n=4))
    assert len(hits) == 1
    assert "area.py:4 reads" in hits[0]


def test_missing_file_is_reported_once(tmp_path: Path) -> None:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    tree = tmp_path / "examples" / "05_F"
    tree.mkdir(parents=True)
    text = ("```text\nerror[x]: y\n --> gone.py:1:1\n"
            "1 | anything\n2 | more\n```\n")
    hits = quoted(chapters / "05_F.md", tree, text)
    assert len(hits) == 1
    assert "gone.py" in hits[0]


def test_bare_fence_and_warning_blocks_count(tmp_path: Path) -> None:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    tree = tmp_path / "examples" / "05_F"
    tree.mkdir(parents=True)
    (tree / "w.py").write_text("a = 1\n", encoding="utf-8")
    text = "```\nwarning[deprecated]: z\n --> w.py:1:1\n1 | a = 2\n```\n"
    hits = quoted(chapters / "05_F.md", tree, text)
    assert len(hits) == 1 and "w.py:1 reads 'a = 1'" in hits[0]
