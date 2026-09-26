#!/usr/bin/env python
"""`tip`: the book's task runner, in place of make.

The tasks live in tools/tasks.py, one decorated function each. This
module holds the machinery they use and the command line:

    tip                        open the picker (a pipe gets the listing)
    tip help [SECTION]         the same, or one section of it
    tip verify                 run a task
    tip verify-ch CH=28        NAME=value sets a variable, as with make
    tip check output-check     several tasks, in order
    tip run-one box_view       a task's positional word (here, F)

`tip` on PATH comes from `uv tool install --editable .` at the repo
root: uv builds a small environment holding prompt_toolkit and this
package, editable, so an edit under tools/ takes effect at once, and
puts a `tip` launcher in its tool directory (`uv tool update-shell`
adds that to PATH). The runner therefore never lives in the project's
.venv, which is what lets `python-upgrade` rebuild that venv while
`tip` is running, the way it could under make. Without the install,
`uv run tip ...` does the same thing from anywhere in the repo, since
`uv sync` installs the same entry point into .venv.

Every step runs in the project's environment through `uv run`, from
the repo root whatever the caller's directory. Each command is echoed before it runs, and the first one to
fail stops the run with its exit status.

A task's `deps` run first, and each task runs at most once per `tip`
invocation, so `tip ty lint` extracts once. That is make's rule for
prerequisites, kept because the tasks were written against it.

Timing: each goal named on the command line ends with a line such as
`tip verify: 1m 32s` (or its exit status and time), and a success is
recorded in build/target_times.json for the listing's time column.
Every step runs with TIP_NESTED=1 in its environment, and a `tip`
started under it prints no line and records nothing, so verify.py and
sweep_checks.py, which time each of their steps themselves, see no
second line per step.
"""
import ast
import difflib
import inspect
import os
import re
import subprocess
import sys
import textwrap
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from tools.config import ROOT

if TYPE_CHECKING:
    from tools.tip_help import Section

# How a step reaches the project's environment. `uv run` syncs .venv
# against uv.lock first when it has drifted, as `$(PY)` did.
UV_RUN: tuple[str, ...] = ("uv", "run")
NESTED = "TIP_NESTED"
INTERRUPTED = 130


class Vars:
    """The `NAME=value` words from the command line.

    A name nobody set reads as "", as an unset make variable does, so a
    task can pass `*v.words("CH")` whether or not CH was given.
    """

    def __init__(self, values: Mapping[str, str] | None = None) -> None:
        self.values = dict(values or {})

    def get(self, name: str, default: str = "") -> str:
        return self.values.get(name) or default

    def words(self, name: str) -> list[str]:
        """The value split on whitespace, as make splits `$(CH)`, so
        `CH="25 28"` passes two arguments."""
        return self.get(name).split()


@dataclass
class Task:
    """One task: its function, its one-line doc, and how to run it.

    `notes` (the function's docstring) is the long-form help the
    picker shows on `?`, and `recipe` is the function body, shown under
    it. `defaults` names what an unset variable means, for the picker's
    prompt; the function applies the default itself. `positional` names
    the variable a bare word after the task sets (`tip run-one x`).
    """
    name: str
    doc: str
    fn: Callable[[Vars], None]
    section: str
    deps: tuple[str, ...] = ()
    secondary: bool = False
    defaults: Mapping[str, str] = field(default_factory=dict)
    positional: str = ""

    @property
    def notes(self) -> str:
        return inspect.cleandoc(self.fn.__doc__ or "")

    @property
    def recipe(self) -> tuple[str, ...]:
        """The function body, less its signature and docstring."""
        try:
            source = textwrap.dedent(inspect.getsource(self.fn))
        except OSError:
            return ()
        tree = ast.parse(source).body[0]
        assert isinstance(tree, ast.FunctionDef)
        body = tree.body
        if self.fn.__doc__:
            body = body[1:]
        lines = source.splitlines()
        return tuple(
            line for stmt in body
            for line in textwrap.dedent("\n".join(
                lines[stmt.lineno - 1:stmt.end_lineno])).splitlines()
            if line.strip() != "pass")


