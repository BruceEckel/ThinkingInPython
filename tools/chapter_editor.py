"""Load a chapter into the chapter editor page and apply a round back.

The chapter editor (`.claude/skills/chapter-editor/chapter_editor.html`)
shows a whole chapter, one block per paragraph, heading, list, or
listing. Bruce reads it and marks what needs work with the mouse: a
Rewrite mark (with an optional note) asks the session to rewrite the
selected text, a Delete mark removes it, and Edit opens a block's
Markdown source for him to change in place. "Send round" hands the
round over. The session then applies it to the Markdown, rewrites
what he marked, runs the verify loop, and loads the chapter back, so
the page shows the new text with the changed blocks highlighted.
The Markdown stays the source of truth; the page's database mirrors it.

    uv run python -m tools.chapter_editor load 30
    uv run python -m tools.chapter_editor apply 30

`load` parses the chapter into blocks and writes one JSON file per
database document under `build/chapter_editor/NN/docs/` plus the
`ArtifactData` batch lists that write them, 50 writes to a batch, and
a copy of the page named for the chapter, to publish. The
first load writes every block. A later one compares the chapter with
the snapshot the previous load left in `state.json` and writes only
what changed: a block whose text changed keeps its id and records its
old text as `previous`, so the page can show the change; a block
whose marks the last `apply` consumed is written again with its
marks cleared; a block gone from the chapter is deleted. The order of
the blocks and their line numbers live in the `meta/chapter` document,
so a block that moves does not need a write.

`apply` reads the documents back, as `ArtifactData`'s `list` with
`out_dir` saves them (`build/chapter_editor/NN/read/blocks/*.json`
and `read/meta/`, unless a directory is named), and
changes the chapter. An in-place edit replaces its block verbatim;
Delete marks are then cut from that text, with the spaces around each
cut tidied. Rewrite marks are not applied: they are the session's
work, so `apply` prints them and saves them to
`build/chapter_editor/NN/round-R.json`. A marked block whose text in
the chapter no longer matches what the page showed (an edit made in
Zed during the round) is a conflict: its edit and marks are listed
for the session to handle by hand, and nothing is applied to it.
"""

import argparse
import datetime
import difflib
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.config import BUILD_DIR, CHAPTERS_DIR, ROOT
from tools.prose import BLOCKQUOTE, FENCE, HEADING, HTML, LIST, TABLE
from tools.repo import write_text_lf

OUT = BUILD_DIR / "chapter_editor"
BATCH = 50
PAGE = ROOT / ".claude" / "skills" / "chapter-editor" / "chapter_editor.html"


@dataclass
class Block:
    start: int  # First line, 0-based.
    end: int  # One past the last line.
    text: str
    kind: str


def kind_of(first: str) -> str:
    if HEADING.match(first):
        return "heading"
    if LIST.match(first):
        return "list"
    if BLOCKQUOTE.match(first):
        return "quote"
    if TABLE.match(first):
        return "table"
    if first.lstrip().startswith("!["):
        return "figure"
    if HTML.match(first):
        return "html"
    return "prose"


def parse(text: str) -> list[Block]:
    """Split a chapter at blank lines, keeping each fence whole.

    A heading is its own block even with no blank line after it, and a
    fence that opens inside a paragraph starts a new block.
    """
    lines = text.split("\n")
    out: list[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        start = i
        if m := FENCE.match(line):
            mark = m.group(1)
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith(mark):
                i += 1
            i = min(i + 1, len(lines))
            kind = "code"
        elif HEADING.match(line):
            i += 1
            kind = "heading"
        else:
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not FENCE.match(lines[i])
                   and not HEADING.match(lines[i])):
                i += 1
            kind = kind_of(line)
        out.append(Block(start, i, "\n".join(lines[start:i]), kind))
    return out


def chapter_file(chapter: str) -> Path:
    found = sorted(CHAPTERS_DIR.glob(f"{int(chapter):02d}_*.md")
                   if chapter.isdigit()
                   else CHAPTERS_DIR.glob(f"{chapter}_*.md"))
    if len(found) != 1:
        raise SystemExit(f"no single chapter file for {chapter!r}")
    return found[0]


def title_of(text: str) -> str:
    for line in text.split("\n"):
        if line.startswith("# "):
            return re.sub(r"\s*\{#[^}]*\}\s*$", "", line[2:]).strip()
    return ""


