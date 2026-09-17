"""Tests for tools/footnote_labels.py: labels unique across a directory."""
from pathlib import Path
from tools.footnote_labels import find
from tools.markdown import Document

def messages(path: Path) -> list[str]:
    return [f.message for f in find(Document.parse(path))]


def write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def test_same_label_in_two_files_is_reported_in_both(tmp_path: Path) -> None:
    a = write(tmp_path, "11_a.md", "Text[^note].\n\n[^note]: First.\n")
    b = write(tmp_path, "17_b.md", "More[^note].\n\n[^note]: Second.\n")
    assert messages(a) == [
        "footnote label [^note] is also defined at 17_b.md:3; a label must "
        "be unique across the book, since the EPUB and PDF concatenate "
        "the chapters"]
    assert messages(b) == [
        "footnote label [^note] is also defined at 11_a.md:3; a label must "
        "be unique across the book, since the EPUB and PDF concatenate "
        "the chapters"]


def test_distinct_labels_are_clean(tmp_path: Path) -> None:
    a = write(tmp_path, "11_a.md", "Text[^one].\n\n[^one]: First.\n")
    write(tmp_path, "17_b.md", "More[^two].\n\n[^two]: Second.\n")
    assert messages(a) == []


def test_repeated_label_in_one_file_is_reported_once(tmp_path: Path) -> None:
    a = write(tmp_path, "11_a.md",
              "Text[^n].\n\n[^n]: First.\n\nMore[^n].\n\n[^n]: Again.\n")
    assert [f.line for f in find(Document.parse(a))] == [7]
    assert "line 3" in messages(a)[0]


def test_definition_inside_a_fence_is_ignored(tmp_path: Path) -> None:
    a = write(tmp_path, "11_a.md", "Text[^n].\n\n[^n]: First.\n")
    write(tmp_path, "17_b.md", "```\n[^n]: not a footnote\n```\n")
    assert messages(a) == []


def test_references_alone_are_not_definitions(tmp_path: Path) -> None:
    a = write(tmp_path, "11_a.md", "Text[^n].\n\n[^n]: First.\n")
    write(tmp_path, "17_b.md", "Cites[^n] the same note.\n")
    assert messages(a) == []


def test_document_from_text_checks_only_itself() -> None:
    doc = Document.from_text("A[^x].\n\n[^x]: One.\n\n[^x]: Two.\n")
    assert [f.line for f in find(doc)] == [5]
