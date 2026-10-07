"""Tests for tools/positional_refs.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.positional_refs import (
    display,
    find,
    key,
    load_baseline,
    main,
)

LOOP = "```python\nfor a in x:\n    pass\nfor b in y:\n    pass\n```\n"
ONE = "```python\nprint(1)\nprint(2)\n```\n"


def hits(text: str) -> list[tuple[int, str, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(h.line, h.kind, h.phrase) for h in find(doc)]


def test_ordinal_span_hit() -> None:
    text = ONE + "\nThe second `print()` shows two.\n"
    assert hits(text) == [(6, "ordinal+span", "The second `print()`")]


def test_ordinal_noun_hit() -> None:
    text = ONE + "\nThe last line prints two.\n"
    assert hits(text) == [(6, "ordinal+noun", "The last line")]


def test_line_number_hit() -> None:
    text = ONE + "\nSee line 3 for the call.\n"
    assert [k for _, k, _ in hits(text)] == ["line-number"]


def test_line_rel_and_n_lines() -> None:
    text = ONE + "\nThe line above sets it, two lines later it ends.\n"
    assert [k for _, k, _ in hits(text)] == ["line-rel", "n-lines"]


def test_construct_hit_needs_two() -> None:
    text = LOOP + "\nThe `for` loop runs.\n"
    assert [k for _, k, _ in hits(text)] == ["construct x2"]
    single = "```python\nfor a in x:\n    pass\n```\n"
    assert hits(single + "\nThe `for` loop runs.\n") == []


def test_construct_ignores_comments() -> None:
    text = ("```python\nfor a in x:  # for each\n    pass\n```\n"
            "\nThe `for` loop runs.\n")
    assert hits(text) == []


def test_first_argument_is_not_a_hit() -> None:
    assert hits(ONE + "\nThe first argument is a name.\n") == []


def test_citation_sentence_is_skipped() -> None:
    text = ONE + "\nThe second `print()` at `[1]` shows two.\n"
    assert hits(text) == []


def test_prose_above_first_listing_is_skipped() -> None:
    text = "The last line matters.\n\n" + ONE
    assert hits(text) == []


def test_heading_ends_the_region() -> None:
    text = ONE + "\n# Next\n\nThe last line matters.\n"
    assert hits(text) == []


def test_no_split_inside_code_span() -> None:
    text = ONE + "\nThe `self.x` call. The last line (see `a? b`) ends.\n"
    found = hits(text)
    assert [k for _, k, _ in found] == ["ordinal+noun"]


def test_sentence_is_whole_sentence() -> None:
    doc = Document.from_text(
        ONE + "\nThe `self.x` is set.\nThe last line\nprints two.\n",
        Path("fixture.md"))
    (hit,) = find(doc)
    assert hit.sentence == "The last line prints two."
    assert hit.line == 7


def test_key_has_no_line_number() -> None:
    k = key("a.md", "the last line", "The  last line\tends.")
    assert k == "a.md\tthe last line\tThe last line ends."


@pytest.fixture
def book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path.resolve()
    monkeypatch.setattr("tools.positional_refs.ROOT", root)
    monkeypatch.setattr("tools.stranded_prepositions.ROOT", root)
    monkeypatch.setattr(
        "tools.positional_refs.BASELINE", root / "baseline.txt")
    (root / "Chapters").mkdir()
    (root / "Solutions").mkdir()
    path = root / "Chapters" / "a.md"
    path.write_text(ONE + "\nThe last line prints two.\n",
                    encoding="utf-8")
    return path


def test_accept_then_zero_new(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--fail"]) == 1
    assert "1 new, 0 accepted" in capsys.readouterr().out
    assert main(["--accept"]) == 0
    capsys.readouterr()
    entries = load_baseline(book.parent.parent / "baseline.txt")
    assert len(entries) == 1
    assert next(iter(entries)).startswith(display(book) + "\t")
    assert main(["--fail"]) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out


def test_edit_retires_entry(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    main(["--accept"])
    capsys.readouterr()
    book.write_text(ONE + "\nThe last line prints one.\n",
                    encoding="utf-8")
    assert main([]) == 0
    assert "1 new, 0 accepted, 1 stale" in capsys.readouterr().out


def test_accept_refuses_paths(book: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(book), "--accept"])
