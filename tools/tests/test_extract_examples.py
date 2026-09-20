"""Tests for tools/extract_examples.py (stray classification)."""
from pathlib import Path

from tools.extract_examples import classify_strays


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
