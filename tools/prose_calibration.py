"""Do Bruce's own rewrites pick out sentences a model scores as unclear?

The prose passes (`/straighten`, `/antecedents`, the clarity agent)
look for sentences that hold a subject open too long, pointer words
with two candidates, and reasoning with a step left out. Before a model
score for any of those can steer a pass, it has to agree with the
author. The evidence is in git: every sentence Bruce rewrote in his own
edits is one he judged worth changing, and the sentences around it that
he read and left alone are ones he judged fine.

So this collects both groups from his editor commits, asks TypeSafe
about each sentence, and reports how well each answer separates the
groups, as an AUC: the chance a rewritten sentence outscores a
left-alone one, where 0.5 is no signal. Longer sentences get rewritten
more and also score higher on every one of these questions, so the
report also gives the AUC of length alone, and each question's AUC
within length bands, which is the part length cannot explain.

Four questions. Three are Scores for one named fault each. The fourth,
`would_rewrite`, is a Noul that asks the author's question directly and
shows six before/after pairs from `bruce_edit_db.md`'s promoted rules
(`EXAMPLES`). Examples drawn from the data would inflate its score on
that data, so the samples split by commit into two halves: the commits
the examples came from are forced into the first, any sample containing
an example's phrase is dropped from the second, and the report is
computed on the second half alone. `would_rewrite` is asked only there.

Which commits count: no Co-Authored-By trailer and a subject of the
form his editor writes ("Update 30_Patterns--Observer.md", "more ch
30"). The deep-review and bare-number commits are left out, since some
of them carry my edits from before the trailer convention. A rewritten
sentence is one in the parent's version of a chapter that no longer
appears, after collapsing whitespace, in the commit's version. Controls
come from the same commit and chapter, as many as it rewrote, drawn
from sentences unchanged there and never rewritten in any collected
commit. List items are left out: the sentence splitter joins a run of
bullets into one "sentence" until it meets terminal punctuation, and
the first run's highest subject-verb score was a joined list. So is
a sentence holding one of Bruce's `[[...]]` draft notes, which is
certain to change and says so in words a model can read.

Answers are cached per question in `build/prose_calibration.json`,
keyed by the sentence and its neighbors and stamped with the question's
wording, so a rerun asks only a new or reworded question. Nothing here
gates or edits a chapter.

    uv run --with typesafe-sdk python -m tools.prose_calibration
    uv run --with typesafe-sdk python -m tools.prose_calibration --dry-run
"""

import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from tools import judgments, sentence_diff
from tools.config import BUILD_DIR, ROOT

CACHE = BUILD_DIR / "prose_calibration.json"
SUBJECT = re.compile(r"^(Update \S+\.md|more ch\b.*)$")
RESTRUCTURED = 0.75
"""A rewrite whose before/after similarity is below this changed the
sentence's shape, not a word or two in it."""

# (rule, commit or "", before, after). One pair per rule, from six
# different rules, so the examples show kinds of rewrite rather than
# one habit six times. A commit named here goes into the example half.
EXAMPLES = [
    ("R4", "",
     "Python functions are first-class, so you can also pass the steps",
     "Because Python functions are first-class, you can also pass the "
     "steps"),
    ("R9", "144c546f",
     "The variations above are Java habits.",
     "All three approaches carry one Java habit: the adapter inherits "
     "from `WhatIWant` so that `op()` accepts it."),
    ("R10", "",
     "The registry also never forgets:",
     "The registry also never removes an entry:"),
    ("R12", "7ec15c2e",
     "Even without that ambiguity, the class solves a problem Python "
     "does not have.",
     "Even without that ambiguity, the builder class solves a problem "
     "Python does not have."),
    ("R15", "2b18eed8",
     "Thus you can isolate, in one place, the effect of changing from "
     "one GUI to another.",
     "The change from one GUI to another then touches one place in "
     "your code."),
    ("R21", "15f58a2d",
     "Subscriptions are strong references: an observable that outlives "
     "its observers keeps alive the instance",
     "Subscriptions are strong references. An observable that outlives "
     "its observers keeps alive the instance"),
]

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
    "would_rewrite": {
        "type": "noul",
        "instructions": {
            "task": (
                "The author of a Python programming book revises the "
                "draft sentence by sentence. Would this author rewrite "
                "`sentence` on the next revision? Use `previous_sentence` "
                "and `next_sentence` as context."),
            "what_this_author_rewrites": [
                {"before": before, "after": after}
                for _, _, before, after in EXAMPLES],
            "note": (
                "The examples show kinds of change, not a checklist: a "
                "buried or missing reason, a vague phrase where a "
                "concrete one exists, a figure standing in for a "
                "mechanism, a pointer with a competing antecedent, a "
                "reader-directed 'you can' where the mechanism could be "
                "the subject, a colon joining two sentences."),
        },
        "criteria": {
            "true": ("The author would change the sentence's wording or "
                     "structure, as in the examples."),
            "false": ("The author would leave the sentence as it is, or "
                      "change at most its punctuation."),
        },
    },
}
HELD_OUT_ONLY = {"would_rewrite"}


