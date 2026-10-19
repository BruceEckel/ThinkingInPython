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
        --proposals build/fault_review/proposals.json \
        --rules build/fault_review/rules.json
    uv run python -m tools.fault_review apply \
        build/fault_review/read/cards \
        --rules-dir build/fault_review/read/proposals

Three filters keep the page small. Chapter 31's pass (2026-10-19)
rewrote whole sections and produced 185 cards: 128 pairs at similarity
0.3 to 0.5 were spurious (old sentences paired with unrelated new
ones), 22 at 0.6 were mixed, and 35 at 0.7 and above were real
one-sentence edits, eleven of them the same word moving (row to rule,
event to input, items to slots). The author read 192 items.

1. A pair below the similarity floor (`edit_patterns.MIN_SIMILARITY`,
   0.6; `--min-similarity X` overrides it) is not recorded, and the
   seed prints the count dropped.
2. A word-for-word replacement that appears in three or more pairs is
   a rename, and a pair whose only changes are renames is not
   recorded. Each rename prints as `rename: "row" -> "rule" in 7
   sentences`.
3. A local proposal makes no card. The seed writes it straight into
   the pair (`fault` cleared, `local` true, `local_basis` "session"),
   exactly the effect of a card marked Local edit.

`meta/pass.json` carries the results: `min_similarity`, `dropped`,
`renames` (a list of `{old, new, count}`), and `locals` (a list of
`{key, line, before, after, fault, ...}`, `fault` being the session's
reason). The page shows them as a header line and one collapsed row,
"N local edits, applied by the session", whose items each have a
Disagree button. Disagree creates the `cards/<key>` document with the
session's reason as the proposed line and no decision, so `apply` reads
it like any other card: an approval replaces the session's local
mark with the fault line, and a Local edit decision records `author`
as the basis. `apply` never touches the `locals` list; a key with a card
simply has its decision read from the card.

`seed` writes one JSON file per database document under
`build/fault_review/docs/` (`meta/pass.json` and `cards/<pair key>.json`)
and the `ArtifactData` batch lists that load them, 50 writes to a
batch. A card's proposal comes from the proposals file, a JSON object
from pair key to either a fault line or `{"fault": ..., "local": true}`
for an edit the session judges local (the `fault` there is its reason),
or else from the pair's stored `fault`. Every card should get a line:
on chapter 30's first page the four cards left blank as local edits had
a disabled Approve and read as broken. Proposing a
fault is a judgment about Bruce's intent, so the session writes that
file; this module never invents one.

`apply` reads the cards back, as `ArtifactData`'s `list` with
`out_dir` saves them, and writes each decision into `edit_pairs.json`:
an approved card's text, edited or not, becomes the pair's `fault`,
and a local edit clears it. Undecided cards are listed and left alone.

The page has a second collection, `proposals`: the rule proposals from
`/bruce-edit-capture`, which Bruce also decides on the page with
Approve, Narrow, or Reject and a note. `seed --rules PATH` takes a JSON
list of proposal objects, each with the fields `label`, `kind`,
`title`, `rule`, `test`, `keep`, `home`, and `evidence`. `kind` is
"Promotion", "Widening", "New candidate", or "New candidate, additive".
An evidence item has a `where` and either `before` and `after` (a
sentence pair) or `text` (a description). The labels must be unique;
`seed` exits with a message naming a missing field or a duplicate
label. It writes `docs/proposals/<label>.json` with `order` (the list
position), `decision` None, and `note` empty added, and appends those
writes to the same batch files, after the cards. Without `--rules`,
`seed` still clears `docs/proposals/`, so a previous pass's proposals
do not linger. The page hides the collection when it is empty.

`apply --rules-dir DIR` reads the `proposals` collection back, saved
the same way, and prints one line per proposal in `order`: `P1
approve`, `P3 narrow: <note>`, `P8 reject: <note>`, or `P5
undecided`, then a count line. It never writes `bruce_edit_db.md`.
That rule store stays hand-written from Bruce's decisions, in his
words, so the printed lines are the input to that edit.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from tools import judgments
from tools.config import BUILD_DIR, ROOT
from tools.edit_patterns import MIN_SIMILARITY, PAIRS_FILE, record_pass

OUT = BUILD_DIR / "fault_review"
BATCH = 50
RULE_FIELDS = ("label", "kind", "title", "rule", "test", "keep",
               "home", "evidence")


