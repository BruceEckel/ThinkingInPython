#!/usr/bin/env python
"""Print categorized help for the Makefile, replacing `grep | awk`.

Every target line ending in a `## text` comment becomes one help entry, and
a `##@ Name` line starts a new section. A target with no doc comment is left
out entirely (most are internal or self-explanatory).

Bare `make` and `make help` both print every section; `make help style`
prints one. A section's *slug*, the name you pass, is the first word of
its `##@` heading, lowercased, and each heading in the full listing leads
with it (`style: Style gates`) so the listing doubles as the index of what
`make help NAME` takes. No separate list of slugs exists to drift: rename
the heading and the slug follows.

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

In a terminal, both forms open the interactive picker in help_picker.py
instead of printing: arrow keys or the mouse choose a target and Enter
runs it. The static listing below is what a pipe, CI, `verify-targets`,
and `--pick never` get, and what the picker falls back to if
prompt_toolkit is not installed.

Output is colored when stdout is a terminal: section headings bold with the
slug highlighted, target names in color. `NO_COLOR` turns it off,
`FORCE_COLOR` (or `--color always`) turns
it on for a pipe, and a legacy Windows console has VT processing switched
on first, since without it the escape codes print as garbage. The render
functions take a Palette and default to the plain one, so wrapping is
measured on uncolored text and the tests see no escape codes.

Usage:
    python tools/make_help.py                    # every section
    python tools/make_help.py style              # one section
    python tools/make_help.py --width 72         # wrap to a fixed width
    python tools/make_help.py --color never      # plain text on a terminal
    python tools/make_help.py --pick never       # the static listing, no picker
    python tools/make_help.py --makefile PATH    # read another Makefile
"""
import argparse
import os
import re
import shutil
import sys
import textwrap
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO

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

@dataclass(frozen=True)
class Palette:
    """ANSI codes for each role in the listing; all empty means plain text."""
    heading: str = ""
    slug: str = ""
    target: str = ""
    dim: str = ""
    reset: str = ""

    def paint(self, code: str, text: str) -> str:
        return f"{code}{text}{self.reset}" if code else text


PLAIN = Palette()
ANSI = Palette(
    heading="\x1b[1m", slug="\x1b[1;36m", target="\x1b[36m",
    dim="\x1b[2m", reset="\x1b[0m")


def _enable_windows_vt() -> bool:
    """Turn on ANSI processing in a legacy Windows console.

    Windows Terminal has it on already; the old conhost does not, and
    prints the escape codes literally. Returns whether the console will
    now interpret them.
    """
    import ctypes
    windll = getattr(ctypes, "windll", None)
    if windll is None:
        return False
    kernel32 = windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False
    wanted = mode.value | 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    return bool(kernel32.SetConsoleMode(handle, wanted))


def can_colorize(stream: IO[str] | None = None,
                 env: Mapping[str, str] | None = None) -> bool:
    """Whether to emit ANSI codes: NO_COLOR wins, then FORCE_COLOR, then
    whether the stream is a terminal (and, on Windows, one that understands
    escape codes)."""
    settings: Mapping[str, str] = os.environ if env is None else env
    if settings.get("NO_COLOR"):
        return False
    if settings.get("FORCE_COLOR"):
        return True
    if settings.get("TERM") == "dumb":
        return False
    stream = sys.stdout if stream is None else stream
    isatty = getattr(stream, "isatty", None)
    if isatty is None or not isatty():
        return False
    if sys.platform == "win32":
        return _enable_windows_vt()
    return True


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


def _table(rows: list[tuple[str, str]], width: int,
           paint: Callable[[str], str] = str) -> list[str]:
    """Two columns, the second wrapped and hanging-indented under itself.

    Three things must survive intact. A hyphenated target name
    (`fix-comment-spacing`) stays whole via break_on_hyphens; an over-long
    word overflows rather than splitting via break_long_words; and a
    backticked command keeps its two words together, which textwrap cannot
    express, so the spaces inside backticks are swapped for a placeholder
    that is not whitespace and swapped back afterward.

    `paint` colors the label; padding is measured on the raw label so the
    escape codes it adds never shift the doc column.
    """
    label_width = max((len(label) for label, _ in rows), default=0)
    lines: list[str] = []
    for label, doc in rows:
        pad = " " * (label_width - len(label))
        lead = f"  {paint(label)}{pad}  "
        indent = " " * (2 + label_width + 2)
        body = width - len(indent)
        if body < MIN_DOC:
            lines.append(f"{lead}{doc}")
            continue
        wrapped = wrap_doc(doc, body)
        lines.append(lead + (wrapped[0] if wrapped else ""))
        lines += [indent + line for line in wrapped[1:]]
    return lines


