"""Tests for tools/passive_voice.py, on recorded spaCy parses.

The parser is a throwaway-environment subprocess, so these tests use
`tools/tests/data/passive_voice_parses.json`, the parser's real answers
for the fixture paragraphs, through a stub keyed by text.
`tools/tests/make_passive_voice_parses.py` regenerates the file.
"""

from pathlib import Path
import pytest
from tools import parsed_prose, passive_voice
from tools.markdown import Document
from tools.parsed_prose import Paragraph, RawSentence, parsed
from tools.passive_voice import find, hits, main
from tools.tests.make_passive_voice_parses import recorded_parser


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
    ("The method is called by the loop.", ["PASSIVE+BY"]),
    ("The value is written once.", ["PASSIVE"]),
    ("A value that is read by two threads needs a lock.", ["PASSIVE+BY"]),
    ("The list is unchanged.", []),
    ("A value stored in the class stays there.", []),
    ("The loop calls the method.", []),
    ("The file got overwritten.", ["PASSIVE"]),
    ("Hint: the result is cached.", []),
    ("The loop runs first. The value is written once.", ["PASSIVE"]),
])
def test_labels(source: str, expected: list[str]) -> None:
    assert labels(source) == expected


def test_a_hit_names_its_auxiliary_and_participle() -> None:
    [hit] = hits(paragraph("The method is called by the loop."))
    assert (hit.auxiliary.text, hit.verb.text) == ("is", "called")
    [hit] = hits(paragraph("The file got overwritten."))
    assert (hit.auxiliary.text, hit.verb.text) == ("got", "overwritten")


def test_the_reported_line_is_the_sentences_first_character() -> None:
    doc = Document.from_text(
        "Some prose.\n\nThe loop runs first,\nand the value is written\n"
        "once.\n", Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.line == 3
    assert found.message == (
        "[PASSIVE] is written: The loop runs first, and the value is "
        "written once.")


def test_the_second_sentence_maps_to_its_own_line() -> None:
    doc = Document.from_text(
        "The loop runs first. The value is written once.\n",
        Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.line == 1
    doc = Document.from_text(
        "Some prose.\n\nThe loop runs first.\nThe value is written once.\n",
        Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.line == 4
    assert found.message == "[PASSIVE] is written: The value is written once."


def test_main_reports_without_failing_and_accepts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(passive_voice, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("The method is called by the loop.\n", encoding="utf-8")
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "NEW" in out and "[PASSIVE+BY] is called: The method" in out
    assert "1 new, 0 accepted" in out
    assert main([str(path), "--fail"], recorded_parser) == 1
    capsys.readouterr()
    shown = passive_voice.display(path)
    passive_voice.write_baseline({passive_voice.key(
        shown, "[PASSIVE+BY] is called: The method is called by the loop.")})
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
    monkeypatch.setattr(passive_voice, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")
    shown = passive_voice.display(path)
    passive_voice.write_baseline({passive_voice.key(
        shown, "[PASSIVE] is gone: Gone.")})
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "stale" in out and "0 new, 0 accepted, 1 stale" in out


def test_a_missing_baseline_is_empty(tmp_path: Path) -> None:
    assert passive_voice.load_baseline(tmp_path / "none.txt") == set()


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