class Registry:
    """Tasks by name, and the listing's layout: each section's title
    and its rows, a row being a task name and whether it is a repeat
    placed there by also(). The module-level section(), task(), and
    also() fill REGISTRY as tools/tasks.py is imported; a test builds
    its own."""

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.layout: list[tuple[str, list[tuple[str, bool]]]] = [("", [])]

    def section(self, title: str) -> None:
        """Start a new section of the listing; later tasks go under it."""
        self.layout.append((title, []))

    def task(self, doc: str, *, deps: Sequence[str] = (),
             secondary: bool = False,
             defaults: Mapping[str, str] | None = None,
             positional: str = "", name: str = "",
             ) -> Callable[[Callable[[Vars], None]], Callable[[Vars], None]]:
        """Register the decorated function as a task in the current
        section.

        The name is the function's with `_` turned into `-` unless
        `name` gives one. `secondary` folds the row out of the listing,
        for a task whose sibling's doc names it.
        """
        def register(fn: Callable[[Vars], None]) -> Callable[[Vars], None]:
            key = name or getattr(fn, "__name__").replace("_", "-")
            if key in self.tasks:
                raise SystemExit(f"tip: task {key!r} is defined twice")
            title, rows = self.layout[-1]
            self.tasks[key] = Task(key, doc, fn, title, tuple(deps),
                                   secondary, dict(defaults or {}),
                                   positional)
            rows.append((key, False))
            return fn
        return register

    def also(self, *names: str) -> None:
        """List tasks defined in other sections here too, at this point
        in the listing."""
        self.layout[-1][1].extend((n, True) for n in names)

    def sections(self) -> list[Section]:
        """The listing: one Section per section() call, in order, with
        each also() name resolved to a copy of its task. A name that no
        task has, or one repeated inside its own section, raises
        SystemExit, since the listing could not show what it says."""
        from tools.tip_help import Section, Target
        found: list[Section] = []
        for title, rows in self.layout:
            slug = title.split()[0].lower() if title else ""
            section = Section(slug, title)
            for key, repeat in rows:
                t = self.tasks.get(key)
                if t is None:
                    raise SystemExit(
                        f"tip: also({key!r}) under {title!r} names no "
                        "task. Check the spelling.")
                if repeat and t.section == title:
                    raise SystemExit(
                        f"tip: also({key!r}) repeats a task inside its "
                        f"own section {title!r}; it is listed there "
                        "already.")
                section.targets.append(Target(
                    t.name, t.doc, t.secondary, notes=t.notes,
                    recipe=t.recipe, prereqs=t.deps, repeat=repeat,
                    defaults=tuple(t.defaults.items())))
            if section.targets:
                found.append(section)
        return found


REGISTRY = Registry()
section = REGISTRY.section
task = REGISTRY.task
also = REGISTRY.also
TASKS = REGISTRY.tasks


def load() -> Registry:
    """Import tools/tasks.py once, filling REGISTRY."""
    if not TASKS:
        import tools.tasks  # noqa: F401
    return REGISTRY


# ---- Steps ----------------------------------------------------------

class StepFailed(Exception):
    """A step exited nonzero; the run stops with its status."""

    def __init__(self, code: int) -> None:
        super().__init__(code)
        self.code = code


def _quote(arg: str) -> str:
    return f'"{arg}"' if not arg or " " in arg else arg


def run(argv: Sequence[str], cwd: Path = ROOT) -> None:
    """Echo `argv` and run it from `cwd` (the repo root unless given);
    raise StepFailed on a nonzero exit."""
    where = "" if cwd == ROOT else f"(in {cwd.relative_to(ROOT)}) "
    print(where + " ".join(_quote(a) for a in argv), flush=True)
    try:
        code = subprocess.call(list(argv), cwd=cwd, env=nested_env())
    except FileNotFoundError:
        print(f"tip: {argv[0]}: command not found", file=sys.stderr)
        code = 127
    if code:
        raise StepFailed(code)