def wrap_doc(doc: str, width: int) -> list[str]:
    """Wrap one doc string to `width`, keeping backticked spans whole.

    Shared with help_picker.py so the picker breaks lines exactly where
    the static listing does.
    """
    wrapped = textwrap.wrap(
        _KEEP_TOGETHER.sub(lambda m: m.group().replace(" ", _JOINER), doc),
        width, break_long_words=False, break_on_hyphens=False)
    return [line.replace(_JOINER, " ") for line in wrapped]


def _rows(targets: list[Target], width: int,
          palette: Palette = PLAIN) -> list[str]:
    return _table([(t.name, t.doc) for t in targets], width,
                  lambda name: palette.paint(palette.target, name))


def _heading(section: Section, palette: Palette) -> str:
    """`style: Style gates`, slug and title each in their own color."""
    return (palette.paint(palette.slug, f"{section.slug}:") + " "
            + palette.paint(palette.heading, section.title))


def check(sections: list[Section]) -> None:
    """Raise SystemExit on a duplicate slug or a slug that shadows a
    target."""
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


def render_section(section: Section, width: int | None = None,
                   palette: Palette = PLAIN) -> str:
    """The heading line names the slug first (`style: Style gates`), so
    the full listing doubles as the index of what `make help NAME` takes."""
    rows = _rows(section.listed(), width or terminal_width(), palette)
    return "\n".join([_heading(section, palette), *rows])


def render_all(sections: list[Section], width: int | None = None,
               palette: Palette = PLAIN) -> str:
    """Every section expanded, in Makefile order: what `make` prints.

    Secondary targets stay folded, as in a single section, since the doc
    text of the sibling that names them is right there above.
    """
    width = width or terminal_width()
    blocks: list[str] = []
    if preamble := next((s for s in sections if not s.slug), None):
        blocks.append("\n".join(_rows(preamble.listed(), width, palette)))
    blocks += [render_section(s, width, palette)
               for s in sections if s.slug]
    return "\n\n".join(blocks)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "topic", nargs="?",
        help="one section to show (the slug its heading starts with)")
    ap.add_argument(
        "--width", type=int, default=None,
        help="wrap doc text to this many columns (default: the terminal's, "
             f"capped at {MAX_WIDTH})")
    ap.add_argument(
        "--makefile", type=Path, default=MAKEFILE,
        help=f"Makefile to read (default: {MAKEFILE.name})")
    ap.add_argument(
        "--color", choices=("auto", "always", "never"), default="auto",
        help="ANSI color: auto (default) colors only a terminal, and "
             "honors NO_COLOR and FORCE_COLOR")
    ap.add_argument(
        "--pick", choices=("auto", "always", "never"), default="auto",
        help="the interactive picker: auto (default) opens it only when "
             "stdin and stdout are a terminal and CI is unset")
    args = ap.parse_args(argv)

    sections = parse(args.makefile.read_text(encoding="utf-8"))
    check(sections)
    width = terminal_width(args.width)
    colored = {"always": True, "never": False}.get(
        args.color, None)
    if colored is None:
        colored = can_colorize()
    palette = ANSI if colored else PLAIN

    match = None
    if args.topic:
        match = next((s for s in sections if s.slug == args.topic), None)
        if match is None:
            known = ", ".join(s.slug for s in sections if s.slug)
            print(f"No subtopic named {args.topic!r}. Try one of: {known}")
            return 2

    if want_picker(args.pick):
        try:
            import help_picker
        except ImportError:
            print("(interactive picker unavailable: `uv sync` installs "
                  "prompt_toolkit)", file=sys.stderr)
        else:
            rows = (help_picker.section_rows(match) if match is not None
                    else help_picker.all_rows(sections))
            # The menu reports a target's failure in its own output and
            # a "(exited with status N)" line; exiting nonzero here too
            # would only make the outer make add "*** [help] Error N",
            # a line that points at the wrong recipe.
            help_picker.pick_and_run(rows, color=colored)
            return 0

    if match is not None:
        print(render_section(match, width, palette))
    else:
        print(render_all(sections, width, palette))
    return 0


def want_picker(choice: str, env: Mapping[str, str] | None = None) -> bool:
    """`auto` means both ends are a terminal and this is not a CI run."""
    if choice == "always":
        return True
    if choice == "never":
        return False
    settings: Mapping[str, str] = os.environ if env is None else env
    if settings.get("CI"):
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


if __name__ == "__main__":
    raise SystemExit(main())
