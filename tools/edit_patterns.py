"""Learn from each sentence Bruce rewrites, then find its like in the book.

`/bruce-edit-capture` turns an editing pass into written rules, and only
a rule seen twice gets applied. This tool works from the examples
instead: every before/after pair from a pass joins
`tools/data/edit_pairs.json`, and each new pair is searched for across
`Chapters/`, so a fault Bruce fixed once in chapter 30 turns up
wherever else the book has it. It reports and never edits; applying a
fix stays a human decision, or a pass's.

A pair alone does not say what its fault was. On the first run, chapter
30's cut of "and this section uses that vocabulary" before a colon
matched 158 sentences for ending in a colon, and a trimmed figure
caption matched every caption in the book. So a pair is searched only
once it carries a `fault`: one line in `edit_pairs.json` naming what
the rewrite fixed, the same judgment `/bruce-edit-capture` makes when
it separates a generalizable edit from a local one. A pair without one
is reported as `needs fault`, and one Bruce's edit made for local
reasons stays that way.

Then three steps, all TypeSafe judgments:

1. Check the pair. A Noul asks whether the pair's own before-sentence
   has the fault (it should) and whether its after-sentence does (it
   should not). A pair that fails is marked `unclear` and not searched:
   a fault a model cannot see in the original is not one it can find
   elsewhere. The first run marked all four exercise renumberings so.
2. Screen the book. One Choice question per sentence offers every
   searchable pair as an option, up to `CHUNK` to a question, plus
   `none`. That costs one question per sentence however many pairs a
   pass made; a Noul per pair per sentence would cost that many times
   more.
3. Confirm. A sentence that gives a pair at least `SCREEN` probability
   gets that pair's Noul, and one at or above `REPORT` is listed,
   strongest first.

`REPORT` is 0.7, from reading the first run's hits (chapter 30's
pass, 2026-09-27). With a fault line, Bruce's own before-sentences
scored 0.83-0.94, and the book's hits above 0.7 were the right shape:
the metadiscourse pair found "Also, notice how much this chapter has
talked about the OS" and a near-twin in chapter 30 itself. Below it
they were loose, and two pairs had nothing above it, correctly: their
nearest hits shared a word ("for example") and not the fault. A pair
whose own before-sentence scores under `REPORT` is `unclear`, since
the fault line does not describe it well enough to search on; the one
such pair, at 0.52, matched 123 unrelated sentences.

Two filters keep a pass that rewrote whole sections from burying the
pairs that matter. Chapter 31's pass (2026-10-19) paired old sentences
with unrelated new ones and made 185 cards: 128 pairs scored 0.3 to
0.5 (all spurious), 22 scored 0.6 (mixed), and 35 scored 0.7 or more
(all real one-sentence edits). So a pair below `MIN_SIMILARITY` is not
recorded, except a cut or an addition: the author's rules (R7, R19,
R34) come from cuts more than from any other edit, and additions are
the rarest and most valued, so a pair with an empty side is kept at
any score and is never a rename. The count is printed as `N rewrites below the 0.6
similarity floor dropped`. Eleven of the real pairs were the same word
moving (row to rule, event to input, items to slots). A replacement of
one word by another that appears in three or more pairs is a rename,
and a pair whose every change is such a rename is not recorded either.
`rename: "row" -> "rule" in 7 sentences` reports each one. A pair that
carries a rename and another change stays a pair.

Answers are cached in `build/edit_patterns.json`, keyed by the pair,
the sentence with its neighbors, and the question's wording, so a
rerun asks only about new pairs and changed sentences.

    tip edit-patterns                          # the open edit-start pass
    tip edit-patterns ARGS="--since edit-start-30"
    tip edit-patterns ARGS="--range a1b2c3d..HEAD"
    tip edit-patterns ARGS=--dry-run
    tip edit-patterns ARGS="--min-similarity 0.5"   # one run's floor
    tip edit-patterns ARGS=--report            # from the cache only
    tip edit-patterns ARGS=--from-rules        # bruce_edit_db.md's rules
    tip edit-patterns ARGS="--pair 30_Patterns--Observer.md:643"  # one pair
"""

import argparse
import datetime
import difflib
import hashlib
import json
import re
import subprocess
import string
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from tools import judgments, sentence_diff
from tools.config import BUILD_DIR, CHAPTERS_DIR, DATA_DIR, ROOT
from tools.repo import md_files, write_text_lf
from tools.sentence_diff import Rewrite, Sentence

