#!/usr/bin/env python3
"""Report which chapter sections no exercise practices.

Reviews kept finding the same shape of gap: a chapter's exercises cluster on
whichever section was most fun to write, leaving whole sections with nothing
for the reader to do. Nothing measured that, so it stayed an impression.

This turns it into a list. For each chapter it reads the `##` sections, notes
which listings each one owns, then reads the `## Exercises` section and maps
every exercise back to the sections it touches. A section that no exercise
reaches is reported.

An exercise reaches a section three ways, all of them literal:

- It names a listing the section owns (`In "sketch.py", add ...`). Listings
  are the `# path/slug.py` first lines of fenced blocks, so a section owns
  every listing defined between its heading and the next one.
- It names a function or class those listings define (`Give `History` a
  maximum depth`). This is the common case by a wide margin: an exercise
  usually names the thing, not the file it lives in.
- It links to the section's anchor (`(#the-error-channel)` or
  `(31_State_Machines.md#the-engine)`), for a link inside this chapter.
- It quotes the section's heading text.

The matching is literal, so it under-reports coverage rather than over-
reporting it: an exercise that practices a section while naming nothing from
it ("Save a `Drawing` with `pickle`" against a section whose listings define
no symbol the exercise mentions) reads as a gap. Confirm a reported section
by eye before acting on it.

This is deliberately a report and not a gate. Not every section wants an
exercise: a section can be a table, a two-paragraph aside, or a conclusion,
and forcing one onto each would be worse than the gap. The output is a
worklist for an author, so it prints and always exits 0 unless asked to
fail with --strict.

    uv run python tools/exercise_coverage.py            # every chapter
    uv run python tools/exercise_coverage.py 19 31      # two chapters
    uv run python tools/exercise_coverage.py --covered  # show both halves
"""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from tools_repo import add_paths_arg, block_slug, md_files

HEADING_RE = re.compile(r"^(#{2,3})\s+(.*?)\s*(?:\{#([^}]+)\})?\s*$")
FENCE_RE = re.compile(r"^```")
ANCHOR_RE = re.compile(r"\(([^)]*#[^)]+)\)")
EXERCISE_RE = re.compile(r"^(\d+)[.)]\s+(.*)$")
DEF_RE = re.compile(r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)",
                    re.MULTILINE)


def slugify(text: str) -> str:
    """Approximate pandoc's auto-slug: the form heading_links.py gates."""
    out = text.lower()
    out = re.sub(r"`([^`]*)`", r"\1", out)
    out = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", out)
    out = re.sub(r"[^a-z0-9 .\-_]", "", out)
    # Pandoc drops leading characters until the first letter, since an
    # HTML id cannot start with a digit: "### 1. Nothing stops ..."
    # becomes "nothing-stops-...".
    out = re.sub(r"^[^a-z]+", "", out.strip())
    return out.replace(" ", "-")


@dataclass
class Section:
    title: str
    anchor: str
    listings: set[str] = field(default_factory=set)
    symbols: set[str] = field(default_factory=set)

    def reached_by(self, text: str) -> bool:
        lowered = text.lower()
        if any(name in text for name in self.listings):
            return True
        if any(re.search(rf"\b{re.escape(sym)}\b", text)
               for sym in self.symbols):
            return True
        if any(self.anchor and self.anchor in ref
               for ref in ANCHOR_RE.findall(text)):
            return True
        bare = re.sub(r"[`*]", "", self.title).lower()
        return len(bare) > 12 and bare in lowered


def parse(path: Path, depth: int = 2) -> tuple[list[Section], list[str]]:
    """Return the chapter's sections and its exercise texts.

    `depth` is the deepest heading level that counts as a section. The
    default of 2 counts `##` only, which is the granularity an author
    thinks in; chapter 41's `itertools` catalog gives every entry a `###`
    heading, and counting those would report 35 "unpracticed sections"
    for one reference chapter. A `###` block's listings are folded into
    the `##` section containing it.
    """
    sections: list[Section] = []
    exercises: list[str] = []
    current: Section | None = None
    in_exercises = False
    in_fence = False
    block: list[str] = []
    pending: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line):
            if in_fence:
                slug = block_slug(block)
                if slug and current is not None:
                    current.listings.add(Path(slug).name)
                    current.symbols.update(DEF_RE.findall("\n".join(block)))
                block = []
            in_fence = not in_fence
            continue
        if in_fence:
            block.append(line)
            continue

        heading = HEADING_RE.match(line)
        if heading:
            title = heading.group(2)
            if len(heading.group(1)) > depth:
                continue  # A subsection belongs to the section above it.
            if pending and in_exercises:
                exercises.append("\n".join(pending))
                pending = []
            in_exercises = title.strip().lower() == "exercises"
            if in_exercises:
                current = None
                continue
            current = Section(title, heading.group(3) or slugify(title))
            sections.append(current)
            continue

        if in_exercises:
            item = EXERCISE_RE.match(line.strip())
            if item:
                if pending:
                    exercises.append("\n".join(pending))
                pending = [item.group(2)]
            elif pending:
                pending.append(line.strip())

    if pending:
        exercises.append("\n".join(pending))
    return sections, exercises


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_paths_arg(ap)
    ap.add_argument("--deep", action="store_true",
                    help="count ### subsections as sections too")
    ap.add_argument("--covered", action="store_true",
                    help="also list the sections that are practiced")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any section is unpracticed")
    args = ap.parse_args()

    selected = []
    for path in md_files():
        if not args.paths or any(
            str(sel) in path.name or path.name.startswith(str(sel))
            for sel in args.paths
        ):
            selected.append(path)

    total_gaps = 0
    for path in selected:
        sections, exercises = parse(path, 3 if args.deep else 2)
        if not exercises or not sections:
            continue
        uncovered = [
            s for s in sections
            if not any(s.reached_by(text) for text in exercises)
        ]
        covered = len(sections) - len(uncovered)
        total_gaps += len(uncovered)
        print(f"{path.name}: {len(exercises)} exercise(s), "
              f"{covered}/{len(sections)} section(s) practiced")
        for s in uncovered:
            print(f"    unpracticed: {s.title}")
        if args.covered:
            for s in sections:
                if s not in uncovered:
                    print(f"    practiced:   {s.title}")

    print(f"\n{total_gaps} unpracticed section(s) across "
          f"{len(selected)} chapter(s).")
    return 1 if (args.strict and total_gaps) else 0


if __name__ == "__main__":
    raise SystemExit(main())
