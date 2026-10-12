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
    uv run python -m tools.fix_triage direct [--commit] [--trailer TEXT]
        [--jobs N]

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
verify-ch`. `apply` refuses a directory holding a card outside the
current `hits.json`, since a read into a directory that already holds an
earlier page's cards leaves them in place.

A pair marked `"direct": true` in `edit_pairs.json` skips the page. The
flag is set after a page where Bruce applied the proposals wholesale.
`direct` applies the proposed rewrites to the chapters. With `--commit`
it gates every edited chapter with `tip verify-ch` and, once all the
gates pass, commits them one chapter per commit, so Bruce reviews the
git diff; one failed gate holds every commit, so the batch is never
half committed. Deletions and
proposals without a rewrite are listed and left for the session, which
reads the next sentence for a lost antecedent. A pair without the flag
is refused.
"""

import argparse
import collections
import concurrent.futures
import hashlib
import json
import re
import subprocess
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


def edit_chapters(
        edits: dict[str, list[tuple[str, str, int]]]) -> list[str]:
    """Replace sentences in chapters; return the `file:line` misses.

    `edits` maps a chapter file to (sentence, new text, line) triples.
    New text "" deletes the sentence.
    """
    failed = []
    for file, todo in sorted(edits.items()):
        path = CHAPTERS_DIR / file
        text = path.read_text(encoding="utf-8")
        edited = 0
        for sentence, new, line in todo:
            m = pattern(sentence).search(text)
            if m is None:
                failed.append(f"{file}:{line}")
                continue
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
            edited += 1
        if edited:
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"{file}: {edited} edit(s)")
    return failed


def apply(read_dir: Path) -> int:
    hits_file = OUT / "hits.json"
    if not hits_file.exists():
        print("fix_triage: no hits.json; run export first")
        return 1
    known = {h["id"] for h in json.loads(
        hits_file.read_text(encoding="utf-8"))["hits"]}
    paths = sorted(read_dir.glob("*.json"))
    stale = sorted(p.stem for p in paths if p.stem not in known)
    if stale:
        print(f"fix_triage: {len(stale)} stale card(s) in {read_dir}, "
              "not in hits.json:")
        for name in stale:
            print(f"  {name}")
        print("delete them or re-read the page's cards into an empty "
              "directory")
        return 1
    cards = []
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        cards.append(doc.get("data", doc))
    tally: dict[str, collections.Counter[str]] = collections.defaultdict(
        collections.Counter)
    edits: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for c in cards:
        tally[c["pair"]][c.get("decision") or "undecided"] += 1
        if c.get("decision") in ("apply", "delete"):
            edits[c["file"]].append(c)
    failed = edit_chapters({
        file: [(c["sentence"],
                "" if c["decision"] == "delete"
                else " ".join(c["rewrite"].split()), c["line"])
               for c in todo]
        for file, todo in edits.items()})
    pairs = judgments.load(PAIRS_FILE)
    for k, counts in tally.items():
        p = pairs.get(k)
        where = f"{p['file']}:{p['line']}" if p else k
        print(f"{where}  " + ", ".join(
            f"{n} {d}" for d, n in sorted(counts.items())))
    for where in failed:
        print(f"not found, left alone: {where}")
    return 1 if failed else 0


def run_gate(nn: str) -> tuple[int, str]:
    """Run the chapter gate; return its exit code and output."""
    r = subprocess.run(
        ["uv", "run", "tip", "verify-ch", f"CH={nn}", "ISOLATED=1"],
        capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


def commit_chapter(file: str, message: str) -> str:
    """Commit one chapter file alone; return the short sha."""
    rel = f"Chapters/{file}"
    subprocess.run(["git", "add", "--", rel], check=True, cwd=ROOT)
    subprocess.run(["git", "commit", "-q", "-m", message, "--", rel],
                   check=True, cwd=ROOT)
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                       check=True, capture_output=True, text=True,
                       cwd=ROOT)
    return r.stdout.strip()


def chapter_number(file: str) -> str:
    return file.split("_", 1)[0]


def commit_message(nn: str, n: int, keys: list[str],
                   pairs: dict[str, dict[str, Any]],
                   trailer: str) -> str:
    noun = "sentence" if n == 1 else "sentences"
    paras = [f"Chapter {nn}: {n} {noun} from the direct fault search"]
    for k in keys:
        p = pairs[k]
        fault = p.get("fault", "")
        first = fault.split(". ", 1)[0] + "." if ". " in fault else fault
        paras.append(
            f"Pair {k} ({p['file']}:{p['line']}), applied without a "
            f"page because the pair is marked direct. Fault: {first}")
    if trailer:
        paras.append(trailer)
    return "\n\n".join(paras)


def direct(commit: bool = False, trailer: str = "",
           jobs: int = 4) -> int:
    hits_file = OUT / "hits.json"
    props_file = OUT / "proposals.json"
    if not hits_file.exists():
        print("fix_triage: no hits.json; run export first")
        return 1
    if not props_file.exists():
        print("fix_triage: no proposals.json")
        return 1
    hits = json.loads(hits_file.read_text(encoding="utf-8"))["hits"]
    proposals = json.loads(props_file.read_text(encoding="utf-8"))
    pairs = judgments.load(PAIRS_FILE)
    refused = False
    for k in dict.fromkeys(h["pair"] for h in hits):
        p = pairs.get(k, {})
        if not p.get("direct"):
            where = f"{p['file']}:{p['line']}" if p else k
            print(f"fix_triage: pair {where} is not marked direct in "
                  "edit_pairs.json; use seed and a page")
            refused = True
    if refused:
        return 1
    edits: dict[str, list[tuple[str, str, int]]] = (
        collections.defaultdict(list))
    used: dict[str, list[str]] = collections.defaultdict(list)
    left: list[str] = []
    for h in hits:
        prop = proposals.get(h["id"])
        where = f"{h['file']}:{h['line']}  {h['sentence'][:60]}"
        if prop is None:
            left.append(f"no proposal: {where}")
        elif prop.get("delete"):
            left.append(f"left for the session (deletion): {where}")
        elif prop.get("not_fault") or not isinstance(
                prop.get("rewrite"), str) or not prop["rewrite"].strip():
            left.append(f"left for the session (no rewrite): {where}")
        else:
            edits[h["file"]].append((
                h["sentence"], " ".join(prop["rewrite"].split()),
                h["line"]))
            if h["pair"] not in used[h["file"]]:
                used[h["file"]].append(h["pair"])
    failed = edit_chapters(edits)
    for where in failed:
        print(f"not found, left alone: {where}")
    missed: collections.Counter[str] = collections.Counter(
        f.rpartition(":")[0] for f in failed)
    counts = {f: len(todo) - missed[f] for f, todo in edits.items()}
    done = {f: n for f, n in counts.items() if n > 0}
    for line in left:
        print(line)
    total = sum(done.values())
    print(f"direct: {total} rewrite(s) in {len(done)} chapter(s), "
          f"{len(left)} left for the session")
    status = 1 if failed else 0
    if not commit or not done:
        return status
    files = sorted(done)
    with concurrent.futures.ThreadPoolExecutor(max(1, jobs)) as pool:
        results = list(pool.map(
            lambda f: run_gate(chapter_number(f)), files))
    bad = [(chapter_number(f), out)
           for f, (code, out) in zip(files, results) if code != 0]
    for nn, output in bad:
        print(f"gate failed: {nn}")
        for line in output.splitlines()[-30:]:
            print(f"  {line}")
    if bad:
        # Every edit stays in the working tree, so one fix and one
        # rerun finish the batch with no chapter committed ahead of it.
        print(f"{len(bad)} gate(s) failed; nothing committed")
        return 1
    for file in files:
        nn = chapter_number(file)
        message = commit_message(nn, done[file], used[file], pairs,
                                 trailer)
        print(f"committed {nn}: {commit_chapter(file, message)}")
    return status


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
    d = sub.add_parser(
        "direct", help="apply the proposals without a page")
    d.add_argument("--commit", action="store_true",
                   help="gate and commit each chapter")
    d.add_argument("--trailer", default="",
                   help="last paragraph of each commit message")
    d.add_argument("--jobs", type=int, default=4,
                   help="gates to run at once (default 4)")
    ap.add_argument("--dir", type=Path, default=OUT,
                    help="working directory for this batch (default "
                         "build/fix_triage)")
    args = ap.parse_args(argv)
    OUT = args.dir.resolve()
    if args.command == "export":
        return export(args.pairs)
    if args.command == "seed":
        return seed()
    if args.command == "direct":
        return direct(args.commit, args.trailer, args.jobs)
    return apply(args.read_dir)


if __name__ == "__main__":
    raise SystemExit(main())
