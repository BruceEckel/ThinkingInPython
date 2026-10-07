"""Tests for tools/internal_names.py, on synthetic chapter trees."""

from pathlib import Path
import pytest
from tools.internal_names import (
    Hit,
    chapter_hits,
    chapters,
    load_baseline,
    main,
    write_baseline,
)

CHAPTER = "05_Foundations--Functions"
CLASS = '''\
class Box:
    def __init__(self) -> None:
        self._items: list[int] = []

    def helper(self) -> int:
        return 1

    def run(self) -> int:
        return self.helper()
'''


@pytest.fixture
def book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A one-chapter tree under an isolated root and baseline."""
    root = tmp_path.resolve()
    monkeypatch.setattr("tools.internal_names.ROOT", root)
    monkeypatch.setattr(
        "tools.internal_names.BASELINE", root / "baseline.txt")
    (root / "Chapters").mkdir()
    (root / "Chapters" / f"{CHAPTER}.md").write_text(
        "# Functions\n", encoding="utf-8")
    (root / "Examples" / CHAPTER).mkdir(parents=True)
    return root


def write_code(root: Path, text: str, name: str = "box.py") -> Path:
    path = root / "Examples" / CHAPTER / name
    path.write_text(text, encoding="utf-8")
    return path


def names(hits: list[Hit]) -> set[str]:
    return {f"{h.owner}.{h.name}" for h in hits}


def test_method_used_only_inside_is_reported(book: Path) -> None:
    write_code(book, CLASS)
    hits = chapter_hits(CHAPTER)
    assert {"Box.helper", "Box.run"} == names(hits)
    helper = next(h for h in hits if h.name == "helper")
    assert (helper.kind, helper.internal) == ("method", 1)
    assert helper.key == f"Examples/{CHAPTER}/box.py::Box.helper"


def test_method_called_from_a_demo_line_is_not(book: Path) -> None:
    write_code(book, CLASS + "\nBox().run()\nBox().helper()\n")
    assert chapter_hits(CHAPTER) == []


def test_use_in_another_file_is_not_a_hit(book: Path) -> None:
    write_code(book, CLASS)
    write_code(book, "x = 1\nprint(Box().run())\n", "demo.py")
    assert names(chapter_hits(CHAPTER)) == {"Box.helper"}


def test_prose_code_span_counts(book: Path) -> None:
    write_code(book, CLASS)
    (book / "Chapters" / f"{CHAPTER}.md").write_text(
        "Call `helper()` and `Box.run`.\n", encoding="utf-8")
    assert chapter_hits(CHAPTER) == []


def test_prose_outside_a_code_span_does_not_count(book: Path) -> None:
    write_code(book, CLASS)
    (book / "Chapters" / f"{CHAPTER}.md").write_text(
        "The helper runs the run method.\n", encoding="utf-8")
    assert names(chapter_hits(CHAPTER)) == {"Box.helper", "Box.run"}


def test_solutions_readme_counts(book: Path) -> None:
    write_code(book, CLASS)
    folder = book / "Solutions" / CHAPTER
    folder.mkdir(parents=True)
    (folder / "README.md").write_text(
        "Use `helper` and `run`.\n", encoding="utf-8")
    assert chapter_hits(CHAPTER) == []


def test_underscore_names_are_skipped(book: Path) -> None:
    write_code(book, CLASS.replace("helper", "_helper").replace(
        "run", "_run"))
    assert chapter_hits(CHAPTER) == []


def test_dataclass_field_is_skipped(book: Path) -> None:
    write_code(book, (
        "from dataclasses import dataclass\n\n"
        "@dataclass\nclass Point:\n    x: int\n"))
    assert chapter_hits(CHAPTER) == []


def test_namedtuple_field_is_skipped(book: Path) -> None:
    write_code(book, (
        "from typing import NamedTuple\n\n"
        "class Point(NamedTuple):\n    x: int\n    y: int = 0\n"))
    assert chapter_hits(CHAPTER) == []


def test_annotated_class_attribute_is_a_classattr(book: Path) -> None:
    write_code(book, "class Config:\n    limit: int = 3\n")
    [hit] = chapter_hits(CHAPTER)
    assert (hit.name, hit.kind) == ("limit", "classattr")


def test_kinds_carry_decorator_suffixes(book: Path) -> None:
    write_code(book, (
        "class Base:\n"
        "    limit = 3\n"
        "    @property\n    def size(self) -> int:\n        return 1\n"
        "    @staticmethod\n    def make() -> int:\n        return 1\n"
        "    @classmethod\n    def build(cls) -> int:\n        return 1\n"
        "    def store(self) -> None:\n        self.seen = 1\n"))
    kinds = {h.name: h.kind for h in chapter_hits(CHAPTER)}
    assert kinds == {
        "limit": "classattr", "size": "property",
        "make": "method/static", "build": "method/cls",
        "store": "method", "seen": "attr",
    }


def test_appendix_and_non_chapter_directories(book: Path) -> None:
    (book / "Chapters" / "A_Appendix.md").write_text("", encoding="utf-8")
    (book / "Examples" / "A_Appendix").mkdir()
    (book / "Examples" / "utils").mkdir()
    assert chapters() == [CHAPTER, "A_Appendix"]


def test_main_reports_then_baseline_suppresses(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_code(book, CLASS)
    assert main(["--fail"]) == 1
    out = capsys.readouterr().out
    assert "NEW" in out and "Box.helper" in out
    assert "2 new, 0 accepted" in out
    assert main([]) == 0
    capsys.readouterr()
    assert main(["--accept"]) == 0
    assert len(load_baseline()) == 2
    assert main(["--fail"]) == 0
    out = capsys.readouterr().out
    assert "Box.helper" not in out
    assert "0 new, 2 accepted" in out


def test_all_lists_accepted_hits(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_code(book, CLASS)
    write_baseline({f"Examples/{CHAPTER}/box.py::Box.helper"})
    assert main(["--all"]) == 0
    out = capsys.readouterr().out
    assert "accepted Examples" in out and "Box.helper" in out
    assert "1 new, 1 accepted" in out


def test_stale_entry_is_listed_and_accept_drops_it(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    write_code(book, CLASS)
    gone = f"Examples/{CHAPTER}/box.py::Box.gone"
    write_baseline({gone})
    assert main([]) == 0
    assert "stale" in capsys.readouterr().out
    assert main(["--accept"]) == 0
    assert gone not in load_baseline()
