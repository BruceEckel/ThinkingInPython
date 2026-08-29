#!/usr/bin/env python
"""Print two-level categorized help for the Makefile, replacing `grep | awk`.

Every target line ending in a `## text` comment becomes one help entry, and
a `##@ Name` line starts a new section. A target with no doc comment is left
out entirely (most are internal or self-explanatory).

The listing has two levels, because a flat one ran to 74 targets. Bare
`make` prints `help`, the everyday commands, and the section list; `make
help style` expands one section. A section's *slug*, the name you pass, is
the first word of its `##@` heading, lowercased. No separate list of slugs
exists to drift: rename the heading and the slug follows.

A target whose comment is `##-` rather than `##` is *secondary*: documented
and smoke-tested, but folded out of the listing because a sibling's doc text
names it (`fix-eol` under `eol`). That keeps `make help style` at ten rows
instead of sixteen without hiding a target from `verify_targets.py`.

Two invariants are enforced rather than assumed, both raising SystemExit
with a message naming the offender:

  * No two sections share a slug.
  * No slug equals a target name. The Makefile neutralizes the word after
    `help` so `make help style` parses as one goal, and that would override
    a real recipe if a slug ever collided with one.

This exists so `make help` has no dependency on `grep`/`awk` being on PATH.
Every other target already requires Python (via `uv run`), so routing help
through it too means one less way for `make help` to fail on a machine that
has GNU Make but not a POSIX toolchain.

`entries()` is the flat (target, doc) view, imported by verify_targets.py
(to enumerate every target) and sweep_checks.py (to look one up). It
reports secondary targets too, so folding a row out of the listing never
drops it from the smoke test.

Doc text wraps to the terminal width, with continuation lines indented under
the doc column so the target names stay in one scannable column. The width
comes from the terminal and is capped at MAX_WIDTH, since a doc string run
across 200 columns is no easier to read than one that overflows 80. A pipe
or a redirect gets the 80-column fallback.

Usage:
    python tools/make_help.py                    # the index (plain `make`)
    python tools/make_help.py --all              # every section (`make help`)
    python tools/make_help.py style              # one section
    python tools/make_help.py --width 72         # wrap to a fixed width
    python tools/make_help.py --makefile PATH    # read another Makefile
"""
import argparse
import re
import shutil
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from tools_config import ROOT

MAKEFILE = ROOT / "Makefile"

# Wrap no wider than this however wide the terminal is, and give up on
# wrapping (printing one long line) rather than squeeze the doc column
# below MIN_DOC, which happens on a very narrow terminal.
MAX_WIDTH = 100
MIN_DOC = 24

# A backticked span wraps as one unit. `\x00` stands in for the spaces
# inside it while textwrap runs, since textwrap splits on anything `\s`
# matches and that includes the non-breaking space U+00A0.
_KEEP_TOGETHER = re.compile(r"`[^`]+`")
_JOINER = "\x00"

_TARGET = re.compile(r"^([a-zA-Z_-]+):.*?##(-?)\s?(.*)$")
_CATEGORY = re.compile(r"^##@\s?(.*)$")

# The handful of targets worth printing above the section list. Kept here
# rather than marked in the Makefile because which commands are "everyday"
# is a judgment about the set as a whole, and reads best in one place;
# main() fails if a name here is not a documented target.
PROMOTED: tuple[str, ...] = ("all", "verify", "gate", "check-ch", "sweep")


@dataclass(frozen=True)
class Target:
    """One documented target. `secondary` hides it from the listing."""
    name: str
    doc: str
    secondary: bool = False


@dataclass(frozen=True)
class Section:
    """One `##@` heading and the targets under it."""
    slug: str
    title: str
    targets: list[Target] = field(default_factory=list)

    def listed(self) -> list[Target]:
        return [t for t in self.targets if not t.secondary]


def parse(text: str) -> list[Section]:
    """Sections in file order. The first holds any pre-heading target."""
    sections = [Section("", "")]
    for line in text.splitlines():
        category = _CATEGORY.match(line)
        if category:
            title = category.group(1)
            sections.append(Section(title.split()[0].lower(), title))
            continue
        target = _TARGET.match(line)
        if target:
            sections[-1].targets.append(Target(
                target.group(1), target.group(3), target.group(2) == "-"))
    return [s for s in sections if s.targets]


def entries(text: str) -> list[tuple[str, str] | tuple[None, str]]:
    """(target, doc) pairs, or (None, title) for a `##@` heading.

    The flat view, kept for verify_targets.py and sweep_checks.py. Includes
    secondary targets, so hiding a row from the listing never hides it from
    the smoke test.
    """
    found: list[tuple[str, str] | tuple[None, str]] = []
    for section in parse(text):
        if section.title:
            found.append((None, section.title))
        found.extend((t.name, t.doc) for t in section.targets)
    return found


def terminal_width(override: int | None = None) -> int:
    """The wrap width: an explicit --width, else the terminal's, capped."""
    if override:
        return override
    return min(shutil.get_terminal_size((80, 24)).columns, MAX_WIDTH)


