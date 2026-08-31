"""Tests for tools/tools_extract.py (routing, conflicts, write, check)."""
from pathlib import Path

from tools_extract import (
    block_content,
    check_against,
    extract,
    write_tree,
)
from tools_markdown import Block, Document


def doc_of(text: str, name: str = "14_Techniques--Decorators.md") -> Document:
    return Document.from_text(text, Path(name))


def chapter_route(doc: Document, block: Block) -> str | None:
    slug = block.slug
    return None if slug is None else f"{doc.path.stem}/{slug}"


# ── routing ───────────────────────────────────────────────────────────────────

def test_a_claimed_block_becomes_a_file() -> None:
    doc = doc_of("```python\n# trace.py\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    assert set(result.files) == {"14_Techniques--Decorators/trace.py"}
    assert result.files["14_Techniques--Decorators/trace.py"].content == "# trace.py\nx = 1\n"

def test_an_unclaimed_block_counts_as_a_fragment() -> None:
    doc = doc_of("```python\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    assert result.files == {}
    assert result.fragments == 1

def test_routers_are_tried_in_order_and_first_wins() -> None:
    doc = doc_of("```python\n# a.py\n```\n")
    first = lambda d, b: "one/a.py"       # noqa: E731
    second = lambda d, b: "two/a.py"      # noqa: E731
    assert set(extract([doc], [first, second]).files) == {"one/a.py"}

def test_a_router_returning_none_falls_through_to_the_next() -> None:
    doc = doc_of("```python\n# a.py\n```\n")
    passes = lambda d, b: None            # noqa: E731
    claims = lambda d, b: "two/a.py"      # noqa: E731
    assert set(extract([doc], [passes, claims]).files) == {"two/a.py"}

def test_language_is_recorded() -> None:
    doc = doc_of("```text\n# data.txt\nrows\n```\n")
    result = extract([doc], [chapter_route])
    assert result.files["14_Techniques--Decorators/data.txt"].language == "text"

def test_source_md_is_recorded() -> None:
    doc = doc_of("```python\n# a.py\n```\n", "08_Foundations--Static_Types.md")
    result = extract([doc], [chapter_route])
    assert result.files["08_Foundations--Static_Types/a.py"].source_md == "08_Foundations--Static_Types.md"

# ── conflicts ─────────────────────────────────────────────────────────────────

def test_identical_duplicate_is_not_a_conflict() -> None:
    body = "```python\n# a.py\nx = 1\n```\n"
    result = extract([doc_of(body), doc_of(body)], [chapter_route])
    assert result.conflicts == []
    assert len(result.files) == 1

def test_differing_duplicate_is_a_conflict_and_first_wins() -> None:
    a = doc_of("```python\n# a.py\nx = 1\n```\n", "01_A.md")
    b = doc_of("```python\n# a.py\nx = 2\n```\n", "01_A.md")
    result = extract([a, b], [chapter_route])
    assert len(result.conflicts) == 1
    assert result.conflicts[0].path == "01_A/a.py"
    assert result.files["01_A/a.py"].content == "# a.py\nx = 1\n"

# ── content normalization ─────────────────────────────────────────────────────

def test_content_gets_exactly_one_trailing_newline() -> None:
    block = Document.from_text("```python\nx = 1\n\n\n```\n").blocks[0]
    assert block_content(block) == "x = 1\n"

def test_content_of_an_empty_block() -> None:
    block = Document.from_text("```python\n```\n").blocks[0]
    assert block_content(block) == "\n"

# ── write and check ───────────────────────────────────────────────────────────

def test_write_tree_creates_nested_dirs(tmp_path: Path) -> None:
    doc = doc_of("```python\n# mouse/Move.py\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    assert write_tree(result, tmp_path) == 1
    written = tmp_path / "14_Techniques--Decorators" / "mouse" / "Move.py"
    assert written.read_text(encoding="utf-8") == "# mouse/Move.py\nx = 1\n"

def test_write_tree_skips_unchanged_files(tmp_path: Path) -> None:
    doc = doc_of("```python\n# a.py\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    assert write_tree(result, tmp_path) == 1
    assert write_tree(result, tmp_path) == 0

def test_check_against_reports_missing(tmp_path: Path) -> None:
    doc = doc_of("```python\n# a.py\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    missing, changed = check_against(result, tmp_path)
    assert missing == ["14_Techniques--Decorators/a.py"]
    assert changed == []

def test_check_against_reports_changed(tmp_path: Path) -> None:
    doc = doc_of("```python\n# a.py\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    write_tree(result, tmp_path)
    target = tmp_path / "14_Techniques--Decorators" / "a.py"
    target.write_text("# a.py\nx = 999\n", encoding="utf-8")
    missing, changed = check_against(result, tmp_path)
    assert missing == []
    assert changed == ["14_Techniques--Decorators/a.py"]

def test_check_against_clean_tree_reports_nothing(tmp_path: Path) -> None:
    doc = doc_of("```python\n# a.py\nx = 1\n```\n")
    result = extract([doc], [chapter_route])
    write_tree(result, tmp_path)
    assert check_against(result, tmp_path) == ([], [])
