#!/usr/bin/env python3
"""Check prose references to numbered exercises against a baseline.

The book refers to its exercises by number: "Exercise 8 works out
which sizes reach which colors", "the reason exercise 3 gives",
"exercise 4 of [Generators](...)". Nothing reads those numbers.
`check_solutions.py` gates that a chapter's exercise list and its
Solutions headings agree with each other, so after an exercise is
inserted the two lists still match and every gate is green, while
each sentence that names a later exercise now names the wrong one.
Chapter 30 collected five such references on 2026-09-19, when commit
a2cc5a98 inserted the pull-model exercise at 2.

Whether a sentence describes its exercise is a judgment. What broke
is mechanical: the title under a referenced number changed. So this
check pairs every reference with the Solutions heading for that
number, `## N. <title>`, in the chapter the reference targets, and
keeps the pairs a human has read in
`tools/data/exercise_refs_baseline.txt`, in the style of
`check_quoted_diagnostics.py`. The default run prints the delta:

    NEW   a pair the baseline lacks: a reference whose exercise has
          a different title now (an insertion, a reorder, a retitle),
          or a reference written since the last accept.
    GONE  a baseline pair that no longer occurs. Never gates.

Exit status is nonzero when NEW is non-empty. Each NEW line is a
sentence to reread against the exercise under that title; fix the
number, or accept the pair with `--accept`. Inserting an exercise
changes the title under every later number, so every reference to a
later exercise fires at once.

An entry is four tab-separated fields: the referring file as
`Tree/Chapter_Name`, the target `Chapter_Name`, the number, and the
title. A chapter name is the file stem after its `NN_Part--` prefix,
so renumbering a chapter or renaming a part leaves the baseline
alone; renaming a chapter does not. Markdown line numbers are left
out so prose edits above a reference do not churn the file.

What counts as a reference, outside fenced blocks and headings:

- "exercise 3", "Exercises 3 and 4", "exercises 3, 4, and 5"
- "the second exercise" (first through tenth; "the second exercises
  `NotInteresting`" is the verb and does not match)
- "the previous exercise" and "the next exercise", resolved from
  the exercise item (Chapters) or the `## N.` section (Solutions)
  the sentence sits in

The target is the file's own chapter unless the reference is tied
to a link: "exercise 4 of [Generators](45_...md)" (also "in" and
"from"), "[Generators](45_...md)'s exercise 4", or "its exercise 9"
and "that chapter's exercise 9" after a chapter link earlier in the
paragraph. A chapter link that merely shares the sentence does not
redirect the reference, because most such sentences cite another
chapter and then name their own exercise.

Two findings are errors whatever the baseline says: a number with
no `## N.` heading in the target's Solutions file, and an exercise
of "the previous chapter" or "the next chapter", which a chapter
split silently retargets; name the chapter with a link instead.

Under-reports by design: "the last three exercises", and an
exercise described without a number, are invisible to it. A
reference that was wrong when the baseline was written stays
accepted; the 2026-09-20 baseline was taken after all 58 references
had been read against their exercises.

Usage:
    python -m tools.exercise_refs            # the delta
    python -m tools.exercise_refs --all      # every reference
    python -m tools.exercise_refs --accept   # rewrite the baseline
    python -m tools.exercise_refs Chapters/30_*.md Solutions/30_*.md
"""
import argparse
import re
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from tools import check_solutions as cs
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.record_check import chapter_name
from tools.report import Finding

BASELINE = DATA_DIR / "exercise_refs_baseline.txt"
HEADER = (
    "# Prose references to numbered exercises, each paired with the\n"
    "# Solutions heading it points at, as last read by a human.\n"
    "# Tree/Chapter_Name<TAB>target Chapter_Name<TAB>number<TAB>\n"
    "# title, one per reference, sorted. Rewritten by\n"
    "# `make exercise-refs-accept`; read the delta with\n"
    "# `make exercise-refs` before accepting.\n"
    "# See tools/exercise_refs.py.\n"
)

ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth",
            "seventh", "eighth", "ninth", "tenth")
RELATIVE = {"previous": -1, "preceding": -1,
            "next": 1, "following": 1}

# "exercise 3", "Exercises 3 and 4", "exercises 3, 4, and 5".
NUMERIC = re.compile(
    r"\bexercises?\s+\d+(?:(?:,\s*|,?\s+and\s+)\d+)*", re.IGNORECASE)
# "second exercise", "previous exercise". The closing \b keeps out
# "the second exercises `NotInteresting`", where the word is a verb.
WORDED = re.compile(
    rf"\b({'|'.join((*ORDINALS, *RELATIVE))})\s+exercise\b",
    re.IGNORECASE)

