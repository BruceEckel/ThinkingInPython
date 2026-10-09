#!/usr/bin/env python3
"""Check that Solutions/NN_*/README.md answers what Chapters/NN_*.md asks.

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
no solution, a solution with no exercise, either list numbered other
than 1..N in order, and a chapter whose Exercises section lacks a link
to its Solutions folder. What it cannot see is a solution that answers the
wrong exercise under the right number; that still needs a human reading
the two side by side.

A listing's name carries the number too. Under `## 3. ...` a listing
named `exercise_N.py` (or `exercise_Nb.py`, `exercise_N_frozen.py`) must
have N == 3, or one of the numbers a combined heading names. Reordering
a chapter's exercises renumbers the headings, and the names stay behind
with nothing else reading them: chapter 30 kept `exercise_3.py` under
`## 2.` that way, so `Solutions/.../exercise_2.py` held the answer
to exercise 4. A listing with any other name (a test file, a helper) is
exempt.

It also checks how a solution *cites* its chapter. A solutions file sits
two directories below the book root (`Solutions/<chapter>/README.md`), so
a link written the way a chapter writes it, `](24_Patterns--Singleton.md#...)`,
resolves inside the chapter's solutions folder, and the one-level form
`](../Chapters/24_Patterns--Singleton.md)` resolves inside `Solutions/`;
both miss. The correct form is `../../Chapters/24_Patterns--Singleton.md`.
Seventeen links were wrong this way before anything looked, and
`heading_links.py` checks only links that carry an `#anchor`. Write `./`
on the front for a deliberate link to a neighboring file.

Each chapter with exercises also links its Solutions folder from the
Exercises section, so a reader browsing `Chapters/` on GitHub can click
through. Between the last `## Exercises` heading and the first exercise
there must be a link of the form `](../Solutions/<chapter stem>/)`; the
file form `](../Solutions/<chapter stem>/README.md)`, with an optional
`#anchor`, is accepted too. A missing link is reported, and so is a
link to another target, which a chapter rename (or the old flat
`../Solutions/<stem>.md` layout) leaves behind. The check holds the
link target only; the sentence around it is the author's to reword.
`--write` inserts the default sentence where the link is missing and
corrects a stale target to the folder form, keeping the author's
wording.

Usage:
    python -m tools.check_solutions           # every chapter
    python -m tools.check_solutions 19 45     # only these chapters
    python -m tools.check_solutions --write   # insert or fix the links
"""

import argparse
import re
from collections.abc import Iterator
from pathlib import Path

from tools.config import CHAPTERS_DIR, SOLUTIONS_DIR, SOLUTIONS_MD
from tools.markdown import Document
from tools.repo import chapter_stem, solutions_file
from tools.report import Finding, report

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

# A link to a chapter one level up, which from `Solutions/<chapter>/` is
# a path inside Solutions/: "](../Chapters/24_Patterns--Singleton.md)".
# Group 1 is the rest of the target. `](../../Chapters/` does not match.
SHALLOW_CHAPTER_LINK = re.compile(r"\]\(\.\./Chapters/([^)\s]*)")

# A link from a chapter into Solutions/, with an optional anchor:
# "](../Solutions/02_Foundations--Tour/)". Group 1 is the target below
# Solutions/ (a folder with its slash, a file, or a stale flat name).
SOLUTIONS_LINK = re.compile(r"\]\(\.\./Solutions/([^)\s#]*)(#[^)\s]*)?\)")


def solutions_targets(stem: str) -> tuple[str, str]:
    """The link targets, below Solutions/, that count as correct."""
    return f"{stem}/", f"{stem}/{SOLUTIONS_MD}"


def solutions_sentence(stem: str) -> str:
    """The default sentence that links a chapter to its Solutions folder."""
    return (f"The [solutions](../Solutions/{stem}/) "
            f"are in the book's repository.")


def intro_span(doc: Document) -> tuple[int, int] | None:
    """(heading, first item) as 0-based line indexes, or None.

    The heading is the last `## Exercises` outside a fence, and the item
    is the first top-level numbered item after it. A chapter with no
    items has no span.
    """
    exercises = exercise_numbers(doc)
    if not exercises:
        return None
    fenced = doc.in_fence()
    heading = max(
        i for i, line in enumerate(doc.lines)
        if not fenced[i] and EXERCISES_HEADING.match(line))
    return heading, exercises[0][1] - 1


def span_links(doc: Document, span: tuple[int, int]) -> Iterator[tuple[int, str]]:
    """(0-based line, target below Solutions/) for each link in the span."""
    fenced = doc.in_fence()
    for i in range(span[0] + 1, span[1]):
        if fenced[i]:
            continue
        for m in SOLUTIONS_LINK.finditer(doc.lines[i]):
            yield i, m.group(1)


