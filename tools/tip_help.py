#!/usr/bin/env python
"""Print categorized help for `tip`, or open its picker.

The tasks and their sections come from tools/tasks.py through
tools/tip.py's Registry: each `section()` call starts a heading, each
`@task` becomes a row with its one-line doc, a `secondary=True` task is
folded out of the listing (still documented and smoke-tested) because
a sibling's doc text names it, and `also()` repeats tasks from other
sections at that point. The sections run from the everyday loop down
to setup and cleanup.

Bare `tip` and `tip help` both print every section; `tip help style`
prints one. A section's *slug*, the name you pass, is the first word
of its heading, lowercased, and each heading in the full listing leads
with it (`style: Style gates`) so the listing doubles as the index of
what `tip help NAME` takes. No separate list of slugs exists to drift:
rename the heading and the slug follows. check() refuses two sections
that share a slug.

`entries()` is the flat (task, doc) view, used by verify_targets.py
(to enumerate every task) and sweep_checks.py (to look one up). It
reports secondary tasks too, so folding a row out of the listing never
drops it from the smoke test, and leaves out `also()` repeats.

Doc text wraps to the terminal width, with continuation lines indented
under the doc column so the task names stay in one scannable column.
The width comes from the terminal and is capped at MAX_WIDTH, since a
doc string run across 200 columns is no easier to read than one that
overflows 80. A pipe or a redirect gets the 80-column fallback.

In a terminal, both forms open the interactive picker in help_picker.py
instead of printing: arrow keys or the mouse choose a task, Enter runs
it, and `?` shows its notes (the task function's docstring) and its
recipe (the function's body). The static listing below is what a
pipe, CI, `verify-targets`, and `--pick never` get, and what the
picker falls back to if prompt_toolkit is not installed.

A time column sits between the name and the doc: this machine's last
successful run of the task (build/target_times.json, written by every
timer in tools/), or, for a task this machine has not run, its tier
from tools/data/target_tiers.txt, which `tip verify-targets` writes.
The column is colored by tier (quick green, long yellow, very long red)
and a legend closes the listing; target_times.py has the thresholds.

Output is colored when stdout is a terminal: section headings bold
with the slug highlighted, task names in color. `NO_COLOR` turns it
off, `FORCE_COLOR` (or `--color always`) turns it on for a pipe, and a
legacy Windows console has VT processing switched on first, since
without it the escape codes print as garbage. The render functions
take a Palette and default to the plain one, so wrapping is measured
on uncolored text and the tests see no escape codes.

Usage (`tip help ARGS` passes ARGS here):
    python -m tools.tip_help                # every section
    python -m tools.tip_help style          # one section
    python -m tools.tip_help --width 72     # wrap to a fixed width
    python -m tools.tip_help --color never  # plain text on a terminal
    python -m tools.tip_help --pick never   # the listing, no picker
"""
import argparse
import os
import re
import shutil
import sys
import textwrap
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import IO

from tools.target_times import TIERS, Timing

# What the time column means, printed once under the listing.
LEGEND = ("Time: this machine's last run, or the tier from "
          "tools/data/target_tiers.txt. Tiers: "
          + ", ".join(f"{name} under {int(limit)} s" if limit < 120
                      else f"{name} under {int(limit // 60)} min"
                      if limit != float("inf") else name
                      for name, limit in TIERS) + ".")

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

@dataclass(frozen=True)
class Palette:
    """ANSI codes for each role in the listing; all empty means plain text."""
    heading: str = ""
    slug: str = ""
    target: str = ""
    dim: str = ""
    reset: str = ""
    quick: str = ""
    long: str = ""
    verylong: str = ""

    def paint(self, code: str, text: str) -> str:
        return f"{code}{text}{self.reset}" if code else text

    def paint_time(self, tier: str, text: str) -> str:
        """The time column's color: a tier's own, `normal` plain."""
        codes = {"quick": self.quick, "long": self.long,
                 "very long": self.verylong}
        return self.paint(codes.get(tier, ""), text)


PLAIN = Palette()
ANSI = Palette(
    heading="\x1b[1m", slug="\x1b[1;36m", target="\x1b[36m",
    dim="\x1b[2m", reset="\x1b[0m",
    quick="\x1b[32m", long="\x1b[33m", verylong="\x1b[31m")


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
    """One documented task, as the listing and the picker show it.

    `secondary` hides it from the listing. `notes` is the task
    function's docstring: the long-form help the picker shows on `?`.
    `recipe` is the function's body, `prereqs` the task's deps, and
    `defaults` what an unset variable means, for the picker's prompt.

    `repeat` marks a copy listed in a second section by `also()`: the
    same task, shown again where a reader would also look for it.
    `entries()` leaves the copies out, so a smoke test through it runs
    each task once.
    """
    name: str
    doc: str
    secondary: bool = False
    notes: str = ""
    recipe: tuple[str, ...] = ()
    prereqs: tuple[str, ...] = ()
    repeat: bool = False
    defaults: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Section:
    """One section() heading and the tasks under it, in order, with
    the tasks an also() repeats here at the point of that call."""
    slug: str
    title: str
    targets: list[Target] = field(default_factory=list)

    def listed(self) -> list[Target]:
        return [t for t in self.targets if not t.secondary]


def load_sections() -> list[Section]:
    """The listing's sections, from tools/tasks.py."""
    from tools.tip import load
    return load().sections()


