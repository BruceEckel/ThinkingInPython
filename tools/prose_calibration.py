"""Do Bruce's own rewrites pick out sentences a model scores as unclear?

The prose passes (`/straighten`, `/antecedents`, the clarity agent)
look for sentences that hold a subject open too long, pointer words
with two candidates, and reasoning with a step left out. Before a model
score for any of those can steer a pass, it has to agree with the
author. The evidence is in git: every sentence Bruce rewrote in his own
edits is one he judged worth changing, and the sentences around it that
he read and left alone are ones he judged fine.

So this collects both groups from his editor commits, asks TypeSafe
three Score questions about each sentence, and reports how well each
score separates the groups, as an AUC: the chance a rewritten sentence
outscores a left-alone one, where 0.5 is no signal. Longer sentences
get rewritten more and also score higher on every one of these
questions, so the report also gives the AUC of length alone, and each
question's AUC within length bands, which is the part length cannot
explain.

Which commits count: no Co-Authored-By trailer and a subject of the
form his editor writes ("Update 30_Patterns--Observer.md", "more ch
30"). The deep-review and bare-number commits are left out, since some
of them carry my edits from before the trailer convention. A rewritten
sentence is one in the parent's version of a chapter that no longer
appears, after collapsing whitespace, in the commit's version. Controls
come from the same commit and chapter, as many as it rewrote, drawn
from sentences unchanged there and never rewritten in any collected
commit.

Answers are cached in `build/prose_calibration.json`, keyed by the
sentence, its neighbors, and the questions' wording, so a rerun asks
only what changed. Nothing here gates or edits a chapter.

    uv run --with typesafe-sdk python -m tools.prose_calibration
    uv run --with typesafe-sdk python -m tools.prose_calibration --dry-run
"""

import argparse
import difflib
import json
import random
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from tools import judgments
from tools.check_self_reference import sentences
from tools.config import BUILD_DIR, ROOT
from tools.markdown import Document

CACHE = BUILD_DIR / "prose_calibration.json"
SUBJECT = re.compile(r"^(Update \S+\.md|more ch\b.*)$")
MIN_CHARS = 40
RESTRUCTURED = 0.75
"""A rewrite whose before/after similarity is below this changed the
sentence's shape, not a word or two in it."""

QUESTIONS: dict[str, dict[str, Any]] = {
    "subject_verb_distance": {
        "type": "score",
        "instructions": (
            "In `sentence`, find the main clause's subject and its verb. "
            "How much does the reader have to hold in mind between "
            "reading the subject and reaching the verb?"),
        "criteria": [
            "The subject and its verb are next to each other or a few "
            "words apart.",
            "A short phrase of up to about eight words separates the "
            "subject from its verb.",
            "A long phrase, a parenthetical, or a relative clause "
            "separates the subject from its verb.",
            "The verb arrives only after stacked modifiers or several "
            "clauses, so the reader holds the subject open for most of "
            "the sentence.",
        ],
    },
    "ambiguous_pointers": {
        "type": "score",
        "instructions": (
            "Consider every pointer word in `sentence`: this, that, "
            "these, those, it, its, they, them, which, the former, the "
            "latter, above, below. Using `previous_sentence` as context, "
            "how clearly does each one name what it points at?"),
        "criteria": [
            "The sentence has no pointer words, or each one is followed "
            "by the noun it stands for.",
            "Each pointer word has one antecedent, clear from the "
            "sentence or the one before it.",
            "At least one pointer word has two plausible antecedents, "
            "and the reader must stop to choose.",
            "A pointer word stands for a whole previous idea or has no "
            "antecedent the reader can identify.",
        ],
    },
    "skipped_steps": {
        "type": "score",
        "instructions": (
            "Using `previous_sentence` and `next_sentence` as context, "
            "does `sentence` leave out a step of reasoning its reader "
            "needs in order to follow it?"),
        "criteria": [
            "The sentence states a fact or an instruction, or every step "
            "of its reasoning is on the page.",
            "The sentence relies on a small inference that a reader "
            "makes without noticing.",
            "The sentence reaches a conclusion that depends on an "
            "unstated step a careful reader must reconstruct.",
            "The sentence asserts a consequence or a reason that the "
            "reader cannot recover from the surrounding text.",
        ],
    },
}
QUESTIONS_KEY = json.dumps(QUESTIONS, sort_keys=True)


@dataclass(frozen=True)
class Sample:
    rewritten: bool
    commit: str
    file: str
    line: int
    previous: str
    sentence: str
    following: str
    after: str
    """The closest sentence in the commit's version, for a rewrite."""
    similarity: float

    @property
    def key(self) -> str:
        return judgments.key(self.previous, self.sentence, self.following,
                             QUESTIONS_KEY)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout


def commits() -> list[str]:
    log = git("log", "--no-merges", "--format=%h%x09%s%x09"
              "%(trailers:key=Co-Authored-By,valueonly,separator=;)",
              "--", "Chapters/")
    return [h for h, subject, trailer in
            (line.split("\t") for line in log.splitlines())
            if not trailer and SUBJECT.match(subject)]


def prose(text: str, name: str) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path(name))
    return [(line, " ".join(s.split())) for line, s in sentences(doc)
            if len(s) >= MIN_CHARS and not s.lstrip().startswith("|")]


