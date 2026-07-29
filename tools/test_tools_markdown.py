"""Tests for tools/tools_markdown.py (the parsed-Markdown Document)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tools_markdown import Block, Document

# ── parsing ───────────────────────────────────────────────────────────────────

def test_no_blocks() -> None:
    doc = Document.from_text("Just prose.\nMore prose.\n")
    assert doc.blocks == []

def test_one_python_block() -> None:
    doc = Document.from_text("A\n\n```python\nx = 1\n```\n\nB\n")
    assert len(doc.blocks) == 1
    block = doc.blocks[0]
    assert block.lang == "python"
    assert block.lines == ["x = 1"]
    assert block.open_at == 2
    assert block.start == 3
    assert block.end == 4

def test_language_captured_for_non_python() -> None:
    doc = Document.from_text("```text\nhi\n```\n")
    assert doc.blocks[0].lang == "text"
    assert not doc.blocks[0].is_python

def test_bare_fence_has_empty_language() -> None:
    doc = Document.from_text("```\nhi\n```\n")
    assert doc.blocks[0].lang == ""

def test_py_counts_as_python() -> None:
    # validate_output.py has always accepted ```py, so Document does too.
    assert Document.from_text("```py\nx=1\n```\n").blocks[0].is_python

def test_indented_fence_is_a_block() -> None:
    # Chapter 17 has an indented ```cpp block with an indented close.
    doc = Document.from_text("Text\n\n    ```cpp\n    int x;\n    ```\n")
    assert [b.lang for b in doc.blocks] == ["cpp"]

def test_multiple_blocks_in_order() -> None:
    doc = Document.from_text(
        "```python\na\n```\ntext\n```text\nb\n```\n"
    )
    assert [b.lang for b in doc.blocks] == ["python", "text"]
    assert [b.lines for b in doc.blocks] == [["a"], ["b"]]

def test_unclosed_block_runs_to_end() -> None:
    doc = Document.from_text("```python\nx = 1\ny = 2\n")
    assert doc.blocks[0].lines == ["x = 1", "y = 2", ""]

def test_python_blocks_filters() -> None:
    doc = Document.from_text(
        "```python\na\n```\n```text\nb\n```\n```python\nc\n```\n"
    )
    assert [b.lines for b in doc.python_blocks()] == [["a"], ["c"]]

# ── line numbers ──────────────────────────────────────────────────────────────

def test_line_number_maps_to_the_file() -> None:
    # Line 1 "A", 2 blank, 3 fence, 4 first code line.
    doc = Document.from_text("A\n\n```python\nx = 1\ny = 2\n```\n")
    block = doc.blocks[0]
    assert block.line_number(0) == 4
    assert block.line_number(1) == 5

# ── slug ──────────────────────────────────────────────────────────────────────

def test_slug_from_path_comment() -> None:
    doc = Document.from_text("```python\n# trace.py\nx = 1\n```\n")
    assert doc.blocks[0].slug == "trace.py"

def test_slug_skips_leading_blank_lines() -> None:
    doc = Document.from_text("```python\n\n# a.py\n```\n")
    assert doc.blocks[0].slug == "a.py"

def test_slug_none_without_path_comment() -> None:
    doc = Document.from_text("```python\nimport os\n```\n")
    assert doc.blocks[0].slug is None

def test_rust_slug_reads_the_slash_comment_form() -> None:
    doc = Document.from_text("```rust\n// fastcount/src/lib.rs\n```\n")
    assert doc.blocks[0].rust_slug == "fastcount/src/lib.rs"

def test_slug_ignores_the_rust_comment_form() -> None:
    # slug is the `#` form whatever the fence language. Making it switch on
    # lang pulled a ```rust block into the Python examples tree.
    doc = Document.from_text("```rust\n// fastcount/src/lib.rs\n```\n")
    assert doc.blocks[0].slug is None

def test_slug_read_from_a_non_python_fence() -> None:
    doc = Document.from_text("```text\n# data.txt\nrows\n```\n")
    assert doc.blocks[0].slug == "data.txt"

def test_slug_backslashes_normalized() -> None:
    doc = Document.from_text("```python\n# mouse\\Move.py\n```\n")
    assert doc.blocks[0].slug == "mouse/Move.py"

# ── prose ─────────────────────────────────────────────────────────────────────

def test_prose_lines_skip_code_and_headings() -> None:
    text = (
        "# Heading\n"
        "Real prose.\n"
        "\n"
        "```python\n"
        "this is code, not prose\n"
        "```\n"
        "- a list item\n"
        "More prose.\n"
    )
    doc = Document.from_text(text)
    assert list(doc.prose_lines()) == [(2, "Real prose."), (8, "More prose.")]

def test_in_fence_covers_the_fence_lines_too() -> None:
    doc = Document.from_text("a\n```python\nx\n```\nb\n")
    assert doc.in_fence() == [False, True, True, True, False, False]

# ── round-trip ────────────────────────────────────────────────────────────────

def test_rendered_round_trips_exactly() -> None:
    text = "A\n\n```python\nx = 1\n```\n"
    assert Document.from_text(text).rendered() == text

def test_rendered_round_trips_without_final_newline() -> None:
    # split("\n") is chosen over splitlines() precisely so this holds.
    text = "A\n\n```python\nx = 1\n```"
    assert Document.from_text(text).rendered() == text

def test_rendered_with_edited_lines() -> None:
    doc = Document.from_text("a\nb\nc\n")
    edited = list(doc.lines)
    edited[1] = "B"
    assert doc.rendered(edited) == "a\nB\nc\n"

def test_parse_reads_the_file(tmp_path: Path) -> None:
    p = tmp_path / "ch.md"
    p.write_text("```python\n# a.py\n```\n", encoding="utf-8")
    doc = Document.parse(p)
    assert doc.path == p
    assert doc.blocks[0].slug == "a.py"

def test_block_is_frozen() -> None:
    block = Document.from_text("```python\nx\n```\n").blocks[0]
    assert isinstance(block, Block)
    try:
        block.lang = "text"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("Block should be immutable")