def entries(sections: list[Section] | None = None,
            ) -> list[tuple[str, str] | tuple[None, str]]:
    """(task, doc) pairs, or (None, title) for a section heading.

    The flat view, kept for verify_targets.py and sweep_checks.py.
    Includes secondary tasks, so hiding a row from the listing never
    hides it from the smoke test, and leaves out `also()` repeats, so a
    task listed in two sections is still one task to run.
    """
    found: list[tuple[str, str] | tuple[None, str]] = []
    for section in load_sections() if sections is None else sections:
        if section.title:
            found.append((None, section.title))
        found.extend((t.name, t.doc) for t in section.targets
                     if not t.repeat)
    return found


def terminal_width(override: int | None = None) -> int:
    """The wrap width: an explicit --width, else the terminal's, capped."""
    if override:
        return override
    return min(shutil.get_terminal_size((80, 24)).columns, MAX_WIDTH)


def _table(rows: list[tuple[str, str, str]], width: int,
           paint: Callable[[str], str] = str,
           paint_time: Callable[[str, str], str] = lambda _tier, t: t,
           tiers: Mapping[str, str] | None = None,
           time_width: int = 0) -> list[str]:
    """Label, time, and doc columns, the doc wrapped and hanging-indented
    under itself. The time column is at least `time_width` wide, so
    every section's doc column lines up, and is left out when that is
    zero and every row's time is empty.

    Three things must survive intact. A hyphenated target name
    (`fix-comment-spacing`) stays whole via break_on_hyphens; an over-long
    word overflows rather than splitting via break_long_words; and a
    backticked command keeps its two words together, which textwrap cannot
    express, so the spaces inside backticks are swapped for a placeholder
    that is not whitespace and swapped back afterward.

    `paint` colors the label and `paint_time` the time (given its tier
    from `tiers`); padding is measured on the raw text so the escape
    codes they add never shift the doc column.
    """
    label_width = max((len(label) for label, _, _ in rows), default=0)
    time_width = max([time_width, *(len(t) for _, t, _ in rows)])
    lines: list[str] = []
    for label, when, doc in rows:
        pad = " " * (label_width - len(label))
        lead = f"  {paint(label)}{pad}  "
        if time_width:
            tier = (tiers or {}).get(label, "")
            lead += paint_time(tier, f"{when:>{time_width}}") + "  "
        indent = " " * (2 + label_width + 2
                        + (time_width + 2 if time_width else 0))
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
          palette: Palette = PLAIN,
          times: Mapping[str, Timing] | None = None) -> list[str]:
    known = times or {}
    return _table(
        [(t.name, known[t.name].label if t.name in known else "", t.doc)
         for t in targets],
        width, lambda name: palette.paint(palette.target, name),
        palette.paint_time,
        {name: timing.tier for name, timing in known.items()},
        max((len(t.label) for t in known.values()), default=0))


def _heading(section: Section, palette: Palette) -> str:
    """`style: Style gates`, slug and title each in their own color."""
    return (palette.paint(palette.slug, f"{section.slug}:") + " "
            + palette.paint(palette.heading, section.title))


def check(sections: list[Section]) -> None:
    """Raise SystemExit when two sections share a slug."""
    slugs = [s.slug for s in sections if s.slug]
    if duplicate := {s for s in slugs if slugs.count(s) > 1}:
        raise SystemExit(
            f"tip: two sections share the slug {sorted(duplicate)}. "
            "Reword one heading so its first word differs.")


def render_section(section: Section, width: int | None = None,
                   palette: Palette = PLAIN,
                   times: Mapping[str, Timing] | None = None) -> str:
    """The heading line names the slug first (`style: Style gates`), so
    the full listing doubles as the index of what `tip help NAME` takes.
    `times` fills the time column; none means no column."""
    rows = _rows(section.listed(), width or terminal_width(), palette,
                 times)
    return "\n".join([_heading(section, palette), *rows])


def legend(width: int, palette: Palette = PLAIN) -> str:
    """The time column's key, wrapped to `width`, dimmed."""
    return "\n".join(palette.paint(palette.dim, line)
                     for line in wrap_doc(LEGEND, width))


def render_all(sections: list[Section], width: int | None = None,
               palette: Palette = PLAIN,
               times: Mapping[str, Timing] | None = None) -> str:
    """Every section expanded, in tasks.py order: what `tip` prints.

    Secondary targets stay folded, as in a single section, since the doc
    text of the sibling that names them is right there above. With
    `times`, the legend for the time column closes the listing.
    """
    width = width or terminal_width()
    blocks: list[str] = []
    if preamble := next((s for s in sections if not s.slug), None):
        blocks.append("\n".join(_rows(preamble.listed(), width, palette,
                                      times)))
    blocks += [render_section(s, width, palette, times)
               for s in sections if s.slug]
    if times:
        blocks.append(legend(width, palette))
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
        "--color", choices=("auto", "always", "never"), default="auto",
        help="ANSI color: auto (default) colors only a terminal, and "
             "honors NO_COLOR and FORCE_COLOR")
    ap.add_argument(
        "--pick", choices=("auto", "always", "never"), default="auto",
        help="the interactive picker: auto (default) opens it only when "
             "stdin and stdout are a terminal and CI is unset")
    args = ap.parse_args(argv)

    sections = load_sections()
    check(sections)
    from tools.target_times import timings
    times = timings()
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
            from tools import help_picker
        except ImportError:
            print("(interactive picker unavailable: `uv sync` installs "
                  "prompt_toolkit)", file=sys.stderr)
        else:
            rows = (help_picker.section_rows(match, times)
                    if match is not None
                    else help_picker.all_rows(sections, times))
            # The menu reports a task's failure in its own output and a
            # "(exited with status N)" line, so the menu exits 0.
            help_picker.pick_and_run(rows, color=colored)
            return 0

    if match is not None:
        print(render_section(match, width, palette, times))
    else:
        print(render_all(sections, width, palette, times))
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
