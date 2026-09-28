"""Turn an edit-patterns hit list into fixes Bruce approves on a page.

`edit_patterns.py` finds the book's sentences that share a fault Bruce
fixed once. A list of 183 metadiscourse sentences is a worklist nobody
reads in a terminal, so the hits go on an artifact page
(`.claude/skills/edit-done/fix_triage.html`): one card per hit, the
sentence in its paragraph, a proposed rewrite editable in place, and
four choices. Apply rewrite and Delete sentence change the chapter;
Skip keeps a sentence that has the fault; Not this fault marks a false
hit. The last two are labels as much as decisions, and `apply` reports
them per fault so the pair's floor can be revisited.

    uv run python -m tools.fix_triage export PAIR [PAIR ...]
    uv run python -m tools.fix_triage seed
    uv run python -m tools.fix_triage apply build/fix_triage/read/cards

`export` writes `build/fix_triage/hits.json`, every hit at or above
each pair's floor, with a stable id per hit. PAIR is a pair key from
`edit_pairs.json` or `FILE:LINE` naming one. The session then writes
`build/fix_triage/proposals.json`, an object from hit id to
`{"rewrite": ...}` or `{"delete": true}` or `{"not_fault": true}`,
since proposing a rewrite is a judgment about the prose. `seed` joins
the two into one database document per card plus batch files of 50
writes. `apply` reads the cards back (as `ArtifactData`'s `list` with
`out_dir` saves them) and edits each chapter: the sentence is found by
its words with any whitespace between them, since the Markdown breaks
lines within it, and replaced or removed. Reflow is left to `tip
verify-ch`.
"""

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from tools import judgments
from tools.config import BUILD_DIR, CHAPTERS_DIR, ROOT
from tools.edit_patterns import (
    PAIRS_FILE, REPORT, Cache, book, confirm_key, example)

OUT = BUILD_DIR / "fix_triage"
BATCH = 50


def find_pair(pairs: dict[str, dict[str, Any]], name: str) -> str:
    if name in pairs:
        return name
    file, _, line = name.rpartition(":")
    for k, p in pairs.items():
        if p["file"] == file and str(p["line"]) == line:
            return k
    sys.exit(f"fix_triage: no pair {name}")


def hit_id(pair: str, file: str, sentence: str) -> str:
    text = f"{pair}|{file}|{sentence}".encode()
    return hashlib.sha256(text).hexdigest()[:16]


