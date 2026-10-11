"""Tests for tools/fault_review.py's proposal documents.

`seed --rules` writes the capture step's rule proposals beside the
cards, in the same batch files, and `apply --rules-dir` prints Bruce's
decisions on them without touching `edit_pairs.json`.
"""
import json
from pathlib import Path
from typing import Any

import pytest

from tools import fault_review

PAIR = {"file": "30_A--B.md", "line": 3, "before": "Old.",
        "after": "New.", "fault": "A fault."}
FIELDS = ("kind", "title", "rule", "test", "keep", "home", "evidence")


def rule(label: str, **over: Any) -> dict[str, Any]:
    body: dict[str, Any] = {f: f"{f} of {label}" for f in FIELDS}
    body["evidence"] = [{"where": "w", "text": "t"}]
    return {"label": label, **body, **over}


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    pairs_file = tmp_path / "edit_pairs.json"
    pairs_file.write_text(json.dumps({"k1": PAIR}), encoding="utf-8")
    monkeypatch.setattr(fault_review, "OUT", tmp_path / "out")
    monkeypatch.setattr(fault_review, "ROOT", tmp_path)
    monkeypatch.setattr(fault_review, "PAIRS_FILE", pairs_file)
    monkeypatch.setattr(fault_review, "record_pass",
                        lambda pairs, since, span: list(pairs))
    return tmp_path


def rules_file(tmp_path: Path, rules: list[dict[str, Any]]) -> Path:
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(rules), encoding="utf-8")
    return path


def test_seed_writes_proposal_docs_after_the_cards(env: Path) -> None:
    path = rules_file(env, [rule("P1"), rule("P2")])
    assert fault_review.seed("tag", None, None, path) == 0
    out = env / "out"
    doc = json.loads((out / "docs/proposals/P2.json")
                     .read_text(encoding="utf-8"))
    assert (doc["order"], doc["decision"], doc["note"]) == (1, None, "")
    assert doc["title"] == "title of P2"
    meta = json.loads((out / "docs/meta/pass.json")
                      .read_text(encoding="utf-8"))
    assert meta["proposals"] == 2
    writes = json.loads((out / "batch1.json").read_text(encoding="utf-8"))
    assert [(w["collection"], w["doc_id"]) for w in writes] == [
        ("meta", "pass"), ("cards", "k1"),
        ("proposals", "P1"), ("proposals", "P2")]


def test_seed_without_rules_clears_old_proposals(env: Path) -> None:
    old = env / "out/docs/proposals"
    old.mkdir(parents=True)
    (old / "P9.json").write_text("{}", encoding="utf-8")
    assert fault_review.seed("tag", None, None) == 0
    assert list(old.glob("*.json")) == []
    writes = json.loads((env / "out/batch1.json")
                        .read_text(encoding="utf-8"))
    assert all(w["collection"] != "proposals" for w in writes)


def test_seed_rejects_a_missing_field(env: Path) -> None:
    bad = rule("P1")
    del bad["keep"]
    with pytest.raises(SystemExit) as info:
        fault_review.seed("tag", None, None, rules_file(env, [bad]))
    assert "keep" in str(info.value)


def test_seed_rejects_a_duplicate_label(env: Path) -> None:
    with pytest.raises(SystemExit) as info:
        fault_review.seed("tag", None, None,
                          rules_file(env, [rule("P1"), rule("P1")]))
    assert "P1" in str(info.value)


def test_apply_prints_each_decision_and_spares_the_pairs(
        env: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cards = env / "cards"
    cards.mkdir()
    props = env / "props"
    props.mkdir()
    decisions = [("P1", "approve", ""), ("P2", "narrow", "only ch30"),
                 ("P3", "reject", "too broad"), ("P4", None, "")]
    for order, (label, decision, note) in enumerate(decisions):
        doc = {"order": order, "label": label, "decision": decision,
               "note": note}
        (props / f"{label}.json").write_text(
            json.dumps({"data": doc}), encoding="utf-8")
    pairs_file = env / "edit_pairs.json"
    before = json.loads(pairs_file.read_text(encoding="utf-8"))
    assert fault_review.apply(cards, props) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[-5:-1] == ["P1 approve", "P2 narrow: only ch30",
                            "P3 reject: too broad", "P4 undecided"]
    assert lines[-1].startswith("4 proposal(s)")
    assert json.loads(pairs_file.read_text(encoding="utf-8")) == before


def test_apply_reports_a_missing_rules_dir(env: Path) -> None:
    assert fault_review.apply(env, env / "nope") == 1
