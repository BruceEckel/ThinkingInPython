"""Tests for tools/fix_triage.py's chapter edits.

A card's sentence is stored with its whitespace collapsed, while the
chapter breaks it across lines (Semantic Line Breaks), so `apply` finds
it by its words. These pin that, and that a deleted sentence standing on
its own lines leaves no blank line behind.
"""
import json
from pathlib import Path

import pytest

from tools import fix_triage


@pytest.fixture
def chapter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(fix_triage, "CHAPTERS_DIR", tmp_path)
    monkeypatch.setattr(fix_triage.judgments, "load", lambda path: {})
    path = tmp_path / "30_A--B.md"
    path.write_text(
        "The classic design comes from GoF,\n"
        "and this section uses that vocabulary:\n"
        "Each observer registers.\n"
        "This paragraph says what the text does.\n"
        "The subject calls them.\n", encoding="utf-8")
    return path


def card(tmp_path: Path, name: str, **fields: object) -> None:
    cards = tmp_path / "cards"
    cards.mkdir(exist_ok=True)
    body = {"pair": "p", "file": "30_A--B.md", "line": 1, **fields}
    (cards / f"{name}.json").write_text(json.dumps({"data": body}),
                                        encoding="utf-8")


def test_a_rewrite_replaces_a_sentence_across_line_breaks(
        chapter: Path, tmp_path: Path) -> None:
    card(tmp_path, "a", decision="apply",
         sentence="The classic design comes from GoF, and this section "
                  "uses that vocabulary:",
         rewrite="The classic design comes from GoF:")
    assert fix_triage.apply(tmp_path / "cards") == 0
    assert chapter.read_text(encoding="utf-8").startswith(
        "The classic design comes from GoF:\nEach observer registers.\n")


def test_a_deleted_sentence_leaves_no_blank_line(
        chapter: Path, tmp_path: Path) -> None:
    card(tmp_path, "b", decision="delete",
         sentence="This paragraph says what the text does.", rewrite="")
    fix_triage.apply(tmp_path / "cards")
    assert chapter.read_text(encoding="utf-8").endswith(
        "Each observer registers.\nThe subject calls them.\n")


def test_skip_and_not_fault_change_nothing(
        chapter: Path, tmp_path: Path) -> None:
    before = chapter.read_text(encoding="utf-8")
    card(tmp_path, "c", decision="skip", sentence="The subject calls them.")
    card(tmp_path, "d", decision="not_fault",
         sentence="Each observer registers.")
    fix_triage.apply(tmp_path / "cards")
    assert chapter.read_text(encoding="utf-8") == before
