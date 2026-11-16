"""Tests for tools/uncaptured_edits.py."""

import subprocess
from pathlib import Path

import pytest

from tools import uncaptured_edits as ue
from tools.uncaptured_edits import (
    Commit, MARKER_FILE, build_notice, write_marker, format_notice, has_trailer, is_prose,
    open_pass, parse_log, parse_status)


@pytest.mark.parametrize("path, expected", [
    ("Chapters/05_X.md", True),
    ("Solutions/05_X/README.md", True),
    ("Solutions/05_X/exercise_1.py", False),
    ("Examples/05_X/a.py", False),
    ("tools/x.py", False),
    ("CLAUDE.md", False),
])
def test_is_prose(path: str, expected: bool) -> None:
    assert is_prose(path) is expected


def test_has_trailer() -> None:
    assert has_trailer("Subject\n\nBody\n\nCo-Authored-By: X <x@y>")
    assert has_trailer("Subject\n\nco-authored-by: x")
    assert not has_trailer("Subject\n\nmentions Co-Authored-By: midline")


def test_open_pass() -> None:
    passes = {"05"}
    assert open_pass("Chapters/05_X.md", passes) == "05"
    assert open_pass("Solutions/05_X/README.md", passes) == "05"
    assert open_pass("Chapters/06_X.md", passes) is None


def test_open_pass_appendix() -> None:
    passes = {"A"}
    assert open_pass("Chapters/A_Effect_Tracking.md", passes) == "A"
    assert open_pass("Solutions/A_Effect_Tracking/README.md", passes) == "A"
    assert open_pass("Chapters/B_An_Effect_Checker.md", passes) is None


def test_parse_log_drops_trailer_and_nonprose() -> None:
    sep, fs = ue.RECORD, ue.FIELD
    text = (
        f"{sep}aaa1111{fs}2026-11-16{fs}Fix{fs}{fs}\n\nChapters/05_X.md\n"
        f"{sep}bbb2222{fs}2026-11-16{fs}Mine{fs}Co-Authored-By: C{fs}\n\n"
        f"Chapters/05_X.md\n"
        f"{sep}ccc3333{fs}2026-11-16{fs}Code{fs}{fs}\n\ntools/x.py\n")
    assert parse_log(text) == [
        Commit("aaa1111", "2026-11-16", "Fix", ("Chapters/05_X.md",))]


def test_parse_status() -> None:
    text = (" M Chapters/05_X.md\0?? tools/x.py\0"
            "R  Chapters/07_Y.md\0Chapters/06_Y.md\0")
    assert parse_status(text) == ["Chapters/05_X.md", "Chapters/07_Y.md"]


COMMIT = Commit("abc1234", "2026-11-16", "Fix it", ("Chapters/05_X.md",))


def test_notice_variants() -> None:
    assert format_notice([], [], set()) == ""
    commits_only = format_notice([COMMIT], [], set(), "deadbee")
    assert "abc1234 2026-11-16 Fix it" in commits_only
    assert "Working tree" not in commits_only
    tree_only = format_notice([], ["Chapters/05_X.md"], {"05"})
    assert "Working tree: Chapters/05_X.md (open pass 05)" in tree_only
    assert "edit-start-05" in tree_only
    assert "Co-Authored-By trailer" not in tree_only
    both = format_notice([COMMIT], ["Chapters/05_X.md"], set())
    assert "abc1234" in both and "Working tree" in both


def test_notice_limits() -> None:
    commits = [Commit(f"h{i}", "d", "s", ("Chapters/05_X.md",))
               for i in range(10)]
    notice = format_notice(commits, [f"Chapters/{i:02d}_X.md"
                                     for i in range(10)], set())
    assert "... and 2 more" in notice
    assert notice.count("... and 2 more") == 2


def run(root: Path, *args: str, env_date: str = "") -> None:
    subprocess.run(
        ["git", "-c", "user.name=T", "-c", "user.email=t@example.com",
         "-c", "commit.gpgsign=false", *args],
        cwd=root, check=True, capture_output=True, text=True,
        encoding="utf-8")


def make_repo(tmp_path: Path) -> Path:
    run(tmp_path, "init", "-q")
    return tmp_path


def test_end_to_end(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "Chapters").mkdir()
    (root / "bruce_edit_db.md").write_text("db\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "Learn")
    chapter = root / "Chapters" / "05_Foundations--X.md"
    chapter.write_text("one\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "Hand edit")
    chapter.write_text("two\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m",
        "Session edit\n\nCo-Authored-By: C <c@example.com>")
    chapter.write_text("three\n", newline="\n")
    run(root, "tag", "edit-start-05")
    notice = build_notice(root)
    assert "Hand edit" in notice
    assert "Session edit" not in notice
    assert "Working tree: Chapters/05_Foundations--X.md" in notice
    assert "open pass 05" in notice


def test_no_db_commit(tmp_path: Path, capsys: pytest.CaptureFixture[str],
                      monkeypatch: pytest.MonkeyPatch) -> None:
    root = make_repo(tmp_path)
    (root / "a.txt").write_text("a\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "First")
    assert build_notice(root) == ""
    monkeypatch.setattr(ue, "ROOT", root)
    assert ue.main([]) == 0
    assert capsys.readouterr().out == ""


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True,
        text=True, encoding="utf-8").stdout.strip()


def hole_repo(root: Path) -> str:
    """A db commit, a hand chapter commit, then a trailer db commit.

    Returns the first commit's hash.
    """
    (root / "Chapters").mkdir()
    (root / "bruce_edit_db.md").write_text("db\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "Learn")
    first = git_out(root, "rev-parse", "HEAD")
    (root / "Chapters" / "05_Foundations--X.md").write_text(
        "one\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "Hand edit")
    (root / "bruce_edit_db.md").write_text("db2\n", newline="\n")
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m",
        "Learn more\n\nCo-Authored-By: C <c@example.com>")
    return first


def put_marker(root: Path, text: str) -> None:
    path = root / MARKER_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def test_marker_closes_the_hole(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    first = hole_repo(root)
    assert build_notice(root) == ""
    put_marker(root, f"# header\n{first}\n")
    notice = build_notice(root)
    assert "Hand edit" in notice
    assert f"since {first[:7]} ({MARKER_FILE})" in notice
    assert "ARGS=--mark" in notice


def test_mark_writes_head(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    first = hole_repo(root)
    put_marker(root, f"{first}\n")
    assert "Hand edit" in build_notice(root)
    short = write_marker(root)
    head = git_out(root, "rev-parse", "HEAD")
    assert short == head[:7]
    text = (root / MARKER_FILE).read_text(encoding="utf-8")
    assert text.startswith("#") and text.rstrip().endswith(head)
    assert "\r" not in text
    assert build_notice(root) == ""


@pytest.mark.parametrize("bad", [
    "0123456789abcdef0123456789abcdef01234567\n",
    "garbage\n",
    "# only a comment\n",
    "",
])
def test_bad_marker_falls_back(tmp_path: Path, bad: str) -> None:
    root = make_repo(tmp_path)
    hole_repo(root)
    put_marker(root, bad)
    assert build_notice(root) == ""