def digest(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def out_dir(chapter: Path) -> Path:
    return OUT / chapter.name.split("_", 1)[0]


def load_state(where: Path) -> dict[str, Any] | None:
    path = where / "state.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(where: Path, state: dict[str, Any]) -> None:
    (where / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def align(old: list[str], new: list[str]):  # noqa: ANN201
    return difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()


def load(chapter: str, force: bool, refresh: bool = False) -> int:
    """Write the page's documents for the chapter as it stands.

    A plain load starts the next round. `refresh` stays in the current
    one, for a change made to the chapter while the page is open with no
    marks on it: each block that changed is outlined with the changes the
    round already shows, and keeps the text it had when the round began
    as its previous version.
    """
    path = chapter_file(chapter)
    where = out_dir(path)
    text = path.read_text(encoding="utf-8")
    blocks = parse(text)
    state = load_state(where)
    if refresh and not state:
        raise SystemExit("nothing loaded yet to refresh")
    if state and not state.get("applied") and not (force or refresh):
        print("the last round was loaded but never applied; apply it "
              "first, or pass --force to load over its marks",
              file=sys.stderr)
        return 1
    docs = where / "docs" / "blocks"
    docs.mkdir(parents=True, exist_ok=True)
    for old in docs.glob("*.json"):
        old.unlink()
    rnd = state["round"] + (0 if refresh else 1) if state else 1
    stamp = rnd  # The round whose page outlines the change.
    info: dict[str, dict[str, Any]] = state["blocks"] if state else {}
    old_order: list[str] = state["order"] if state else []
    consumed = set(state.get("consumed", [])) if state else set()
    next_id = state["next_id"] if state else 1
    order: list[str] = []
    writes: list[dict[str, Any]] = []
    changed = 0

    def fresh() -> str:
        nonlocal next_id
        bid = f"b{next_id:04d}"
        next_id += 1
        return bid

    def put(bid: str, b: Block, previous: str | None, when: int) -> None:
        doc = {"kind": b.kind, "source": b.text, "changed": when,
               "previous": previous, "marks": [], "edit": None}
        info[bid] = {"source": b.text, "kind": b.kind, "changed": when,
                     "previous": previous}
        file = docs / f"{bid}.json"
        file.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        writes.append({"op": "set", "collection": "blocks", "doc_id": bid,
                       "file_path": str(file)})

    new_texts = [b.text for b in blocks]
    old_texts = [info[bid]["source"] for bid in old_order]
    gone: list[str] = []
    for op, i1, i2, j1, j2 in align(old_texts, new_texts):
        if op == "equal":
            for bid, b in zip(old_order[i1:i2], blocks[j1:j2]):
                order.append(bid)
                if bid in consumed or not state:
                    rec = info.get(bid, {})
                    put(bid, b, rec.get("previous"), rec.get("changed", 0))
            continue
        olds, news = old_order[i1:i2], blocks[j1:j2]
        for k, b in enumerate(news):
            if k < len(olds):
                bid = olds[k]
                rec = info[bid]
                keep = refresh and rec.get("changed") == stamp
                put(bid, b, rec.get("previous") if keep else rec["source"],
                    stamp)
            else:
                bid = fresh()
                put(bid, b, None, stamp if state else 0)
            order.append(bid)
            changed += 1
        gone.extend(olds[len(news):])
    for bid in gone:
        info.pop(bid, None)
        writes.append({"op": "delete", "collection": "blocks", "doc_id": bid})
    meta = {"chapter": path.name.split("_", 1)[0], "title": title_of(text),
            "file": path.relative_to(ROOT).as_posix(), "round": rnd,
            "status": "open", "order": order,
            "lines": [b.start + 1 for b in blocks],
            "loaded": datetime.datetime.now().isoformat(timespec="seconds")}
    (where / "docs" / "meta").mkdir(parents=True, exist_ok=True)
    meta_file = where / "docs" / "meta" / "chapter.json"
    meta_file.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    # The meta document goes last: the page reopens for marking only
    # once every block it lists is in place.
    writes.append({"op": "set", "collection": "meta", "doc_id": "chapter",
                   "file_path": str(meta_file)})
    write_page(path)
    # The store refuses a write to an existing document unless it names
    # the version last read. The session saves the versions its round
    # read listed as `read/versions.json`, {"blocks/b0004": 4, ...}.
    pins = where / "read" / "versions.json"
    versions = json.loads(pins.read_text(encoding="utf-8")) if (
        state and pins.exists()) else {}
    for w in writes:
        if v := versions.get(f"{w['collection']}/{w['doc_id']}"):
            w["if_version"] = v
    for old in where.glob("batch*.json"):
        old.unlink()
    for i in range(0, len(writes), BATCH):
        (where / f"batch{i // BATCH + 1}.json").write_text(
            json.dumps(writes[i:i + BATCH]), encoding="utf-8")
    save_state(where, {"round": rnd, "order": order, "blocks": info,
                       "next_id": next_id, "consumed": [],
                       "applied": False, "digest": digest(text)})
    print(f"round {rnd}: {len(blocks)} blocks, {changed} changed, "
          f"{len(gone)} removed, {len(writes)} writes in "
          f"{-(-len(writes) // BATCH)} batch file(s) under "
          f"{where.relative_to(ROOT)}")
    return 0


def write_page(chapter: Path) -> Path:
    """Copy the page template, titled for `chapter`, to publish."""
    number = chapter.name.split("_", 1)[0]
    page = PAGE.read_text(encoding="utf-8").replace(
        "<title>Chapter Editor</title>",
        f"<title>Chapter {number} Editor</title>", 1)
    target = out_dir(chapter) / f"chapter_editor_{number}.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return target


def read_doc(path: Path) -> dict[str, Any]:
    """A saved document, whether saved bare or wrapped with its id."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("data", doc)


CLOSERS = ".,;:!?)]"


def join(left: str, right: str) -> str:
    """Close the gap one cut leaves: one space, or none before a closer."""
    left, right = left.rstrip(" \t"), right.lstrip(" \t")
    if left.endswith("\n") and right.startswith("\n"):
        return left + right[1:]  # The cut took a whole line.
    if (not left or not right or left.endswith("\n")
            or right.startswith("\n") or right[0] in CLOSERS
            or left[-1] in "(["):
        return left + right
    return left + " " + right


def cut(text: str, spans: list[tuple[int, int]]) -> tuple[str, list[int]]:
    """Remove `spans` from `text`, returning the text and each cut's place.

    A line the cuts empty is dropped. A blank line an in-place edit
    added (a paragraph split in two) stays, one blank line at most.
    """
    merged: list[list[int]] = []
    for s, e in sorted(spans):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    places = []
    for s, e in reversed(merged):
        left = text[:s]
        text = join(left, text[e:])
        places.append(len(left.rstrip(" \t")))
    text = re.sub(r"\n{3,}", "\n\n", text).strip("\n")
    return text, places[::-1]


def context(text: str, at: int, width: int = 70) -> str:
    s = max(0, at - width)
    return ("…" if s else "") + text[s:at + width].replace("\n", " ") + (
        "…" if at + width < len(text) else "")


def apply(chapter: str, read: Path, force: bool) -> int:
    path = chapter_file(chapter)
    where = out_dir(path)
    state = load_state(where)
    if not state:
        raise SystemExit("no state.json: load the chapter first")
    meta_path = next(iter(sorted((read / "meta").glob("*.json"))), None)
    meta = read_doc(meta_path) if meta_path else {}
    if meta.get("round") != state["round"]:
        raise SystemExit(f"the page is on round {meta.get('round')}, the "
                         f"last load was round {state['round']}")
    if meta.get("status") not in ("submitted", "applying") and not force:
        raise SystemExit("the round has not been sent from the page; "
                         "pass --force to apply it anyway")
    text = path.read_text(encoding="utf-8")
    blocks = parse(text)
    order: list[str] = state["order"]
    info = state["blocks"]
    at: dict[str, int] = {}
    for op, i1, i2, j1, _ in align([info[b]["source"] for b in order],
                                    [b.text for b in blocks]):
        if op == "equal":
            for k in range(i2 - i1):
                at[order[i1 + k]] = j1 + k
    replace: dict[int, str | None] = {}
    rewrites: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    deletions: list[str] = []
    consumed: list[str] = []
    edits = 0
    for file in sorted((read / "blocks").glob("*.json")):
        bid = file.stem
        doc = read_doc(file)
        marks = doc.get("marks") or []
        edit = doc.get("edit")
        if not marks and edit is None:
            continue
        consumed.append(bid)
        idx = at.get(bid)
        if idx is None or blocks[idx].text != doc.get("source"):
            conflicts.append({"id": bid, "source": doc.get("source"),
                              "edit": edit, "marks": marks})
            continue
        base = edit if edit is not None else doc["source"]
        edits += edit is not None
        dels = [(m["start"], m["end"]) for m in marks
                if m.get("kind") == "delete"
                and base[m["start"]:m["end"]] == m.get("quote")]
        stale = [m for m in marks if m.get("kind") == "delete"
                 and base[m["start"]:m["end"]] != m.get("quote")]
        new, places = cut(base, dels) if dels else (base, [])
        for place in places:
            deletions.append(f"{bid}: {context(new, min(place, len(new)))}")
        replace[idx] = new if new.strip() else None
        for m in [m for m in marks if m.get("kind") == "rewrite"] + stale:
            rewrites.append({"id": bid, "quote": m.get("quote", ""),
                             "note": m.get("note", ""),
                             "delete": m.get("kind") == "delete"})
    lines = text.split("\n")
    for idx in sorted(replace, reverse=True):
        b = blocks[idx]
        new = replace[idx]
        if new is None:
            end = b.end + 1 if b.end < len(lines) and not lines[b.end].strip() \
                else b.end
            lines[b.start:end] = []
        else:
            lines[b.start:b.end] = new.split("\n")
    new_text = "\n".join(lines)
    if new_text != text:
        write_text_lf(path, new_text)
    # Find each rewrite's block in the new text, for the worklist.
    after = parse(new_text)
    for r in rewrites + conflicts:
        q = r.get("quote") or (r.get("source") or "")[:40]
        hit = next((b for b in after if q and q in b.text), None)
        r["line"] = hit.start + 1 if hit else None
        r["text"] = hit.text if hit else None
    rnd = state["round"]
    report = {"round": rnd, "rewrites": rewrites, "conflicts": conflicts,
              "deletions": deletions, "edits": edits}
    (where / f"round-{rnd}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    state["consumed"] = consumed
    state["applied"] = True
    save_state(where, state)
    rel = path.relative_to(ROOT).as_posix()
    print(f"round {rnd}: {edits} in-place edit(s), {len(deletions)} "
          f"deletion(s) applied, {len(rewrites)} rewrite(s) to do, "
          f"{len(conflicts)} conflict(s)")
    for d in deletions:
        print(f"  cut  {d}")
    for r in rewrites:
        what = "DELETE (stale offsets)" if r["delete"] else "REWRITE"
        print(f"\n{what} {rel}:{r['line']}  “{r['quote']}”")
        if r["note"]:
            print(f"  note: {r['note']}")
    for c in conflicts:
        print(f"\nCONFLICT {c['id']} (chapter text changed during the "
              f"round), near {rel}:{c['line']}")
        if c["edit"] is not None:
            print(f"  edit: {c['edit']}")
        for m in c["marks"]:
            print(f"  {m.get('kind')}: “{m.get('quote')}” {m.get('note', '')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("load", help="write the page's documents")
    s.add_argument("chapter", help="chapter number, e.g. 30")
    s.add_argument("--force", action="store_true",
                   help="load over a round that was never applied")
    s.add_argument("--refresh", action="store_true",
                   help="update the open round in place (no marks on it)")
    g = sub.add_parser("page", help="rewrite the page copy only, for a "
                       "template change in the middle of a round")
    g.add_argument("chapter")
    a = sub.add_parser("apply", help="apply a sent round to the chapter")
    a.add_argument("chapter")
    a.add_argument("read_dir", type=Path, nargs="?",
                   help="the documents as ArtifactData saved them "
                        "(default build/chapter_editor/NN/read)")
    a.add_argument("--force", action="store_true",
                   help="apply a round the page has not sent")
    args = ap.parse_args(argv)
    if args.command == "load":
        return load(args.chapter, args.force, args.refresh)
    if args.command == "page":
        print(write_page(chapter_file(args.chapter)).relative_to(ROOT))
        return 0
    read = args.read_dir or out_dir(chapter_file(args.chapter)) / "read"
    return apply(args.chapter, read, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