def load_rules(path: Path | None) -> list[dict[str, Any]]:
    """The proposals in `path`, checked; exit on a bad one."""
    if path is None:
        return []
    rules: list[dict[str, Any]] = json.loads(
        path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    for i, rule in enumerate(rules):
        for field in RULE_FIELDS:
            if field not in rule:
                raise SystemExit(
                    f"proposal {i} ({rule.get('label', '?')}) is "
                    f"missing the field {field!r}")
        if rule["label"] in seen:
            raise SystemExit(f"duplicate proposal label "
                             f"{rule['label']!r}")
        seen.add(rule["label"])
    return rules


def seed(since: str | None, span: str | None, proposals: Path | None,
         rules: Path | None = None,
         min_similarity: float = MIN_SIMILARITY) -> int:
    rule_docs = load_rules(rules)
    pairs = judgments.load(PAIRS_FILE)
    recorded = record_pass(pairs, since, span, min_similarity)
    keys = recorded.keys
    proposed: dict[str, Any] = (
        json.loads(proposals.read_text(encoding="utf-8"))
        if proposals else {})
    docs = OUT / "docs"
    for sub in ("meta", "cards", "proposals"):
        (docs / sub).mkdir(parents=True, exist_ok=True)
        for old in (docs / sub).glob("*.json"):
            old.unlink()
    source = span or since or ""
    writes: list[dict[str, str]] = []
    blank = 0
    locals_: list[dict[str, Any]] = []
    cards = 0
    for k in keys:
        p = pairs[k]
        entry = proposed.get(k, p.get("fault", ""))
        fault = entry["fault"] if isinstance(entry, dict) else entry
        if isinstance(entry, dict) and entry.get("local"):
            # The session's judgment stands unless Bruce disagrees.
            p["fault"] = ""
            p["local"] = True
            p["local_basis"] = "session"
            locals_.append({
                "key": k, "file": p["file"], "line": p["line"],
                "heading": p.get("heading", ""),
                "paragraph": p.get("paragraph", ""),
                "before": p["before"], "after": p["after"],
                "fault": fault})
            continue
        blank += not fault.strip()
        card = {
            "order": cards, "file": p["file"], "line": p["line"],
            "heading": p.get("heading", ""),
            "paragraph": p.get("paragraph", ""),
            "before": p["before"], "after": p["after"],
            "proposed": fault, "fault": fault, "local_hint": False,
            "decision": None}
        cards += 1
        path = docs / "cards" / f"{k}.json"
        path.write_text(json.dumps(card, ensure_ascii=False),
                        encoding="utf-8")
        writes.append({"op": "set", "collection": "cards", "doc_id": k,
                       "file_path": str(path)})
    judgments.save(PAIRS_FILE, pairs)
    for i, item in enumerate(locals_):
        item["order"] = cards + i
    stray = [k for k in proposed if k not in keys]
    files = sorted({pairs[k]["file"] for k in keys})
    meta = {"source": source, "files": files, "count": len(keys),
            "proposals": len(rule_docs),
            "seeded": datetime.date.today().isoformat(),
            "min_similarity": min_similarity,
            "dropped": recorded.dropped, "renames": recorded.renames,
            "locals": locals_}
    (docs / "meta" / "pass.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    writes.insert(0, {"op": "set", "collection": "meta",
                      "doc_id": "pass",
                      "file_path": str(docs / "meta" / "pass.json")})
    for order, rule in enumerate(rule_docs):
        doc = {"order": order, **rule, "decision": None, "note": ""}
        path = docs / "proposals" / f"{rule['label']}.json"
        path.write_text(json.dumps(doc, ensure_ascii=False),
                        encoding="utf-8")
        writes.append({"op": "set", "collection": "proposals",
                       "doc_id": rule["label"], "file_path": str(path)})
    for i in range(0, len(writes), BATCH):
        (OUT / f"batch{i // BATCH + 1}.json").write_text(
            json.dumps(writes[i:i + BATCH]), encoding="utf-8")
    if blank:
        print(f"{blank} card(s) have no proposed line; give every card "
              "one, marking local edits with \"local\": true",
              file=sys.stderr)
    if stray:
        print(f"{len(stray)} proposal key(s) name no pair the filters "
              "kept, ignored", file=sys.stderr)
    for line in recorded.lines():
        print(line)
    print(f"{cards} cards, {len(locals_)} local edits applied, "
          f"{len(rule_docs)} rule proposals "
          f"({blank} cards with no proposed fault; "
          f"{-(-len(writes) // BATCH)} batch file(s) in "
          f"{OUT.relative_to(ROOT)})")
    return 0


def read_card(path: Path) -> dict[str, Any]:
    """A saved document, whether saved bare or wrapped with its id."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("data", doc)


def report_rules(rules_dir: Path) -> None:
    """Print Bruce's decision on each proposal; write nothing."""
    docs = sorted((read_card(p) for p in rules_dir.glob("*.json")),
                  key=lambda d: d.get("order", 0))
    counts: dict[str, int] = {}
    for doc in docs:
        decision = doc.get("decision") or "undecided"
        counts[decision] = counts.get(decision, 0) + 1
        note = " ".join(str(doc.get("note", "")).split())
        extra = f": {note}" if note and decision in (
            "narrow", "reject") else ""
        print(f"{doc['label']} {decision}{extra}")
    summary = ", ".join(f"{n} {name}" for name, n in counts.items())
    print(f"{len(docs)} proposal(s): {summary or 'none'}")


def apply(read_dir: Path, rules_dir: Path | None = None) -> int:
    if rules_dir is not None and not rules_dir.is_dir():
        print(f"{rules_dir}: no such directory", file=sys.stderr)
        return 1
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
                # A card made by "Disagree" on a local edit wins.
                pairs[k].pop("local", None)
                pairs[k].pop("local_basis", None)
                approved += 1
            case "local":
                pairs[k]["fault"] = ""
                pairs[k]["local"] = True
                pairs[k]["local_basis"] = "author"
                local += 1
            case _:
                undecided.append(where)
    judgments.save(PAIRS_FILE, pairs)
    print(f"{approved} fault line(s) approved, {local} local edit(s)")
    for where in undecided:
        print(f"undecided: {where}")
    if rules_dir is not None:
        report_rules(rules_dir)
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
    s.add_argument("--min-similarity", type=float,
                   default=MIN_SIMILARITY,
                   help="drop rewrites scoring below this "
                        f"(default {MIN_SIMILARITY})")
    s.add_argument("--rules", type=Path,
                   help="JSON list of rule proposals for the page")
    a = sub.add_parser("apply", help="write the decisions to the pairs")
    a.add_argument("read_dir", type=Path,
                   help="the cards as ArtifactData saved them")
    a.add_argument("--rules-dir", type=Path,
                   help="the proposals as ArtifactData saved them")
    args = ap.parse_args(argv)
    if args.command == "seed":
        return seed(args.since, args.span, args.proposals,
                    args.rules, args.min_similarity)
    return apply(args.read_dir, args.rules_dir)


if __name__ == "__main__":
    raise SystemExit(main())