def collect(seed: int) -> list[Sample]:
    rng = random.Random(seed)
    per_commit: list[tuple[list[Sample], list[Sample]]] = []
    for commit in commits():
        changed = git("show", "--format=", "--name-only", "--diff-filter=M",
                      commit, "--", "Chapters/").split()
        for path in changed:
            before = prose(git("show", f"{commit}^:{path}"), path)
            after = prose(git("show", f"{commit}:{path}"), path)
            kept = {s for _, s in after}
            added = [s for s in kept if s not in {b for _, b in before}]
            rewrites, alone = [], []
            for i, (line, s) in enumerate(before):
                prev = before[i - 1][1] if i else ""
                nxt = before[i + 1][1] if i + 1 < len(before) else ""
                if s in kept:
                    alone.append(Sample(False, commit, Path(path).name,
                                        line, prev, s, nxt, "", 1.0))
                    continue
                best, ratio = "", 0.0
                for a in added:
                    r = difflib.SequenceMatcher(None, s, a).ratio()
                    if r > ratio:
                        best, ratio = a, r
                rewrites.append(Sample(True, commit, Path(path).name, line,
                                       prev, s, nxt, best, round(ratio, 3)))
            if rewrites:
                per_commit.append((rewrites, alone))
    ever_rewritten = {s.sentence for r, _ in per_commit for s in r}
    out: dict[str, Sample] = {}
    for rewrites, alone in per_commit:
        for s in rewrites:
            out.setdefault(s.sentence, s)
        pool = [s for s in alone if s.sentence not in ever_rewritten
                and s.sentence not in out]
        for s in rng.sample(pool, min(len(rewrites), len(pool))):
            out.setdefault(s.sentence, s)
    return list(out.values())


def auc(high: list[float], low: list[float]) -> float:
    """P(a score from `high` beats one from `low`), ties counting half."""
    if not high or not low:
        return float("nan")
    wins = sum((h > lo) + 0.5 * (h == lo) for h in high for lo in low)
    return wins / (len(high) * len(low))


def banded_auc(rows: list[tuple[Sample, float]], bands: int = 3) -> float:
    """Mean AUC within length bands, weighted by pairs per band."""
    lengths = sorted(len(s.sentence) for s, _ in rows)
    cuts = [lengths[len(lengths) * k // bands] for k in range(1, bands)]

    def band(s: Sample) -> int:
        return sum(len(s.sentence) >= c for c in cuts)

    total = weight = 0.0
    for b in range(bands):
        hi = [v for s, v in rows if band(s) == b and s.rewritten]
        lo = [v for s, v in rows if band(s) == b and not s.rewritten]
        if hi and lo:
            total += auc(hi, lo) * len(hi) * len(lo)
            weight += len(hi) * len(lo)
    return total / weight if weight else float("nan")


def progress(done: int, total: int) -> None:
    print(f"\r  {done}/{total}", end="", file=sys.stderr, flush=True)
    if done == total:
        print(file=sys.stderr)


def report(samples: list[Sample], cache: dict[str, dict[str, Any]]) -> None:
    groups = {
        "all rewrites": [s for s in samples if s.rewritten],
        f"restructured (similarity < {RESTRUCTURED})":
            [s for s in samples if s.rewritten
             and s.similarity < RESTRUCTURED],
    }
    alone = [s for s in samples if not s.rewritten]
    print(f"{len(alone)} left alone; "
          + "; ".join(f"{len(v)} {k}" for k, v in groups.items()))

    measures: dict[str, Any] = {
        "length (chars)": lambda s: float(len(s.sentence))}
    for q in QUESTIONS:
        measures[q] = (lambda q: lambda s:
                       cache[s.key]["answers"][q]["score"])(q)

    for name, rewritten in groups.items():
        print(f"\n{name} vs left alone")
        print(f"  {'measure':24} {'AUC':>5} {'in bands':>9} "
              f"{'mean rewritten':>15} {'mean alone':>11}")
        for label, f in measures.items():
            rows = [(s, f(s)) for s in rewritten + alone]
            hi = [v for s, v in rows if s.rewritten]
            lo = [v for s, v in rows if not s.rewritten]
            banded = ("" if label.startswith("length")
                      else f"{banded_auc(rows):.2f}")
            print(f"  {label:24} {auc(hi, lo):5.2f} {banded:>9} "
                  f"{mean(hi):15.2f} {mean(lo):11.2f}")

    print("\nHighest-scoring rewrites per question (before -> after):")
    for q in QUESTIONS:
        top = sorted((s for s in samples if s.rewritten),
                     key=lambda s: -cache[s.key]["answers"][q]["score"])[:3]
        print(f"\n  {q}")
        for s in top:
            score = cache[s.key]["answers"][q]["score"]
            print(f"    {score:.2f} {s.file[:2]}:{s.line} {s.commit}")
            print(f"      - {s.sentence[:160]}")
            print(f"      + {s.after[:160] or '(deleted)'}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="count the samples and what would be asked")
    ap.add_argument("--seed", type=int, default=30,
                    help="seed for choosing the left-alone sentences")
    args = ap.parse_args(argv)

    samples = collect(args.seed)
    cache = judgments.load(CACHE)
    new = [s for s in samples if s.key not in cache]
    if args.dry_run:
        rewritten = sum(s.rewritten for s in samples)
        print(f"{len(commits())} commits, {rewritten} rewritten, "
              f"{len(samples) - rewritten} left alone, {len(new)} to ask")
        return 0
    if new:
        answers = judgments.ask(
            [({"previous_sentence": s.previous, "sentence": s.sentence,
               "next_sentence": s.following}, QUESTIONS) for s in new],
            progress)
        for s, a in zip(new, answers):
            cache[s.key] = {"file": s.file, "line": s.line,
                            "sentence": s.sentence, "answers": a}
        CACHE.parent.mkdir(exist_ok=True)
        judgments.save(CACHE, cache)
    report(samples, cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
