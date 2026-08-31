#!/usr/bin/env python3
"""Flag cross-chapter links whose text claims something the target may not say.

`heading_links.py` proves a link's target exists. Nothing proves the target
says what the sentence claims about it, and reviews kept finding links that
resolve cleanly while pointing at a section describing something else.

A tool cannot settle that question, because it is about meaning. It can
narrow it. Every cross-chapter link falls into one of three shapes, and only
the third can be wrong in this way:

1. `[Iterators](23_Patterns--Iterators.md)` names the chapter. The link text is the
   chapter's title, so it asserts nothing beyond "this chapter exists."
2. `[The General Form of `replace()`](12_...#the-general-form-of-replace)`
   quotes the target heading. The text and the target agree by construction;
   if the heading is later renamed, `heading_links.py` catches it.
3. `[the price-and-weight example](37_...#adding-operations)` is a phrase the
   author wrote describing what is over there. Nothing checks it. This is the
   shape that goes stale when the target is rewritten, and the shape that was
   wrong in every instance found by hand.

A fourth shape looks like the third and is harmless: `[sentinel](05_...)`,
`[narrows](08_...#narrowing)`, `[mangled](11_...)`. The link text is one word
of the running sentence, hyperlinked to wherever that term is taught, so it
claims nothing about the target's content either. Those are filtered out by
word count, which `--min-words` tunes; below the threshold a link is treated
as an inline term link rather than a claim.

So: resolve each link's target heading, then report the links whose text
matches neither the chapter title nor the target heading. That is the
worklist a human (or an agent) reads against the target.

Overlap is measured on lowercased word sets with punctuation and code ticks
stripped, ignoring short function words. `--threshold` tunes how much
overlap counts as quoting the heading; the default of 0.5 was chosen by
running the book and reading the boundary cases.

    uv run python tools/check_claims.py              # every chapter
    uv run python tools/check_claims.py 33 27        # two chapters
    uv run python tools/check_claims.py --all        # every link, classified
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from tools_config import CHAPTERS_DIR
from tools_repo import add_paths_arg, md_files

LINK_RE = re.compile(
    r"\[([^\]]+)\]\((\d{2}_[A-Za-z_]+\.md)(?:#([a-z0-9._-]+))?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*(?:\{#([^}]+)\})?\s*$")
STOP = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "is", "it",
    "of", "on", "or", "that", "the", "to", "with", "what", "why", "how",
    "when", "does", "do", "not", "its", "this", "you", "your", "are",
}


def words(text: str) -> set[str]:
    text = re.sub(r"`([^`]*)`", r"\1", text.lower())
    return {w for w in re.findall(r"[a-z0-9_]+", text) if w not in STOP}


def overlap(a: str, b: str) -> float:
    """Fraction of the smaller word set that the two share."""
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


@dataclass(frozen=True)
class Target:
    title: str
    headings: dict[str, str]


def slugify(text: str) -> str:
    out = re.sub(r"`([^`]*)`", r"\1", text.lower())
    out = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", out)
    out = re.sub(r"[^a-z0-9 .\-_]", "", out)
    # Pandoc drops leading characters until the first letter, since an
    # HTML id cannot start with a digit: "### 1. Nothing stops ..."
    # becomes "nothing-stops-...".
    out = re.sub(r"^[^a-z]+", "", out.strip())
    return out.replace(" ", "-")


def load(path: Path) -> Target:
    title = path.stem
    headings: dict[str, str] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        text = m.group(1)
        if line.startswith("# "):
            title = text
        headings[m.group(2) or slugify(text)] = text
    return Target(title, headings)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_paths_arg(ap)
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="overlap at or above this counts as quoting")
    ap.add_argument("--min-words", type=int, default=3,
                    help="link texts shorter than this are term links")
    ap.add_argument("--all", action="store_true",
                    help="print every link with its classification")
    args = ap.parse_args()

    targets: dict[str, Target] = {}
    for path in md_files([CHAPTERS_DIR]):
        targets[path.name] = load(path)

    selected = [
        p for p in md_files([CHAPTERS_DIR])
        if not args.paths or any(
            str(s) in p.name or p.name.startswith(str(s)) for s in args.paths)
    ]

    flagged = total = 0
    for path in selected:
        hits: list[str] = []
        for n, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            for text, target_file, anchor in LINK_RE.findall(line):
                total += 1
                target = targets.get(target_file)
                if target is None:
                    continue
                heading = target.headings.get(anchor or "", "")
                names_chapter = overlap(text, target.title) >= args.threshold
                quotes_heading = bool(heading) and (
                    overlap(text, heading) >= args.threshold)
                term_link = len(words(text)) < args.min_words
                if names_chapter or quotes_heading or term_link:
                    if args.all:
                        kind = ("chapter" if names_chapter
                                else "heading" if quotes_heading
                                else "term")
                        hits.append(f"  {n}: [{text}] -> {kind}")
                    continue
                flagged += 1
                where = f"{target_file}#{anchor}" if anchor else target_file
                hits.append(
                    f"  {n}: [{text}]\n"
                    f"      -> {where}\n"
                    f"      target heading: "
                    f"{heading or '(no anchor: chapter top)'}")
        if hits:
            print(f"{path.name}:")
            print("\n".join(hits))

    print(f"\n{flagged} of {total} cross-chapter link(s) make a claim "
          f"nothing checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
