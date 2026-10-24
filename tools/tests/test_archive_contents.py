"""Tests for tools/archive_contents.py: the list must match the directory."""
from pathlib import Path
from tools.archive_contents import listed_names, problems

def make_archive(tmp_path: Path, readme: str,
                 *names: str) -> tuple[Path, Path]:
    for name in names:
        (tmp_path / name).write_text("x", encoding="utf-8")
    path = tmp_path / "README.md"
    path.write_text(readme, encoding="utf-8")
    return tmp_path, path


def test_bullets_yield_their_filenames() -> None:
    text = ("Intro naming `not_a_bullet.md`.\n\n"
            "- `~a.md`: one\n  continued `~c.md`\n- `~b.md` \u2014 two\n")
    assert listed_names(text) == {"~a.md", "~b.md"}


def test_matching_list_passes(tmp_path: Path) -> None:
    directory, readme = make_archive(
        tmp_path, "- `~a.md`: one\n- `~b.md`: two\n", "~a.md", "~b.md")
    assert problems(directory, readme) == []


def test_unlisted_file_and_dangling_bullet_fail(tmp_path: Path) -> None:
    directory, readme = make_archive(
        tmp_path, "- `~a.md`: one\n- `~gone.md`: two\n", "~a.md", "~new.md")
    assert problems(directory, readme) == [
        "archive/~new.md: no bullet in archive/README.md",
        "archive/README.md lists `~gone.md`, which is not in archive/",
    ]
