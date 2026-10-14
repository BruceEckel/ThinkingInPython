"""Tests for tools/stranded_possessives.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.stranded_possessives import find, main


def hits(text: str) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(f.line, f.message) for f in find(doc)]


@pytest.mark.parametrize("text", [
    "The call has the subclass's type, not the base's.",
    "The catalog above is GoF's.",
    "The engine is the chapter's.",
    "It finds the proxy's, which hides the rest.",
    "The total that `a` reports is `Tally`'s.",
    "The base's is hidden (the subclass's).",
    "The type is the subclass's\nand the base's is hidden.",
])
def test_hit(text: str) -> None:
    assert hits(text)


@pytest.mark.parametrize("text", [
    "It's the base's type.",
    "Let's use the wrapper's `__dict__`.",
    "The subclass's\ntype is not the base's type.",
    "That's what the chapter's example shows.",
    "```python\n# the base's\n```",
    "# The base's",
])
def test_no_hit(text: str) -> None:
    assert not hits(text)


def test_line_is_the_possessives() -> None:
    assert hits("Intro.\n\nThe type\nis the base's.\n")[0][0] == 4


def test_main_reports_without_failing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("The engine is the chapter's.\n", encoding="utf-8")
    assert main([str(path)]) == 0
    assert "1 new" in capsys.readouterr().out
    assert main([str(path), "--fail"]) == 1
