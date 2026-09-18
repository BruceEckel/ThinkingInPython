"""Tests for tools/by_hand.py. None of them opens a window."""
from pathlib import Path

import pytest

from tools import by_hand
from tools.by_hand import by_hand_patterns, resolve, run_all
from tools.config import NORUN_FILE
from tools.repo import load_glob_list

# ── the header inside norun.txt ───────────────────────────────────────────────

NORUN = """\
# A comment.
06_Modules/a_package/module4.py

# [by-hand]
# Tkinter views.
30_Observer/box_view.py
38_Simulation/*/*_view.py  # a trailing comment
# [something-else]
99_Later/prompt.py
"""

def test_only_the_by_hand_section_is_read() -> None:
    assert by_hand_patterns(NORUN) == [
        "30_Observer/box_view.py",
        "38_Simulation/*/*_view.py",
    ]

def test_no_header_means_nothing_starts() -> None:
    assert by_hand_patterns("30_Observer/box_view.py\n") == []

def test_the_header_hides_nothing_from_make_run(tmp_path: Path) -> None:
    # run_examples.py reads the same file through load_glob_list(), and a
    # header is a comment to it: every pattern still skips.
    path = tmp_path / "norun.txt"
    path.write_text(NORUN, encoding="utf-8")
    assert len(load_glob_list(path)) == 4

# ── patterns to files ─────────────────────────────────────────────────────────

def tree_with(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (tmp_path / "utils").mkdir(exist_ok=True)
    return tmp_path

def test_resolve_matches_globs_and_reports_stale(tmp_path: Path) -> None:
    tree = tree_with(tmp_path, {
        "30_Observer/box_view.py": "",
        "38_Simulation/rats/rats_view.py": "",
        "38_Simulation/rats/rats.py": "",
    })
    found, stale = resolve(
        ["30_Observer/box_view.py", "38_Simulation/*/*_view.py",
         "31_Gone/vending_view.py"], tree)
    assert [p.name for p in found] == ["box_view.py", "rats_view.py"]
    assert stale == ["31_Gone/vending_view.py"]

def test_a_file_two_patterns_match_starts_once(tmp_path: Path) -> None:
    tree = tree_with(tmp_path, {"30_Observer/box_view.py": ""})
    found, stale = resolve(["30_Observer/*.py", "*/box_view.py"], tree)
    assert len(found) == 1
    assert stale == []

# ── the real file, listed and never started ───────────────────────────────────

def test_list_prints_the_real_entries_and_opens_nothing(
        capsys: pytest.CaptureFixture[str]) -> None:
    assert by_hand.main(["--list"]) == 0
    listed = capsys.readouterr().out.split()
    assert listed, "norun.txt has a # [by-hand] section with entries"
    assert all(line.startswith("Examples/") for line in listed)
    assert all(line.endswith("_view.py") for line in listed)

def test_every_by_hand_entry_is_also_skipped_by_make_run() -> None:
    text = NORUN_FILE.read_text(encoding="utf-8")
    assert set(by_hand_patterns(text)) <= set(load_glob_list(NORUN_FILE))

# ── starting and waiting, with scripts that end on their own ─────────────────

def test_run_all_reports_each_exit_and_its_stderr(tmp_path: Path) -> None:
    tree = tree_with(tmp_path, {
        "10_Ch/fine.py": "print('ok')\n",
        "10_Ch/broken.py": "raise RuntimeError('no display')\n",
    })
    paths = [tree / "10_Ch/fine.py", tree / "10_Ch/broken.py"]
    outcomes = {o.path.name: o for o in run_all(paths, tree)}
    assert outcomes["fine.py"].returncode == 0
    assert outcomes["fine.py"].errors == ""
    assert outcomes["broken.py"].returncode == 1
    assert "RuntimeError: no display" in outcomes["broken.py"].errors

def test_each_example_runs_from_its_own_directory_with_utils(
        tmp_path: Path) -> None:
    tree = tree_with(tmp_path, {
        "utils/helper.py": "VALUE = 7\n",
        "10_Ch/data.txt": "here",
        "10_Ch/reads.py": (
            "from pathlib import Path\n"
            "from helper import VALUE\n"
            "assert Path('data.txt').read_text() == 'here'\n"
            "assert VALUE == 7\n"),
    })
    [outcome] = run_all([tree / "10_Ch/reads.py"], tree)
    assert (outcome.returncode, outcome.errors) == (0, "")
