#!/usr/bin/env python3
"""The arrow-key and mouse picker behind `make` and `make help`.

make_help.py parses the Makefile into sections of documented targets and
prints them as text. When it is attached to a terminal it hands the same
sections here instead, and this module shows them as a full-screen list:
Up/Down (or PageUp/PageDown, Home/End) move the highlight, Enter runs the
highlighted target, Left or Backspace goes back a level, Esc leaves without
running anything, and typing letters jumps to the first target whose name
starts with them. The mouse works too: a click selects a row, a second
click on the selected row runs it, and the wheel scrolls.

Three views match the three levels of the static listing. Plain `make`
opens the index: the everyday targets, then the sections, where Enter on
a section drills into it. `make help` opens every section expanded, and
`make help style` opens one section. A target whose doc text mentions
`CH=` gets a one-line prompt for the chapter before it runs, since that
is how those targets are scoped.

The picker runs in the terminal's alternate screen, so it vanishes on
exit and the chosen target's output scrolls in the normal buffer. The
command is echoed first (`$ make sweep`), and the picker's exit status is
the target's. MAKEFLAGS and MAKELEVEL are dropped from the child's
environment: `make help` is itself a make recipe, and a sub-make would
otherwise announce "Entering directory" around every run.

Only the interactive loop needs a terminal. `Picker` takes prompt_toolkit's
input and output objects, so the tests drive it with a pipe input and a
dummy output and check which target came back.

Usage: not run directly; make_help.py imports it. `python
tools/make_help.py --pick never` skips it, `--pick always` forces it.
"""
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.input import Input
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.key_binding.key_bindings import NotImplementedOrNone
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.mouse_handlers import MouseHandler
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.output import Output
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

from make_help import MAX_WIDTH, MIN_DOC, PROMOTED, Section, Target, wrap_doc
from tools_config import ROOT

PAGE = 10        # rows a PageUp/PageDown moves
WHEEL = 3        # rows one wheel notch moves

COLOR = Style.from_dict({
    "heading": "bold",
    "slug": "bold ansicyan",
    "target": "ansicyan",
    "dim": "ansibrightblack",
    "selected": "reverse",
    "footer": "reverse",
})
MONO = Style.from_dict({
    "heading": "bold",
    "slug": "bold",
    "selected": "reverse",
    "footer": "reverse",
})


@dataclass(frozen=True)
class Row:
    """One line group in a view. Only target and section rows take the
    highlight; headings and blanks are skipped over."""
    kind: str                       # "heading", "target", "section", "blank"
    label: str = ""                 # target name, section slug, or a heading
    doc: str = ""                   # doc text, or a heading's title
    section: Section | None = None
    target: Target | None = None

    @property
    def selectable(self) -> bool:
        return self.kind in ("target", "section")


def index_rows(sections: Sequence[Section]) -> list[Row]:
    """Plain `make`: the everyday targets, then the sections to drill into."""
    by_name = {t.name: t for s in sections for t in s.targets}
    rows = [Row("heading", doc="Everyday")]
    rows += [Row("target", n, by_name[n].doc, target=by_name[n])
             for n in PROMOTED]
    rows.append(Row("blank"))
    rows.append(Row("heading", doc="Sections (Enter opens one)"))
    rows += [Row("section", s.slug, f"{s.title} ({len(s.listed())})",
                 section=s) for s in sections if s.slug]
    return rows


def section_rows(section: Section) -> list[Row]:
    """`make help style`: one section's heading and its listed targets."""
    rows = [Row("heading", f"{section.slug}:", section.title)]
    rows += [Row("target", t.name, t.doc, target=t) for t in section.listed()]
    return rows


def all_rows(sections: Sequence[Section]) -> list[Row]:
    """`make help`: every section expanded, a blank line between them."""
    rows: list[Row] = []
    for section in sections:
        if not section.slug:
            continue
        if rows:
            rows.append(Row("blank"))
        rows += section_rows(section)
    return rows


