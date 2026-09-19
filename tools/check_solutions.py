#!/usr/bin/env python3
"""Check that Solutions/NN_*.md answers the exercises Chapters/NN_*.md asks.

`heading_links.py` gates anchors and `extract_solutions.py` gates the code,
but the correspondence between a chapter's "## Exercises" list and its
solution headings is pure prose on both sides, so nothing watched it.
Editing an exercise, deleting one, or adding one at the end left the
solutions silently answering a different question, which is worse for a
reader than no answer at all.

This compares the two numberings:

- A chapter's exercises are the top-level ordered-list items under its
  final `## Exercises` heading. A chapter whose Exercises section holds
  only prose (chapter 1 describes the convention rather than setting any)
  has no exercises and needs no Solutions file.
- A solution's answers are the `## N. ...` headings in the Solutions
  file. One heading can answer several exercises at once, written
  `## 1 & 2. ...`, `## 1, 2. ...`, or `## 1-3. ...`, which is the right
  form when two exercises share one worked answer.

Reported: a chapter with exercises and no Solutions file, an exercise with
no solution, a solution with no exercise, and either list numbered other
than 1..N in order. What it cannot see is a solution that answers the
wrong exercise under the right number; that still needs a human reading
the two side by side.

A listing's name carries the number too. Under `## 3. ...` a listing
named `exercise_N.py` (or `exercise_Nb.py`, `exercise_N_frozen.py`) must
have N == 3, or one of the numbers a combined heading names. Reordering
a chapter's exercises renumbers the headings, and the names stay behind
with nothing else reading them: chapter 30 kept `exercise_3.py` under
`## 2.` that way, so `SolutionsCode/.../exercise_2.py` held the answer
to exercise 4. A listing with any other name (a test file, a helper) is
exempt.

It also checks how a solution *cites* its chapter. `Solutions/` sits
beside `Chapters/`, so a link written the way a chapter writes it,
`](24_Patterns--Singleton.md#...)`, resolves to `Solutions/24_Patterns--Singleton.md`, a real
file with the wrong content. The correct form is `../Chapters/24_Patterns--Singleton.md`.
Seventeen links were wrong this way before anything looked. Write `./` on
the front for a deliberate link to a neighboring solution.

Usage:
    python -m tools.check_solutions           # every chapter
    python -m tools.check_solutions 19 45     # only these chapters
"""

import argparse
import re
from collections.abc import Iterator
from pathlib import Path

from tools.config import ROOT
from tools.markdown import Document
from tools.report import Finding, report

CHAPTERS_DIR = ROOT / "Chapters"
SOLUTIONS_DIR = ROOT / "Solutions"

# The heading that opens a chapter's exercise list.
EXERCISES_HEADING = re.compile(r"^#{1,6}\s+Exercises\s*$")

# Any ATX heading, used to find where the exercise section ends.
HEADING = re.compile(r"^#{1,6}\s+")

# A top-level ordered-list item: "1.  Rewrite ...". Indented continuation
# lines and nested lists are not items, so the leading column matters.
ITEM = re.compile(r"^(\d+)\.\s+\S")

# A solution heading's number, or the several it answers together:
# "## 3. A pool of connections", "## 1 & 2. A Triangle in both styles".
ANSWER = re.compile(r"^([\d\s&,-]+?)\.\s+\S")

# How the numbers in a combined heading are separated.
JOINERS = re.compile(r"[&,]")

# A listing named for its exercise: "exercise_3.py", "exercise_3b.py",
# "exercise_3_frozen.py". Matched against the slug's last path part.
EXERCISE_LISTING = re.compile(r"^exercise_(\d+)")

# A Markdown link to a numbered book file with no directory in front of
# it, so it resolves beside the linking file: "](24_Patterns--Singleton.md#state)".
# A leading "./" or "../" fails the match, which is the opt-out.
# The `-` in the class is for the `--` that sets a chapter's part name
# off from its title (`26_Patterns--Surrogate.md`); without it this check
# silently stops matching every chapter and reports nothing.
BARE_CHAPTER_LINK = re.compile(r"\]\((\d{2}_[A-Za-z_-]+\.md)([^)]*)\)")


def exercise_numbers(doc: Document) -> list[tuple[int, int]]:
    """(number, line) for each exercise under the last Exercises heading.

    The last one, because a chapter can mention the word in passing
    earlier; the exercises always close the file.
    """
    fenced = doc.in_fence()
    found: list[tuple[int, int]] = []
    inside = False
    for index, line in enumerate(doc.lines):
        if fenced[index]:
            continue
        if EXERCISES_HEADING.match(line):
            inside, found = True, []
            continue
        if inside and HEADING.match(line):
            inside = False
        if inside:
            m = ITEM.match(line)
            if m:
                found.append((int(m.group(1)), index + 1))
    return found