# A link to a chapter file, from Chapters/ or from Solutions/.
CHAPTER_LINK = re.compile(
    r"\]\((?:\.\./Chapters/)?([\w-]+)\.md(?:#[\w-]*)?\)")
LINK_AFTER = re.compile(
    r"\s+(?:of|in|from)\s+\[[^\]]*" + CHAPTER_LINK.pattern)
LINK_BEFORE = re.compile(CHAPTER_LINK.pattern + r"['\u2019]s\s+$")
POINTS_BACK = re.compile(
    r"\b(?:its|that chapter's)\s+$", re.IGNORECASE)
NEIGHBOR_CHAPTER = re.compile(
    r"\b(?:previous|last|next|preceding|following) chapter's\s+"
    r"(?:\w+\s+)?$", re.IGNORECASE)


@dataclass(frozen=True)
class Paragraph:
    """Joined prose lines, and the exercise they sit in (0: none)."""
    text: str
    starts: tuple[tuple[int, int], ...]  # (text offset, line number)
    exercise: int

    def line_at(self, offset: int) -> int:
        return max(n for start, n in self.starts if start <= offset)


@dataclass(frozen=True)
class Reference:
    """One exercise number a sentence names, and where it points."""
    path: Path
    line: int
    number: int
    target: str  # the target chapter's file stem, "" for a neighbor
    phrase: str


def paragraphs(doc: Document, solutions: bool) -> Iterator[Paragraph]:
    """Prose paragraphs outside fences, tagged with their exercise.

    In a chapter the exercise is the numbered item under the last
    Exercises heading; in a Solutions file it is the `## N.` section
    (the first number of a combined heading). A numbered item opens a
    new paragraph, so "the previous exercise" resolves per item.
    """
    fenced = doc.in_fence()
    exercise, inside = 0, False
    pending: list[tuple[int, str]] = []

    def flush() -> Iterator[Paragraph]:
        if pending:
            starts, offset = [], 0
            for n, line in pending:
                starts.append((offset, n))
                offset += len(line) + 1
            yield Paragraph(" ".join(line for _, line in pending),
                            tuple(starts), exercise)
            pending.clear()

    for index, raw in enumerate(doc.lines):
        line = raw.strip()
        if fenced[index] or not line:
            yield from flush()
            continue
        if cs.HEADING.match(raw):
            yield from flush()
            answer = cs.ANSWER.match(raw.lstrip("#").strip())
            if solutions:
                exercise = (
                    cs.expand(answer.group(1))[0] if answer else 0)
            else:
                inside = bool(cs.EXERCISES_HEADING.match(raw))
                exercise = 0
            continue
        item = cs.ITEM.match(raw) if inside else None
        if item:
            yield from flush()
            exercise = int(item.group(1))
        pending.append((index + 1, line))
    yield from flush()


def target_of(para: Paragraph, start: int, end: int, own: str) -> str:
    """The chapter stem a reference at text[start:end] points at."""
    before, after = para.text[:start], para.text[end:]
    if NEIGHBOR_CHAPTER.search(before):
        return ""
    if m := LINK_AFTER.match(after):
        return m.group(1)
    if m := LINK_BEFORE.search(before):
        return m.group(1)
    if POINTS_BACK.search(before):
        links = CHAPTER_LINK.findall(before)
        if links:
            return links[-1]
    return own


def references(path: Path) -> Iterator[Reference]:
    doc = Document.parse(path)
    solutions = path.parent.name == "Solutions"
    for para in paragraphs(doc, solutions):
        found: list[tuple[int, int, list[int]]] = []
        for m in NUMERIC.finditer(para.text):
            numbers = [int(n) for n in re.findall(r"\d+", m.group())]
            found.append((m.start(), m.end(), numbers))
        for m in WORDED.finditer(para.text):
            word = m.group(1).lower()
            if word in RELATIVE:
                if not para.exercise:
                    continue
                number = para.exercise + RELATIVE[word]
            else:
                number = ORDINALS.index(word) + 1
            found.append((m.start(), m.end(), [number]))
        for start, end, numbers in sorted(found):
            target = target_of(para, start, end, path.stem)
            for number in numbers:
                yield Reference(path, para.line_at(start), number,
                                target, para.text[start:end])


def titles(root: Path, stem: str) -> dict[int, str]:
    """{exercise number: heading title} from a chapter's Solutions."""
    path = root / "Solutions" / f"{stem}.md"
    found: dict[int, str] = {}
    if not path.exists():
        return found
    for _, text in Document.parse(path).headings():
        if m := cs.ANSWER.match(text):
            title = text.split(".", 1)[1].strip()
            for number in cs.expand(m.group(1)):
                found[number] = title
    return found


