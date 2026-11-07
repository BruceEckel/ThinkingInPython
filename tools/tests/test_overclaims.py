"""Tests for tools/overclaims.py's `[LEAD]` rule."""

from pathlib import Path
import pytest
from tools import overclaims
from tools.markdown import Document
from tools.overclaims import find_leads, main

CHAPTER_45 = """\
Each approach gives up one side's loop:

- The callback turns the consumer inside out:
  the body of its loop becomes `consume()`,
  a function the producer's loop calls.
- The list keeps both loops but runs the producer's loop to completion before the consumer's loop starts.
- The class turns the producer inside out:
  its loop becomes the bookkeeping in `__next__()`.
"""


def hits(text: str) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(f.line, f.message) for f in find_leads(doc)]


def test_chapter_45_fires_on_the_exempting_item() -> None:
    found = hits(CHAPTER_45)
    assert [line for line, _ in found] == [6]
    message = found[0][1]
    assert message.startswith(
        "[LEAD] Each approach gives up one side's loop: -> ")
    assert "The list keeps both loops" in message


@pytest.mark.parametrize("text", [
    "Three ways to write it:\n\n- The list keeps both loops.\n",
    "Each approach gives up a loop:\n\n"
    "- The callback inverts it.\n- The class inverts it.\n",
    "Each approach gives up a loop.\n\n- The list keeps both loops.\n",
    "Both loops run. The question has two answers:\n\n"
    "- The list keeps both loops.\n",
    "1. Supply each of these steps twice:\n"
    "   - Convert the letters.\n"
    "   - Count the words.\n"
    "2. Write two classes that both type-check.\n",
])
def test_no_hit(text: str) -> None:
    assert not hits(text)


def test_exercise_lead_in_reads_its_nested_items() -> None:
    found = hits(
        "1. Supply each of these steps twice:\n"
        "   - Convert the letters.\n"
        "   - Keep both files.\n"
        "2. Write two classes.\n")
    assert [line for line, _ in found] == [3]


def test_survey_only_and_never_baselined(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text(CHAPTER_45, encoding="utf-8")
    baseline = tmp_path / "baseline.txt"
    monkeypatch.setattr(overclaims, "BASELINE", baseline)
    assert main([str(path)]) == 0
    assert "[LEAD]" not in capsys.readouterr().out
    assert main([str(path), "--survey"]) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "[LEAD]" in out
    assert out.splitlines()[-1] == "1 survey"
    assert main([str(path), "--accept"]) == 0
    assert "[LEAD]" not in baseline.read_text(encoding="utf-8")
