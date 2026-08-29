#!/usr/bin/env python3
"""The arrow-key and mouse picker behind `make` and `make help`.

make_help.py parses the Makefile into sections of documented targets and
prints them as text. When it is attached to a terminal it hands the same
sections here instead, and this module shows them as a full-screen list:
Up/Down (or PageUp/PageDown, Home/End) move the highlight, Enter runs the
highlighted target, and Esc leaves without running anything. Typing
searches: the list narrows to the targets whose name or doc text contains
what has been typed (`/` also starts a search, for the habit), the
matched text is underlined in the names, the highlight lands on the first
name match when there is one, Backspace edits the query, and Esc clears
it. The mouse works too: a click selects a row, a second click on the
selected row runs it, and the wheel scrolls.

Plain `make` and `make help` open every section; `make help style` opens
one. A target whose doc text mentions `CH=` gets a one-line prompt for
the chapter before it runs, since that is how those targets are scoped.

The picker runs in the terminal's alternate screen, so it vanishes on
exit and the chosen target's output scrolls in the normal buffer. The
command is echoed first (`$ make sweep`). When the target finishes, a
one-line prompt waits: Return reopens the menu with the highlight where
it was, Esc quits, and the exit status is the last target's. MAKEFLAGS
and MAKELEVEL are dropped from the child's environment: `make help` is
itself a make recipe, and a sub-make would otherwise announce "Entering
directory" around every run.

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
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.input import Input
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.mouse_handlers import MouseHandler
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.output import Output
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

from make_help import MAX_WIDTH, MIN_DOC, Section, Target, wrap_doc
from tools_config import ROOT

if TYPE_CHECKING:
    # A type alias prompt_toolkit defines only for checkers.
    from prompt_toolkit.key_binding.key_bindings import NotImplementedOrNone

PAGE = 10        # rows a PageUp/PageDown moves
WHEEL = 3        # rows one wheel notch moves

COLOR = Style.from_dict({
    "heading": "bold",
    "slug": "bold ansicyan",
    "target": "ansicyan",
    "match": "underline",
    "dim": "ansibrightblack",
    "selected": "reverse",
    "footer": "reverse",
})
MONO = Style.from_dict({
    "heading": "bold",
    "slug": "bold",
    "match": "underline",
    "selected": "reverse",
    "footer": "reverse",
})


@dataclass(frozen=True)
class Row:
    """One line group in a view. Only target rows take the highlight;
    headings and blanks are skipped over."""
    kind: str                       # "heading", "target", "blank"
    label: str = ""                 # target name, or a heading's slug
    doc: str = ""                   # doc text, or a heading's title
    target: Target | None = None

    @property
    def selectable(self) -> bool:
        return self.kind == "target"


def section_rows(section: Section) -> list[Row]:
    """`make help style`: one section's heading and its listed targets."""
    rows = [Row("heading", f"{section.slug}:", section.title)]
    rows += [Row("target", t.name, t.doc, target=t) for t in section.listed()]
    return rows


def all_rows(sections: Sequence[Section]) -> list[Row]:
    """`make` and `make help`: every section, a blank line between."""
    rows: list[Row] = []
    for section in sections:
        if not section.slug:
            continue
        if rows:
            rows.append(Row("blank"))
        rows += section_rows(section)
    return rows


