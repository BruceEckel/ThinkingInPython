"""Tests for tools/trailing_tags.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.trailing_tags import find, main


def hits(text: str) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(f.line, f.message) for f in find(doc)]


@pytest.mark.parametrize("text", [
    "An action belongs in that state's row, written once.",
    "Each contains the loop that iterates over the data, written once.",
    "`bind()` is the sequence `composing.py` repeats at every "
    "step, written once.",
    "The list is kept, unchanged.",
    "The key is a duplicate, the same rule any duplicate key follows.",
])
def test_r32_hit(text: str) -> None:
    assert [m[:6] for _, m in hits(text)] == ["[R32] "]


@pytest.mark.parametrize("text", [
    "In return, the action can read the input.",
    "The trade-off is size.",
    "On the plus side, it is fast.",
    "The price of `__getattr__()` is a slower lookup.",
    "What you get back is a list.",
])
def test_r35_hit(text: str) -> None:
    assert [m[:6] for _, m in hits(text)] == ["[R35] "]


@pytest.mark.parametrize("text", [
    "The class is a `logged` instance, stored as a class attribute.",
    "The call is made, then the result is read.",
    "It runs, written in C.",
    "```python\n# in return, written once\n```",
    "# In return",
])
def test_no_hit(text: str) -> None:
    assert not hits(text)


def test_line_is_the_clause_end() -> None:
    assert hits("Intro.\n\nThe row holds it,\nwritten once.\n")[0][0] == 4


def test_main_reports_without_failing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("In return, it reads.\n", encoding="utf-8")
    assert main([str(path)]) == 0
    assert "1 new" in capsys.readouterr().out
    assert main([str(path), "--fail"]) == 1
