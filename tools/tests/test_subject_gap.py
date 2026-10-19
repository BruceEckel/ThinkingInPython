"""Tests for tools/subject_gap.py, with the spaCy half stubbed out.

The parser runs in a throwaway environment, so these tests hand `find()`
and `main()` a stub parser: the recorded real parse of the chapter 31
sentence (`tools/tests/data/sentence_shapes_parses.json`) for the rule,
and an empty parse for the plumbing. They check the rule on the token
table, offset-to-line mapping, the printed form, the baseline key, and
the unavailable-parser path.
"""

from pathlib import Path
import pytest
from tools import parsed_prose, subject_gap
from tools.markdown import Document
from tools.parsed_prose import RawSentence
from tools.subject_gap import (
    Hit,
    ParserUnavailable,
    find,
    key,
    main,
    message,
)
from tools.tests.make_sentence_shapes_parses import recorded_parser

SENTENCE = ("A state's row holds its action, so an action that must "
            "run on every entry into that state appears once.")
TEXT = (
    "# Heading\n"
    "\n"
    "Intro paragraph.\n"
    "\n"
    "A state's row holds its action,\n"
    "so an action that must run on every entry into that state\n"
    "appears once.\n"
    "\n"
    "```python\n"
    "# not prose\n"
    "```\n"
)


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", tmp_path / "parses")


def empty(texts: list[str]) -> list[list[RawSentence]]:
    return [[] for _ in texts]


def test_find_maps_the_subject_to_its_line() -> None:
    doc = Document.from_text(TEXT, Path("fixture.md"))
    found = list(find([doc], recorded_parser))
    assert len(found) == 1
    assert found[0].line == 6
    assert found[0].message.startswith("[relcl] action .. appears: ")
    assert found[0].message.endswith(SENTENCE)


def test_a_higher_gap_finds_nothing() -> None:
    doc = Document.from_text(TEXT, Path("fixture.md"))
    assert list(find([doc], recorded_parser, gap=30)) == []


def test_find_sends_one_text_per_paragraph() -> None:
    seen: list[list[str]] = []

    def spy(texts: list[str]) -> list[list[RawSentence]]:
        seen.append(texts)
        return empty(texts)

    doc = Document.from_text(TEXT, Path("fixture.md"))
    assert list(find([doc], spy)) == []
    assert seen == [["Intro paragraph.", SENTENCE]]


def test_find_with_no_prose_never_calls_the_parser() -> None:
    doc = Document.from_text("```python\nx = 1\n```\n", Path("f.md"))

    def boom(texts: list[str]) -> list[list[RawSentence]]:
        raise AssertionError("parser called")

    assert list(find([doc], boom)) == []


def test_message_and_key_normalize_whitespace() -> None:
    hit: Hit = {"offset": 0, "subject": "a", "verb": "is", "gap": 9,
                "kinds": ["acl", "prep"], "sentence": "x  y\nz"}
    assert message(hit) == "[acl,prep] a .. is: x y z"
    assert key("Chapters/a.md", "x  y") == "Chapters/a.md\tx y"


def test_main_reports_and_accepts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(subject_gap, "BASELINE", tmp_path / "baseline.txt")
    path = tmp_path / "a.md"
    path.write_text(TEXT, encoding="utf-8")
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "NEW " in out and "1 new, 0 accepted" in out
    assert main([str(path), "--fail"], recorded_parser) == 1
    capsys.readouterr()
    subject_gap.write_baseline({key(
        subject_gap.display(path),
        "[relcl] action .. appears: " + SENTENCE)})
    assert main([str(path), "--fail"], recorded_parser) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out


def test_main_survives_a_missing_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")

    def gone(texts: list[str]) -> list[list[RawSentence]]:
        raise ParserUnavailable("uv: command not found")

    assert main([str(path), "--fail"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err
