"""Tests for tools/marker_placement.py."""
import sys
from pathlib import Path

from tools.marker_placement import check_block


def place(tmp_path: Path, source: str) -> tuple[str, bool]:
    """Check one slugless block; return its new text and whether it moved."""
    block = source.splitlines(keepends=True)
    result = check_block(block, tmp_path / "x.md", "ch", 0,
                         tree=tmp_path, skips=[])
    assert not result.stuck, result.notes
    return "".join(result.lines), result.moved


def test_clumped_runs_move_to_their_statements(tmp_path: Path) -> None:
    text, moved = place(tmp_path, (
        "def announce(cls):\n"
        "    print('decorating', cls.__name__)\n"
        "    return cls\n"
        "\n"
        "@announce\n"
        "class Point:\n"
        "    pass\n"
        "\n"
        "print('done')\n"
        "#: decorating Point\n"
        "#: done\n"))
    assert moved
    assert text == (
        "def announce(cls):\n"
        "    print('decorating', cls.__name__)\n"
        "    return cls\n"
        "\n"
        "@announce\n"
        "class Point:\n"
        "    pass\n"
        "#: decorating Point\n"
        "\n"
        "print('done')\n"
        "#: done\n")


def test_placed_runs_stay(tmp_path: Path) -> None:
    source = "print(1)\n#: 1\nprint(2)\n#: 2\n"
    assert place(tmp_path, source) == (source, False)


def test_import_output_goes_below_the_import_block(tmp_path: Path) -> None:
    (tmp_path / "noisy.py").write_text("print('imported')\n")
    sys.path.insert(0, str(tmp_path))
    try:
        text, moved = place(tmp_path, (
            "import noisy\n"
            "import os\n"
            "\n"
            "print(os.sep in '/\\\\')\n"
            "#: imported\n"
            "#: True\n"))
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("noisy", None)
    assert moved
    assert text == (
        "import noisy\n"
        "import os\n"
        "\n"
        "#: imported\n"
        "print(os.sep in '/\\\\')\n"
        "#: True\n")


def test_partial_line_joins_the_next_statement(tmp_path: Path) -> None:
    source = "print('a', end=' ')\nprint('b')\n#: a b\n"
    assert place(tmp_path, source) == (source, False)


def test_trailing_indented_comment_belongs_to_its_block(
    tmp_path: Path,
) -> None:
    source = (
        "if True:\n"
        "    print('x')\n"
        "    # A closing remark\n"
        "#: x\n")
    assert place(tmp_path, source) == (source, False)


def test_unmarked_output_below_the_last_run_is_ignored(
    tmp_path: Path,
) -> None:
    source = "print(1)\n#: 1\nprint('varies')\n"
    assert place(tmp_path, source) == (source, False)


def test_committed_text_moves_unchanged(tmp_path: Path) -> None:
    # A measurement that differs from run to run keeps its marker text
    text, moved = place(tmp_path, (
        "print(0.5)\n"
        "print('end')\n"
        "#: 0.4\n"
        "#: end\n"))
    assert moved
    assert text == "print(0.5)\n#: 0.4\nprint('end')\n#: end\n"
