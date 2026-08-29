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
selected row runs it, and the wheel scrolls. `?` opens full help for the highlighted
target: its doc line, the `#` comment block above it in the
Makefile, and the recipe it runs, in place of the list. Up/Down (and
PageUp/PageDown, Home/End, the wheel) scroll the notes, Enter runs the
target from there, and Esc, `?`, or Backspace returns to the list with
the highlight where it was.

Plain `make` and `make help` open every section; `make help style` opens
one. A target whose doc text mentions a variable (`CH=12`, `VERSION=1.0`,
`ARGS=--help`) gets a one-line prompt for each before it runs, showing
the doc's example; Enter leaves one out. `VERSION=` comes prefilled
with a guess from the release tags: the highest `vX.Y.Z` with its patch
bumped, or its minor bumped when the patch is 0 (after 0.4.2 comes
0.4.3; after 0.4.0 comes 0.5.0), so Enter accepts it and typing
replaces it.

The picker runs in the terminal's alternate screen, so it vanishes on
exit and the chosen target's output scrolls in the normal buffer. The
command is echoed first (`$ make sweep`) and recorded for the shell's
history, so Up-arrow can repeat it without the menu. Two routes, since
a child process cannot add to a shell's live history itself. When
MAKE_MENU_RECORD names a file, the command is appended there and the
`make` wrapper in tools/menu_history.ps1 (PowerShell) or
tools/menu_history.sh (bash, zsh) feeds it to the shell's own history
API after make returns, which is immediate. Otherwise the command is
appended to every shell history file that exists: PSReadLine's
`ConsoleHost_history.txt` (merged in when PSReadLine next writes, so
after your next command), `~/.zsh_history` (extended format when the
file uses it; SHARE_HISTORY or INC_APPEND_HISTORY sees it at once), and
`~/.bash_history` (read at startup, so the next session). No history
file is created, and cmd.exe keeps none. When the target finishes, a
one-line prompt waits: Return reopens the menu with the highlight where
it was and Esc quits. A failing target gets a "(make X exited with
status N)" line first, and Ctrl-C during a run gets "(interrupted: make
X)" rather than a traceback; the menu itself exits 0 either way, since
the target's own output has said what happened and a nonzero status
would only make the outer make add an "Error" line naming the `help`
recipe. MAKEFLAGS
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
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from prompt_toolkit.application import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.input import Input
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import (
    ConditionalContainer, HSplit, Layout, Window)
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
    "recipe": "ansiyellow",
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
        self.notes: Target | None = None     # the target `?` opened
        self.notes_scroll = 0
        self.window = Window(
            FormattedTextControl(self._body, show_cursor=False),
            always_hide_cursor=True, wrap_lines=False)
        self.notes_window = Window(
            FormattedTextControl(self._notes_body, show_cursor=False),
            always_hide_cursor=True, wrap_lines=False)
        showing_notes = Condition(lambda: self.notes is not None)
        self.app: Application[Target | None] = Application(
            layout=Layout(HSplit([
                ConditionalContainer(self.window, ~showing_notes),
                ConditionalContainer(self.notes_window, showing_notes),
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

    def open_notes(self) -> None:
        """Show the highlighted target's notes; nothing if none is."""
        target = self.chosen()
        if target is not None:
            self.notes = target
            self.notes_scroll = 0

    def close_notes(self) -> None:
        self.notes = None

    def scroll_notes(self, delta: int) -> None:
        """Move the notes view `delta` lines, clamped at the top; the
        window clamps the bottom itself when it renders."""
        self.notes_scroll = max(0, self.notes_scroll + delta)

    def scroll_notes_to_end(self, last: bool) -> None:
        if last and self.notes is not None:
            self.notes_scroll = len(notes_lines(self.notes, self._width()))
        else:
            self.notes_scroll = 0

    # ---- keys

    def _bindings(self) -> KeyBindings:
        kb = KeyBindings()

        def step(delta: int) -> None:
            if self.notes is None:
                self.move(delta)
            else:
                self.scroll_notes(delta)

        def to_end(last: bool) -> None:
            if self.notes is None:
                self.move_to_end(last)
            else:
                self.scroll_notes_to_end(last)

        @kb.add("up")
        def _up(event: KeyPressEvent) -> None:
            step(-1)

        @kb.add("down")
        def _down(event: KeyPressEvent) -> None:
            step(1)

        @kb.add("pageup")
        def _pageup(event: KeyPressEvent) -> None:
            step(-PAGE)

        @kb.add("pagedown")
        def _pagedown(event: KeyPressEvent) -> None:
            step(PAGE)

        @kb.add("home")
        def _home(event: KeyPressEvent) -> None:
            to_end(last=False)

        @kb.add("end")
        def _end(event: KeyPressEvent) -> None:
            to_end(last=True)

        @kb.add("enter")
        def _enter(event: KeyPressEvent) -> None:
            target = self.chosen()
            if target is not None:
                event.app.exit(result=target)

        @kb.add("?")
        def _notes(event: KeyPressEvent) -> None:
            if self.notes is None:
                self.open_notes()
            else:
                self.close_notes()

        @kb.add("backspace")
        def _backspace(event: KeyPressEvent) -> None:
            if self.notes is not None:
                self.close_notes()
            elif self.query:
                self.search(self.query[:-1])

        @kb.add("escape", eager=True)
        def _escape(event: KeyPressEvent) -> None:
            if self.notes is not None:
                self.close_notes()
            elif self.query:
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
            if self.notes is not None:
                return              # the notes view does not search
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

    def _notes_mouse(self, event: MouseEvent) -> "NotImplementedOrNone":
        if event.event_type == MouseEventType.SCROLL_UP:
            self.scroll_notes(-WHEEL)
        elif event.event_type == MouseEventType.SCROLL_DOWN:
            self.scroll_notes(WHEEL)
        else:
            return NotImplemented
        return None

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

    def _notes_body(self) -> StyleAndTextTuples:
        """The open target's notes as fragments, scrolled to
        `notes_scroll`: the cursor marker sits on that line so the
        window keeps it in view, the same trick `_body` uses for the
        highlight's heading."""
        if self.notes is None:
            return []
        lines = notes_lines(self.notes, self._width())
        self.notes_scroll = min(self.notes_scroll, max(0, len(lines) - 1))
        fragments: StyleAndTextTuples = []
        for i, (style, text) in enumerate(lines):
            if i == self.notes_scroll:
                fragments.append(("[SetCursorPosition]", ""))
            fragments.append((style, text, self._notes_mouse))
            fragments.append(("", "\n", self._notes_mouse))
        self.notes_window.vertical_scroll = self.notes_scroll
        return fragments

    def _footer(self) -> StyleAndTextTuples:
        if self.notes is not None:
            keys = (f"{self.notes.name}:   Up/Down scroll   Enter run   "
                    "Esc back")
        elif self.query:
            n = len(self._selectable_indexes())
            hits = f"{n} match" + ("" if n == 1 else "es")
            keys = (f"Search: {self.query}   ({hits})   "
                    "Enter run   Esc clear")
        else:
            keys = ("Up/Down move   Enter run   ? help   Esc quit   "
                    "type to search")
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


NOTES_INDENT = "  "
RECIPE_INDENT = "    "


def notes_lines(target: Target, width: int) -> list[tuple[str, str]]:
    """What `?` shows for `target`, as (style, text) lines fitting
    `width`: the name and doc line, the Makefile's comment block above
    the target rewrapped paragraph by paragraph (a paragraph with an
    indented line is kept as written, since its layout is deliberate),
    the prerequisite targets under "Prerequisites:", and the recipe
    under "Runs:". A target with none of the three says so.
    """
    body = max(MIN_DOC, width - len(NOTES_INDENT))
    lines: list[tuple[str, str]] = [("class:slug", target.name)]
    lines += [("", NOTES_INDENT + text)
              for text in wrap_doc(target.doc, body)]
    for paragraph in target.notes.split("\n\n"):
        raw = paragraph.splitlines()
        if not raw:
            continue
        lines.append(("", ""))
        if any(line[:1].isspace() for line in raw):
            wrapped = raw
        else:
            wrapped = wrap_doc(" ".join(line.strip() for line in raw), body)
        lines += [("", NOTES_INDENT + text) for text in wrapped]
    if target.prereqs:
        lines.append(("", ""))
        lines.append(("class:heading", "Prerequisites:"))
        lines += [("class:recipe", RECIPE_INDENT + text)
                  for text in wrap_doc(" ".join(target.prereqs),
                                       max(MIN_DOC, width - len(RECIPE_INDENT)))]
    if target.recipe:
        lines.append(("", ""))
        lines.append(("class:heading", "Runs:"))
        lines += [("class:recipe", RECIPE_INDENT + command)
                  for command in target.recipe]
    if not (target.notes or target.prereqs or target.recipe):
        lines.append(("", ""))
        lines.append(("class:dim", NOTES_INDENT
                      + "(no notes, prerequisites, or recipe in the Makefile)"))
    return lines


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


_VARIABLE = re.compile(r"\b([A-Z][A-Z_]*)=([^\s,;)]*)")

# Variables a target's doc mentions that the menu should not ask about:
# `make all ARGS=--help` only lists what `all` would run, which is not
# what someone picking `all` from a menu wants to be asked on every run.
NO_PROMPT: dict[str, frozenset[str]] = {
    "all": frozenset({"ARGS"}),
}


def variables(target: Target) -> list[tuple[str, str]]:
    """The `NAME=example` variables a target's doc mentions, in order,
    each once, minus NO_PROMPT's: what to prompt for before running it."""
    skip = NO_PROMPT.get(target.name, frozenset())
    found: dict[str, str] = {}
    for name, example in _VARIABLE.findall(target.doc):
        if name not in skip:
            found.setdefault(name, example)
    return list(found.items())


def make_command(target: Target,
                 values: Mapping[str, str] | None = None) -> list[str]:
    """The argv that runs `target`, with each non-empty `NAME=value`
    from `values` appended in order."""
    exe = shutil.which("make") or "make"
    argv = [exe, target.name]
    for name, value in (values or {}).items():
        if value:
            argv.append(f"{name}={value}")
    return argv


def ask_variables(target: Target) -> dict[str, str]:
    """Prompt for each variable the target's doc mentions, prefilled
    with a guess where one exists."""
    values: dict[str, str] = {}
    for name, example in variables(target):
        guess = guess_value(name)
        if guess:
            hint = "Enter accepts"
            example_hint = ""
        else:
            hint = ("Enter for the whole book" if name == "CH"
                    else "Enter to skip")
            example_hint = f"e.g. {example}, " if example else ""
        values[name] = prompt(f"{name}= ({example_hint}{hint}): ",
                              default=guess).strip()
    return values


def guess_value(name: str) -> str:
    """A prefill for a variable's prompt, or "" when there is none."""
    if name == "VERSION":
        return next_version(release_tags()) or ""
    return ""


def release_tags() -> list[str]:
    """Every git tag in the repo, or none if git is unavailable."""
    try:
        out = subprocess.run(["git", "tag", "--list"], cwd=ROOT,
                             capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    return out.stdout.split()


_RELEASE_TAG = re.compile(r"^v?(\d+(?:\.\d+)*)$")


def next_version(tags: Iterable[str]) -> str | None:
    """The release after the highest `vX.Y.Z` among `tags`: the patch
    bumped, or the minor bumped and the patch zeroed when the patch is
    0. Two-part versions count as patch 0 (1.0 -> 1.1). None with no
    version tag."""
    versions: list[tuple[int, ...]] = []
    for tag in tags:
        if m := _RELEASE_TAG.match(tag.strip()):
            versions.append(tuple(int(n) for n in m.group(1).split(".")))
    if not versions:
        return None
    last = max(versions)
    parts = list(last) + [0] * (3 - len(last)) if len(last) < 3 else list(last)
    if parts[2] == 0:
        parts[1] += 1
    else:
        parts[2] += 1
    if len(last) < 3:
        parts = parts[:len(last)]
    return ".".join(str(n) for n in parts)


def history_files(env: Mapping[str, str] | None = None,
                  home: Path | None = None) -> list[Path]:
    """The shell history files a command can be appended to: each
    well-known location that already exists, in a stable order."""
    settings: Mapping[str, str] = os.environ if env is None else env
    home = Path.home() if home is None else home
    candidates: list[Path] = []
    if appdata := settings.get("APPDATA"):
        candidates.append(Path(appdata) / "Microsoft" / "Windows"
                          / "PowerShell" / "PSReadLine"
                          / "ConsoleHost_history.txt")
    candidates.append(home / ".local" / "share" / "powershell"
                      / "PSReadLine" / "ConsoleHost_history.txt")
    if histfile := settings.get("HISTFILE"):
        candidates.append(Path(histfile))
    candidates += [home / ".bash_history", home / ".zsh_history"]
    return [p for p in dict.fromkeys(candidates) if p.is_file()]


def record_history(command: str, files: Iterable[Path],
                   now: float | None = None) -> list[Path]:
    """Append `command` to each history file; the ones that took it."""
    written: list[Path] = []
    for path in files:
        line = command
        if path.name == ".zsh_history" and _zsh_extended(path):
            stamp = int(time.time() if now is None else now)
            line = f": {stamp}:0;{command}"
        try:
            with path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            continue
        written.append(path)
    return written


def _zsh_extended(path: Path) -> bool:
    """Whether a zsh history file uses EXTENDED_HISTORY's `: ts:0;cmd`."""
    try:
        with path.open("rb") as f:
            tail = f.read()[-4096:]
    except OSError:
        return False
    lines = [ln for ln in tail.splitlines() if ln.strip()]
    return bool(lines) and lines[-1].startswith(b": ")


RECORD_VAR = "MAKE_MENU_RECORD"


def record_command(command: str, env: Mapping[str, str] | None = None,
                   home: Path | None = None) -> list[Path]:
    """Record `command` for the shell: into the file MAKE_MENU_RECORD
    names when a wrapper set it, else into the history files. The
    paths written."""
    settings: Mapping[str, str] = os.environ if env is None else env
    if record := settings.get(RECORD_VAR):
        path = Path(record)
        try:
            with path.open("a", encoding="utf-8") as f:
                f.write(command + "\n")
        except OSError:
            return []
        return [path]
    return record_history(command, history_files(settings, home))


INTERRUPTED = 130       # the conventional exit status after Ctrl-C


def run_target(target: Target) -> int:
    """Echo and run `make <target>` as a fresh top-level make, after
    recording the command for the shell history.

    Ctrl-C reaches every process on the console at once, so the target
    and its make are already stopping when it lands here as a
    KeyboardInterrupt; a one-line note replaces the traceback and the
    menu's Return/Esc prompt follows as usual. Ctrl-C at a variable
    prompt cancels the run before it starts.
    """
    try:
        values = ask_variables(target)
    except KeyboardInterrupt:
        print("\n(cancelled)")
        return INTERRUPTED
    argv = make_command(target, values)
    command = f"make {' '.join(argv[1:])}"
    record_command(command)
    print(f"$ {command}", flush=True)
    env = {k: v for k, v in os.environ.items()
           if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
    try:
        status = subprocess.call(argv, cwd=ROOT, env=env)
    except KeyboardInterrupt:
        print(f"\n(interrupted: {command})")
        return INTERRUPTED
    except OSError as e:
        print(f"could not run make: {e}", file=sys.stderr)
        return 1
    if status:
        print(f"({command} exited with status {status})")
    return status


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

    try:
        return session(pick, run_target, ask_return_or_esc)
    except KeyboardInterrupt:
        # Inside the picker and the prompts Ctrl-C is a key, handled
        # there; this catches one that lands between them.
        print()
        return INTERRUPTED