def export(names: list[str]) -> int:
    pairs = judgments.load(PAIRS_FILE)
    cache = Cache()
    sentences = book()
    hits: list[dict[str, Any]] = []
    faults = {}
    for name in names:
        k = find_pair(pairs, name)
        p = pairs[k]
        floor = p.get("floor", REPORT)
        faults[k] = {**example(p), "file": p["file"], "line": p["line"]}
        for f, s in sentences:
            v = cache.get(confirm_key(p, s))
            if v is not None and v >= floor:
                hits.append({
                    "id": hit_id(k, f, s.text), "pair": k, "file": f,
                    "line": s.line, "heading": s.heading,
                    "paragraph": s.paragraph, "sentence": s.text,
                    "score": v})
    hits.sort(key=lambda h: (h["file"], h["line"]))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "hits.json").write_text(json.dumps(
        {"faults": faults, "hits": hits}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    by = collections.Counter(h["pair"] for h in hits)
    for k, n in by.items():
        print(f"{pairs[k]['file']}:{pairs[k]['line']}  {n} hits")
    print(f"{len(hits)} hits in {(OUT / 'hits.json').relative_to(ROOT)}")
    return 0


def seed() -> int:
    data = json.loads((OUT / "hits.json").read_text(encoding="utf-8"))
    proposals = json.loads(
        (OUT / "proposals.json").read_text(encoding="utf-8"))
    docs = OUT / "docs"
    for sub in ("faults", "cards"):
        (docs / sub).mkdir(parents=True, exist_ok=True)
        for old in (docs / sub).glob("*.json"):
            old.unlink()
    writes = []
    for k, fault in data["faults"].items():
        path = docs / "faults" / f"{k}.json"
        path.write_text(json.dumps(fault, ensure_ascii=False),
                        encoding="utf-8")
        writes.append({"op": "set", "collection": "faults", "doc_id": k,
                       "file_path": str(path)})
    missing = 0
    for order, h in enumerate(data["hits"]):
        prop = proposals.get(h["id"])
        missing += prop is None
        prop = prop or {}
        card = {
            "order": order, "pair": h["pair"], "file": h["file"],
            "line": h["line"], "heading": h["heading"],
            "paragraph": h["paragraph"], "sentence": h["sentence"],
            "proposed": prop.get("rewrite", ""),
            "rewrite": prop.get("rewrite", ""),
            "suggest": ("delete" if prop.get("delete") else
                        "not_fault" if prop.get("not_fault") else
                        "rewrite"),
            "note": prop.get("note", ""),
            "flagged": h.get("flagged", ""),
            "decision": None}
        path = docs / "cards" / f"{h['id']}.json"
        path.write_text(json.dumps(card, ensure_ascii=False),
                        encoding="utf-8")
        writes.append({"op": "set", "collection": "cards",
                       "doc_id": h["id"], "file_path": str(path)})
    for old in OUT.glob("batch*.json"):
        old.unlink()
    for i in range(0, len(writes), BATCH):
        (OUT / f"batch{i // BATCH + 1}.json").write_text(
            json.dumps(writes[i:i + BATCH]), encoding="utf-8")
    print(f"{len(data['hits'])} cards, {missing} without a proposal, "
          f"{-(-len(writes) // BATCH)} batch file(s)")
    return 0


def pattern(sentence: str) -> re.Pattern[str]:
    """The sentence's words with any run of whitespace between them."""
    return re.compile(r"\s+".join(re.escape(w) for w in sentence.split()))


def apply(read_dir: Path) -> int:
    cards = []
    for path in sorted(read_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        cards.append(doc.get("data", doc))
    tally: dict[str, collections.Counter[str]] = collections.defaultdict(
        collections.Counter)
    edits: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for c in cards:
        tally[c["pair"]][c.get("decision") or "undecided"] += 1
        if c.get("decision") in ("apply", "delete"):
            edits[c["file"]].append(c)
    failed = []
    for file, todo in sorted(edits.items()):
        path = CHAPTERS_DIR / file
        text = path.read_text(encoding="utf-8")
        for c in todo:
            m = pattern(c["sentence"]).search(text)
            if m is None:
                failed.append(f"{file}:{c['line']}")
                continue
            new = ("" if c["decision"] == "delete"
                   else " ".join(c["rewrite"].split()))
            start, end = m.start(), m.end()
            if not new:
                # Take the separating whitespace after the sentence too,
                # or a blank remains where it stood.
                while end < len(text) and text[end] in " \t":
                    end += 1
                if end < len(text) and text[end] == "\n" and (
                        start == 0 or text[start - 1] == "\n"):
                    end += 1
            text = text[:start] + new + text[end:]
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"{file}: {len(todo)} edit(s)")
    pairs = judgments.load(PAIRS_FILE)
    for k, counts in tally.items():
        p = pairs.get(k)
        where = f"{p['file']}:{p['line']}" if p else k
        print(f"{where}  " + ", ".join(
            f"{n} {d}" for d, n in sorted(counts.items())))
    for where in failed:
        print(f"not found, left alone: {where}")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    global OUT
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export", help="write the hits for these pairs")
    e.add_argument("pairs", nargs="+", help="pair key or FILE:LINE")
    sub.add_parser("seed", help="join hits and proposals into cards")
    a = sub.add_parser("apply", help="edit the chapters from the cards")
    a.add_argument("read_dir", type=Path)
    ap.add_argument("--dir", type=Path, default=OUT,
                    help="working directory for this batch (default "
                         "build/fix_triage)")
    args = ap.parse_args(argv)
    OUT = args.dir.resolve()
    if args.command == "export":
        return export(args.pairs)
    if args.command == "seed":
        return seed()
    return apply(args.read_dir)


if __name__ == "__main__":
    raise SystemExit(main())