def solutions_links(chapter: Path, doc: Document) -> Iterator[Finding]:
    """Findings for a missing or stale link under the Exercises heading."""
    span = intro_span(doc)
    if span is None:
        return
    links = list(span_links(doc, span))
    stem = chapter_stem(chapter)
    if any(target in solutions_targets(stem) for _, target in links):
        return
    fix = "run `tip fix-solutions-links`"
    if not links:
        yield Finding(
            chapter, span[0] + 1,
            f"no link to Solutions/{stem}/ under the Exercises "
            f"heading; {fix}")
    for i, target in links:
        yield Finding(
            chapter, i + 1,
            f"link names Solutions/{target}, but this chapter is "
            f"{stem}; {fix}")


def with_solutions_link(text: str, name: str) -> str:
    """`text` with its Solutions link inserted, or its target corrected.

    `name` is the chapter's stem or filename. A link that names another
    target keeps its wording and anchor and changes only the target, to
    the folder form. With no link, the default sentence goes in as
    its own paragraph just before the first exercise. Line endings and
    every other line stay as they are.
    """
    stem = chapter_stem(name)
    doc = Document.from_text(text)
    span = intro_span(doc)
    if span is None:
        return text
    links = list(span_links(doc, span))
    if any(t in solutions_targets(stem) for _, t in links):
        return text
    lines = list(doc.lines)
    if links:
        for i, _ in links:
            lines[i] = SOLUTIONS_LINK.sub(
                lambda m: f"](../Solutions/{stem}/{m.group(2) or ''})",
                lines[i])
        return doc.rendered(lines)
    cr = "\r" if lines[span[0]].endswith("\r") else ""
    at = span[1]
    new = [solutions_sentence(stem) + cr, cr]
    if lines[at - 1].strip():
        new.insert(0, cr)
    lines[at:at] = new
    return doc.rendered(lines)


def write_links(chapters: list[Path]) -> list[Path]:
    """Insert or correct the link in each chapter that needs it.

    Returns the chapters changed. A chapter with no exercises or no
    Solutions file is left alone.
    """
    changed: list[Path] = []
    for chapter in chapters:
        if not solutions_file(chapter, SOLUTIONS_DIR).exists():
            continue
        old = chapter.read_bytes().decode("utf-8")
        new = with_solutions_link(old, chapter.name)
        if new != old:
            chapter.write_bytes(new.encode("utf-8"))
            changed.append(chapter)
    return changed


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
                f"link to {m.group(1)} resolves inside the solutions "
                f"folder, not the chapter; write "
                f"../../Chapters/{m.group(1)}",
            )
        for m in SHALLOW_CHAPTER_LINK.finditer(line):
            yield Finding(
                solutions, lineno,
                f"link to ../Chapters/{m.group(1)} resolves inside "
                f"Solutions/, not the chapter; write "
                f"../../Chapters/{m.group(1)}",
            )


def compare(chapter: Path) -> Iterator[Finding]:
    """Findings for one chapter against its Solutions file."""
    exercises = exercise_numbers(Document.parse(chapter))
    solutions = solutions_file(chapter, SOLUTIONS_DIR)
    where = f"Solutions/{chapter_stem(chapter)}/{SOLUTIONS_MD}"
    if solutions.exists():
        yield from chapter_citations(solutions)
    if not exercises:
        return
    if not solutions.exists():
        yield Finding(
            chapter, exercises[0][1],
            f"{len(exercises)} exercise(s) but no {where}",
        )
        return

    yield from solutions_links(chapter, Document.parse(chapter))
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
                f"exercise {number} has no solution in {where}",
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
    ap.add_argument(
        "--write", action="store_true",
        help="insert the Solutions link where missing and correct a "
             "stale target, then exit")
    args = ap.parse_args(argv)

    if args.write:
        changed = write_links(selected(args.chapters))
        for path in changed:
            print(f"fixed {path.name}")
        print(f"{len(changed)} chapter(s) changed.")
        return 0

    findings = (f for c in selected(args.chapters) for f in compare(c))
    return report(
        findings,
        clean="Exercises and solutions line up.",
        problem="{n} problem(s) in Solutions/. Write the missing "
                "solution, renumber so each `## N.` heading matches its "
                "exercise, rename the listing to match its heading, or "
                "fix the chapter link, or run `tip fix-solutions-links` "
                "when the Exercises section's Solutions link is missing "
                "or stale.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