def py(module: str, *args: str) -> None:
    """`python -m module args` in the project environment."""
    run([*UV_RUN, "python", "-m", module, *args])


def tool(name: str, *args: str) -> None:
    """A console script from the project environment (ty, ruff, ...)."""
    run([*UV_RUN, name, *args])


def tip_argv(*words: str) -> list[str]:
    """The argv that runs `tip words...` as a child process from this
    interpreter, for the tools that run tasks one at a time
    (verify.py, sweep_checks.py, verify_targets.py, release.py)."""
    return [sys.executable, "-m", "tools.tip", *words]


def nested_env() -> dict[str, str]:
    """This environment with TIP_NESTED set, so a child `tip` prints
    no timing line and records nothing: the caller times it."""
    return {**os.environ, NESTED: "1"}


def invoke(name: str, v: Vars) -> None:
    """Run another task and its deps, as a recipe's `$(MAKE) name` did."""
    Runner(v).run(name)


class Runner:
    """Runs tasks with their deps, each at most once."""

    def __init__(self, v: Vars, registry: Registry | None = None) -> None:
        self.vars = v
        self.registry = registry or load()
        self.done: set[str] = set()

    def run(self, name: str) -> None:
        if name in self.done:
            return
        t = self.registry.tasks[name]
        for dep in t.deps:
            self.run(dep)
        t.fn(self.vars)
        self.done.add(name)


# ---- Command line ---------------------------------------------------

_ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.DOTALL)


def parse_argv(argv: Iterable[str]) -> tuple[list[str], dict[str, str]]:
    """Split the words into goals and `NAME=value` assignments."""
    goals: list[str] = []
    values: dict[str, str] = {}
    for word in argv:
        if m := _ASSIGN.match(word):
            values[m.group(1)] = m.group(2)
        else:
            goals.append(word)
    return goals, values


def format_seconds(seconds: float) -> str:
    """`12.3s` under a minute, `1m 32s` under an hour, else `1h 02m 05s`."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, rest = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {rest:02.0f}s"
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}h {minutes:02d}m {rest:02.0f}s"


def report(goal: str, code: int, seconds: float) -> str:
    """The one line printed after a goal finishes."""
    elapsed = format_seconds(seconds)
    if code == 0:
        return f"tip {goal}: {elapsed}"
    return f"tip {goal}: failed (exit {code}) after {elapsed}"


def unknown(goal: str) -> str:
    near = difflib.get_close_matches(goal, load().tasks, n=3)
    hint = f" Did you mean {', '.join(near)}?" if near else ""
    return f"tip: no task named {goal!r}.{hint} `tip help` lists them."


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("help", "-h", "--help"):
        from tools.tip_help import main as help_main
        return help_main(args[1:])
    goals, values = parse_argv(args)
    if not goals:
        from tools.tip_help import main as help_main
        return help_main([])
    tasks = load().tasks
    first = tasks.get(goals[0])
    if first and first.positional and len(goals) > 1:
        values.setdefault(first.positional, goals.pop(1))
    for goal in goals:
        if goal not in tasks:
            print(unknown(goal), file=sys.stderr)
            return 2
    timed = not os.environ.get(NESTED)
    runner = Runner(Vars(values))
    for goal in goals:
        sys.stdout.flush()
        start = time.monotonic()
        try:
            runner.run(goal)
            code = 0
        except StepFailed as e:
            code = e.code
        except KeyboardInterrupt:
            code = INTERRUPTED
        seconds = time.monotonic() - start
        if timed:
            print(report(goal, code, seconds), flush=True)
        if code:
            return code
        if timed:
            from tools.target_times import record
            record(goal, seconds)
    return 0


if __name__ == "__main__":
    # Under `python -m tools.tip` this file runs as __main__, a second
    # copy of the module beside the `tools.tip` that tools/tasks.py
    # imports and fills. Calling that copy's main() reads the filled
    # registry; this copy's would be empty.
    import importlib
    raise SystemExit(importlib.import_module("tools.tip").main())
