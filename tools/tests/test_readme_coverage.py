"""Tests for tools/readme_coverage.py: every tool needs a README name."""
from pathlib import Path
from tools.readme_coverage import named, problems


def make_tools(tmp_path: Path, readme: str, *files: str) -> tuple[Path, Path]:
    for name in files:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    path = tmp_path / "README.md"
    path.write_text(readme, encoding="utf-8")
    return tmp_path, path


def test_filename_or_dotted_name_counts() -> None:
    assert named("check_all.py", "## check_all.py")
    assert named("check_all.py", "uv run python -m tools.check_all")
    assert not named("check.py", "uv run python -m tools.check_all")


def test_named_tools_pass(tmp_path: Path) -> None:
    directory, readme = make_tools(
        tmp_path, "## a.py\nThe `figs/` package.\n",
        "a.py", "__init__.py", "figs/__init__.py", "data/x.txt")
    assert problems(directory, readme) == []


def test_unnamed_module_and_package_fail(tmp_path: Path) -> None:
    directory, readme = make_tools(
        tmp_path, "## a.py\n", "a.py", "b.py", "figs/one.py")
    assert problems(directory, readme) == [
        "tools/b.py: not named in tools/README.md",
        "tools/figs/: not named in tools/README.md",
    ]