def wording(question: str) -> str:
    text = json.dumps(QUESTIONS[question], sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


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
        return judgments.key(self.previous, self.sentence, self.following)


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


def collect(seed: int) -> list[Sample]:
    rng = random.Random(seed)
    per_commit: list[tuple[list[Sample], list[Sample]]] = []
    for commit in commits():
        changed = git("show", "--format=", "--name-only", "--diff-filter=M",
                      commit, "--", "Chapters/").split()
        for path in changed:
            name = Path(path).name
            found, left = sentence_diff.diff(
                git("show", f"{commit}^:{path}"),
                git("show", f"{commit}:{path}"), path)
            rewrites = [Sample(True, commit, name, r.before.line,
                               r.before.previous, r.before.text,
                               r.before.following, r.after, r.similarity)
                        for r in found]
            alone = [Sample(False, commit, name, s.line, s.previous,
                            s.text, s.following, "", 1.0) for s in left]
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


def held_out(samples: list[Sample]) -> list[Sample]:
    """The half no example came from, minus any sample quoting one.

    Commits split by a hash of their id, so the split is stable across
    runs and unrelated to date or chapter; each example's commit is
    forced into the other half.
    """
    forced = {c for _, c, _, _ in EXAMPLES if c}
    phrases = [before[:40] for _, _, before, _ in EXAMPLES]

    def second_half(commit: str) -> bool:
        if any(commit.startswith(f) or f.startswith(commit)
               for f in forced):
            return False
        return hashlib.sha256(commit.encode()).digest()[0] % 2 == 1

    return [s for s in samples if second_half(s.commit)
            and not any(p in s.sentence for p in phrases)]


def auc(high: list[float], low: list[float]) -> float:
    """P(a score from `high` beats one from `low`), ties counting half."""
    if not high or not low:
        return float("nan")
    wins = sum((h > lo) + 0.5 * (h == lo) for h in high for lo in low)
    return wins / (len(high) * len(low))


def auc_se(a: float, n_high: int, n_low: int) -> float:
    """Hanley and McNeil's standard error for an AUC, the width to read
    a difference between two rows against."""
    q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    var = (a * (1 - a) + (n_high - 1) * (q1 - a * a)
           + (n_low - 1) * (q2 - a * a)) / (n_high * n_low)
    return var ** 0.5


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


def value(answer: dict[str, Any]) -> float:
    return answer["score"] if "score" in answer else answer["noul"]


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
    print(f"held-out half: {len(alone)} left alone; "
          + "; ".join(f"{len(v)} {k}" for k, v in groups.items()))

    measures: dict[str, Callable[[Sample], float]] = {
        "length (chars)": lambda s: float(len(s.sentence))}
    for q in QUESTIONS:
        measures[q] = (lambda q: lambda s:
                       value(cache[s.key]["answers"][q]))(q)

    for name, rewritten in groups.items():
        print(f"\n{name} vs left alone")
        print(f"  {'measure':24} {'AUC':>5} {'±se':>5} {'in bands':>9} "
              f"{'mean rewritten':>15} {'mean alone':>11}")
        for label, f in measures.items():
            rows = [(s, f(s)) for s in rewritten + alone]
            hi = [v for s, v in rows if s.rewritten]
            lo = [v for s, v in rows if not s.rewritten]
            banded = ("" if label.startswith("length")
                      else f"{banded_auc(rows):.2f}")
            a = auc(hi, lo)
            se = auc_se(a, len(hi), len(lo))
            print(f"  {label:24} {a:5.2f} {se:5.2f} {banded:>9} "
                  f"{mean(hi):15.2f} {mean(lo):11.2f}")

    print("\nHighest-scoring rewrites per question (before -> after):")
    for q in QUESTIONS:
        top = sorted((s for s in samples if s.rewritten),
                     key=lambda s: -value(cache[s.key]["answers"][q]))[:3]
        print(f"\n  {q}")
        for s in top:
            score = value(cache[s.key]["answers"][q])
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

    samples = held_out(collect(args.seed))
    cache = judgments.load(CACHE)

    def missing(s: Sample) -> dict[str, dict[str, Any]]:
        stamped = cache.get(s.key, {}).get("wording", {})
        return {q: spec for q, spec in QUESTIONS.items()
                if stamped.get(q) != wording(q)}

    todo = [(s, m) for s in samples if (m := missing(s))]
    if args.dry_run:
        rewritten = sum(s.rewritten for s in samples)
        asks = sum(len(m) for _, m in todo)
        print(f"{len(commits())} commits; held-out half: {rewritten} "
              f"rewritten, {len(samples) - rewritten} left alone; "
              f"{asks} questions to ask")
        return 0
    if todo:
        answers = judgments.ask(
            [({"previous_sentence": s.previous, "sentence": s.sentence,
               "next_sentence": s.following}, m) for s, m in todo],
            progress)
        for (s, m), a in zip(todo, answers):
            entry = cache.setdefault(s.key, {
                "file": s.file, "line": s.line, "sentence": s.sentence,
                "answers": {}, "wording": {}})
            entry["answers"].update(a)
            entry["wording"].update({q: wording(q) for q in m})
        CACHE.parent.mkdir(exist_ok=True)
        judgments.save(CACHE, cache)
    report(samples, cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
