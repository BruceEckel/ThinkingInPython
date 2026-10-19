"""Tests for tools/pointer_words.py, on recorded spaCy parses.

The parser is a throwaway-environment subprocess, so these tests use
`tools/tests/data/pointer_words_parses.json`, the parser's real answers
for the fixture paragraphs, through a stub keyed by text.
`tools/tests/make_pointer_words_parses.py` regenerates the file.
"""

from pathlib import Path
import pytest
from tools import parsed_prose, pointer_words
from tools.markdown import Document
from tools.parsed_prose import Paragraph, RawSentence, parsed
from tools.pointer_words import find, hits, main, message
from tools.tests.make_pointer_words_parses import recorded_parser


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", tmp_path / "parses")


def paragraph(source: str) -> Paragraph:
    doc = Document.from_text(source, Path("fixture.md"))
    [[found]] = parsed([doc], recorded_parser, use_cache=False)
    return found


def messages(source: str) -> list[str]:
    found = paragraph(source)
    return [message(found, hit) for hit in hits(found)]


PROXY = "The proxy stores the level. "


@pytest.mark.parametrize("source, expected", [
    (PROXY + "It never consults the implementation again.",
     ["[IT] it -> proxy, level: It never consults the implementation "
      "again."]),
    (PROXY + "The proxy never consults the implementation again.", []),
    ("The handler checks the key. This is the fast path.",
     ["[THIS] This: This is the fast path."]),
    ("The handler checks the key. This check is the fast path.", []),
    ("It is the loop that calls the method.", []),
    ("The function runs. It returns quickly.", []),
    ("The function returns a wrapper. It keeps the name.",
     ["[IT] it -> function, wrapper: It keeps the name."]),
    (PROXY + "Then it never consults the implementation again.",
     ["[IT] it -> proxy, level: Then it never consults the "
      "implementation again."]),
    ("The responders hold the values. They are weak references.",
     ["[IT] they -> responders, values: They are weak references."]),
    ("It stores the level.",
     ["[IT] it -> (opens paragraph): It stores the level."]),
    ("Hint: this is the fast path. It stores the level.", []),
])
def test_messages(source: str, expected: list[str]) -> None:
    assert messages(source) == expected


def test_the_label_follows_the_pronoun() -> None:
    [hit] = hits(paragraph(
        "The handler checks the key. This is the fast path."))
    assert (hit.label, hit.pronoun.text, hit.candidates) == (
        "THIS", "This", ())
    [hit] = hits(paragraph(PROXY + "Then it never consults the "
                           "implementation again."))
    assert (hit.label, hit.pronoun.text, hit.candidates) == (
        "IT", "it", ("proxy", "level"))


def test_the_reported_line_is_the_sentences_first_character() -> None:
    doc = Document.from_text(
        "Some prose.\n\nThe proxy stores the level.\nIt never consults the\n"
        "implementation again.\n", Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.line == 4
    assert found.message == (
        "[IT] it -> proxy, level: It never consults the implementation "
        "again.")


def test_main_prints_every_hit_and_fails_on_request(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("The handler checks the key. This is the fast path.\n",
                    encoding="utf-8")
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "[THIS] This: This is" in out
    assert "1 pointer sentences (1 [THIS], 0 [IT])" in out
    assert main([str(path), "--fail"], recorded_parser) == 1
    capsys.readouterr()
    clean = tmp_path / "b.md"
    clean.write_text("Some prose.\n", encoding="utf-8")
    assert main([str(clean), "--fail"], recorded_parser) == 0
    assert "0 pointer sentences" in capsys.readouterr().out


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