class Picker:
    """A full-screen list over one view, with a stack of views behind it
    so Enter on a section and Left afterward round-trip."""

    def __init__(self, sections: Sequence[Section], rows: list[Row], *,
                 color: bool = True, input: Input | None = None,
                 output: Output | None = None) -> None:
        self.sections = sections
        self.rows = rows
        self.stack: list[tuple[list[Row], int]] = []
        self.cursor = self._first_selectable(rows)
        self.prefix = ""
        self.app: Application[Target | None] = Application(
            layout=Layout(HSplit([
                Window(FormattedTextControl(self._body, show_cursor=False),
                       always_hide_cursor=True, wrap_lines=False),
                Window(FormattedTextControl(self._footer), height=1,
                       style="class:footer"),
            ])),
            key_bindings=self._bindings(),
            style=COLOR if color else MONO,
            mouse_support=True, full_screen=True,
            input=input, output=output)

    def run(self) -> Target | None:
        return self.app.run()

    # ---- state

    @staticmethod
    def _first_selectable(rows: list[Row]) -> int:
        return next((i for i, r in enumerate(rows) if r.selectable), 0)

    def _selectable_indexes(self) -> list[int]:
        return [i for i, r in enumerate(self.rows) if r.selectable]

    def move(self, delta: int) -> None:
        """Step the highlight `delta` selectable rows, clamped at the ends."""
        indexes = self._selectable_indexes()
        if not indexes:
            return
        at = indexes.index(self.cursor) if self.cursor in indexes else 0
        self.cursor = indexes[max(0, min(len(indexes) - 1, at + delta))]

    def move_to_end(self, last: bool) -> None:
        indexes = self._selectable_indexes()
        if indexes:
            self.cursor = indexes[-1] if last else indexes[0]

    def jump(self, prefix: str) -> bool:
        """Highlight the first row whose label starts with `prefix`."""
        for i in self._selectable_indexes():
            if self.rows[i].label.lower().startswith(prefix.lower()):
                self.cursor = i
                return True
        return False

    def activate(self) -> Target | None:
        """Enter: a target ends the picker, a section opens its rows."""
        row = self.rows[self.cursor]
        if row.kind == "target":
            return row.target
        if row.kind == "section" and row.section is not None:
            self.stack.append((self.rows, self.cursor))
            self.rows = section_rows(row.section)
            self.cursor = self._first_selectable(self.rows)
            self.prefix = ""
        return None

    def back(self) -> bool:
        """Left/Backspace: return to the view Enter came from, if any."""
        if not self.stack:
            return False
        self.rows, self.cursor = self.stack.pop()
        self.prefix = ""
        return True

    # ---- keys

    def _bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("up")
        def _up(event: KeyPressEvent) -> None:
            self.move(-1)

        @kb.add("down")
        def _down(event: KeyPressEvent) -> None:
            self.move(1)

        @kb.add("pageup")
        def _pageup(event: KeyPressEvent) -> None:
            self.move(-PAGE)

        @kb.add("pagedown")
        def _pagedown(event: KeyPressEvent) -> None:
            self.move(PAGE)

        @kb.add("home")
        def _home(event: KeyPressEvent) -> None:
            self.move_to_end(last=False)

        @kb.add("end")
        def _end(event: KeyPressEvent) -> None:
            self.move_to_end(last=True)

        @kb.add("enter")
        def _enter(event: KeyPressEvent) -> None:
            target = self.activate()
            if target is not None:
                event.app.exit(result=target)

        @kb.add("left")
        def _left(event: KeyPressEvent) -> None:
            if not self.back():
                event.app.exit(result=None)

        @kb.add("backspace")
        def _backspace(event: KeyPressEvent) -> None:
            if self.prefix:
                self.prefix = self.prefix[:-1]
                if self.prefix:
                    self.jump(self.prefix)
            elif not self.back():
                event.app.exit(result=None)

        @kb.add("escape", eager=True)
        def _escape(event: KeyPressEvent) -> None:
            if self.prefix:
                self.prefix = ""
            else:
                event.app.exit(result=None)

        @kb.add("c-c")
        def _interrupt(event: KeyPressEvent) -> None:
            event.app.exit(result=None)

        @kb.add("<any>")
        def _typed(event: KeyPressEvent) -> None:
            text = event.data
            if len(text) != 1 or not text.isprintable() or text == " ":
                return
            if self.jump(self.prefix + text):
                self.prefix += text

        return kb

    # ---- mouse

    def _mouse(self, index: int) -> MouseHandler:
        def handler(event: MouseEvent) -> NotImplementedOrNone:
            if event.event_type == MouseEventType.SCROLL_UP:
                self.move(-WHEEL)
            elif event.event_type == MouseEventType.SCROLL_DOWN:
                self.move(WHEEL)
            elif event.event_type == MouseEventType.MOUSE_UP:
                if not self.rows[index].selectable:
                    return None
                if self.cursor == index:
                    target = self.activate()
                    if target is not None:
                        self.app.exit(result=target)
                else:
                    self.cursor = index
            else:
                return NotImplemented
            return None
        return handler

    # ---- rendering

    def _width(self) -> int:
        return min(self.app.output.get_size().columns or 80, MAX_WIDTH)

    def _body(self) -> StyleAndTextTuples:
        width = self._width()
        label_width = max(
            (len(r.label) for r in self.rows if r.selectable), default=0)
        indent = 2 + label_width + 2
        body = width - indent
        fragments: StyleAndTextTuples = []
        for i, row in enumerate(self.rows):
            handler = self._mouse(i)
            selected = i == self.cursor
            extra = " class:selected" if selected else ""
            if selected:
                fragments.append(("[SetCursorPosition]", ""))
            if row.kind == "blank":
                fragments.append(("", "\n", handler))
                continue
            if row.kind == "heading":
                if row.label:
                    fragments.append(("class:slug", row.label, handler))
                    if row.doc:
                        fragments.append(("", " ", handler))
                fragments.append(("class:heading", row.doc, handler))
                fragments.append(("", "\n", handler))
                continue
            label_style = ("class:target" if row.kind == "target"
                           else "class:slug") + extra
            pad = " " * (label_width - len(row.label))
            lines = (wrap_doc(row.doc, body) if body >= MIN_DOC
                     else [row.doc])
            first = lines[0] if lines else ""
            fragments += [
                (extra.strip(), "  ", handler),
                (label_style, row.label, handler),
                (extra.strip(), f"{pad}  {first}", handler),
                ("", "\n", handler),
            ]
            for line in lines[1:]:
                fragments.append((extra.strip(), " " * indent + line, handler))
                fragments.append(("", "\n", handler))
        return fragments

    def _footer(self) -> StyleAndTextTuples:
        keys = "Up/Down move   Enter run   Left back   Esc quit   type to jump"
        if self.prefix:
            keys += f": {self.prefix}"
        return [("class:footer", f" {keys}")]


def make_command(target: Target, chapter: str = "") -> list[str]:
    """The argv that runs `target`, with CH= appended when given."""
    exe = shutil.which("make") or "make"
    argv = [exe, target.name]
    if chapter:
        argv.append(f"CH={chapter}")
    return argv


def wants_chapter(target: Target) -> bool:
    return "CH=" in target.doc


def run_target(target: Target) -> int:
    """Echo and run `make <target>` as a fresh top-level make."""
    chapter = ""
    if wants_chapter(target):
        chapter = prompt("CH= (Enter for the whole book): ").strip()
    argv = make_command(target, chapter)
    print(f"$ make {' '.join(argv[1:])}", flush=True)
    env = {k: v for k, v in os.environ.items()
           if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
    try:
        return subprocess.call(argv, cwd=ROOT, env=env)
    except OSError as e:
        print(f"could not run make: {e}", file=sys.stderr)
        return 1


def pick_and_run(sections: Sequence[Section], rows: list[Row], *,
                 color: bool = True) -> int:
    """Open the picker on `rows`; run what it returns. 0 if nothing was."""
    target = Picker(sections, rows, color=color).run()
    if target is None:
        return 0
    return run_target(target)
