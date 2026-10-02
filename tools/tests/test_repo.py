"""Tests for tools/repo.py's view of the Solutions layout.

Each chapter's solutions are `Solutions/<chapter stem>/README.md`, so a
solutions file's own stem says nothing about its chapter. These tests pin
the helpers that give the chapter back, and the directory listing that
finds both layouts' files.
"""
from pathlib import Path

import pytest

from tools.config import ROOT, SOLUTIONS_DIR
from tools.repo import (
    SOLUTIONS_MD,
    chapter_stem,
    is_solutions_file,
    md_files,
    solutions_file,
    solutions_files,
)

STEM = "05_Foundations--Functions"


def test_a_chapter_gives_its_own_stem() -> None:
    assert chapter_stem(Path("Chapters") / f"{STEM}.md") == STEM
    assert chapter_stem(f"{STEM}.md") == STEM
    assert chapter_stem(STEM) == STEM


def test_a_solutions_file_gives_its_directory_name() -> None:
    path = Path("Solutions") / STEM / SOLUTIONS_MD
    assert is_solutions_file(path)
    assert chapter_stem(path) == STEM
    assert chapter_stem(ROOT / "Solutions" / STEM / "README.md") == STEM


def test_a_readme_elsewhere_is_not_a_solutions_file() -> None:
    assert not is_solutions_file(Path("tools") / "README.md")
    assert not is_solutions_file(Path("README.md"))
    assert not is_solutions_file(Path("Solutions") / STEM / "notes.md")
    assert not is_solutions_file(Path("Chapters") / f"{STEM}.md")
    assert chapter_stem(Path("tools") / "README.md") == "README"


def test_solutions_file_builds_the_path_from_any_form_of_the_chapter(
        tmp_path: Path) -> None:
    want = SOLUTIONS_DIR / STEM / "README.md"
    assert solutions_file(STEM) == want
    assert solutions_file(f"{STEM}.md") == want
    assert solutions_file(Path("Chapters") / f"{STEM}.md") == want
    assert solutions_file(want) == want
    assert solutions_file(STEM, tmp_path) == tmp_path / STEM / "README.md"


def build(tmp_path: Path) -> Path:
    solutions = tmp_path / "Solutions"
    for stem in ("03_B", "02_A"):
        (solutions / stem).mkdir(parents=True)
        (solutions / stem / "README.md").write_text("# s\n", encoding="utf-8")
        (solutions / stem / "exercise_1.py").write_text("", encoding="utf-8")
    (solutions / "loose").mkdir()
    (solutions / "loose" / "notes.md").write_text("", encoding="utf-8")
    return solutions


def test_solutions_files_are_the_sorted_readmes(tmp_path: Path) -> None:
    solutions = build(tmp_path)
    assert solutions_files(solutions) == [
        solutions / "02_A" / "README.md", solutions / "03_B" / "README.md"]


def test_md_files_on_a_nested_solutions_tree(tmp_path: Path) -> None:
    solutions = build(tmp_path)
    assert md_files([solutions]) == solutions_files(solutions)


def test_md_files_on_a_flat_directory_is_unchanged(tmp_path: Path) -> None:
    for name in ("b.md", "a.md", "c.txt"):
        (tmp_path / name).write_text("", encoding="utf-8")
    assert md_files([tmp_path]) == [tmp_path / "a.md", tmp_path / "b.md"]


def test_md_files_names_a_file_directly(tmp_path: Path) -> None:
    one = tmp_path / "one.md"
    assert md_files([one]) == [one]


@pytest.mark.book
def test_the_real_solutions_tree_has_one_readme_per_chapter_folder() -> None:
    files = md_files([SOLUTIONS_DIR])
    assert files == solutions_files()
    assert all(p.name == SOLUTIONS_MD for p in files)
    assert files, "Solutions/ holds no chapter folders"
