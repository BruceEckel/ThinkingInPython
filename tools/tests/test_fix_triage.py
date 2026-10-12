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
    monkeypatch.setattr(fix_triage, "OUT", tmp_path / "out")
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "hits.json").write_text(json.dumps(
        {"faults": {}, "hits": [{"id": i} for i in "abcd"]}),
        encoding="utf-8", newline="\n")
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


def test_a_card_outside_hits_json_is_refused(
        chapter: Path, tmp_path: Path,
        capsys: pytest.CaptureFixture[str]) -> None:
    before = chapter.read_text(encoding="utf-8")
    card(tmp_path, "a", decision="apply",
         sentence="The subject calls them.", rewrite="Observers run.")
    card(tmp_path, "old1", decision="delete",
         sentence="Each observer registers.")
    assert fix_triage.apply(tmp_path / "cards") == 1
    out = capsys.readouterr().out
    assert "1 stale card(s)" in out
    assert "old1" in out
    assert chapter.read_text(encoding="utf-8") == before


def test_apply_needs_hits_json(
        chapter: Path, tmp_path: Path,
        capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "out" / "hits.json").unlink()
    card(tmp_path, "a", decision="apply",
         sentence="The subject calls them.", rewrite="Observers run.")
    assert fix_triage.apply(tmp_path / "cards") == 1
    assert "run export first" in capsys.readouterr().out


def test_cards_all_in_hits_json_are_applied(
        chapter: Path, tmp_path: Path) -> None:
    card(tmp_path, "a", decision="apply",
         sentence="The subject calls them.", rewrite="Observers run.")
    assert fix_triage.apply(tmp_path / "cards") == 0
    assert "Observers run.\n" in chapter.read_text(encoding="utf-8")


def direct_setup(chapter: Path, tmp_path: Path,
                 monkeypatch: pytest.MonkeyPatch,
                 flag: bool) -> None:
    pair = {"file": "30_A--B.md", "line": 1,
            "fault": "A first claim. A second claim."}
    if flag:
        pair["direct"] = True
    monkeypatch.setattr(
        fix_triage.judgments, "load", lambda path: {"p": pair})
    hits = [
        {"id": "a", "pair": "p", "file": "30_A--B.md", "line": 4,
         "sentence": "The subject calls them."},
        {"id": "b", "pair": "p", "file": "30_A--B.md", "line": 3,
         "sentence": "This paragraph says what the text does."}]
    out = tmp_path / "out"
    (out / "hits.json").write_text(json.dumps(
        {"faults": {}, "hits": hits}), encoding="utf-8", newline="\n")
    (out / "proposals.json").write_text(json.dumps({
        "a": {"rewrite": "Observers run."},
        "b": {"delete": True}}), encoding="utf-8", newline="\n")


def test_direct_refuses_a_pair_without_the_flag(
        chapter: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    before = chapter.read_text(encoding="utf-8")
    direct_setup(chapter, tmp_path, monkeypatch, flag=False)
    assert fix_triage.direct() == 1
    assert "not marked direct" in capsys.readouterr().out
    assert chapter.read_text(encoding="utf-8") == before


def test_direct_applies_rewrites_and_leaves_deletions(
        chapter: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    direct_setup(chapter, tmp_path, monkeypatch, flag=True)
    assert fix_triage.direct() == 0
    text = chapter.read_text(encoding="utf-8")
    assert "Observers run." in text
    assert "This paragraph says what the text does." in text
    out = capsys.readouterr().out
    assert "left for the session (deletion)" in out
    assert "direct: 1 rewrite(s) in 1 chapter(s), 1 left" in out


def test_direct_commit_runs_the_gate_per_chapter(
        chapter: Path, tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    direct_setup(chapter, tmp_path, monkeypatch, flag=True)
    gates: list[str] = []
    commits: list[tuple[str, str]] = []

    def gate(nn: str) -> tuple[int, str]:
        gates.append(nn)
        return 0, ""

    def commit(file: str, message: str) -> str:
        commits.append((file, message))
        return "abc1234"

    monkeypatch.setattr(fix_triage, "run_gate", gate)
    monkeypatch.setattr(fix_triage, "commit_chapter", commit)
    assert fix_triage.direct(commit=True, trailer="Co-Authored-By: X") == 0
    assert gates == ["30"]
    [(file, message)] = commits
    assert file == "30_A--B.md"
    assert message.startswith(
        "Chapter 30: 1 sentence from the direct fault search")
    assert "Fault: A first claim." in message
    assert message.splitlines()[-1] == "Co-Authored-By: X"


def test_direct_commit_skips_a_failed_gate(
        chapter: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    direct_setup(chapter, tmp_path, monkeypatch, flag=True)
    commits: list[str] = []
    monkeypatch.setattr(
        fix_triage, "run_gate", lambda nn: (1, "boom\n"))
    monkeypatch.setattr(
        fix_triage, "commit_chapter",
        lambda file, message: commits.append(file) or "x")
    assert fix_triage.direct(commit=True) == 1
    assert commits == []
    out = capsys.readouterr().out
    assert "gate failed: 30" in out
    assert "  boom" in out
    assert "Observers run." in chapter.read_text(encoding="utf-8")


def test_one_failed_gate_holds_every_commit(
        chapter: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    direct_setup(chapter, tmp_path, monkeypatch, flag=True)
    other = tmp_path / "31_C--D.md"
    other.write_text("A sentence to rewrite.\n", encoding="utf-8")
    out = tmp_path / "out"
    hits = json.loads((out / "hits.json").read_text(encoding="utf-8"))
    hits["hits"].append({"id": "c", "pair": "p", "file": "31_C--D.md",
                         "line": 1, "sentence": "A sentence to rewrite."})
    (out / "hits.json").write_text(json.dumps(hits), encoding="utf-8",
                                   newline="\n")
    props = json.loads((out / "proposals.json").read_text(encoding="utf-8"))
    props["c"] = {"rewrite": "A rewritten sentence."}
    (out / "proposals.json").write_text(json.dumps(props), encoding="utf-8",
                                        newline="\n")
    commits: list[str] = []
    monkeypatch.setattr(
        fix_triage, "run_gate",
        lambda nn: (1, "boom\n") if nn == "31" else (0, ""))
    monkeypatch.setattr(
        fix_triage, "commit_chapter",
        lambda file, message: commits.append(file) or "x")
    assert fix_triage.direct(commit=True) == 1
    assert commits == []
    out_text = capsys.readouterr().out
    assert "gate failed: 31" in out_text
    assert "1 gate(s) failed; nothing committed" in out_text
    assert "Observers run." in chapter.read_text(encoding="utf-8")
    assert other.read_text(encoding="utf-8") == "A rewritten sentence.\n"
