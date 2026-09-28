"""Tests for tools/chapter_editor.py: parse, load, apply, and reload."""
import json
from pathlib import Path

import pytest

from tools import chapter_editor as ce

CHAPTER = """\
# Observer

An opening paragraph
that runs over two lines.

## Section {#sec}

A `code span` stays whole. Cut this sentence.
The rest stays.

```python
# obs/demo.py
print("hi")
```

- a list item
- another

Last paragraph.
"""


@pytest.fixture
def chapter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    path = chapters / "99_Patterns--Observer.md"
    path.write_text(CHAPTER, encoding="utf-8")
    monkeypatch.setattr(ce, "CHAPTERS_DIR", chapters)
    monkeypatch.setattr(ce, "OUT", tmp_path / "out")
    monkeypatch.setattr(ce, "ROOT", tmp_path)
    return path


def docs(where: Path) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in (where / "docs" / "blocks").glob("*.json")}


def page_round(where: Path, read: Path, marks: dict[str, dict]) -> None:
    """Save the documents the way ArtifactData's list does, with marks."""
    meta = json.loads((where / "docs/meta/chapter.json").read_text("utf-8"))
    meta["status"] = "applying"
    (read / "meta").mkdir(parents=True)
    (read / "blocks").mkdir()
    (read / "meta/chapter.json").write_text(json.dumps({"data": meta}))
    state = json.loads((where / "state.json").read_text("utf-8"))
    for bid, rec in state["blocks"].items():
        doc = {"source": rec["source"], "marks": [], "edit": None,
               **marks.get(bid, {})}
        (read / "blocks" / f"{bid}.json").write_text(
            json.dumps({"id": bid, "data": doc}))


def test_parse_keeps_fences_and_headings_whole() -> None:
    kinds = [b.kind for b in ce.parse(CHAPTER)]
    assert kinds == ["heading", "prose", "heading", "prose", "code",
                     "list", "prose"]


def test_first_load_writes_every_block_and_meta_last(chapter: Path) -> None:
    assert ce.load("99", force=False) == 0
    where = ce.OUT / "99"
    batch = json.loads((where / "batch1.json").read_text("utf-8"))
    assert len(batch) == 8
    assert batch[-1]["collection"] == "meta"


def find(where: Path, text: str) -> str:
    return next(k for k, d in docs(where).items() if text in d["source"])


def test_a_round_applies_edits_and_cuts(chapter: Path, tmp_path: Path
                                        ) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    cut_id = find(where, "Cut this")
    edit_id = find(where, "Last paragraph")
    source = docs(where)[cut_id]["source"]
    quote = "Cut this sentence."
    s = source.index(quote)
    page_round(where, tmp_path / "read", {
        cut_id: {"marks": [
            {"kind": "delete", "start": s, "end": s + len(quote),
             "quote": quote},
            {"kind": "rewrite", "start": 0, "end": 1, "quote": "A",
             "note": "clearer"}]},
        edit_id: {"edit": "The final paragraph."}})
    assert ce.apply("99", tmp_path / "read") == 0
    text = chapter.read_text(encoding="utf-8")
    assert "A `code span` stays whole.\nThe rest stays." in text
    assert "The final paragraph.\n" in text
    report = json.loads((where / "round-1.json").read_text("utf-8"))
    assert [r["note"] for r in report["rewrites"]] == ["clearer"]
    # The reload keeps ids, records the old text, and clears the marks.
    ce.load("99", force=False)
    after = docs(where)
    assert set(after) == {cut_id, edit_id}
    assert after[edit_id]["previous"] == "Last paragraph."
    assert after[edit_id]["changed"] == 2


def test_a_cut_that_empties_a_block_removes_it(chapter: Path,
                                               tmp_path: Path) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    page_round(where, tmp_path / "read", {bid: {"marks": [
        {"kind": "delete", "start": 0, "end": 15,
         "quote": "Last paragraph."}]}})
    ce.apply("99", tmp_path / "read")
    assert chapter.read_text("utf-8").endswith("- another\n")
    ce.load("99", force=False)
    batch = json.loads((where / "batch1.json").read_text("utf-8"))
    assert {"op": "delete", "collection": "blocks",
            "doc_id": bid, "if_version": 1} in batch


def test_a_block_changed_in_the_file_is_a_conflict(chapter: Path,
                                                   tmp_path: Path) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    page_round(where, tmp_path / "read", {bid: {"edit": "Mine."}})
    chapter.write_text(CHAPTER.replace("Last paragraph.", "Zed's."),
                       encoding="utf-8")
    ce.apply("99", tmp_path / "read")
    assert "Zed's." in chapter.read_text("utf-8")
    report = json.loads((where / "round-1.json").read_text("utf-8"))
    assert report["conflicts"][0]["edit"] == "Mine."


