"""Tests for tools/check_skip_lists.py."""
from pathlib import Path

from tools.check_skip_lists import numbered_patterns, stale
from tools.repo import load_glob_list

LIST = """\
# A comment, then a blank line.

07_Classes/gui_view.py
38_Simulation/*/*_view.py  # a trailing comment
# [by-hand]
19_Concurrency/renamed_away.py
"""

def build(tmp_path: Path) -> tuple[Path, Path, Path]:
    examples = tmp_path / "Examples"
    solutions = tmp_path / "SolutionsCode"
    for tree, rel in [(examples, "07_Classes/gui_view.py"),
                      (solutions, "38_Simulation/rats/rats_view.py")]:
        path = tree / rel
        path.parent.mkdir(parents=True)
        path.write_text("", encoding="utf-8")
    skip = tmp_path / "norun.txt"
    skip.write_text(LIST, encoding="utf-8")
    return skip, examples, solutions

def test_line_numbers_and_patterns_match_the_loader(tmp_path: Path) -> None:
    skip, _, _ = build(tmp_path)
    found = numbered_patterns(skip)
    assert found == [
        (3, "07_Classes/gui_view.py"),
        (4, "38_Simulation/*/*_view.py"),
        (6, "19_Concurrency/renamed_away.py"),
    ]
    assert [pattern for _, pattern in found] == load_glob_list(skip)

def test_a_pattern_passes_when_either_tree_matches(tmp_path: Path) -> None:
    skip, examples, solutions = build(tmp_path)
    findings = stale((skip,), (examples, solutions))
    assert [(f.line, f.path) for f in findings] == [(6, skip)]
    assert "`19_Concurrency/renamed_away.py`" in findings[0].message
    assert "Examples/ or SolutionsCode/" in findings[0].message

def test_pycache_does_not_keep_a_pattern_alive(tmp_path: Path) -> None:
    skip, examples, solutions = build(tmp_path)
    cached = examples / "19_Concurrency/__pycache__/renamed_away.py"
    cached.parent.mkdir(parents=True)
    cached.write_text("", encoding="utf-8")
    skip.write_text("19_Concurrency/*/renamed_away.py\n", encoding="utf-8")
    assert len(stale((skip,), (examples, solutions))) == 1

def test_a_missing_list_or_tree_is_not_an_error(tmp_path: Path) -> None:
    assert stale((tmp_path / "absent.txt",), (tmp_path / "Nowhere",)) == []

def test_the_real_lists_are_clean() -> None:
    assert stale() == []