class Picker:
    """A full-screen list over `rows`; `run()` returns the chosen target."""

    def __init__(self, rows: list[Row], *, color: bool = True,
                 cursor: int | None = None, input: Input | None = None,
                 output: Output | None = None) -> None:
        self.all_rows = rows
        self.rows = rows
        self.cursor = (cursor if cursor is not None
                       else self._first_selectable(rows))
        self.query = ""
        self.window = Window(
            FormattedTextControl(self._body, show_cursor=False),
            always_hide_cursor=True, wrap_lines=False)
        self.app: Application[Target | None] = Application(
            layout=Layout(HSplit([
                self.window,
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

    def search(self, query: str) -> None:
        """Narrow the list to the targets matching `query` (name or doc,
        case-insensitive), keeping their section headings. The highlight
        stays on the current target if it still shows, else moves to the
        first name match, else the first match."""
        current = self.rows[self.cursor] if self.rows else None
        self.query = query
        self.rows = filter_rows(self.all_rows, query)
        indexes = self._selectable_indexes()
        if current in self.rows and current.selectable:
            self.cursor = self.rows.index(current)
        elif indexes:
            named = [i for i in indexes
                     if query.lower() in self.rows[i].label.lower()]
            self.cursor = (named or indexes)[0]
        else:
            self.cursor = 0

    def chosen(self) -> Target | None:
        return self.rows[self.cursor].target

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
            target = self.chosen()
            if target is not None:
                event.app.exit(result=target)

        @kb.add("backspace")
        def _backspace(event: KeyPressEvent) -> None:
            if self.query:
                self.search(self.query[:-1])

        @kb.add("escape", eager=True)
        def _escape(event: KeyPressEvent) -> None:
            if self.query:
                self.search("")
            else:
                event.app.exit(result=None)

        @kb.add("c-c")
        def _interrupt(event: KeyPressEvent) -> None:
            event.app.exit(result=None)

        @kb.add("<any>")
        def _typed(event: KeyPressEvent) -> None:
            text = event.data
            if len(text) != 1 or not text.isprintable():
                return
            if text == "/" and not self.query:
                return              # `/` opens the search; it is already open
            if text == " " and not self.query:
                return              # a stray space is not a search
            self.search(self.query + text)

        return kb

    # ---- mouse

    def _mouse(self, index: int) -> MouseHandler:
        def handler(event: MouseEvent) -> "NotImplementedOrNone":
            if event.event_type == MouseEventType.SCROLL_UP:
                self.move(-WHEEL)
            elif event.event_type == MouseEventType.SCROLL_DOWN:
                self.move(WHEEL)
            elif event.event_type == MouseEventType.MOUSE_UP:
                if not self.rows[index].selectable:
                    return None
                if self.cursor == index:
                    self.app.exit(result=self.chosen())
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
        """The list as fragments; also caps the window's scroll at the
        highlighted target's section heading.

        prompt_toolkit scrolls only as far as it must to keep the cursor
        row on screen, so after arrowing past the first screen and then
        searching, the highlight could sit on the top line with its
        heading just above it. Capping the scroll here, before the
        window computes its own, keeps the heading visible whenever the
        highlight is. Line numbers are counted as the rows render, since
        a wrapped doc takes more than one.
        """
        width = self._width()
        label_width = max(
            (len(r.label) for r in self.rows if r.selectable), default=0)
        indent = 2 + label_width + 2
        body = width - indent
        fragments: StyleAndTextTuples = []
        line = heading_line = cursor_heading = 0
        for i, row in enumerate(self.rows):
            handler = self._mouse(i)
            selected = i == self.cursor
            extra = " class:selected" if selected else ""
            if selected:
                fragments.append(("[SetCursorPosition]", ""))
                cursor_heading = heading_line
            if row.kind == "blank":
                fragments.append(("", "\n", handler))
                line += 1
                continue
            if row.kind == "heading":
                heading_line = line
                if row.label:
                    fragments.append(("class:slug", row.label, handler))
                    if row.doc:
                        fragments.append(("", " ", handler))
                fragments.append(("class:heading", row.doc, handler))
                fragments.append(("", "\n", handler))
                line += 1
                continue
            label_style = "class:target" + extra
            pad = " " * (label_width - len(row.label))
            lines = (wrap_doc(row.doc, body) if body >= MIN_DOC
                     else [row.doc])
            first = lines[0] if lines else ""
            fragments.append((extra.strip(), "  ", handler))
            for text, hit in split_match(row.label, self.query):
                style = label_style + (" class:match" if hit else "")
                fragments.append((style, text, handler))
            fragments += [
                (extra.strip(), f"{pad}  {first}", handler),
                ("", "\n", handler),
            ]
            for more in lines[1:]:
                fragments.append((extra.strip(), " " * indent + more, handler))
                fragments.append(("", "\n", handler))
            line += len(lines) or 1
        self.window.vertical_scroll = min(
            self.window.vertical_scroll, cursor_heading)
        return fragments

    def _footer(self) -> StyleAndTextTuples:
        if self.query:
            n = len(self._selectable_indexes())
            hits = f"{n} match" + ("" if n == 1 else "es")
            keys = (f"Search: {self.query}   ({hits})   "
                    "Enter run   Esc clear")
        else:
            keys = "Up/Down move   Enter run   Esc quit   type to search"
        return [("class:footer", f" {keys}")]


def filter_rows(rows: list[Row], query: str) -> list[Row]:
    """The rows whose target matches `query`, under their headings, with
    a blank between sections; every row when `query` is empty."""
    if not query:
        return rows
    needle = query.lower()
    kept: list[Row] = []
    group: list[Row] = []       # the current heading plus its matches
    for row in [*rows, Row("blank")]:
        if row.kind == "heading":
            group = [row]
        elif row.kind == "blank":
            if len(group) > 1:
                if kept:
                    kept.append(Row("blank"))
                kept += group
            group = []
        elif needle in row.label.lower() or needle in row.doc.lower():
            group.append(row)
    return kept


def split_match(label: str, query: str) -> list[tuple[str, bool]]:
    """`label` cut into (text, is_match) pieces around each occurrence
    of `query`, case-insensitive; one unmatched piece when nothing hits."""
    if not query:
        return [(label, False)]
    pieces: list[tuple[str, bool]] = []
    low, needle, i = label.lower(), query.lower(), 0
    while (j := low.find(needle, i)) != -1:
        if j > i:
            pieces.append((label[i:j], False))
        pieces.append((label[j:j + len(needle)], True))
        i = j + len(needle)
    if i < len(label):
        pieces.append((label[i:], False))
    return pieces


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


def ask_return_or_esc(input: Input | None = None,
                      output: Output | None = None) -> bool:
    """After a target runs: True on Return (back to the menu), False on
    Esc or Ctrl-C (quit). Other keys are ignored."""
    kb = KeyBindings()

    @kb.add("enter")
    def _again(event: KeyPressEvent) -> None:
        event.app.exit(result=True)

    @kb.add("escape", eager=True)
    @kb.add("c-c")
    def _quit(event: KeyPressEvent) -> None:
        event.app.exit(result=False)

    hint = "Return: back to the menu   Esc: quit"
    app: Application[bool] = Application(
        layout=Layout(Window(FormattedTextControl(hint), height=1)),
        key_bindings=kb, erase_when_done=True, input=input, output=output)
    return app.run()


def session(pick: Callable[[int | None], tuple[Target | None, int]],
            run: Callable[[Target], int],
            ask: Callable[[], bool]) -> int:
    """The menu loop, with its three interactions injected so it can be
    tested without a terminal or a make.

    `pick(cursor)` shows the menu highlighted at `cursor` (None for the
    first target) and returns the chosen target (None to quit) and the
    highlight to restore; `run` runs a target and returns its status;
    `ask` returns True to reopen the menu. The result is the last run's
    status, or 0 if nothing ran.
    """
    status = 0
    cursor: int | None = None
    while True:
        target, cursor = pick(cursor)
        if target is None:
            return status
        status = run(target)
        if not ask():
            return status


def pick_and_run(rows: list[Row], *, color: bool = True) -> int:
    """Open the picker on `rows` and loop: run the choice, wait for
    Return or Esc, reopen or quit."""
    def pick(cursor: int | None) -> tuple[Target | None, int]:
        picker = Picker(rows, color=color, cursor=cursor)
        return picker.run(), picker.cursor

    return session(pick, run_target, ask_return_or_esc)