PAIRS_FILE = DATA_DIR / "edit_pairs.json"
CACHE = BUILD_DIR / "edit_patterns.json"
REPORT_FILE = BUILD_DIR / "edit_patterns.md"
CHUNK = 20
SCREEN = 0.15
REPORT = 0.7
"""The default listing floor. A pair whose hits Bruce has labeled carries
its own `floor` in `edit_pairs.json`, with a `floor_basis` saying which
labels set it. The rule used on 2026-09-27: the floor that keeps the
most right-labeled hits while at least 70% of the labeled hits at or
above it are right, the higher floor on a tie. Ten labels per fault
moved the floors from 0.62 (R21, nine of ten right) to 0.84 (R2, whose
0.72-0.74 band was all wrong), and for three faults the score did not
rank the right hits first at all, so a floor is a rough filter."""
MIN_SIMILARITY = 0.6
"""A rewrite scoring below this is not recorded as a pair. Evidence,
chapter 31's pass of 2026-10-19: 128 pairs at 0.3 to 0.5 were all
spurious (a section rewrite pairs an old sentence with an unrelated
new one), 22 at 0.6 were mixed, and 35 at 0.7 and above were all real
one-sentence edits. `--min-similarity X` overrides it for one run.
A deletion (a pair whose `after` is empty, which `record_pass` stores
when the score is below `DELETED`) is exempt, and so is an addition (a
pair whose `before` is empty). `sentence_diff.diff` anchors every pair
on an old sentence, so it emits deletions but never additions; the
exemption covers an addition should a pair ever carry one."""
RENAME_MIN = 3
"""A word-for-word replacement in at least this many pairs is a rename."""
DELETED = 0.3
"""Below this similarity the rewrite's nearest new sentence is not its
successor, and the pair is treated as a deletion."""
SHOWN = 12
TRIM = string.punctuation + "\u201c\u201d\u2018\u2019"


def example(pair: dict[str, Any]) -> dict[str, str]:
    return {"fault": pair.get("fault", ""),
            "before": pair["before"],
            "after": pair["after"] or "(the author deleted the sentence)"}


CONFIRM = {
    "type": "noul",
    "instructions": {
        "task": (
            "This book's author rewrote `example.before` as "
            "`example.after` to fix the fault `example.fault` names. "
            "Does `sentence` have that fault, so that the same kind of "
            "rewrite would improve it? Judge the fault as named, not "
            "shared words, shared punctuation, or a shared topic. "
            "`paragraph` is the paragraph holding `sentence`, and "
            "`section_heading` names its section; judge any condition "
            "the fault states about the surrounding passage from "
            "them."),
    },
    "criteria": {
        "true": ("`sentence` has the fault the example's rewrite fixed, "
                 "and the same kind of change would improve it."),
        "false": ("`sentence` does not have that fault, or has it only "
                  "in a form the author's rewrite would not touch."),
    },
}

SCREEN_INSTRUCTIONS = (
    "Each option other than `none` is a rewrite this book's author "
    "made to one sentence: its `before` became its `after`, fixing the "
    "fault its `fault` names. Which option's fault does `sentence` "
    "also have? Judge the fault as named, not shared words, shared "
    "punctuation, or a shared topic. `paragraph` is the paragraph "
    "holding `sentence`, and `section_heading` names its section; "
    "judge any condition a fault states about the surrounding passage "
    "from them.")
NONE = ("`sentence` has none of the faults these rewrites fixed.")


