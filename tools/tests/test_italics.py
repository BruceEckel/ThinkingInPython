"""tools/italics.py: emphasis, repeated, and late italics."""

from pathlib import Path
import pytest
from tools.italics import find, key, load_baseline, main, write_baseline
from tools.markdown import Document
from tools.stranded_prepositions import display

NAMES = frozenset({"visitor"})


def hits(text: str) -> list[str]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [f.message.split(" :: ")[0] for f in find(doc, NAMES)]


def test_first_italic_is_an_introduction() -> None:
    assert hits("A *closure* captures names.\n") == []


def test_function_word_is_emphasis() -> None:
    assert hits("It *is* the same.\n") == ["[EMPHASIS] *is*"]
    assert hits("Strategy defers *how*.\n") == ["[EMPHASIS] *how*"]


def test_second_italic_repeats() -> None:
    text = "A *closure* is a function.\n\nEach *closure* holds a cell.\n"
    assert hits(text) == ["[REPEAT] *closure*"]


def test_term_used_before_its_italics() -> None:
    text = "The event loops run.\n\nAn *event loop* schedules tasks.\n"
    assert hits(text) == ["[EARLIER] *event loop*"]


def test_earlier_use_in_the_same_sentence() -> None:
    assert hits("The task, a *task*, runs.\n") == ["[EARLIER] *task*"]


@pytest.mark.parametrize("text", [
    "Read *Design Patterns* first.\n\nThen *Design Patterns* again.\n",
    "A *Visitor* walks.\n\nThe *Visitor* again.\n",
    "Use **bold** and **bold** twice.\n",
    "Call `*args` and `*args` freely.\n",
    "```\nA *closure* here.\n```\n\nThe *closure* introduced.\n",
    "# The *heading*\n\nThe *heading* introduced.\n",
    "> A *quote*.\n\nThe *quote* introduced.\n",
])
def test_skips(text: str) -> None:
    assert hits(text) == []


def test_line_is_the_spans_line() -> None:
    doc = Document.from_text(
        "A closure\ncaptures. The *closure*\nruns.\n", Path("f.md"))
    (finding,) = find(doc, NAMES)
    assert finding.line == 2


@pytest.fixture
def book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Two files with one hit each and an isolated baseline path."""
    root = tmp_path.resolve()
    monkeypatch.setattr("tools.stranded_prepositions.ROOT", root)
    monkeypatch.setattr("tools.italics.ROOT", root)
    monkeypatch.setattr("tools.italics.BASELINE", root / "base.txt")
    monkeypatch.setattr("tools.italics.pattern_names", lambda: NAMES)
    (root / "Chapters").mkdir()
    (root / "Solutions").mkdir()
    for name in ("a.md", "b.md"):
        (root / "Chapters" / name).write_text(
            "It *is* so.\n", encoding="utf-8")
    return root / "Chapters" / "a.md"


def test_accept_with_paths_touches_only_their_entries(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--fail"]) == 1
    assert "2 new, 0 accepted" in capsys.readouterr().out
    other = key("Chapters/b.md", "[EMPHASIS] *was* :: It *was* so")
    write_baseline({other})
    assert main([str(book), "--accept"]) == 0
    capsys.readouterr()
    base = book.parent.parent / "base.txt"
    assert load_baseline(base) == {
        other, key(display(book), "[EMPHASIS] *is* :: It *is* so")}
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "1 new, 1 accepted, 1 stale" in out
    assert "NEW      Chapters/b.md:1:" in out
