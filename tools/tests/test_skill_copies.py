"""Tests for tools/skill_copies.py: two skill copies must match."""
from pathlib import Path
from tools.skill_copies import compare

def write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_bytes(text.encode("utf-8"))
    return path


def test_identical_files_match(tmp_path: Path) -> None:
    a = write(tmp_path, "a.md", "one\ntwo\n")
    b = write(tmp_path, "b.md", "one\ntwo\n")
    assert compare(a, b) is None


def test_differing_line_is_named(tmp_path: Path) -> None:
    a = write(tmp_path, "a.md", "one\ntwo\nthree\n")
    b = write(tmp_path, "b.md", "one\ntwo\nTHREE\n")
    message = compare(a, b)
    assert message is not None
    assert str(a) in message
    assert str(b) in message
    assert "line 3" in message


def test_prefix_reports_where_longer_file_continues(
    tmp_path: Path,
) -> None:
    a = write(tmp_path, "a.md", "one\ntwo\n")
    b = write(tmp_path, "b.md", "one\ntwo\nthree\n")
    message = compare(a, b)
    assert message is not None
    assert "line 3" in message


def test_missing_file_is_named(tmp_path: Path) -> None:
    a = write(tmp_path, "a.md", "one\n")
    b = tmp_path / "absent.md"
    message = compare(a, b)
    assert message is not None
    assert str(b) in message
    assert "missing" in message