def resolve(refs: list[Reference], root: Path,
            ) -> tuple[list[tuple[Reference, str]], list[Finding]]:
    """(reference, baseline entry) pairs, and the hard errors."""
    cache: dict[str, dict[int, str]] = {}
    pairs: list[tuple[Reference, str]] = []
    errors: list[Finding] = []
    for ref in refs:
        if not ref.target:
            errors.append(Finding(
                ref.path, ref.line,
                f'"{ref.phrase}" belongs to a neighboring chapter; '
                "name the chapter with a link, so a chapter split "
                "cannot retarget it"))
            continue
        if ref.target not in cache:
            cache[ref.target] = titles(root, ref.target)
        title = cache[ref.target].get(ref.number)
        if title is None:
            errors.append(Finding(
                ref.path, ref.line,
                f'"{ref.phrase}": Solutions/{ref.target}.md has no '
                f"exercise {ref.number}"))
            continue
        source = f"{ref.path.parent.name}/{chapter_name(ref.path)}"
        name = chapter_name(Path(ref.target))
        pairs.append(
            (ref, f"{source}\t{name}\t{ref.number}\t{title}"))
    return pairs, errors


def load_baseline(path: Path = BASELINE) -> Counter[str]:
    if not path.exists():
        return Counter()
    return Counter(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )


def write_baseline(entries: Counter[str],
                   path: Path = BASELINE) -> None:
    body = "".join(f"{line}\n" for line in sorted(entries.elements()))
    path.write_text(HEADER + body, encoding="utf-8", newline="\n")


def scoped(baseline: Counter[str], paths: list[Path]) -> Counter[str]:
    """The baseline entries whose referring file is among `paths`."""
    sources = {f"{p.parent.name}/{chapter_name(p)}" for p in paths}
    return Counter({entry: n for entry, n in baseline.items()
                    if entry.split("\t", 1)[0] in sources})


def describe(ref: Reference, entry: str) -> str:
    _, name, number, title = entry.split("\t", 3)
    path = ref.path
    if path.is_relative_to(Path.cwd()):
        path = path.relative_to(Path.cwd())
    return (f'{path.as_posix()}:{ref.line}: "{ref.phrase}" -> '
            f"{name} {number}. {title}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files to check (default: "
                         "Chapters/ and Solutions/ under --root)")
    ap.add_argument("--all", action="store_true",
                    help="list every reference with its title")
    ap.add_argument("--accept", action="store_true",
                    help="rewrite the baseline from the current run")
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="tree holding Chapters/ and Solutions/ "
                         "(default: the repo)")
    ap.add_argument("--baseline", type=Path, default=BASELINE,
                    help=f"baseline file (default: {BASELINE.name})")
    args = ap.parse_args(argv)
    if args.paths and args.accept:
        ap.error(
            "--accept rewrites the whole baseline; give no paths")
    paths = [Path(p) for p in args.paths] or sorted(
        list((args.root / "Chapters").glob("*.md"))
        + list((args.root / "Solutions").glob("*.md")))
    refs = [ref for path in paths for ref in references(path)]
    pairs, errors = resolve(refs, args.root)
    for error in errors:
        print(error.format())
    if args.all:
        for ref, entry in pairs:
            print(describe(ref, entry))
        print(f"exercise references: {len(pairs)} paired, "
              f"{len(errors)} error(s)")
        return 1 if errors else 0
    now = Counter(entry for _, entry in pairs)
    if args.accept:
        write_baseline(now, args.baseline)
        print(f"Baseline written: {sum(now.values())} entries in "
              f"{args.baseline}")
        return 1 if errors else 0
    before = scoped(load_baseline(args.baseline), paths)
    new, gone = now - before, before - now
    for ref, entry in pairs:
        if entry in new:
            print(f"NEW   {describe(ref, entry)}")
    for entry in sorted(gone.elements()):
        source, name, number, title = entry.split("\t", 3)
        print(f"GONE  {source}: {name} {number}. {title}")
    print(f"exercise references: {sum(now.values())} paired, "
          f"{sum(new.values())} new, {sum(gone.values())} gone, "
          f"{len(errors)} error(s), baseline {sum(before.values())}")
    if new:
        print("Reread each NEW sentence against the exercise under "
              "that title: fix the number, or "
              "`make exercise-refs-accept`.")
    return 1 if new or errors else 0


if __name__ == "__main__":
    sys.exit(main())
