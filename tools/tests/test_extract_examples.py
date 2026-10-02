"""Tests for tools/extract_examples.py (stray classification)."""
from pathlib import Path

import pytest

from tools import extract_solutions
from tools.config import SOLUTIONS_MD
from tools.extract import extract
from tools.extract_examples import (
    classify_strays,
    find_strays,
    is_derived,
    report_strays,
    route,
)
from tools.markdown import Document
from tools.repo import md_files


def chapters(tmp_path: Path, **files: str) -> list[str | Path]:
    """Write a Markdown tree and return it as a `search` argument."""
    for stem, text in files.items():
        (tmp_path / f"{stem}.md").write_text(text, encoding="utf-8")
    return [tmp_path]


def test_a_name_its_own_chapter_mentions_is_referenced(tmp_path: Path) -> None:
    search = chapters(tmp_path, ch30="Run `helper.py` by hand.\n")
    assert classify_strays(["ch30/helper.py"], search) == ([], ["ch30/helper.py"])


def test_a_name_no_chapter_mentions_is_orphaned(tmp_path: Path) -> None:
    search = chapters(tmp_path, ch30="Nothing here names it.\n")
    assert classify_strays(["ch30/helper.py"], search) == (["ch30/helper.py"], [])


def test_another_chapters_listing_of_the_same_name_does_not_rescue_it(
    tmp_path: Path,
) -> None:
    """The renumbering case: every chapter has an exercise_2.py.

    Chapter 2's own listing must not make chapter 30's leftover look
    referenced, or `--prune` can never delete it.
    """
    search = chapters(tmp_path,
                      ch02="```python\n# exercise_2.py\n```\n",
                      ch30="```python\n# exercise_3.py\n```\n")
    orphaned, referenced = classify_strays(["ch30/exercise_2.py"], search)
    assert orphaned == ["ch30/exercise_2.py"]
    assert referenced == []


def test_a_stray_outside_any_chapter_dir_searches_every_chapter(
    tmp_path: Path,
) -> None:
    """utils/ has no Markdown of its own, so any chapter may name it."""
    search = chapters(tmp_path,
                      ch02="Nothing.\n",
                      ch30="Every chapter imports `record.py`.\n")
    assert classify_strays(["utils/record.py"], search) == ([], ["utils/record.py"])


def test_a_longer_name_containing_the_stray_does_not_count(tmp_path: Path) -> None:
    search = chapters(tmp_path, ch30="```python\n# exercise_2_narrowing.py\n```\n")
    assert classify_strays(["ch30/exercise_2.py"], search) == (["ch30/exercise_2.py"], [])


# ── Solutions/<chapter>/README.md beside its generated code ──────────────────

def solutions_tree(tmp_path: Path, **readmes: str) -> Path:
    """Solutions/<stem>/README.md for each keyword; returns Solutions/."""
    for stem, text in readmes.items():
        folder = tmp_path / "Solutions" / stem
        folder.mkdir(parents=True)
        (folder / "README.md").write_text(text, encoding="utf-8")
    return tmp_path / "Solutions"


def test_a_stray_is_classified_by_its_chapters_readme(tmp_path: Path) -> None:
    solutions = solutions_tree(
        tmp_path, ch30="Run `helper.py` by hand.\n", ch02="Nothing.\n")
    assert classify_strays(["ch30/helper.py"], [solutions]) == (
        [], ["ch30/helper.py"])
    assert classify_strays(["ch02/helper.py"], [solutions]) == (
        ["ch02/helper.py"], [])


def test_the_source_readme_is_not_a_stray(tmp_path: Path) -> None:
    solutions = solutions_tree(tmp_path, ch30="# s\n")
    (solutions / "ch30" / "exercise_1.py").write_text("", encoding="utf-8")
    (solutions / "ch30" / "leftover.py").write_text("", encoding="utf-8")
    result = extract([Document.parse(p) for p in md_files([solutions])],
                     [route])
    strays = find_strays(result, solutions, source_md=SOLUTIONS_MD)
    assert strays == ["ch30/exercise_1.py", "ch30/leftover.py"]


def test_without_the_source_name_a_readme_is_a_stray(tmp_path: Path) -> None:
    solutions = solutions_tree(tmp_path, ch30="# s\n")
    result = extract([], [route])
    assert find_strays(result, solutions) == ["ch30/README.md"]


def test_prune_deletes_a_stray_py_and_never_a_markdown_file(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    solutions = solutions_tree(tmp_path, ch30="Names nothing.\n")
    stray = solutions / "ch30" / "gone.py"
    stray.write_text("", encoding="utf-8")
    notes = solutions / "ch30" / "notes.md"
    notes.write_text("keep me\n", encoding="utf-8")
    readme = solutions / "ch30" / "README.md"
    before = readme.read_bytes()
    orphaned, _ = report_strays(
        ["ch30/gone.py", "ch30/notes.md", "ch30/README.md"], solutions,
        search=[solutions], prune=True)
    assert not stray.exists()
    assert notes.read_text(encoding="utf-8") == "keep me\n"
    assert readme.read_bytes() == before
    assert orphaned == ["ch30/notes.md", "ch30/README.md"]
    assert "left alone" in capsys.readouterr().out


def test_write_into_a_committed_tree_leaves_the_readme_alone(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stem = "02_Foundations--Tour"
    text = "# Tour\n\n```python\n# exercise_1.py\nprint(1)\n```\n"
    solutions = solutions_tree(tmp_path, **{stem: text})
    readme = solutions / stem / "README.md"
    before = readme.read_bytes()
    monkeypatch.setattr(extract_solutions, "SOLUTIONS_DIR", solutions)
    assert not is_derived(solutions)
    assert extract_solutions.main(["--write", "-o", str(solutions)]) == 0
    assert readme.read_bytes() == before
    assert (solutions / stem / "exercise_1.py").read_text(
        encoding="utf-8") == "# exercise_1.py\nprint(1)\n"


def test_check_and_prune_leave_the_readme_in_a_synced_tree(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    stem = "02_Foundations--Tour"
    text = "# Tour\n\n```python\n# exercise_1.py\nprint(1)\n```\n"
    solutions = solutions_tree(tmp_path, **{stem: text})
    readme = solutions / stem / "README.md"
    before = readme.read_bytes()
    monkeypatch.setattr(extract_solutions, "SOLUTIONS_DIR", solutions)
    monkeypatch.setattr(extract_solutions, "COMMITTED_DIR", solutions)
    extract_solutions.main(["--write", "-o", str(solutions)])
    assert extract_solutions.main([]) == 0
    assert "README" not in capsys.readouterr().out
    assert extract_solutions.main(["--prune"]) == 0
    assert readme.read_bytes() == before
