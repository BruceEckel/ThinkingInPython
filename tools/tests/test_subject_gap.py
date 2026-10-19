"""Tests for tools/subject_gap.py, with the spaCy half stubbed out.

The parser runs in a throwaway environment, so these tests hand `find()`
and `main()` a fake parser that answers with canned hits, and check the
plumbing around it: paragraph collection, offset-to-line mapping, the
printed form, the baseline key, and the unavailable-parser path.
"""

from pathlib import Path
import pytest
from tools import subject_gap
from tools.markdown import Document
from tools.subject_gap import (
    Hit,
    ParserUnavailable,
    find,
    key,
    main,
    message,
)

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


def canned(texts: list[str], gap: int) -> list[list[Hit]]:
    """A hit on 'action' in any paragraph that contains the chapter 31 sentence."""
    out: list[list[Hit]] = []
    for text in texts:
        hits: list[Hit] = []
        marker = "so an action"
        if marker in text:
            hits.append({
                "offset": text.index(marker) + len("so an "),
                "subject": "action",
                "verb": "appears",
                "gap": gap,
                "kinds": ["relcl"],
                "sentence": text,
            })
        out.append(hits)
    return out


def test_find_maps_the_subject_offset_to_its_line() -> None:
    doc = Document.from_text(TEXT, Path("fixture.md"))
    found = list(find([doc], canned))
    assert len(found) == 1
    assert found[0].line == 6
    assert found[0].message.startswith("[relcl] action .. appears: ")


def test_find_sends_one_text_per_paragraph() -> None:
    seen: list[list[str]] = []

    def spy(texts: list[str], gap: int) -> list[list[Hit]]:
        seen.append(texts)
        return [[] for _ in texts]

    doc = Document.from_text(TEXT, Path("fixture.md"))
    assert list(find([doc], spy)) == []
    assert seen == [["Intro paragraph.",
                     "A state's row holds its action, so an action that must "
                     "run on every entry into that state appears once."]]


def test_find_with_no_prose_never_calls_the_parser() -> None:
    doc = Document.from_text("```python\nx = 1\n```\n", Path("f.md"))

    def boom(texts: list[str], gap: int) -> list[list[Hit]]:
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
    assert main([str(path)], canned) == 0
    out = capsys.readouterr().out
    assert "NEW " in out and "1 new, 0 accepted" in out
    assert main([str(path), "--fail"], canned) == 1
    capsys.readouterr()
    sentence = " ".join(TEXT.splitlines()[4:7])
    subject_gap.write_baseline({key(subject_gap.display(path),
                                    "[relcl] action .. appears: " + sentence)})
    assert main([str(path), "--fail"], canned) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out


def test_main_survives_a_missing_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")

    def gone(texts: list[str], gap: int) -> list[list[Hit]]:
        raise ParserUnavailable("uv: command not found")

    assert main([str(path), "--fail"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err
