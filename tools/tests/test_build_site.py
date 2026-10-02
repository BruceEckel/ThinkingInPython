"""Tests for tools/build_site.py's Solutions note.

The built site, EPUB, and PDF carry only the chapters, so load_chapter()
adds one sentence under each chapter's last `## Exercises` heading that
links the chapter's Solutions file on GitHub.
"""
from pathlib import Path
import pytest
from tools import build_site
from tools.build_site import (
    SOLUTIONS_URL,
    load_chapter,
    rewrite_md_links,
)

NAME = "05_Foundations--Demo.md"
NOTE = (f"The [solutions to these exercises]({SOLUTIONS_URL}/{NAME}) "
        "are in the book's repository.")


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "Solutions").mkdir()
    monkeypatch.setattr(build_site, "ROOT", tmp_path)
    return tmp_path


def chapter(root: Path, text: str, solutions: bool = True) -> Path:
    md = root / NAME
    md.write_text(text, encoding="utf-8")
    if solutions:
        (root / "Solutions" / NAME).write_text("# S\n", encoding="utf-8")
    return md


def test_note_follows_the_exercises_heading(root: Path) -> None:
    md = chapter(root, "# Demo\n\nbody\n\n## Exercises\n\n1. First\n")
    _, body = load_chapter(md)
    assert "## Exercises\n\n" + NOTE + "\n\n1. First" in body


def test_note_gets_its_own_paragraph_without_a_blank_line(root: Path) -> None:
    md = chapter(root, "# Demo\n\n## Exercises\n1. First\n")
    _, body = load_chapter(md)
    assert "## Exercises\n\n" + NOTE + "\n\n1. First" in body


def test_no_note_without_a_solutions_file(root: Path) -> None:
    md = chapter(root, "# Demo\n\n## Exercises\n\n1. First\n", solutions=False)
    _, body = load_chapter(md)
    assert "solutions to these exercises" not in body


def test_no_note_without_an_exercises_heading(root: Path) -> None:
    md = chapter(root, "# Demo\n\nbody\n")
    _, body = load_chapter(md)
    assert "solutions to these exercises" not in body


def test_heading_inside_a_fence_is_ignored(root: Path) -> None:
    md = chapter(root, "# Demo\n\n```text\n## Exercises\n```\n\nbody\n")
    _, body = load_chapter(md)
    assert "solutions to these exercises" not in body


def test_last_exercises_heading_is_used(root: Path) -> None:
    md = chapter(root, "# Demo\n\n## Exercises\n\nx\n\n"
                       "### Exercises\n\n1. First\n")
    _, body = load_chapter(md)
    assert body.count(NOTE) == 1
    assert "### Exercises\n\n" + NOTE in body


def test_url_survives_rewrite_md_links() -> None:
    assert rewrite_md_links(NOTE) == NOTE
