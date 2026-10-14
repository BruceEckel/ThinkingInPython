"""Tests for tools/version_pins.py: find and bump version pins in prose."""
from pathlib import Path
import pytest
from tools.version_pins import (
    KeepEntry,
    find_pins,
    parse_keeps,
    rewrite,
    unmatched_keeps,
)

def write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def test_stale_pin_is_found_with_line_and_versions(tmp_path: Path) -> None:
    f = write(tmp_path, "a.md", "Intro.\nUnder `ty` 0.0.70 it works.\n")
    [pin] = find_pins([f], "0.0.87", root=tmp_path)
    assert (pin.line, pin.found, pin.installed) == (2, "0.0.70", "0.0.87")
    assert pin.stale
    assert "Under `ty` 0.0.70" in pin.text


def test_current_pin_is_not_stale(tmp_path: Path) -> None:
    f = write(tmp_path, "a.md", "Under `ty` 0.0.87 it works.\n")
    [pin] = find_pins([f], "0.0.87", root=tmp_path)
    assert not pin.stale


def test_bare_ty_without_a_version_is_not_a_pin(tmp_path: Path) -> None:
    f = write(tmp_path, "a.md", "Run `ty` now; `ty`'s 0.0.56 is old.\n")
    assert find_pins([f], "0.0.87", root=tmp_path) == []


def test_kept_line_is_skipped(tmp_path: Path) -> None:
    f = write(tmp_path, "CLAUDE.md", "Both `ty` 0.0.78 then.\n")
    keeps = [KeepEntry("CLAUDE.md", "Both `ty` 0.0.78")]
    [pin] = find_pins([f], "0.0.87", root=tmp_path, keeps=keeps)
    assert pin.kept
    assert not pin.stale
    assert rewrite(f, "0.0.87", keep=["Both `ty` 0.0.78"]) == 0
    assert f.read_bytes() == b"Both `ty` 0.0.78 then.\n"


def test_rewrite_bumps_stale_and_keeps_lf(tmp_path: Path) -> None:
    f = write(tmp_path, "a.md",
              "On `ty` 0.0.70 a.\nOn `ty` 0.0.87 b.\nOther 0.0.70.\n")
    assert rewrite(f, "0.0.87") == 1
    assert f.read_bytes() == (
        b"On `ty` 0.0.87 a.\nOn `ty` 0.0.87 b.\nOther 0.0.70.\n")


def test_two_pins_on_one_line_both_rewrite(tmp_path: Path) -> None:
    f = write(tmp_path, "a.md", "`ty` 0.0.70 and `ty` 0.0.71 differ.\n")
    assert rewrite(f, "0.0.87") == 2
    assert f.read_text(encoding="utf-8") == (
        "`ty` 0.0.87 and `ty` 0.0.87 differ.\n")


def test_rewrite_with_nothing_stale_leaves_file_alone(
        tmp_path: Path) -> None:
    f = write(tmp_path, "a.md", "`ty` 0.0.87 here.\n")
    assert rewrite(f, "0.0.87") == 0


def test_keep_entry_matching_nothing_is_reported(tmp_path: Path) -> None:
    write(tmp_path, "CLAUDE.md", "Both `ty` 0.0.78 then.\n")
    good = KeepEntry("CLAUDE.md", "0.0.78")
    wrong_text = KeepEntry("CLAUDE.md", "no such text")
    no_file = KeepEntry("missing.md", "x")
    assert unmatched_keeps(tmp_path, [good, wrong_text, no_file]) == [
        wrong_text, no_file]


def test_parse_keeps_skips_comments_and_blanks() -> None:
    text = "# comment\n\nCLAUDE.md:both `ty` 0.0.78\n"
    assert parse_keeps(text) == [KeepEntry("CLAUDE.md", "both `ty` 0.0.78")]


@pytest.mark.parametrize("version", ["0.0.87", "1.2.3"])
def test_version_group_only_is_replaced(tmp_path: Path, version: str) -> None:
    f = write(tmp_path, "a.md", "x `ty` 0.0.70 y\n")
    rewrite(f, version)
    assert f.read_text(encoding="utf-8") == f"x `ty` {version} y\n"
