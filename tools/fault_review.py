"""Seed and read back the fault-line review page for an editing pass.

`/edit-done` step 3b asks Bruce to approve a one-line `fault` for each
sentence he rewrote, since `edit_patterns.py` searches the book only
for a pair that carries one. Approving thirteen lines in a terminal
transcript is slow, so the proposals go on an artifact page instead
(`.claude/skills/edit-done/fault_review.html`): one card per rewrite,
the proposed line editable in place, and Approve or Local edit on each.
The page keeps his choices in its database; this module prepares what
the page shows and applies what he chose.

    uv run python -m tools.fault_review seed --since edit-start-30 \
        --proposals build/fault_review/proposals.json
    uv run python -m tools.fault_review apply build/fault_review/read/cards

`seed` writes one JSON file per database document under
`build/fault_review/docs/` (`meta/pass.json` and `cards/<pair key>.json`)
and the `ArtifactData` batch lists that load them, 50 writes to a
batch. A card's proposal comes from the proposals file, a JSON object
from pair key to fault line, or else from the pair's stored `fault`.
Proposing a fault is a judgment about Bruce's intent, so the session
writes that file; this module never invents one.

`apply` reads the cards back, as `ArtifactData`'s `list` with
`out_dir` saves them, and writes each decision into `edit_pairs.json`:
an approved card's text, edited or not, becomes the pair's `fault`,
and a local edit clears it. Undecided cards are listed and left alone.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from tools import judgments
from tools.config import BUILD_DIR, ROOT
from tools.edit_patterns import PAIRS_FILE, record_pass

OUT = BUILD_DIR / "fault_review"
BATCH = 50


def seed(since: str | None, span: str | None, proposals: Path | None
         ) -> int:
    pairs = judgments.load(PAIRS_FILE)
    keys = record_pass(pairs, since, span)
    judgments.save(PAIRS_FILE, pairs)
    proposed: dict[str, str] = (
        json.loads(proposals.read_text(encoding="utf-8"))
        if proposals else {})
    docs = OUT / "docs"
    for sub in ("meta", "cards"):
        (docs / sub).mkdir(parents=True, exist_ok=True)
        for old in (docs / sub).glob("*.json"):
            old.unlink()
    source = span or since or ""
    files = sorted({pairs[k]["file"] for k in keys})
    meta = {"source": source, "files": files, "count": len(keys),
            "seeded": datetime.date.today().isoformat()}
    (docs / "meta" / "pass.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    writes = [{"op": "set", "collection": "meta", "doc_id": "pass",
               "file_path": str(docs / "meta" / "pass.json")}]
    for order, k in enumerate(keys):
        p = pairs[k]
        fault = proposed.get(k, p.get("fault", ""))
        card = {
            "order": order, "file": p["file"], "line": p["line"],
            "heading": p.get("heading", ""),
            "paragraph": p.get("paragraph", ""),
            "before": p["before"], "after": p["after"],
            "proposed": fault, "fault": fault,
            "decision": None}
        path = docs / "cards" / f"{k}.json"
        path.write_text(json.dumps(card, ensure_ascii=False),
                        encoding="utf-8")
        writes.append({"op": "set", "collection": "cards", "doc_id": k,
                       "file_path": str(path)})
    for i in range(0, len(writes), BATCH):
        (OUT / f"batch{i // BATCH + 1}.json").write_text(
            json.dumps(writes[i:i + BATCH]), encoding="utf-8")
    blank = sum(1 for k in keys if not proposed.get(
        k, pairs[k].get("fault")))
    print(f"{len(keys)} cards ({blank} with no proposed fault), "
          f"{-(-len(writes) // BATCH)} batch file(s) in "
          f"{OUT.relative_to(ROOT)}")
    return 0


def read_card(path: Path) -> dict[str, Any]:
    """A saved document, whether saved bare or wrapped with its id."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("data", doc)


def apply(read_dir: Path) -> int:
    pairs = judgments.load(PAIRS_FILE)
    approved = local = 0
    undecided = []
    for path in sorted(read_dir.glob("*.json")):
        k = path.stem
        card = read_card(path)
        if k not in pairs:
            print(f"{k}: no such pair in {PAIRS_FILE.name}, skipped",
                  file=sys.stderr)
            continue
        where = f"{card['file']}:{card['line']}"
        match card.get("decision"):
            case "approve" if card.get("fault", "").strip():
                pairs[k]["fault"] = " ".join(card["fault"].split())
                approved += 1
            case "local":
                pairs[k]["fault"] = ""
                local += 1
            case _:
                undecided.append(where)
    judgments.save(PAIRS_FILE, pairs)
    print(f"{approved} fault line(s) approved, {local} local edit(s)")
    for where in undecided:
        print(f"undecided: {where}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("seed", help="write the page's documents")
    s.add_argument("--since", help="compare REF with the working tree")
    s.add_argument("--range", dest="span", help="compare A..B")
    s.add_argument("--proposals", type=Path,
                   help="JSON object: pair key -> proposed fault line")
    a = sub.add_parser("apply", help="write the decisions to the pairs")
    a.add_argument("read_dir", type=Path,
                   help="the cards as ArtifactData saved them")
    args = ap.parse_args(argv)
    if args.command == "seed":
        return seed(args.since, args.span, args.proposals)
    return apply(args.read_dir)


if __name__ == "__main__":
    raise SystemExit(main())