def digest(value: Any) -> str:
    text = json.dumps(value, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def pair_key(before: str, after: str) -> str:
    return judgments.key(before, after)


def context(s: Sentence) -> dict[str, str]:
    """What a question sees of one sentence. The paragraph replaced the
    neighboring sentences: chapter 30's "generated" fault, conditioned
    on a passage that does not name the mechanism, still matched five
    chapter 12 sentences whose neighbors did not say `@dataclass` and
    whose paragraphs did."""
    return {"section_heading": s.heading, "paragraph": s.paragraph,
            "sentence": s.text}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout


def open_pass() -> str:
    tags = git("tag", "-l", "edit-start-*").split()
    if len(tags) != 1:
        sys.exit("edit_patterns: name the edit with --since or --range; "
                 f"open edit-start tags: {' '.join(tags) or 'none'}")
    return tags[0]


def rewrites(since: str | None, span: str | None
             ) -> Iterator[tuple[str, Rewrite]]:
    """(chapter file, rewrite) for each sentence the edit rewrote.

    `--since REF` covers REF to the working tree, which is what an
    editing pass is: commits along the way and uncommitted edits alike.
    `--range A..B` covers two commits. Either way the edit is one diff,
    before against after, whoever made each change: a pass is judged by
    whether the chapter got better (Bruce, 2026-09-28), and until then
    commits with a Co-Authored-By trailer were skipped. An
    `edit-start-NN` tag narrows the diff to chapter NN.
    """
    if span:
        start, end = span.split("..")
        end = end or "HEAD"
    else:
        start, end = since or open_pass(), ""
    chapter = re.fullmatch(r"edit-start-(\w+)", start)
    paths = ([f"Chapters/{chapter[1]}_*.md"] if chapter else ["Chapters/"])
    names = git("diff", "--name-only", "--diff-filter=M", start,
                *([end] if end else []), "--", *paths).split()
    for path in names:
        after = (git("show", f"{end}:{path}") if end
                 else (ROOT / path).read_text(encoding="utf-8"))
        found, _ = sentence_diff.diff(
            git("show", f"{start}:{path}"), after, path)
        for r in found:
            yield path.split("/")[-1], r


@dataclass
class Recorded:
    """What `record_pass` did: the kept pairs' keys, the number of
    rewrites below the similarity floor, and the renames collapsed."""
    keys: list[str]
    dropped: int = 0
    renames: list[dict[str, Any]] = field(default_factory=list)
    floor: float = MIN_SIMILARITY

    def lines(self) -> list[str]:
        out = [f"{self.dropped} rewrites below the {self.floor:g} "
               "similarity floor dropped (section rewrites, not "
               "sentence edits)"]
        out += [f'rename: "{r["old"]}" -> "{r["new"]}" in '
                f'{r["count"]} sentences' for r in self.renames]
        return out


def tokens(text: str) -> list[str]:
    """Lowercase words with punctuation and code ticks off their edges."""
    words = (w.strip(TRIM).lower() for w in text.split())
    return [w for w in words if w]


def replacements(before: str, after: str
                 ) -> tuple[set[tuple[str, str]], bool]:
    """The word-for-word replacements between two sentences, and whether
    any other change (an insertion, a deletion, a reshaped phrase)
    remains."""
    a, b = tokens(before), tokens(after)
    found: set[tuple[str, str]] = set()
    other = False
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if op == "replace" and i2 - i1 == j2 - j1:
            found.update(zip(a[i1:i2], b[j1:j2]))
        else:
            other = True
    return found, other


def find_renames(rows: list[tuple[str, str]], minimum: int = RENAME_MIN
                 ) -> tuple[list[dict[str, Any]], set[int]]:
    """The renames among (before, after) rows, and the indexes of the
    rows whose only changes are renames."""
    changes = [replacements(b, a) for b, a in rows]
    counts: dict[tuple[str, str], int] = {}
    for found, _ in changes:
        for pair in found:
            counts[pair] = counts.get(pair, 0) + 1
    chosen = {pair for pair, n in counts.items() if n >= minimum}
    renames = [{"old": o, "new": n, "count": counts[(o, n)]}
               for o, n in sorted(chosen, key=lambda p: (-counts[p], p))]
    collapsed = {i for i, (found, other) in enumerate(changes)
                 if found and not other and found <= chosen}
    return renames, collapsed


def cut_or_added(r: Rewrite) -> bool:
    """A deletion or an addition: a pair with an empty side."""
    return (not r.before.text or not r.after
            or r.similarity < DELETED)


def record_pass(pairs: dict[str, dict[str, Any]], since: str | None,
                span: str | None, min_similarity: float = MIN_SIMILARITY
                ) -> Recorded:
    """Add the edit's rewrites to `pairs`, minus those below the
    similarity floor and those that only rename a word."""
    source = span or since or open_pass()
    today = datetime.date.today().isoformat()
    found = list(rewrites(since, span))
    kept = [(f, r) for f, r in found
            if r.similarity >= min_similarity or cut_or_added(r)]
    renames, collapsed = find_renames(
        [(r.before.text, "" if cut_or_added(r) else r.after)
         for _, r in kept])
    result = Recorded([], len(found) - len(kept), renames, min_similarity)
    survivors = {id(r) for i, (_, r) in enumerate(kept)
                 if i not in collapsed}
    stale = set()
    for f, r in found:
        after = r.after if r.similarity >= DELETED else ""
        k = pair_key(r.before.text, after)
        if id(r) not in survivors:
            stale.add(k)
            continue
        result.keys.append(k)
        entry = pairs.setdefault(k, {
            "file": f, "line": r.before.line,
            "before": r.before.text, "after": after,
            "previous": r.before.previous,
            "following": r.before.following,
            "similarity": r.similarity, "source": source,
            "added": today, "fault": "", "status": "new"})
        # Refreshed on every run, so a pair stored before these fields
        # existed gains them.
        entry["heading"] = r.before.heading
        entry["paragraph"] = r.before.paragraph
    # An earlier run may have stored a pair that the filters now drop.
    for k in stale - set(result.keys):
        old = pairs.get(k)
        if (old and old.get("source") == source and not old["fault"]
                and old["status"] == "new" and not old.get("local")):
            del pairs[k]
    return result


RULES_FILE = ROOT / "bruce_edit_db.md"
SIGHTING = re.compile(r'"([^"]{12,}?)"\s*->\s*"([^"]*?)"')


SIGHTINGS_TRIED = 8


def rule_pairs() -> Iterator[list[dict[str, Any]]]:
    """Each promoted rule in `bruce_edit_db.md`, as candidate pairs.

    A rule already states its fault: the title says what to do, the
    **Test.** line says where it applies, and **Keep when.** says where
    it does not. Every quoted sighting (the `SIGHTINGS_TRIED` longest)
    is a candidate example, and `best_example()` keeps one. Taking the
    longest sighting, as the first version did, gave R12 its
    counter-example: the one sighting where Bruce un-named a pointer,
    which its own fault line then could not see.
    """
    text = RULES_FILE.read_text(encoding="utf-8")
    promoted = text[text.index("\n## Rules"):text.index("\n## Candidates")]
    for block in re.split(r"\n### ", promoted)[1:]:
        head, _, body = block.partition("\n")
        rule, _, title = head.partition(". ")

        def field(name: str) -> str:
            m = re.search(rf"\*\*{name}\.\*\*(.*?)(?:\n\n|\Z)", body, re.S)
            return " ".join(m[1].split()) if m else ""

        sightings = sorted(set(SIGHTING.findall(" ".join(body.split()))),
                           key=lambda p: -len(p[0]))[:SIGHTINGS_TRIED]
        if not sightings:
            continue
        keep = field("Keep when")
        fault = f"{title}. {field('Test')}"
        if keep and not keep.lower().startswith("none"):
            fault += f" Not a fault when: {keep}"
        yield [{"file": RULES_FILE.name, "line": 0, "rule": rule,
                "before": before, "after": after, "previous": "",
                "following": "", "similarity": 0.0, "fault": fault}
               for before, after in sightings]


def best_example(cache: "Cache", candidates: list[dict[str, Any]]
                 ) -> dict[str, Any]:
    """The candidate whose own before shows the fault most and whose
    after shows it least, by the pair check's two scores."""
    confirm(cache, [(p, own(p, side)) for p in candidates
                    for side in ("before", "after") if p[side]])

    def margin(p: dict[str, Any]) -> float:
        after = (cache.get(confirm_key(p, own(p, "after")))
                 if p["after"] else 0.0)
        return cache.get(confirm_key(p, own(p, "before"))) - after

    return max(candidates, key=margin)


def book() -> list[tuple[str, Sentence]]:
    return [(p.name, s) for p in md_files([CHAPTERS_DIR])
            for s in sentence_diff.prose(p.read_text(encoding="utf-8"),
                                         p.name)]


def progress(done: int, total: int) -> None:
    print(f"\r  {done}/{total}", end="", file=sys.stderr, flush=True)
    if done == total:
        print(file=sys.stderr)


class Cache:
    """Answers keyed by what the question saw, saved as one JSON map."""

    def __init__(self) -> None:
        self.data: dict[str, Any] = (
            json.loads(CACHE.read_text(encoding="utf-8"))
            if CACHE.exists() else {})

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def put(self, key: str, value: Any) -> None:
        self.data[key] = value

    def save(self) -> None:
        CACHE.parent.mkdir(exist_ok=True)
        write_text_lf(CACHE, json.dumps(self.data) + "\n")


def confirm_key(pair: dict[str, Any], s: Sentence) -> str:
    return "confirm:" + judgments.key(
        digest(example(pair)), digest(context(s)), digest(CONFIRM))


def confirm(cache: Cache, jobs: list[tuple[dict[str, Any], Sentence]]
            ) -> None:
    """Ask each (pair, sentence) Noul not already cached."""
    todo = [(p, s) for p, s in jobs if cache.get(confirm_key(p, s)) is None]
    if not todo:
        return
    answers = judgments.ask(
        [({**context(s), "example": example(p)}, {"fits": CONFIRM})
         for p, s in todo], progress)
    for (p, s), a in zip(todo, answers):
        cache.put(confirm_key(p, s), a["fits"]["noul"])


def own(p: dict[str, Any], side: str) -> Sentence:
    """The pair's before or after, set in the before's paragraph."""
    paragraph = p.get("paragraph", "")
    if side == "after":
        paragraph = paragraph.replace(p["before"], p["after"])
    return Sentence(p["line"], p[side], p["previous"], p["following"],
                    p.get("heading", ""), paragraph)


def check_pairs(cache: Cache, pairs: dict[str, dict[str, Any]],
                keys: list[str]) -> None:
    """Step 1: does each pair's fault show in its before, not its after?"""
    described = [pairs[k] for k in keys if pairs[k].get("fault")]
    confirm(cache, [(p, own(p, side)) for p in described
                    for side in ("before", "after") if p[side]])
    for k in keys:
        p = pairs[k]
        if not p.get("fault"):
            p["status"] = "needs fault"
            p.pop("check", None)
            continue
        before = cache.get(confirm_key(p, own(p, "before")))
        after = (cache.get(confirm_key(p, own(p, "after")))
                 if p["after"] else 0.0)
        p["check"] = {"before": before, "after": after}
        p["status"] = ("searchable" if before >= REPORT and after < REPORT
                       else "unclear")


def screen(cache: Cache, pairs: dict[str, dict[str, Any]],
           keys: list[str], sentences: list[tuple[str, Sentence]]
           ) -> dict[str, list[tuple[str, Sentence]]]:
    """Step 2: the sentences that give each pair some probability."""
    chunks = [keys[i:i + CHUNK] for i in range(0, len(keys), CHUNK)]
    hits: dict[str, list[tuple[str, Sentence]]] = {k: [] for k in keys}
    for chunk in chunks:
        options = {f"r{i}": example(pairs[k]) for i, k in enumerate(chunk)}
        question = {"instructions": SCREEN_INSTRUCTIONS,
                    "criteria": {**options, "none": NONE}}
        tag = digest(question)

        def key(s: Sentence) -> str:
            return "screen:" + judgments.key(tag, digest(context(s)))

        todo = [s for _, s in sentences if cache.get(key(s)) is None]
        if todo:
            print(f"screening {len(todo)} sentences against "
                  f"{len(chunk)} rewrites", file=sys.stderr)
            answers = judgments.ask(
                [(context(s), {"screen": question}) for s in todo],
                progress)
            for s, a in zip(todo, answers):
                cache.put(key(s), a["screen"]["probabilities"])
            cache.save()
        for f, s in sentences:
            probs = cache.get(key(s))
            for i, k in enumerate(chunk):
                if probs.get(f"r{i}", 0.0) >= SCREEN:
                    hits[k].append((f, s))
    return hits


def report(pairs: dict[str, dict[str, Any]], keys: list[str],
           found: dict[str, list[tuple[str, Sentence, float]]]) -> str:
    lines = []
    for k in keys:
        p = pairs[k]
        where = (p["rule"] if p.get("rule")
                 else f"{p['file']}:{p['line']}")
        lines.append(f"## {where}")
        lines.append(f"- before: {p['before']}")
        lines.append(f"- after:  {p['after'] or '(deleted)'}")
        lines.append(f"- fault:  {p.get('fault') or '(none yet)'}")
        c = p.get("check")
        lines.append(f"- status: {p['status']}" + (
            f" (before {c['before']:.2f}, after {c['after']:.2f})"
            if c else ""))
        rows = sorted(found.get(k, []), key=lambda r: -r[2])
        if p["status"] != "searchable":
            lines.append("")
            continue
        lines.append(f"- {len(rows)} sentence(s) at or above {p.get('floor', REPORT)}")
        for f, s, v in rows[:SHOWN]:
            lines.append(f"  - {v:.2f} {CHAPTERS_DIR.name}/{f}:{s.line}: "
                         f"{s.text}")
        if len(rows) > SHOWN:
            lines.append(f"  - ... {len(rows) - SHOWN} more")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="compare REF with the working tree")
    ap.add_argument("--range", dest="span", help="compare A..B")
    ap.add_argument("--min-similarity", type=float, default=MIN_SIMILARITY,
                    help="drop rewrites scoring below this "
                         f"(default {MIN_SIMILARITY})")
    ap.add_argument("--dry-run", action="store_true",
                    help="list the edit's rewrites and the cost; ask nothing")
    ap.add_argument("--pair", action="append", default=[],
                    help="search for this stored pair (its key, or "
                         "FILE:LINE); repeatable")
    ap.add_argument("--from-rules", action="store_true",
                    help="search for every promoted rule in "
                         "bruce_edit_db.md")
    ap.add_argument("--report", action="store_true",
                    help="report every stored pair from the cache")
    args = ap.parse_args(argv)

    pairs: dict[str, dict[str, Any]] = judgments.load(PAIRS_FILE)
    cache = Cache()

    if args.report:
        keys = list(pairs)
    elif args.pair:
        keys = []
        for name in args.pair:
            file, _, line = name.rpartition(":")
            match = [k for k, v in pairs.items() if k == name
                     or (v["file"] == file and str(v["line"]) == line)]
            if not match:
                sys.exit(f"edit_patterns: no stored pair {name}")
            keys += match
    elif args.from_rules:
        today = datetime.date.today().isoformat()
        rules = list(rule_pairs())
        if args.dry_run:
            for candidates in rules:
                print(f"{candidates[0]['rule']}: {len(candidates)} "
                      f"sighting(s); {candidates[0]['fault'][:120]}")
            print(f"\n{len(rules)} rules, "
                  f"{sum(len(c) for c in rules) * 2} check questions")
            return 0
        keys = []
        for candidates in rules:
            rp = best_example(cache, candidates)
            k = judgments.key(rp["rule"], rp["before"], rp["after"])
            keys.append(k)
            carried = {}
            for old in [o for o, v in pairs.items()
                        if v.get("rule") == rp["rule"] and o != k]:
                # An example this run did not choose. A floor set from
                # Bruce's labels belongs to the rule, not the example.
                carried = {f: pairs[old][f] for f in ("floor", "floor_basis")
                           if f in pairs[old]}
                del pairs[old]
            entry = pairs.setdefault(k, {**rp, "source": rp["rule"],
                                         "added": today, "status": "new"})
            entry.update(carried)
            entry["fault"] = rp["fault"]  # the store is the authority
        cache.save()
    else:
        recorded = record_pass(pairs, args.since, args.span,
                               args.min_similarity)
        keys = recorded.keys
        if args.dry_run:
            # Recording the pairs asks nothing, and `/edit-done` step 3b
            # seeds its fault-line page from them.
            judgments.save(PAIRS_FILE, pairs)
            for k in keys:
                p = pairs[k]
                print(f"{p['file']}:{p['line']}  {p['similarity']:.2f}")
                print(f"  - {p['before']}")
                print(f"  + {p['after'] or '(deleted)'}")
            print()
            for line in recorded.lines():
                print(line)
            n = len(book())
            chunks = -(-len(keys) // CHUNK)
            print(f"\n{len(keys)} rewrites; screening costs about "
                  f"{n * chunks} questions ({n} sentences x {chunks} "
                  "chunk(s)), plus confirmations")
            return 0
        if not keys:
            print("No rewritten sentences in this edit.")
            return 0

    check_pairs(cache, pairs, keys)
    cache.save()
    judgments.save(PAIRS_FILE, pairs)
    searchable = [k for k in keys if pairs[k]["status"] == "searchable"]

    edited = {pairs[k][side] for k in pairs for side in ("before", "after")}
    sentences = [(f, s) for f, s in book() if s.text not in edited]
    found: dict[str, list[tuple[str, Sentence, float]]] = {}
    if searchable and not args.report:
        hits = screen(cache, pairs, searchable, sentences)
        confirm(cache, [(pairs[k], s)
                        for k in searchable for _, s in hits[k]])
        cache.save()
    for k in searchable:
        rows = []
        for f, s in sentences:
            v = cache.get(confirm_key(pairs[k], s))
            if v is not None and v >= pairs[k].get("floor", REPORT):
                rows.append((f, s, v))
        found[k] = rows

    text = report(pairs, keys, found)
    REPORT_FILE.parent.mkdir(exist_ok=True)
    write_text_lf(REPORT_FILE, text)
    print(text)
    needs = sum(pairs[k]["status"] == "needs fault" for k in keys)
    unclear = len(keys) - len(searchable) - needs
    print(f"{len(searchable)} rewrite(s) searched, {unclear} unclear, "
          f"{needs} need a fault line in {PAIRS_FILE.name}; "
          f"report in {REPORT_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
