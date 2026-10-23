"""Tests for tools/expletives.py, on recorded spaCy parses.

The parser is a throwaway-environment subprocess, so these tests use
`tools/tests/data/expletives_parses.json`, the parser's real answers
for the fixture paragraphs, through a stub keyed by text.
`tools/tests/make_expletives_parses.py` regenerates the file.
"""

from pathlib import Path
import pytest
from tools import expletives, parsed_prose
from tools.expletives import find, hits, main
from tools.markdown import Document
from tools.parsed_prose import Paragraph, RawSentence, parsed
from tools.tests.make_expletives_parses import recorded_parser


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", tmp_path / "parses")


def paragraph(source: str) -> Paragraph:
    doc = Document.from_text(source, Path("fixture.md"))
    [[found]] = parsed([doc], recorded_parser, use_cache=False)
    return found


def labels(source: str) -> list[str]:
    return [hit.label for hit in hits(paragraph(source))]


@pytest.mark.parametrize("source, expected", [
    ("There is a simpler design.", ["THERE"]),
    ("A simpler design exists.", []),
    ("There are three parts.", ["THERE"]),
    ("The loop calls the method.", []),
    ("It is easy to add a state.", ["IT-IS"]),
    ("Adding a state is easy.", []),
    ("It is a record.", []),
    ("It is true that the loop stops.", ["IT-IS"]),
    ("Put the file there.", []),
    ("Caching there is one way to build a Singleton.", []),
    ("In hindsight, it might have been better to name the file.",
     ["IT-IS"]),
    ('The message says "there is no such file".', []),
    ("Without a guard, there is a race.", ["THERE"]),
    ("Hint: there is a race.", []),
    ("There is a race, and it is easy to add a lock.",
     ["THERE", "IT-IS"]),
])
def test_labels(source: str, expected: list[str]) -> None:
    assert labels(source) == expected


def test_a_hit_names_its_frame() -> None:
    doc = Document.from_text("There is a simpler design.", Path("f.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.message == (
        "[THERE] there is: There is a simpler design.")
    doc = Document.from_text("It is easy to add a state.", Path("f.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.message.startswith("[IT-IS] it is easy: ")
    doc = Document.from_text(
        "In hindsight, it might have been better to name the file.",
        Path("f.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.message.startswith(
        "[IT-IS] it might have been better: ")


def test_two_constructions_in_one_sentence_report_twice() -> None:
    doc = Document.from_text(
        "There is a race, and it is easy to add a lock.\n",
        Path("fixture.md"))
    found = list(find([doc], recorded_parser))
    assert [f.message.split("]")[0] for f in found] == ["[THERE", "[IT-IS"]
    assert {f.line for f in found} == {1}


def test_main_reports_without_failing_and_accepts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(expletives, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("There is a simpler design.\n", encoding="utf-8")
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "NEW" in out and "[THERE] there is: There is a simpler" in out
    assert "1 new, 0 accepted" in out
    assert main([str(path), "--fail"], recorded_parser) == 1
    capsys.readouterr()
    shown = expletives.display(path)
    expletives.write_baseline({expletives.key(
        shown, "[THERE] there is: There is a simpler design.")})
    assert main([str(path), "--fail"], recorded_parser) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out
    assert main([str(path), "--all"], recorded_parser) == 0
    assert "accepted" in capsys.readouterr().out
    assert main([str(path), "--accept"], recorded_parser) == 0
    assert "added 0, dropped 0" in capsys.readouterr().out


def test_a_stale_entry_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(expletives, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")
    shown = expletives.display(path)
    expletives.write_baseline({expletives.key(
        shown, "[THERE] there is: Gone.")})
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "stale" in out and "0 new, 0 accepted, 1 stale" in out


def test_a_missing_baseline_is_empty(tmp_path: Path) -> None:
    assert expletives.load_baseline(tmp_path / "none.txt") == set()


def test_main_survives_a_missing_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")

    def gone(texts: list[str]) -> list[list[RawSentence]]:
        raise parsed_prose.ParserUnavailable("uv: command not found")

    assert main([str(path), "--fail"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err
    assert main([str(path), "--calibrate"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err