def expand(prefix: str) -> list[int]:
    """The exercise numbers a heading's `1 & 2` or `1-3` prefix names."""
    numbers: list[int] = []
    for part in JOINERS.split(prefix):
        low, dash, high = part.strip().partition("-")
        if dash:
            numbers.extend(range(int(low), int(high) + 1))
        elif low:
            numbers.append(int(low))
    return numbers


def answer_numbers(doc: Document) -> list[tuple[int, int]]:
    """(number, line) for each exercise the Solutions file answers.

    A combined `## 1 & 2.` heading contributes both numbers at its own
    line, so the caller sees the same flat sequence either way.
    """
    found: list[tuple[int, int]] = []
    for lineno, text in doc.headings():
        m = ANSWER.match(text)
        if m:
            found.extend((n, lineno) for n in expand(m.group(1)))
    return found


def misnamed_listings(doc: Document) -> Iterator[Finding]:
    """Findings for an `exercise_N.py` under a heading numbered otherwise.

    A listing above the first numbered heading has no number to match and
    draws nothing.
    """
    sections: list[tuple[int, list[int], str]] = []
    for lineno, text in doc.headings():
        m = ANSWER.match(text)
        if m:
            sections.append((lineno, expand(m.group(1)), m.group(1)))
    for block in doc.python_blocks():
        slug = block.slug
        m = EXERCISE_LISTING.match(Path(slug).name) if slug else None
        above = [s for s in sections if s[0] <= block.open_at]
        if not m or not above:
            continue
        _, numbers, prefix = above[-1]
        if int(m.group(1)) not in numbers:
            yield Finding(
                doc.path, block.start + 1,
                f"{slug} sits under heading {prefix.strip()}; name it "
                f"for the exercise it answers",
            )


def out_of_order(
    numbered: list[tuple[int, int]], path: Path, what: str,
) -> Iterator[Finding]:
    """Findings for a list numbered anything other than 1..N in order."""
    for position, (number, line) in enumerate(numbered, start=1):
        if number != position:
            yield Finding(
                path, line,
                f"{what} numbered {number} where {position} was expected",
            )


def chapter_citations(solutions: Path) -> Iterator[Finding]:
    """Findings for a chapter link that resolves inside Solutions/."""
    for lineno, line in Document.parse(solutions).outside_fences():
        for m in BARE_CHAPTER_LINK.finditer(line):
            yield Finding(
                solutions, lineno,
                f"link to {m.group(1)} resolves to Solutions/, not the "
                f"chapter; write ../Chapters/{m.group(1)}",
            )


def compare(chapter: Path) -> Iterator[Finding]:
    """Findings for one chapter against its Solutions file."""
    exercises = exercise_numbers(Document.parse(chapter))
    solutions = SOLUTIONS_DIR / chapter.name
    if solutions.exists():
        yield from chapter_citations(solutions)
    if not exercises:
        return
    if not solutions.exists():
        yield Finding(
            chapter, exercises[0][1],
            f"{len(exercises)} exercise(s) but no Solutions/{chapter.name}",
        )
        return

    solutions_doc = Document.parse(solutions)
    answers = answer_numbers(solutions_doc)
    yield from out_of_order(exercises, chapter, "exercise")
    yield from out_of_order(answers, solutions, "solution")
    yield from misnamed_listings(solutions_doc)

    answered = {n for n, _ in answers}
    for number, line in exercises:
        if number not in answered:
            yield Finding(
                chapter, line,
                f"exercise {number} has no solution in "
                f"Solutions/{chapter.name}",
            )
    asked = {n for n, _ in exercises}
    for number, line in answers:
        if number not in asked:
            yield Finding(
                solutions, line,
                f"solution {number} answers no exercise in "
                f"Chapters/{chapter.name}",
            )


def selected(numbers: list[str]) -> list[Path]:
    """The chapters to check: all of them, or the ones named by number."""
    chapters = sorted(CHAPTERS_DIR.glob("*.md"))
    if not numbers:
        return chapters
    wanted = {n.zfill(2) for n in numbers}
    return [p for p in chapters if p.stem.partition("_")[0] in wanted]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "chapters", nargs="*",
        help="chapter numbers to check (default: all)")
    args = ap.parse_args(argv)

    findings = (f for c in selected(args.chapters) for f in compare(c))
    return report(
        findings,
        clean="Exercises and solutions line up.",
        problem="{n} problem(s) in Solutions/. Write the missing "
                "solution, renumber so each `## N.` heading matches its "
                "exercise, rename the listing to match its heading, or "
                "fix the chapter link.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
