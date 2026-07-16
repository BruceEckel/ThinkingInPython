"""Tests for tools/fix_imports.py (the pure splicing logic)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fix_imports import block_slug, collect_markdown, splice_markdown


# ── block_slug ────────────────────────────────────────────────────────────────

def test_block_slug_simple() -> None:
    assert block_slug(["# trace.py\n", "import os\n"]) == "trace.py"

def test_block_slug_subpath_normalized() -> None:
    assert block_slug(["# mouse/Move.py\n"]) == "mouse/Move.py"

def test_block_slug_none_without_path_line() -> None:
    assert block_slug(["import os\n", "print(os.getcwd())\n"]) is None

def test_block_slug_skips_blank_lines() -> None:
    assert block_slug(["\n", "# a.py\n"]) == "a.py"

def test_block_slug_utils_prefix() -> None:
    assert block_slug(["# utils/display.py\n"]) == "utils/display.py"


# ── splice_markdown ───────────────────────────────────────────────────────────

def fixed_map(mapping: dict[str, str]):
    return lambda slug: mapping.get(slug)


def test_splice_replaces_changed_block() -> None:
    src = (
        "Intro.\n\n"
        "```python\n# a.py\nimport b, a\n```\n\n"
        "Outro.\n"
    )
    new_text, changed = splice_markdown(
        src, fixed_map({"a.py": "# a.py\nimport a, b\n"})
    )
    assert changed == ["a.py"]
    assert "import a, b\n" in new_text
    assert "import b, a\n" not in new_text
    # Surrounding prose and fences are preserved.
    assert new_text.startswith("Intro.\n\n```python\n")
    assert new_text.endswith("```\n\nOutro.\n")

def test_splice_leaves_unchanged_block() -> None:
    src = "```python\n# a.py\nimport a, b\n```\n"
    new_text, changed = splice_markdown(
        src, fixed_map({"a.py": "# a.py\nimport a, b\n"})
    )
    assert changed == []
    assert new_text == src

def test_splice_ignores_block_without_slug() -> None:
    src = "```python\nimport b, a\n```\n"
    # No path line, so fixed_for is never consulted.
    new_text, changed = splice_markdown(src, fixed_map({}))
    assert changed == []
    assert new_text == src

def test_splice_ignores_non_python_fence() -> None:
    src = "```text\n# a.py\nimport b, a\n```\n"
    new_text, changed = splice_markdown(
        src, fixed_map({"a.py": "WRONG"})
    )
    assert changed == []
    assert new_text == src

def test_splice_handles_py_fence_label() -> None:
    src = "```py\n# a.py\nimport b, a\n```\n"
    new_text, changed = splice_markdown(
        src, fixed_map({"a.py": "# a.py\nimport a, b\n"})
    )
    assert changed == ["a.py"]

def test_splice_multiple_blocks() -> None:
    src = (
        "```python\n# a.py\nimport b, a\n```\n\n"
        "```python\n# c.py\nimport d, c\n```\n"
    )
    new_text, changed = splice_markdown(
        src,
        fixed_map({
            "a.py": "# a.py\nimport a, b\n",
            "c.py": "# c.py\nimport c, d\n",
        }),
    )
    assert changed == ["a.py", "c.py"]
    assert "import a, b\n" in new_text
    assert "import c, d\n" in new_text

def test_splice_none_fixed_leaves_block() -> None:
    src = "```python\n# a.py\nimport b, a\n```\n"
    new_text, changed = splice_markdown(src, fixed_map({}))
    assert changed == []
    assert new_text == src


# ── collect_markdown ──────────────────────────────────────────────────────────

def test_collect_markdown_single_file(tmp_path: Path) -> None:
    p = tmp_path / "ch.md"
    p.write_text("", encoding="utf-8")
    assert collect_markdown([p]) == [p]

def test_collect_markdown_excludes_non_md(tmp_path: Path) -> None:
    py = tmp_path / "ch.py"
    py.write_text("", encoding="utf-8")
    assert collect_markdown([py]) == []

def test_collect_markdown_directory(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("", encoding="utf-8")
    b.write_text("", encoding="utf-8")
    assert set(collect_markdown([tmp_path])) == {a, b}
