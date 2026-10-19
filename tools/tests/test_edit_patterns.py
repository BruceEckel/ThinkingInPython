"""Tests for tools/edit_patterns.py's similarity floor and renames."""
from pathlib import Path
from typing import Any

import pytest

from tools import edit_patterns
from tools.sentence_diff import Rewrite, Sentence


def rewrite(before: str, after: str, similarity: float
            ) -> tuple[str, Rewrite]:
    s = Sentence(1, before, "", "")
    return "31_A--B.md", Rewrite(s, after, similarity)


def run(monkeypatch: pytest.MonkeyPatch,
        rows: list[tuple[str, Rewrite]], **kw: Any
        ) -> tuple[edit_patterns.Recorded, dict[str, dict[str, Any]]]:
    monkeypatch.setattr(edit_patterns, "rewrites",
                        lambda since, span: iter(rows))
    pairs: dict[str, dict[str, Any]] = {}
    return edit_patterns.record_pass(pairs, "tag", None, **kw), pairs


def test_floor_drops_below_and_keeps_above(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [rewrite("Alpha one.", "Alpha uno.", 0.55),
            rewrite("Beta two.", "Beta dos extra.", 0.65)]
    rec, pairs = run(monkeypatch, rows)
    assert rec.dropped == 1
    assert [pairs[k]["before"] for k in rec.keys] == ["Beta two."]
    assert rec.lines()[0].startswith(
        "1 rewrites below the 0.6 similarity floor dropped")


def test_min_similarity_override_keeps_the_lower_pair(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [rewrite("Alpha one.", "Alpha uno.", 0.55)]
    rec, _ = run(monkeypatch, rows, min_similarity=0.5)
    assert rec.dropped == 0
    assert len(rec.keys) == 1


def renamed(n: int) -> list[tuple[str, Rewrite]]:
    return [rewrite(f"The row holds item {i}.",
                    f"The rule holds item {i}.", 0.9) for i in range(n)]


def test_three_pure_renames_collapse(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rec, _ = run(monkeypatch, renamed(3))
    assert rec.keys == []
    assert rec.renames == [{"old": "row", "new": "rule", "count": 3}]
    assert 'rename: "row" -> "rule" in 3 sentences' in rec.lines()


def test_two_renames_are_not_enough(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rec, _ = run(monkeypatch, renamed(2))
    assert len(rec.keys) == 2
    assert rec.renames == []


def test_rename_plus_another_change_stays_a_pair(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rows = renamed(3) + [rewrite("The row is updated here.",
                                 "The rule is updated.", 0.8)]
    rec, pairs = run(monkeypatch, rows)
    assert [pairs[k]["before"] for k in rec.keys] == [
        "The row is updated here."]
    assert rec.renames[0]["count"] == 4


def test_dropped_pair_is_pruned_from_the_store(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    rows = [rewrite("Alpha one.", "Alpha uno.", 0.55)]
    monkeypatch.setattr(edit_patterns, "rewrites",
                        lambda since, span: iter(rows))
    k = edit_patterns.pair_key("Alpha one.", "Alpha uno.")
    pairs = {k: {"source": "tag", "fault": "", "status": "new"}}
    edit_patterns.record_pass(pairs, "tag", None)
    assert pairs == {}


def test_deletion_is_kept_at_any_similarity(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rec, pairs = run(monkeypatch, [rewrite("Cut this.", "", 0.0)])
    assert rec.dropped == 0
    assert [pairs[k]["after"] for k in rec.keys] == [""]
    assert rec.renames == []


def test_insertion_is_kept_at_any_similarity(
        monkeypatch: pytest.MonkeyPatch) -> None:
    rec, pairs = run(monkeypatch, [rewrite("", "A new sentence.", 0.4)])
    assert rec.dropped == 0
    assert [pairs[k]["after"] for k in rec.keys] == ["A new sentence."]