def test_join_closes_gaps() -> None:
    assert ce.cut("One two, three.", [(3, 7)]) == ("One, three.", [3])
    assert ce.cut("Keep (drop) this.", [(6, 10)]) == ("Keep () this.", [6])


def test_a_cut_of_a_whole_line_leaves_no_gap() -> None:
    assert ce.cut("One.\nTwo.\nThree.", [(5, 9)]) == ("One.\nThree.", [5])


def test_an_edit_can_split_a_paragraph(chapter: Path, tmp_path: Path
                                       ) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    page_round(where, tmp_path / "read",
               {bid: {"edit": "First half.\n\nSecond half."}})
    ce.apply("99", tmp_path / "read")
    assert chapter.read_text("utf-8").endswith(
        "- another\n\nFirst half.\n\nSecond half.\n")
    ce.load("99", force=False)
    after = docs(where)
    assert after[bid]["source"] == "First half."
    assert any(d["source"] == "Second half." and d["previous"] is None
               for d in after.values())


def test_a_reload_pins_each_write_to_the_version_read(chapter: Path,
                                                      tmp_path: Path) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    read = where / "read"
    page_round(where, read, {bid: {"edit": "Changed."}})
    (read / "versions.json").write_text(
        json.dumps({f"blocks/{bid}": 7, "meta/chapter": 3}))
    ce.apply("99", read)
    ce.load("99", force=False)
    batch = json.loads((where / "batch1.json").read_text("utf-8"))
    pins = {w["doc_id"]: w.get("if_version") for w in batch}
    assert pins == {bid: 7, "chapter": 3}


def test_a_load_pins_the_next_load_from_its_own_batch(
        chapter: Path, tmp_path: Path) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    page_round(where, tmp_path / "read", {bid: {"edit": "Round one."}})
    (where / "read").mkdir()
    (where / "read" / "versions.json").write_text(
        json.dumps({f"blocks/{bid}": 5, "meta/chapter": 3}))
    ce.apply("99", tmp_path / "read")
    ce.load("99", force=False)  # Pins 5 and 3; leaves 6 and 4.
    assert not (where / "read" / "versions.json").exists()
    chapter.write_text(chapter.read_text("utf-8").replace(
        "Round one.", "Round one, refreshed."), encoding="utf-8")
    ce.load("99", force=False, refresh=True)
    batch = json.loads((where / "batch1.json").read_text("utf-8"))
    pins = {w["doc_id"]: w.get("if_version") for w in batch}
    assert pins == {bid: 6, "chapter": 4}


def test_pin_fills_in_a_version_the_ledger_lacks(chapter: Path) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    (where / "versions.json").write_text(json.dumps({"meta/chapter": 2}))
    chapter.write_text(chapter.read_text("utf-8").replace(
        "Last paragraph", "Final paragraph"), encoding="utf-8")
    ce.load("99", force=False, refresh=True)
    batch = json.loads((where / "batch1.json").read_text("utf-8"))
    assert {w["doc_id"]: w.get("if_version") for w in batch} == {
        bid: None, "chapter": 2}
    assert ce.pin("99", [f"blocks/{bid}=4"]) == 0
    batch = json.loads((where / "batch1.json").read_text("utf-8"))
    assert {w["doc_id"]: w.get("if_version") for w in batch} == {
        bid: 4, "chapter": 2}
    ledger = json.loads((where / "versions.json").read_text("utf-8"))
    assert ledger == {f"blocks/{bid}": 5, "meta/chapter": 3}


def test_a_refresh_stays_in_the_round(chapter: Path, tmp_path: Path) -> None:
    ce.load("99", force=False)
    where = ce.OUT / "99"
    bid = find(where, "Last paragraph")
    page_round(where, tmp_path / "read", {bid: {"edit": "Round one."}})
    ce.apply("99", tmp_path / "read")
    ce.load("99", force=False)  # Round 2 shows round 1's change.
    chapter.write_text(chapter.read_text("utf-8").replace(
        "Round one.", "Refreshed."), encoding="utf-8")
    assert ce.load("99", force=False, refresh=True) == 0
    doc = docs(where)[bid]
    assert (doc["changed"], doc["previous"]) == (2, "Last paragraph.")
    state = json.loads((where / "state.json").read_text("utf-8"))
    assert state["round"] == 2