def _table(rows: list[tuple[str, str]], width: int) -> list[str]:
    """Two columns, the second wrapped and hanging-indented under itself.

    Three things must survive intact. A hyphenated target name
    (`fix-comment-spacing`) stays whole via break_on_hyphens; an over-long
    word overflows rather than splitting via break_long_words; and a
    backticked command keeps its two words together, which textwrap cannot
    express, so the spaces inside backticks are swapped for a placeholder
    that is not whitespace and swapped back afterward.
    """
    label_width = max((len(label) for label, _ in rows), default=0)
    lines: list[str] = []
    for label, doc in rows:
        lead = f"  {label:<{label_width}}  "
        body = width - len(lead)
        if body < MIN_DOC:
            lines.append(f"{lead}{doc}")
            continue
        wrapped = textwrap.wrap(
            _KEEP_TOGETHER.sub(lambda m: m.group().replace(" ", _JOINER), doc),
            body, break_long_words=False, break_on_hyphens=False)
        wrapped = [line.replace(_JOINER, " ") for line in wrapped]
        lines.append(lead + (wrapped[0] if wrapped else ""))
        lines += [" " * len(lead) + line for line in wrapped[1:]]
    return lines


def _rows(targets: list[Target], width: int) -> list[str]:
    return _table([(t.name, t.doc) for t in targets], width)


def check(sections: list[Section]) -> None:
    """Raise SystemExit on a duplicate slug, a slug that shadows a target,
    or a PROMOTED name that no longer exists."""
    named = [s for s in sections if s.slug]
    slugs = [s.slug for s in named]
    if duplicate := {s for s in slugs if slugs.count(s) > 1}:
        raise SystemExit(
            f"make_help: two sections share the slug {sorted(duplicate)}. "
            "Reword one heading so its first word differs.")

    targets = {t.name for s in sections for t in s.targets}
    if shadowed := sorted(set(slugs) & targets):
        raise SystemExit(
            f"make_help: section slug {shadowed} is also a target name. "
            "The Makefile's `help` guard would override that recipe; "
            "reword the heading.")

    if missing := sorted(set(PROMOTED) - targets):
        raise SystemExit(
            f"make_help: PROMOTED names {missing} are not documented "
            "targets. Update PROMOTED in tools/make_help.py.")


def render_index(sections: list[Section], width: int | None = None) -> str:
    """The default listing: help, the everyday commands, the section list."""
    width = width or terminal_width()
    by_name = {t.name: t for s in sections for t in s.targets}
    lines: list[str] = []

    if preamble := next((s for s in sections if not s.slug), None):
        lines += _rows(preamble.listed(), width)

    lines.append("\nEveryday:")
    lines += _rows([by_name[n] for n in PROMOTED], width)

    lines.append("\nSubtopics (`make help NAME`; `make help` lists them all):")
    named = [s for s in sections if s.slug]
    slug_width = max(len(s.slug) for s in named)
    lines += _table(
        [(f"{s.slug:<{slug_width}}  {len(s.listed()):>2}", s.title)
         for s in named], width)
    return "\n".join(lines)


def render_section(section: Section, width: int | None = None) -> str:
    """The heading line names the slug first (`style: Style gates`), so
    the full listing doubles as the index of what `make help NAME` takes."""
    rows = _rows(section.listed(), width or terminal_width())
    return "\n".join([f"{section.slug}: {section.title}", *rows])


def render_all(sections: list[Section], width: int | None = None) -> str:
    """Every section expanded, in Makefile order: what `make help` prints.

    Secondary targets stay folded, as in a single section, since the doc
    text of the sibling that names them is right there above.
    """
    width = width or terminal_width()
    blocks: list[str] = []
    if preamble := next((s for s in sections if not s.slug), None):
        blocks.append("\n".join(_rows(preamble.listed(), width)))
    blocks += [render_section(s, width) for s in sections if s.slug]
    return "\n\n".join(blocks)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "topic", nargs="?",
        help="section to expand (a slug from the default listing)")
    ap.add_argument(
        "--all", action="store_true",
        help="print every section expanded (what `make help` runs)")
    ap.add_argument(
        "--width", type=int, default=None,
        help="wrap doc text to this many columns (default: the terminal's, "
             f"capped at {MAX_WIDTH})")
    ap.add_argument(
        "--makefile", type=Path, default=MAKEFILE,
        help=f"Makefile to read (default: {MAKEFILE.name})")
    args = ap.parse_args(argv)

    sections = parse(args.makefile.read_text(encoding="utf-8"))
    check(sections)
    width = terminal_width(args.width)

    if args.all:
        print(render_all(sections, width))
        return 0
    if not args.topic:
        print(render_index(sections, width))
        return 0

    match = next((s for s in sections if s.slug == args.topic), None)
    if match is None:
        known = ", ".join(s.slug for s in sections if s.slug)
        print(f"No subtopic named {args.topic!r}. Try one of: {known}")
        return 2
    print(render_section(match, width))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
