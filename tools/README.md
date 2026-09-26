# Book tooling

Scripts that keep the book honest: extract every code example from the
Markdown and run it, render the Markdown into a static HTML site, and gate
both in CI.

## The idea

The Markdown chapters in `Chapters/` are the source of truth for the book's
prose *and* its code. A fenced block becomes an extractable file when its first
non-blank line is a path comment naming the file, relative to its chapter:

````markdown
```python
# trace.py
def trace(func): ...
```
````

The file is written under a directory named for the chapter it appears in (the
Markdown file's stem). So `# trace.py` in `14_Techniques--Decorators.md` is
extracted to `14_Techniques--Decorators/trace.py`. The slug carries no chapter prefix; the extractor adds
it. A slug may include a sub-path (`# mouse/mouse_action.py`) to group related
files within one chapter. Renaming or renumbering a chapter therefore moves its
example folder to match. Blocks without such a first line are illustrative
fragments and are ignored. Data files (`.txt`, `.dat`) tagged the same way are
extracted too, so examples that read them can run.

`Examples/` is the curated copy committed to git. `build/examples/` is a
throwaway tree (git-ignored) regenerated from the Markdown for running.

`Solutions/*.md` (worked exercise answers) go through the exact same
extract/validate/ty/ruff/pytest pipeline, via a parallel set of tools and
`tip` targets described in [extract_solutions.py](#extract_solutions.py)
below. The one difference is that a Solutions code block is
**self-contained**: it redeclares whatever small piece of book context it
needs (a class, a helper function) rather than importing from `Examples/`,
so the two trees never couple and a change to a book example cannot silently
break a Solutions file.

## How this directory is laid out

`tools/` holds four kinds of thing, told apart by name:

* **Entry points** (`extract_examples.py`, `validate_output.py`, ...) run
  as `uv run python -m tools.<name>` from the repository root, almost
  always through a `tip` target. Each one's module docstring is its
  reference, and `--help` prints it. `tools/` is a package, so `-m` is
  the only form that works: run as a bare script, a module cannot find
  its siblings.
* **Shared libraries** (`config.py`, `repo.py`, `markdown.py`, ...) define
  no command and are only imported, as `tools.config` and so on. The
  package is what keeps them apart from the book: `validate_output.py`
  execs every book listing in its own process, and chapter 24 has a
  listing called `config.py`, so a bare `config` module on `sys.path`
  would be found by that chapter's `import config` through the
  `sys.modules` cache. `tools.config` is a key no listing can collide
  with. See `tools/repo.py`'s docstring.
* **`data/`** holds the word lists, allowlists, and glob lists the checks
  read (`wordlist.txt`, `norun.txt`, `banned_phrases.txt`, ...), so this
  directory lists code and nothing else.
* **`tests/`** holds the harness's own unit tests, run by `tip tools-test`
  and as the first step of `tip gate`. They are separate from the book's
  example tests, which live in the chapters and run from `build/examples/`.

The libraries are worth knowing before reading any entry point, because
together they are why a check is usually thirty lines:

| Module | What it provides |
| --- | --- |
| `config.py` | Paths and the convention regexes. Constants only, no behavior. |
| `repo.py` | Small shared behaviors: walking `Chapters/`, reading a glob list, running a subprocess. |
| `markdown.py` | `Document.parse()`: one parse of a Markdown file into lines, fenced `Block`s, and headings. |
| `prose.py` | Which lines are prose, and which inline spans (code, footnotes) to ignore within one. |
| `pycode.py` | Walking fenced Python and finding a real `#` comment in a line, string-aware. |
| `report.py` | `Finding` and `Check`, the shape every check produces and the reporter that prints them. |
| `extract.py` | Routing blocks to paths, conflict detection, and writing or checking a tree. |

A check is a function from a `Document` to `Finding`s, which is what lets
`check_all.py` run all of them over one parse, and what lets a test build a
document in memory with no filesystem at all.

This README covers the tools you invoke by hand and the conventions behind
them. It is deliberately not an inventory of all forty files: `tip help`
lists every target, and each script's `--help` prints its own docstring.

## Commands

Tooling is managed by [uv](https://docs.astral.sh/uv/). Apart from putting
`tip` on PATH (below), there is no setup
step: the first `tip` target you run creates `.venv` with the dev tools
pinned by `uv.lock`, since every target goes through `uv run`. To build
the environment without running a target:

```
uv sync          # optional: the first `uv run` or `tip` target does the same
```

Run `tip tools-check` to confirm everything resolved (`uv`, `ty`,
`ruff`, `pytest`); `tip tools-check-full` also checks `pandoc`, `typst`,
`vale`, and `gh`, needed only for the site, EPUB, PDF, prose, and release
targets, and prints the install commands for anything missing. See
[check_tools.py](#check_tools.py) below. If something you expect to work
doesn't, `tip doctor` (see [doctor.py](#doctor.py)) checks for the couple
of environment problems that look like a bug in the book but aren't.

`tip` is the book's task runner, a Python script in this directory.
To put it on PATH, on Windows, macOS, or Linux, run this at the
repository root:

```
uv tool install --editable .
uv tool update-shell   # only if uv's tool directory is not on PATH yet
```

The runner lives in its own tool environment, outside `.venv`, so
`tip python-upgrade` can rebuild `.venv` while `tip` runs. Without the
install, `uv run tip ...` works inside the repository, because `uv sync`
installs the same `tip` entry point into `.venv`.

Run targets with `tip` (they go through `uv run`); `tip help` prints the
complete, categorized list, generated from the task registry in
`tools/tasks.py` so it never
drifts out of date (see [tip_help.py](#tip_help.py) below). Every target
named on the command line
prints its wall-clock time when it finishes (`tip verify: 1m 32s`);
[tip.py](#tip.py) explains the mechanism. The everyday ones:

```
tip verify     # every fixer, refresh markers, sync Examples/ and SolutionsCode/, then the full gate but the site
tip ci         # the full local gate: check, ty, ruff, run, pytest, site
```

`tip verify` is the loop to repeat after editing a chapter: every
mutating fixer (the comment-style fixers, import sorting, blank-line
cleanup), then a refresh of the `#:` output markers in both trees, then
a sync of your Markdown changes out to `Examples/` and `SolutionsCode/`
(so the drift check passes), the figure gallery, then every gate except
the site build; see [verify.py](#verify.py) below. It refreshes markers
(`output`) *before* syncing, on purpose: `gate`/`solutions-gate` also
refresh markers, but only after whatever sync step ran ahead of them
already copied the Markdown, so a marker that needed fixing would
otherwise stay one sync behind until the *next* run caught it up. `tip
ci` runs the gate (with site) without syncing first, so it still fails
on drift, the way GitHub Actions does; `tip verify site` is the same
run with the sync.

## tip_help.py

Prints the `tip help` listing, or in a terminal hands it to
`help_picker.py` (below) so a target can be chosen with the arrow keys
or the mouse and run with Enter. In `tools/tasks.py`, each
`@task("one-line doc")` function becomes one entry; a
`section("Title")` call starts a new section. Bare `tip` and `tip help` show every section;
`tip help NAME` shows one, where `NAME` is the first word of that
section's heading, lowercased (each heading leads with it, as in
`style: Style gates`). A pipe, a CI run (`CI` set), or `--pick never`
gets the static text.
`secondary=True` on a `@task` marks a target secondary: documented and smoke-tested,
but folded out of the listing because a sibling's doc text names it
(each `fix-*` under the check it repairs). An `also("name", ...)` call
repeats targets defined in other sections into the section it sits in,
at that point, so a target that belongs to two jobs (`sync` is an
everyday step and a code-examples step) is listed under both; the flat
`entries()` view reports it once, so the smoke test runs it once. The
sections run from the everyday loop down to setup and cleanup, most
used first.

Doc text wraps to the terminal width (capped at 100, falling back to 80
when the output is piped), with continuation lines indented under the doc
column so the target names stay in one column. A backticked command and a
hyphenated target name both wrap as one unit.

A time column sits between the name and the doc: how long the target
took the last time it passed on this machine (`56s`, `1m 32s`), or, for
a target this machine has not run, its tier from the committed
`tools/data/target_tiers.txt` (`quick`, `normal`, `long`, `very long`).
The column is colored by tier, green for quick, yellow for long, red for
very long, and a legend closes the listing. [target_times.py](#target_times.py)
below has the sources and the thresholds.

```
tip              # every section's targets (so does `tip help`)
tip help style   # one section's targets

uv run python -m tools.tip_help --width 72   # wrap to a fixed width
uv run python -m tools.tip_help --pick never # static text in a terminal
```

## help_picker.py

The interactive side of `tip help`, built on `prompt_toolkit` (a dev
dependency; without it `tip help` falls back to the static listing and
says so). A full-screen list of the same sections and doc text:
Up/Down, PageUp/PageDown, Home/End move the highlight, Enter runs the
highlighted target, and Esc leaves without running anything. Typing
searches: the list narrows to the targets whose name or description
contains the text (`/` also starts a search), the match is underlined in
the names, the highlight lands on the first name match, Backspace edits
the query, and Esc clears it. A mouse click selects a row, a second
click on the selected row runs it, and the wheel scrolls. `?` replaces
the list with the highlighted target's full help: its doc line, the
task function's docstring (the long-form
help the one-line summary condenses), and the recipe it runs (the
function's body). Up/Down
and the wheel scroll the notes, Enter runs the target from there, and
Esc, `?`, or Backspace returns to the list with the highlight where it
was. A target with no docstring shows only its doc and recipe, so
writing the docstring is what makes `?` useful for a target.
`tip` and `tip help` open every section; `tip help style` opens one.

The chosen target runs as a fresh top-level `tip`
(`python -m tools.tip`, so it prints its own timing line), after echoing the
command; a target whose doc mentions a variable (`CH=12`,
`VERSION=1.0`, `ARGS=--help`) first prompts for each, showing the doc's
example, with Enter leaving it out (for `CH=`, the whole book).
`VERSION=` comes prefilled from the release tags: the highest `vX.Y.Z`
with its patch bumped, or its minor bumped when the patch is 0 (after
0.4.2 comes 0.4.3; after 0.4.0 comes 0.5.0), so Enter accepts the guess
and typing replaces it. The command line (`tip sweep`,
`tip check-ch CH=12`) is also recorded for the shell's history, so
Up-arrow repeats it without the menu. For that to show on the very
next Up, source the `tip` wrapper for your shell from your profile:

```
. C:\git\ThinkingInPython\tools\menu_history.ps1    # PowerShell, in $PROFILE
. /c/git/ThinkingInPython/tools/menu_history.sh     # bash or zsh, in ~/.bashrc or ~/.zshrc
```

The wrapper names a scratch file in `TIP_MENU_RECORD`, runs the real
`tip`, and feeds what the menu wrote there to the shell's own history
call (PSReadLine's `AddToHistory`, bash's `history -s`, zsh's `print
-s`). A child process cannot do that itself, which is why the wrapper
exists. Without it, the menu appends the command to every shell history
file that exists instead, and the shell picks that up on its own
schedule: PSReadLine merges other writers' lines when it next writes, so
after your next command; zsh with `SHARE_HISTORY` or `INC_APPEND_HISTORY`
at once; bash at its next startup. No history file is created, and
cmd.exe has none. When it finishes, a one-line
prompt waits: Return reopens the menu with the highlight where it was
and Esc quits. A target that fails gets a "(tip X exited with status
N)" line before that prompt, and Ctrl-C during a run gets
"(interrupted: tip X)" instead of a traceback; the menu itself always
exits 0, since the target's own output has already said what happened.
The tests drive the real
key bindings through prompt_toolkit's pipe input, so they need no
terminal.

## verify.py

Runs `tip verify`: the everyday edit-and-check loop, as an ordered list
of `tip` targets (`VERIFY_TARGETS` in the script) run one at a time as
their own subprocess, stopping at the first failure. Add or remove a
target name in that list to change what `tip verify` runs; its `--help`
text comes straight from that target's own one-line doc in
`tools/tasks.py` (the same one `tip help` reads), so nothing else needs
updating.

```
tip verify               # run every target in VERIFY_TARGETS, in order
tip verify ARGS=--help   # list them, with their doc text, without running
```

## sweep_checks.py

`tip gate` stops at its first failing step, which is right when you broke
one thing. It is wrong right after a tool upgrade, when the question is not
whether something broke but how much did. Worse, `gate` names
`solutions-gate` in its `deps`, so the whole Solutions half runs
first and can hide every `Chapters/` failure behind it, the opposite of the
order the recipe reads in.

`tip sweep` runs each check to completion and summarizes which failed:

```
tip sweep     # every check over both trees, all failures, exit 1 if any
```

`tip tools-upgrade` ends with it, so an upgrade's damage arrives attached
to the upgrade that caused it. The list is `SWEEP_TARGETS` in the script,
and each row's description is read from that target's own one-line doc in
`tools/tasks.py`. Each target covers both build trees, and `ty` and `lint` run
one invocation over both, so a failure in one tree never hides the
other's. The `#:` markers
are deliberately not swept: `tip verify` rewrites a stale marker instead
of failing on it, so a nondeterministic listing would report a difference
here every run.

## tip.py

The task runner. `tip TASK [TASK...] [NAME=value ...]` runs the named
tasks from `tools/tasks.py`, in order. A task's `deps` run first, and
each task runs at most once per invocation, so `tip ty lint` extracts
once. A variable takes the `NAME=value` form (`tip verify-ch CH=28`),
and a value with spaces splits into separate arguments, so `CH="25 28"`
names two chapters. A task with a positional variable also takes a bare
word: `tip run-one box_view` binds `box_view` to `F`. Every step runs
through `uv run` from the repository root, whatever the caller's
directory, and is echoed before it runs; the first step that fails
stops the run with its exit status. An unknown task name gets a "Did
you mean" suggestion.

Each goal named on the command line prints its wall-clock time when it
ends:

```
tip verify
...
tip verify: 1m 32s
```

A failing goal reports its exit code and the time instead
(`tip gate: failed (exit 2) after 40.1s`), and the exit
code still reaches the shell. Every step runs with `TIP_NESTED=1` in
its environment, and a `tip` started under it prints no timing line and
records nothing. `verify.py` and `sweep_checks.py` run each step as
`python -m tools.tip NAME` and time each step themselves, so `tip verify` and `tip sweep`
show a seconds column in their summary tables. Each of those, and the runner,
records a passing run's time in `build/target_times.json` for the help listing's time column
(see [target_times.py](#target_times.py)).

## verify_targets.py

Smoke-tests every target in `tip help`, so a target that broke stays
broken for one run rather than until someone happens to use it. Read-only
and idempotent targets run directly; a target that bakes `--fix`/`--write`
into its recipe runs in a disposable git worktree, so this working tree is
never touched. `tools-upgrade`, `python-upgrade`, `serve`, and `local`
never run at all, being network or environment mutations or a server that
blocks forever. Logs land in `build/target_test_logs/`. Each passing
target's time is recorded for the help listing, and the run ends by
rewriting `tools/data/target_tiers.txt`, the committed tier per target
that the listing falls back on for a target this machine has not run.
Commit that file when the run changes it.

## target_times.py

Where the help listing's time column comes from. Two sources, the first
preferred: `build/target_times.json`, this machine's last passing run of
each target, written by everything that already times a run
(`tip.py` for every goal named on a command line, `verify.py` and
`sweep_checks.py` for each of their steps, `verify_targets.py` for every
target it runs), and `tools/data/target_tiers.txt`, committed, one tier
per target, which `verify_targets.py` writes from its own measurements
and merges over the lines already there. The tiers are quick (under 5 s),
normal (under 30 s), long (under 2 min), and very long; `TIERS` in the
script sets them. A tier changes rarely, which keeps the committed file's
diffs small, while the local cache carries real seconds.

```
uv run python -m tools.target_times   # what the listing knows, per target
```

## check_chapter.py

The full gate spends most of its time executing every listing in all 44
chapters, almost none of which is about the chapter you just edited. This
runs the same code-example checks scoped to one:

```
tip check-ch CH=12     # or CH=12_Techniques--Data_Classes_as_Types
```

It rebuilds `build/examples/` whole-book first (cheap, and necessary since
a chapter's listings import their siblings), then narrows the expensive
step, `validate_output.py --update`, to that chapter, and finishes with the
listing gates plus `ty`, `ruff`, and `pytest` over that chapter's directory.

## Status stamps: gate_stamp.py and tool_stamp.py

Both write to `build/`, which is gitignored, so neither can enter a commit
or dirty a diff.

**`gate_stamp.py` (`tip gate-status`)** records a pass of the gate along
with a hash of every `Chapters/` and `Solutions/` file, so it answers the
question that matters after an editing session, which is not "when did the
gate run" but "has anything changed since it did":

```
gate passed 12 minutes ago (2026-07-25 14:03), at commit d6b9ad6
3 files changed since: 23_Patterns--Iterators.md, 24_Patterns--Singleton.md, ...
```

**`tool_stamp.py` (`tip tools-status`)** records when `tip tools-upgrade`
last ran. Upgrading is deliberately manual, since it rewrites the tracked
`uv.lock` and can invoke winget or Homebrew, and the cost of that choice is
drifting quietly for months and then meeting every breaking change at once.
So the gate prints one line when the stamp is old. It never fails and never
touches a tracked file, so it cannot turn a green gate red. That line is a
reminder for the author; nothing should act on it automatically.

## check_tools.py

Checks that the tools this project needs are actually installed and prints
a version line or a MISSING install hint for each. The basic tier is what a
reader needs for the everyday commands: `uv` itself, plus the uv-managed
dev tools (`ty`, `ruff`, `pytest`) that `uv run` resolves from `uv.lock`.
`git` is checked too but marked "assumed" (you already needed
it to get this far), so its absence doesn't fail the exit code. `--full`
adds the tools a book maintainer needs for the rest of `tip help`: `pandoc`
(`tip site`, `tip local`, `tip epub`, `tip pdf`), `typst` (`tip pdf`),
the standalone `vale` binary (`tip prose`), `gh` (`tip release`), pyright
(`tip pyright-review`; on Ubuntu its bundled node also needs `libatomic1`),
and an SVG rasterizer, any of `resvg`, `rsvg-convert`, `magick`, or
`inkscape` (the EPUB's figures, `tip cover`, `coupling-panels-png`).

A failing run ends with the commands that install what is missing on the
machine it ran on, ready to paste: one `winget install` line on Windows,
one `brew install` line where Homebrew is on PATH, one `sudo apt install`
line on the Debian family, and a download command for a tool the package
manager lacks (Ubuntu packages neither `typst` nor `vale`, so those come
from their GitHub release archives, and so does pandoc, since Ubuntu's own
is older than the EPUB and PDF builds' floor, `build_epub.PANDOC_MINIMUM`).
Each tool's packages per manager are in the script's `TOOLS` list, and
`install_hint(name)` gives a build script the same per-machine command for
its own error message.

```
tip tools-check        # uv, ty, ruff, pytest (git checked, assumed)
tip tools-check-full   # the above, plus pandoc, typst, vale, gh, pyright, a rasterizer
```

## doctor.py

Read-only diagnostics for the environment problems that look like a bug in
the book but are actually local machine state. `.python-version` pins a
floating minor (e.g. `3.15`), so `uv sync` always resolves to *some* build
of it — but a stale `uv` binary can keep resolving the same old prerelease
(alpha/beta) indefinitely, since it only learns a newer one exists once it
is updated itself. `doctor.py` compares the active interpreter against
every build `uv python list --all-versions` currently knows about for the
pinned minor and flags it if a newer one exists that isn't active. On
Windows it also checks whether a process (typically an editor's `ruff`/`ty`
language server) is running from `.venv`, since that holds a file lock
that makes `uv sync` — and so `tip python-upgrade` — fail with "Access is
denied" removing `.venv\Scripts`. Every check prints ok/WARN and, on WARN,
the exact fix command; nothing is installed, upgraded, or killed.

```
tip doctor
```

## upgrade_tools.py

Updates the project's tools to their latest versions. `uv self update`
updates uv itself (a no-op with its own message if uv was installed via
pipx, Homebrew, or winget rather than its standalone installer). `uv lock
--upgrade` then `uv sync` upgrade every uv-managed dev tool (`ty`, `ruff`,
`pytest`, `codespell`, ...) to the latest version `pyproject.toml` allows,
rewriting `uv.lock`; review `git diff uv.lock` before committing. `pandoc`
and `vale` are standalone binaries uv does not manage, so this is
best-effort: it tries winget (Windows) or Homebrew, whichever is on PATH,
and falls back to printing the install link if neither works. `git` is
left alone, the one tool `check_tools.py` treats as assumed. For the pinned Python
version itself, use `upgrade_python.py` below instead.

```
tip tools-upgrade   # update uv, ty/ruff/pytest/..., and (best-effort) pandoc/vale
```

## upgrade_python.py

Upgrades the pinned development Python and resyncs the environment. With no
argument, `tip python-upgrade` fetches the latest patch of the minor pinned
in `.python-version` (e.g. the newest 3.14.x). With `TO=3.15`, it first
repins: rewrites `.python-version` and the `requires-python` floor in
`pyproject.toml`, then syncs. Either way it finishes by running `tip
verify`. It runs through `uv run --no-project` so the orchestrating
interpreter is never the venv that `uv sync` is about to rebuild.

```
tip python-upgrade           # latest patch of the pinned minor, then verify
tip python-upgrade TO=3.15   # repin to a new minor, then verify
```

## extract_examples.py

Default mode is **check**: nothing is written. It reports

* examples present in the book but missing from `Examples/`,
* examples whose book text differs from `Examples/`, and
* conflicting duplicates (the same path tagged twice with different content).

It exits non-zero on any of these, so CI catches prose/code drift. Pass
`--write` to materialize `build/examples/` (use `-o DIR` for another target).

Check mode also looks the other way, at *strays*: a file under `Examples/`
that no current block generates, typically left by a rename or deletion.
A stray whose bare filename appears nowhere in `Chapters/*.md` is
*orphaned* and fails the check; one still mentioned there (a hand-written
helper) is *referenced* and only reported, since deleting it needs a human.

```
tip sync    # write Examples/ and SolutionsCode/ from the Markdown
tip check   # verify the Markdown matches both committed trees
tip prune   # delete the orphaned strays check flags, in both trees
```

A block whose slug starts with `rust/` (e.g. `# rust/fastcount/demo.py`)
is skipped here on purpose: see `extract_rust.py` below.

## extract_rust.py

A second, separate extractor for the Rust/PyO3 examples in
[Converting a Slow Function to Rust](../Chapters/18_Techniques--Performance.md#converting-a-slow-function-to-rust),
extended to a second language. A ` ```rust ` block whose first line is a
Rust comment naming the file (relative to `rust/`, e.g.
`// fastcount/src/lib.rs`) extracts there; a ` ```python ` block whose
slug starts with `rust/` (the Python caller `extract_examples.py` skips
above) extracts to that same path. Default mode is **check** against the
committed `rust/` tree; pass `--write` to update it.

This tool only ever touches the specific files a book block names
(`src/lib.rs`, a demo `.py`), never the rest of a crate directory
(`Cargo.toml`, `pyproject.toml`, real hand-maintained project files). It
does not build or run anything, that needs a Rust toolchain and is never
done by the main build; see `rust/README.md` and the `rust-*` tasks
(`tip rust-all`, crate list in `CRATES` in `tools/tasks.py`), the only
tasks that enter `rust/` or need a Rust toolchain.

```
python -m tools.extract_rust            # check vs rust/
python -m tools.extract_rust --write     # update rust/
```

## run_examples.py

Runs every `.py` under `build/examples/`, each in its own directory so the
examples' relative data paths resolve. Reports passed / skipped / timed-out /
failed and exits non-zero if anything fails or times out.

`test_*.py` and `conftest.py` are skipped here: they are pytest files, run by
`tip test` (`uv run pytest build/examples`), not as standalone scripts. See
the Testing chapter.

* Narrow the run: `python -m tools.run_examples 31_Patterns--State_Machines`
* Adjust the kill timeout: `--timeout 20` (default 60s)
* Parallelism: runs on all cores by default (`-j auto`); each example is its
  own subprocess, so this is safe. Use `-j 1` for serial, or `-j N` for a fixed
  count. (pytest runs serially by default; enable xdist with
  `tip test PYTEST_N="-n auto"`.)

### run_one_example.py: one example, by hand

`run_examples.py` captures output and reports pass/fail, which is what a gate
wants and not what a reader wants. `run_one_example.py` runs a single example
and streams its output:

```
tip run-one deque_timing
python -m tools.run_one_example Examples/03_Foundations--Containers/deque_timing.py
```

The argument is a path, a bare file name, or any substring of the path; a
substring matching several files lists them and exits 2. It reads `Examples/`
first, the committed tree, so it needs no extract step, and falls back to
`build/examples/`.

It supplies the same two things `run_one()` above does, the example's own
directory as the working directory and the tree's `utils/` on `PYTHONPATH`,
and prints the equivalent `cd` and `PYTHONPATH` commands before running. That
banner is the point: `ModuleNotFoundError: No module named 'benchmark'` is
what a reader gets running an example from the repo root, and the fix should
be visible rather than buried in a wrapper.

### Skipping examples that can't run unattended

Some examples open GUI windows, read stdin, or depend on dead frameworks. Skip
them two ways:

* an inline `# extract: no-run` line in the file, or
* a glob pattern in `tools/data/norun.txt`.

Only skip examples that cannot run even when correct, such as ones needing a
GUI or user input. A newly broken example should stay visible as a failure,
not be skipped.

### Regression baseline

Most examples failed during the Phase 2 modernization, so a runner that was
red on every one of them would have gated nothing.
`tools/data/examples_baseline.txt` records the set of then-failing examples. Two
modes use it:

```
python -m tools.run_examples --baseline        # fail only on NEW breakage
python -m tools.run_examples --write-baseline   # regenerate the baseline
```

The book is now fully modernized, so the baseline is **empty** and CI runs a
strict pass: every example must run. The `--baseline` mechanism remains for
future bulk work (e.g. importing a batch of new, not-yet-fixed examples): record
them with `--write-baseline`, gate only regressions with `--baseline`, then trim
entries as you repair them.

## validate_output.py

Maintains the `#:` output markers. A listing states its own expected stdout
in trailing `#:` comment lines, so a reader sees the result next to the code
and the build can prove it is still true:

```python
print(2 ** 10)
#: 1024
```

The tool runs each block from its extracted chapter directory (so imports and
relative data paths resolve as they do for `run_examples.py`) and compares
captured stdout against the markers. Default mode reports mismatches;
`--update` rewrites the Markdown to match what ran. A block with no `#:`
marker at all is left alone, but a lone bare `#:` is treated as a
not-yet-filled-in placeholder and is always filled, even without `--update`.

```
tip output-check   # verify markers, no rewrite
tip output         # rewrite stale markers in Chapters/
```

The gate runs `--update`, so a stale marker self-heals rather than failing
the build, the same way `fix-eol` and `sync` do. Two consequences are worth
knowing. First, **check `git diff Chapters/` after a gate run**: a marker
that changed is the build telling you an example's output moved, which is
sometimes the bug rather than the fix. A timing- or ordering-dependent
listing can flip its marker between runs with nothing to flag it. Second,
self-healing covers marker *text* only; an exception raised where none was
expected still fails.

Every block runs in one process, which is why the module drops each block's
namespace and forces a `gc.collect()` before moving on: a class defined in a
block forms a reference cycle with its own globals, so refcounting never
frees it, and a `__del__` firing later would land in a different block's
captured stdout. `-j` splits the work across processes; a block needing to
stay unrun carries the same `# extract: no-run` marker `run_examples.py`
honors.

When pointed at `Solutions/`, `--tree` must be **absolute**; see
[extract_solutions.py](#extract_solutions.py) below.

## extract_solutions.py

The exact counterpart of `extract_examples.py`, pointed at `Solutions/`
instead of `Chapters/`; it imports and reuses that module's `extract()`,
`check_against()`, `write_tree()`, and `is_derived()` rather than duplicating
them. `SolutionsCode/` is the committed copy (like `Examples/`);
`build/solutions/` is the throwaway tree used for running (like
`build/examples/`). Same two modes: check (default, compares against
`SolutionsCode/`) and `--write` (materializes a tree, default
`build/solutions/`, or `-o DIR`).

Check mode reports strays the same way `extract_examples.py` does, using
that module's `find_strays()` and `report_strays()`. A file under
`SolutionsCode/` that no block generates is *orphaned* when its name
appears nowhere in `Solutions/*.md` (fails the check) and *referenced*
when it still does (reported for a human). A renumbered exercise is the
usual source. The grep covers the solutions alone: a leftover named only
by a chapter is still orphaned here, since no solution block generates it
and the chapter's own copy lives under `Examples/`.

The `tip` targets that cover `Examples/` cover this tree in the same
run: `sync`, `check`, `prune`, `extract`, `output`, `output-check`,
`ty`, `lint`, `run`, and `test` each take both trees (until 2026-09-24
each had a `solutions-*` twin). Two targets are Solutions-only:

```
tip solutions-numbering      # every exercise has a solution (below)
tip solutions-gate           # numbering, drift, output, ty, ruff, run, pytest
```

`solutions-gate` runs as part of the main `gate` (and therefore `verify`
and `ci`), so a Solutions regression fails the same build a book
regression would. An extractable Solutions block with no `#:` marker and
no `# file.py` slug is a deliberately-unrun illustrative fragment, the
same convention `Chapters/` uses for code that only makes sense narrated
in prose (a type error, a race outcome); `run` executes the two dozen
answers that have a slug but carry no marker and are not tests.

`validate_output.py` needs an **absolute** `--tree` when pointed at
`Solutions/`: a block runs with its cwd inside `build/solutions/<chapter>/`,
and a relative tree argument stops resolving once cwd changes underneath it
(the `run_location()` gotcha `run_examples.py`'s own `--tree` warning
already describes). `tools/tasks.py` passes `SOLUTIONS_TREE`, an
absolute path, for this reason; do the
same when invoking `validate_output.py --tree` on `Solutions/` by hand.

## check_solutions.py

`extract_solutions.py` gates the code in `Solutions/`, and `heading_links.py`
gates its anchors, but whether a chapter's exercises have answers is prose on
both sides, so nothing watched it. Editing an exercise, deleting one, or adding
one at the end left the solutions silently answering a different question. A
2026 sweep found fifteen chapters out of step, including five with no
`Solutions/` file at all.

This compares two numberings: the top-level ordered-list items under a
chapter's last `## Exercises` heading, and the `## N. ...` headings in the
matching `Solutions/` file. It reports a chapter with exercises and no
solutions file, an exercise with no solution, a solution answering no exercise,
and either list numbered anything but 1..N in order.

```
tip solutions-numbering            # every chapter
tip solutions-numbering ARGS=19    # only chapter 19
```

Two conventions it knows about. A chapter whose Exercises section holds only
prose (chapter 1 describes the convention rather than setting any) has no
exercises and needs no `Solutions/` file. And one heading may answer several
exercises at once, written `## 1 & 2. ...`, `## 1, 2. ...`, or `## 1-3. ...`,
which is the right form when two exercises share one worked answer; a heading
with no leading number at all (`## Shared code: the microgrid`) is a preamble
and counts as no answer.

What it cannot see is a solution that answers the wrong exercise under the
right number, which still needs a human reading the two side by side. It runs
first in `solutions-gate`, being the cheapest step and the only one that
notices a missing answer.

It also checks how a solution cites its chapter, which is a trap the layout
sets. `Solutions/` sits beside `Chapters/` with the same file names, so a link
copied from a chapter, `](24_Patterns--Singleton.md#state)`, resolves to
`Solutions/24_Patterns--Singleton.md`: a real file, wrong content, no warning from
anything. Seventeen links were wrong this way before anything looked. The
correct form is `](../Chapters/24_Patterns--Singleton.md#state)`, and a leading `./`
marks a deliberate link to a neighboring solution.

`heading_links.py` covers the other half. The gate now runs its `anchors`
check over `Solutions/` as well (see `GATE_DOCS` in `tools/tasks.py`), which
catches an anchor that names no heading in whatever file it does reach; three
of those were dead in `Solutions/` for the same "nothing looked here" reason.
Neither check sees an anchorless link to a file that exists, so the two
together are the coverage: `check_solutions.py` for the missing prefix,
`heading_links.py` for the anchor.

## reflow_prose.py

Rewrites prose paragraphs in `Chapters/*.md` so each sentence sits on its own
line ("semantic line breaks"). This keeps edits and their diffs sentence-grained
instead of reflowing a whole hard-wrapped paragraph on every word change. Code
fences, indented code, tables, headings, list items, blockquotes, HTML blocks,
horizontal rules, and YAML front matter are left untouched; inline code spans
and footnotes are masked so their internal punctuation never triggers a split.

A sentence longer than `--width` (default 80) is broken further at top-level
clause punctuation (`,`, `;`, `:`), so no line is wide enough to wrap in an
editor. A greedy fill inserts only the breaks needed, and a minimum-length guard
keeps a short lead-in clause from being stranded on its own line; if the only
break points are too early to help, the sentence stays on one line. Punctuation
inside parentheses, brackets, inline code, or footnotes is never a break point.

A single newline inside a paragraph is a soft break (a space) under the site's
pandoc reader (`markdown+smart`), so reflowed prose renders identically. The
tool rewrites a file only when its whitespace-normalized text is unchanged, so
it can never add, drop, or alter a word; a file that fails that check is left
alone and reported.

```
tip reflow-check        # report which chapters would change, no write
tip reflow              # rewrite the whole book
tip reflow CH=02        # rewrite one chapter (by number, name part, or path)
tip reflow-check CH=02  # preview one chapter, no write
uv run python -m tools.reflow_prose --diff Tour   # diff a chapter by name part
```

A positional argument (or `CH=`) may be a file path or a chapter selector
matched against `Chapters/`: a number or stem prefix (`02`,
`02_Foundations--Tour`) or a substring (`Containers`). With no argument the whole book is processed.

## rewrite.py

Runs the AI editing passes over one chapter's prose, in place. Each pass is
one headless `claude -p "/<skill> <chapter>"` run of a skill (from
`.claude/skills/` or an installed plugin) with `--permission-mode
acceptEdits`, scoped by an appended system note to the chapter's prose
(never a fenced block or a `#:` marker, never git). After every pass the
chapter is reflowed and the cheap prose gates run (`banned_phrases.py`,
`heading_links.py`, the `extract_examples.py` drift check), so a pass that
touched a listing or broke a link fails right there. The chain stops at the
first failure.

```
tip rewrite CH=25                        # default passes (elements-of-style, bruce-edit-apply)
tip rewrite CH=25 ARGS=--list            # show the passes, run nothing
tip rewrite CH=25 ARGS=--dry-run         # print the commands only
tip rewrite CH=25 ARGS="--passes activate"
tip rewrite CH=25 ARGS=--all             # every pass, opt-in ones included
```

The passes live in `PASSES` in the script, in run order (general rules
first, Bruce's own captured practices last); adding a tool is appending an
entry. A pass marked `default` runs on a bare `tip rewrite`; the rest are
opt-in, so a skill whose rules say "only when explicitly asked"
(`readability`) stays off until named here, which counts as the ask. Each
pass runs once per invocation, deliberately: repeated cut-passes sand the
voice off a chapter, so a second lap is a second `tip rewrite`.

Not a gate: it costs tokens and is nondeterministic, so it is never part of
`verify`/`gate`/`ci`, refuses to run under `CI`, and `verify_targets.py`
excludes it. Review `git diff` before committing what it did.

## Spelling and prose style

Several layers, all optional and not part of the default CI gate.

**Spelling: codespell (`tip spell`).** A uv-managed dev tool, so it runs through
`uv run`. It prints one line per suspected misspelling and exits non-zero if it
finds any, so **no output means clean** (a silent return to the prompt is a
pass). It matches a curated misspelling dictionary rather than a full one, so it
stays low-noise even over code comments and examples, but it will not catch an
unusual typo that is not on its list ("fixted" for "fixed"); for that there is
the full-dictionary check below. Configuration lives in `[tool.codespell]` in
`pyproject.toml`; words it flags wrongly (design-pattern terms like `adaptee`,
foreign-language quotes, deliberate code strings) are listed in
`tools/data/codespell-ignore.txt`. Scope it with `CH=`, for example
`tip spell CH=02`.

**Full-dictionary spelling: spellcheck.py (`tip spell`).** Where codespell
knows only a curated list, `tools/spellcheck.py` (using the uv-managed
`pyspellchecker`) checks every prose word against a real English dictionary, so
a novel typo is caught. It checks prose only: code blocks, inline code,
footnotes, and link URLs are stripped via `tools.prose`, so identifiers do not
flood it. Two more things are not prose either, and both once produced findings
that looked like typos: a heading's explicit `{#anchor}`, whose slug splits into
words that are not (`sys-monitoring` gives "sys", `dont-start-the-engine` gives
"dont"), and the continuation lines of a multi-line HTML comment, which the
stateless classifier cannot see past its opening line. Accepted terms
(technical words, names, coined words) live in
`tools/data/wordlist.txt`, one lowercase word per line. When it flags a real term,
add it there; when it flags a typo, fix the prose. Use
`uv run python -m tools.spellcheck --summary` to see the unique unknowns by
count, which makes seeding the word list quick. `tip spell-add` automates the
"add it there" step for both checkers: it accepts every unknown word into
the wordlist, and every word codespell flags into
`tools/data/codespell-ignore.txt`, each sorted and deduplicated. The second
half matters because the two checkers keep separate lists and read
different text: codespell reads code too, so a class name it dislikes
(`OnlyOnce`) fails `tip spell` while never reaching `spellcheck.py`. It
cannot tell a real term from a typo, so always review
`git diff tools/data/` before committing.

**Mechanical prose: prose_lint (`tip spell`).** `tools/prose_lint.py` runs
alongside codespell and catches small mechanical slips a spell checker ignores:
more than one space between words, a space before `.`/`,`/`;`/`!`/`?`, more than
one blank line in a row, a period or comma left outside a closing quote, and
trailing whitespace (a two-space hard break is allowed). It shares the
`tools/prose.py` classifier with `reflow_prose.py`, so fenced and indented code,
tables, blockquotes, and HTML are skipped, and inline code spans and footnotes
are ignored inside a prose line; headings and list-item text are checked but
their markers are not. It is report-only and exits non-zero on any finding. Run
it directly with `uv run python -m tools.prose_lint Markdown` (or a single file).

The quote check reads a quoted *literal* differently from quoted prose. The book
puts the mark inside a quoted phrase (`"easier to ask forgiveness than
permission,"`) but outside a literal, where moving it in would put a comma into
a `pytest -k` substring or a period into an error message the reader matches
against. A quote holding an inline code span, and a single-token quote such as
`"overdraft"`, are therefore skipped. A multi-word literal fits neither shape,
so write that one as an inline code span rather than as a quotation.

**House style: Vale (`tip prose`).** Vale is a standalone binary, not a Python
package, so install it once (`winget install errata-ai.Vale`,
`brew install vale`, or see <https://vale.sh/docs/install>). Vale parses Markdown
and checks only text, never code spans or fenced code, so the rules never fire on
identifiers or examples. Spelling is left to codespell; Vale enforces house style
only. The rules live in `styles/House/` and are wired up by `.vale.ini`:

* `EmDash` (error): no `—`, `–`, or `--` used as a dash.
* `Filler` (warning): throat-clearing phrases ("this is the whole idea", and so on).

The community packages for passive-voice and usage checks are listed in
`.vale.ini` (`Packages = write-good, proselint`); `tip prose` runs `vale
sync` to download them into the gitignored `styles/` the first time, when
that directory has no `write-good`.

## check_all.py

The checks below each have their own script and their own `tip` target,
which is what you want when one thing is broken and you are iterating on
it. Running them one at a time means an interpreter startup and a fresh
parse of all 45 chapters per tool, and N summaries instead of one answer to
the question "is the book clean?"

This runs them together: every file is parsed once into a `Document` and
handed to each check, and all findings land in one list sorted by file and
line, so the report reads top to bottom through the book rather than
grouped by which tool noticed.

```
tip checks                # every Markdown check, one pass
tip checks ARGS=--list    # their names and descriptions
tip fix-checks            # apply every fix they can make
```

The registry is the explicit `CHECKS` list in the script, deliberately not
directory discovery: an explicit list is greppable, and it cannot surprise
the interpreter that also execs book listings. Adding a check means
importing it and adding it there, after which it appears in `--list`, in
the default run, and as a selectable name.

`gate` runs the selection named by `GATE_CHECKS` in `tools/tasks.py`, which is
now the whole registry: `prose-lint` was the last holdout and joined once
its findings were cleared. `tip checks` runs the same registry plus the
Vale prose lint, which the gate leaves out because Vale is a standalone
binary rather than a uv-managed one.

## check_line_endings.py

`.gitattributes` (`* text=auto eol=lf`) already keeps committed blobs LF on
every platform, so the repo and the Linux CI build are always LF. This tool
guards the **working tree**: on Windows an editor can write CRLF into a source
file, which is harmless to git but produces noisy warnings and inconsistent
local files. `tip eol` reads `git ls-files --eol` (so it honors the binary
markers in `.gitattributes`) and fails if any tracked text file has CRLF or
mixed endings. It is part of the `tip ci` gate. There is no auto-convert in the
build; run the fixer explicitly when the check flags something:

```
tip eol       # check, exit 1 on CRLF (part of `tip ci`)
tip fix-eol   # convert any offenders to LF
```

## listing_format.py

The book favors dense listings: at most one blank line in a row, and no blank
line between import groups. Ruff's isort config (`no-lines-before`,
`lines-after-imports = 1`) enforces the import layout, but only on the extracted
`.py` files: it cannot rewrite the `Chapters/` source, and it does not check
blank-line counts between defs at all. This tool closes both gaps by checking
the Markdown directly. It is string-aware, so blank lines inside triple-quoted
strings are never touched, and it only looks at ```python blocks. It is part of
the `tip ci` gate; like line endings, there is no auto-fix in the build:

```
tip listings       # check, exit 1 on extra blank lines (part of `tip ci`)
tip fix-listings   # remove the offending blank lines
```

Do not run `ruff format` on the examples: it would re-expand to two blank lines
between top-level defs and undo the density. The gate runs `ruff check` (the
linter) only, which is happy with one blank line.

## fix_imports.py

Sorts the import block of each ```python listing and drops unused imports,
writing back to the Markdown. ruff's import rules are already part of the
lint gate, but that gate runs on `build/examples/`, which is regenerated
from the Markdown, so an automatic fix has to land in the source.

It runs ruff on the real extracted files rather than on each block in
isolation, which matters: ruff's isort only classifies a listing's sibling
imports as first-party when it can see those files on disk, so fixing the
tree in place sorts the way the gate expects. Then it splices each fixed
file back into the block it came from. It extracts nothing itself, so run
it against a built tree (`tip fix-imports` depends on `extract`).

```
tip fix-imports    # rewrite the listings' import blocks
```

Deliberately-unused imports stay: `--select I,F401` respects the
`per-file-ignores` in `pyproject.toml`, which is what keeps the chapter
example that exists to show that importing a module runs its top-level code
from having its unused import deleted.

## banned_phrases.py

Fails the build if any phrase listed in `tools/data/banned_phrases.txt` appears
anywhere in `Chapters/`, prose and code alike (unlike Vale, which only sees
prose). Matching is a literal, case-sensitive substring; each occurrence is
reported as `path:line:col`. Use it to retire a construct book-wide, for example
`from __future__ import annotations`, which is unnecessary on Python 3.14. Edit
the phrases file to add or remove entries (blank lines and `#` comments are
ignored). It is part of the `tip ci` gate.

```
tip banned    # fail if any banned phrase is in the book (part of `tip ci`)
```

## comment_periods.py

Enforces the comment-period policy in ```python listings: a one-line comment
ends without a period; only a multiline comment (two or more consecutive
full-line `#` comments) reads as sentences and keeps its periods. So it flags a
trailing period on an inline comment or a lone full-line comment, but leaves
multiline blocks alone. It is string-aware (a `#` inside a string is not a
comment) and skips an ellipsis (`...`). It is part of the `tip ci` gate.

```
tip comment-periods       # check (part of `tip ci`)
tip fix-comment-periods   # strip the trailing periods
```

## capitalize_comments.py

Enforces that a prose comment in a ```python listing starts with a capital. The
prose-vs-code judgment is a heuristic, so it skips code-identifier first words,
single letters, and keywords, and continuation lines of a multiline comment. Its
unavoidable false positives (program output like `# total = 7`, an identifier
reference like `# n is the counter`, schematic notation like `# name -> subclass`)
are listed by comment text in `tools/data/comment_caps_allow.txt` and skipped. It is
part of the `tip ci` gate.

```
tip comment-caps       # check (part of `tip ci`)
tip fix-comment-caps   # capitalize the flagged comments
```

When the checker is wrong, add the comment's text to the allowlist; when it is
right, capitalize the comment (or run `tip fix-comment-caps`).

## comment_spacing.py

Enforces that an inline comment in a ```python listing (code precedes it on
the same line) starts exactly two spaces after the code ends. A full-line
comment and a `#:` output marker have no code on their line to measure the
gap from, so both are left alone. It is string-aware (a `#` inside a string
is not a comment) and collapses any gap, including one used to
column-align several comments, to two spaces. It is part of the `tip ci`
gate.

```
tip comment-spacing       # check (part of `tip ci`)
tip fix-comment-spacing   # collapse the gaps to two spaces
```

## heading_links.py

Verifies that every heading-anchor link resolves to a real heading, so a typo
does not ship as a dead in-page link. Markdown can link to a heading with
`[text](#id)` (same file) or `[text](08_Foundations--Static_Types.md#id)` (another chapter).
The tool reproduces pandoc's anchor rule (lowercase, spaces to hyphens,
punctuation and backticks removed, leading non-letters dropped), honors an
explicit `{#id}` on a heading, collects every id, and checks each `#anchor`
link against it. A bad cross-file link also reports a missing target file. It is
part of the `tip ci` gate; there is nothing to auto-fix.

```
tip anchors    # check (part of `tip ci`)
```

To make an anchor stable against rewording, give the target heading an explicit
id: `## Heading {#stable-id}`, then link `(chapter.md#stable-id)`.

The gate checks `Chapters/` and this README (`GATE_DOCS` in `tools/tasks.py`).
Two links in here were dead for a while precisely because nothing looked
outside `Chapters/`. Only the anchors check runs over this file: `banned`
would fire on the worked example in
[banned_phrases.py](#banned_phrases.py) above, which names a banned phrase
in order to explain the tool.

## footnote_labels.py

Fails if two chapters define the same reference footnote, `[^label]:`.
A label only has to be unique within one Markdown document, and the
site renders each chapter as its own page, so two chapters can share a
label and the site is fine. The EPUB and PDF concatenate every chapter
into one document first, and there pandoc keeps the first definition
and drops the rest with one warning in the build output, so the second
chapter's reference silently shows the first chapter's note. Chapter 17
carried chapter 11's `parametrize` note through release 0.5.9 that way.

```
tip footnotes    # check (part of the gate through GATE_CHECKS)
```

Definitions inside fenced code are ignored, and references are not
checked: one note may be cited many times, and a reference to a label
with no definition is a pandoc warning on every build, site included.
The fix is to rename one label at both its reference and its
definition.

## check_quoted_diagnostics.py

Advisory. The book quotes `ty` output in fenced blocks that begin
`error[...]` or `warning[...]`, each with a ` --> file.py:LINE:COL`
location and gutter lines reproducing the listing's source. Nothing
gates those: `#:` markers are validated against a run, but a quoted
diagnostic is prose, so a listing edit that shifts a line, or a `ty`
upgrade that rewords a message, leaves the quote stale with every
gate green. The 2026-09-14 claims sweep found such quotes in four
chapters and several Solutions files.

`tip quoted-diagnostics` reads every quoted block in `Chapters/` and
`Solutions/`, follows each location line, and compares every gutter
line with that line of the extracted listing, searching the file's
own build directory, then (for a Solutions file) the chapter's, then
`build/examples/utils`. A gutter line matches when it equals the
file's line, or equals it with a trailing `# type: ignore` removed,
or equals the file's line with its leading `# ` removed (the book's
commented-out probe convention); ty's multi-line span bar and
indentation are ignored.

About a dozen quotes are deliberately against an edited copy of the
listing (a `match` block removed, a `ValueError` deleted from an
annotation, a line added), and the shifted line numbers are right for
that copy. Those live in `tools/data/quoted_diagnostics_baseline.txt`,
in the style of `pyright_review.py`, as `markdown path<TAB>message`
with the Markdown line number dropped so prose edits above a quote do
not churn the file. The default run prints only the delta, NEW and
GONE, and exits nonzero on NEW, which is why it is part of `gate`: a
NEW hit is either a stale quote to fix or a fresh deliberate edit to
accept with `tip quoted-diagnostics-accept`. `--all` lists every hit
regardless of the baseline.

## exercise_refs.py

The book names its exercises by number in prose: "Exercise 8 works
out which sizes reach which colors", "the reason exercise 3 gives",
"exercise 4 of [Generators](...)". `check_solutions.py` gates that a
chapter's exercise list and its Solutions headings agree with each
other, so after an exercise is inserted the two still agree, every
gate is green, and each sentence naming a later exercise names the
wrong one. Chapter 30 collected five such references when commit
a2cc5a98 inserted an exercise at 2.

Whether a sentence describes its exercise is a judgment, but the
failure is mechanical: the title under a referenced number changed.
`tip exercise-refs` pairs every reference in `Chapters/` and
`Solutions/` with the Solutions heading for its number, `## N.
<title>`, in the chapter the reference targets, and compares the
pairs with `tools/data/exercise_refs_baseline.txt`. NEW is a pair the
baseline lacks (the exercise under that number changed, or the
reference was written since the last accept) and fails the gate; GONE
reports and does not. Reread each NEW sentence against the title
printed beside it, then fix the number or run
`tip exercise-refs-accept`. `--all` lists every pair.

It reads "exercise 3", "exercises 3 and 4", "the second exercise",
and "the previous/next exercise" (resolved from the exercise item or
the `## N.` section the sentence sits in). The target is the file's
own chapter unless the reference is tied to a chapter link: "exercise
4 of [Generators](...)", "[Generators](...)'s exercise 4", or "its
exercise 9" after a link earlier in the paragraph. Two findings are
errors that no baseline accepts: a number the target's Solutions file
lacks, and an exercise of "the previous chapter", which a chapter
split retargets silently. Entries are keyed by chapter name, so a
renumbering leaves the baseline alone and a chapter rename does not.
"The last three exercises" and an exercise described without a
number are invisible to it.

## Advisory checks: check_links.py and list_todos.py

Neither is part of `verify`/`gate`/`ci`. Run them now and then.

**`check_links.py` (`tip links`)** requests every unique external
`http(s)://` URL in the book and reports connection errors, timeouts, and
statuses at or above 400. HEAD is tried first, with one GET retry for
servers that treat HEAD differently. It stays out of the gate on purpose:
the network is flaky, sites rate-limit, and a dead external link should
never block a build. Internal cross-references are `heading_links.py`'s
job, not this one.

**`list_todos.py` (`tip todos`)** lists `TODO(tag): ...` markers left in
the Markdown. A marker is an HTML comment, so pandoc strips it from the
rendered site while it stays greppable in the source:

```
<!-- TODO(py315-deps): NumPy has no Python 3.15 wheel yet. Once it
does, convert this indented block to a real, fenced, tested example. -->
```

The tag groups related markers that share one underlying blocker, and
doubles as a plain `grep -rn "TODO(py315-deps)" Chapters/` when you care
about only one of them. It always exits 0, being informational.

## build_site.py

Renders `Chapters/*.md` into a browsable site under `build/site/` (git-ignored).
Pandoc converts each chapter; the script adds the title page, an ordered
contents list, a sidebar, previous/next links, and syntax-highlighting CSS.

The book's **Part dividers are generated here, not written in the Markdown.**
The `PARTS` map names Part I (Foundations, before chapter `02`), Part II
(Techniques, before `09`), and Part III (Patterns, before `17`); the builder
emits each heading in the table of contents before its starting chapter, with
the Introduction standing alone above Part I. So a chapter file with no "Part"
heading is correct: to move or rename a Part, edit `PARTS`, not the chapters.

Book images are referenced in the Markdown as `_images/<name>` with no
extension. The builder resolves each to the real file in `resources/images`
(`decorator` to `decorator.gif`), copies the referenced ones into
`build/site/images/`, and warns about any reference with no matching file.

Cross-references between chapters use standard relative Markdown links to the
target chapter's `.md` file, for example
`[Factory](27_Patterns--Factory.md)`.
These render correctly on GitHub; the builder rewrites intra-book `.md` links to
`.html` so they also resolve in the site. External links (which carry a scheme)
are left alone.

Requires `pandoc` on PATH. Run `python -m tools.build_site` (or `tip site`);
use `-o DIR` to build elsewhere. `tip serve` builds nothing and serves the
existing `build/site/` at <http://localhost:8000>; `tip local` builds, serves,
watches for edits, and opens a browser at the site.

`rebuild_chapter()` is the incremental entry point `serve.py --watch` uses:
it re-renders one chapter (a single pandoc run, against the ~46 of a full
build) plus the index page and the search index, both of which a changed
heading affects and neither of which needs pandoc. It returns `False` for a
path that is not a book chapter, or when `build/site/` does not exist yet,
leaving the caller to do a full build.

## build_epub.py

Renders the same `Chapters/*.md` into two EPUBs under `build/epub/`
(git-ignored): `ThinkingInPython-color.epub`, whose listings carry color
syntax highlighting for backlit readers, and `ThinkingInPython-eink.epub`,
which bolds keywords and italicizes comments instead, for grayscale e-ink
screens. Both come from one assembly and one set of token spans (the running
CPython's own `tokenize`, so 3.15-only syntax needs no third-party lexer);
only the stylesheet differs. The colors are mid-tones chosen to stay
readable on both white and black, since Kindle's dark mode keeps a declared
color as given. Run `tip epub`; `-o DIR` builds elsewhere, and
`--keep-source` leaves the generated pandoc input under `<out>/src/` when
you need to see what pandoc was handed. Needs `pandoc`, like `site`.
`tip clean-epub` removes the directory.

Chapter discovery, titles, the Part dividers, and the image map all come from
`build_site.py`, so the EPUB's contents match the site's rather than drifting
from it. What differs is linking. The site keeps one HTML page per chapter, so
a cross-reference stays a link between files and the builder only rewrites
`.md` to `.html`. An EPUB is a single document, and merging the chapters makes
the book's anchors ambiguous: 44 chapters end in `## Exercises`, and
`#immutability`, `#generators`, `#lambdas` and six other anchors each appear in
two to four chapters. Pandoc's own de-duplication numbers repeats in document
order, so `[Immutability](12_Techniques--Data_Classes_as_Types.md#immutability)` would
quietly open chapter 3.

So every heading gets an explicit id namespaced by chapter number, and every
link is rewritten to match:

| Markdown | In the EPUB |
| --- | --- |
| `## Immutability` | `## Immutability {#ch12-immutability}` |
| `[x](12_Techniques--Data_Classes_as_Types.md#immutability)` | `[x](#ch12-immutability)` |
| `[x](#immutability)` (same chapter) | `[x](#ch12-immutability)` |
| `[x](24_Patterns--Singleton.md)` | `[x](#ch24)` |

The `ch` prefix is not decoration: an EPUB is XHTML, where an id may not start
with a digit. The old ids come from `heading_links.pandoc_anchor()`, the
function the `anchors` gate checks links with, so a link the gate accepts is a
link this build resolves; its per-file de-duplication is mirrored too, so a
chapter with two identical headings keeps pandoc's `-1` suffix inside its own
namespace. A link naming a chapter's *own* title heading is aliased to the
chapter's root id, since `load_chapter()` lifts that heading out into the
title. Anything that still resolves to nothing is reported and left unlinked,
which is a stricter check than the gate's: `heading_links.py` skips an anchor
containing a period, and chapter 13 has one.

`--release VERSION` (what `tip release` passes) stamps the title page
with the release number and today's date via `release_line()`
("Release 1.0 · August 23, 2026"). That stamp lands in the pandoc
`date` metadata field, which pandoc then cannot parse as a date and
would leave the OPF's machine-readable `dc:date` empty, so the build
also passes pandoc an `--epub-metadata` file holding the ISO date.
`build_pdf.py` shares `metadata_yaml()`, so the same flag stamps the
PDF's title page too, with no OPF concern there.

Tests live in `tools/tests/test_build_epub.py`. They are worth keeping green:
a namespacing bug produces a valid EPUB whose links open the wrong chapter,
with nothing in the build to show for it.

## listing_links.py

Turns a listing's name in the prose into a link to the listing. The
chapters name their listings in backticks (`the dictionary in
`shape_table.py``), and `check_unique_slugs.py` keeps every basename
unique, so each mention has one target. `build_site.py` and
`build_epub.py` call this at build time: every slugged block gets an id
derived from its path comment (`listing-registry.py`,
`listing-mouse-MouseAction.py`), and every `name.py` code span outside
a fence and outside an existing link becomes a link to it, same page or
cross-chapter on the site, in-document in the EPUB, carrying the class
`listing-link` for the stylesheet. Only a code span holding the bare
name is a mention; `from registry import make` stays code, and so does
a name two chapters both define. Nothing changes in `Chapters/`, so do
not write these links by hand.

Both builders take `--no-listing-links`. `build_pdf.py` passes the
option off itself: with `hang_code=False` nothing writes the ids, and
typst rejects a link to a missing label. On the site the two rewrites
must run links first, then fence ids: the attribute-form fence opener
(```` ``` {#id .python} ````) is not one `tools.markdown` reads as a
fence, so the reverse order sees every prose line after a listing as
code. `site_rewrite()` fixes the order and
`tools/tests/test_listing_links.py` pins it.

On the site, `resources/static/link-preview.js` (copied beside the
pages with its stylesheet `link-preview.css`, and loaded by
`template.html`) adds a hover panel: resting the
pointer on a listing link shows the listing in a floating box, cloned
from the page or, for a cross-chapter link, fetched once from the other
page. Clicking the link still jumps to the listing, so the panel needs
no switch to turn it off. A device with no hover gets no panel. The
EPUB has no script, so its links only jump.

The same panel serves every other link into the book, with no class
and no build step: the script reads the `href`. A link to a heading
shows the heading and the text under it, up to the next heading of
that level or `MAX_BLOCKS` blocks, and then says the text continues.
A link naming a chapter and no anchor shows the chapter's title and
opening text. A footnote reference shows the note. Three kinds of link
get no panel: one to another site (a browser will not let the page
read it), the page's navigation (Contents, the chapter's table of
contents, previous/next, a footnote's back-link), and any link inside
a panel.

The contents page loads the script too (`render_index()` names the two
files, since it does not go through the template), so a chapter title
there shows that chapter's opening. The stylesheet repeats the few
prose rules an excerpt needs, because `style.css` styles a table of
contents and no prose, and it reads `--heading-font`, which the
template and `render_css()` both set in `:root`.

A finger cannot hover, so a tap stands in: the first tap on a link
shows the panel, whose caption carries a "Go there" link, a second tap
on the same link follows it, and a tap anywhere else closes the panel.
The script decides per interaction, from the `pointerType` of the last
`pointerdown`, so a laptop with a touch screen gets hover from its
mouse and taps from its screen. The caption is sticky, which keeps
"Go there" in view while a long excerpt scrolls.

`tip preview-check` (`tools/site_preview_check.js`) builds the site
and then uses the previews under jsdom: it hovers every link on every
page, taps the first link of each kind on each page, and fails on a
link into the book with no panel, a navigation link with one, or a
panel with an id, a back-link, or a stray `#place` link in it. It
needs node, which no gate does, and its first run installs jsdom
(major version pinned in the script) under `build/node/` from the
network, so it is in no local gate and `verify-targets` skips it. The
`site` job in `.github/workflows/ci.yml` does run it, between the
build and the Pages upload: the runner's pandoc is not the local one,
and the previews depend on the HTML it writes. It reads the script from `resources/static`
and the pages from `build/site`, so after an edit to the script alone,
`node tools/site_preview_check.js 29 index` reruns it on a few pages
in a couple of seconds. jsdom lays nothing out: check where the panel
sits and how it looks in a browser.

## make_cover.py

Generates the covers and favicon. Two modes, chosen by whether
`resources/cover-source.jpg` exists. **Art mode** (the usual one):
that image, whatever its size, is composited with the book's
typography; the page background is sampled from the image's corners
and the art's edges are feathered into it, so any art on its own
paper color drops in seamlessly. To restyle the book, replace
`cover-source.jpg` and run `tip cover`. **Drawn mode** (no source
image): a parametric serpent computed by the script, a python coiled
into an infinity sign in the site's palette.

Either way the outputs under `resources/static/` are committed, so
the book builds never need the generator's tools (`resvg` to render,
Pillow to encode). Four cover roles: the EPUB covers
(`cover-{color,eink}.jpg` or `.png`, 1600x2560, Kindle's ratio, the
e-ink one derived as autocontrasted grayscale), the PDF's full-bleed
first page (`cover-letter.{jpg,svg}`, US Letter ratio), and the
site's index art (`cover-art.{jpg,svg}`). The builders accept either
file family, and each mode deletes the other's outputs. Plus
`favicon.svg`: a serpent's eye, gold iris with a slit pupil on deep
green, in the cover art's palette, linked from every site page
(picked from candidate galleries for staying legible at 16 px on
both light and dark browser chrome). And `chapter-ornament.{svg,png}`:
a band of diamond scales that sits under every chapter title, the SVG
on the site (template.html) and the PNG in the PDF and EPUBs
(injected by build_epub.py's shared assembly, which also places the
cover art on each Part divider page). And `chapter-snake.png`: the
serpent alone on a transparent ground, 320 px wide, which
template.html sets to the left of each chapter title on the site (and
above it on a narrow screen). In art mode `snake_cutout()` makes it
from `cover-source.jpg` with Pillow alone: the paper around the
serpent and inside each loop becomes transparent, and the image is
cropped to what remains. The EPUBs set it on its own line under each
chapter title, above the ornament. The index page and the PDF do
not use it. `--preview` writes a small `cover-preview.png` for quick
iteration.

## build_pdf.py

Renders the same `Chapters/*.md` into one PDF at
`build/pdf/ThinkingInPython.pdf` (git-ignored). Run `tip pdf`; `-o DIR`
builds elsewhere, and `--keep-source` leaves the generated pandoc input
under `<out>/src/`. Needs `pandoc` plus `typst`, the PDF engine pandoc
drives (`winget install Typst.Typst`; `tip tools-check-full` verifies
both). `tip clean-pdf` removes the directory.

The assembly is `build_epub.book_markdown()`, so everything above about
namespaced anchors and rewritten links applies here unchanged. The one
difference is `hang_code=False`: the EPUB rewrites listings into raw-HTML
`<pre>` blocks for its hanging indent, and pandoc's typst writer drops raw
HTML, so the PDF keeps listings as fenced blocks. Nothing needs the hang
there anyway: ruff caps listing lines at 70 characters, which fits the
page, and typst highlights fenced Python itself. Typst also renders the
SVG diagrams directly, so the EPUB's PNG rasterization step has no PDF
counterpart. Page breaks before each Part and chapter and the table of
contents come from pandoc's stock typst template plus the `header.typ`
the builder writes (`header_typst()`). That header also sets a running
footer on every page but the title page: chapter name on the left (the
nearest level-1 heading, so TOC pages read "Contents"), page number on
the right, and, on a `--release` build only, the release stamp in the
center. The template's page numbering stays on even though the footer
replaces its output, because the outline formats the TOC's page
numbers through it.

## release.py

Publishes a GitHub release whose uploaded assets are exactly the fresh
PDF and the two EPUB variants (`-color` and `-eink`). Run
`tip release VERSION=1.0`; the tag is the version
with a `v` prefix (`v1.0`), created on origin at the branch tip. Needs
`git` and an authenticated `gh` (`gh auth login`).

The order is preflight, verify, build, publish, cheapest first. The
preflight refuses a dirty tree, a detached HEAD, a branch whose tip
does not match origin, and a tag that already exists (locally or on
origin): the tag must point at the pushed commit the assets were built
from. Then `tip verify` runs the full gate, so a book that fails it
can never ship. If verify's self-healing fixers rewrite tracked files,
the run stops and asks for a review-commit-push before trying again,
since the tree no longer matches the pushed commit. Only then are the
PDF and EPUBs rebuilt (both builders wipe their output directory first,
which is what makes the assets fresh) and handed to `gh release
create`. All are built with the `--release` stamp, so their title
pages tell the reader which release they hold and when it was made
("Release 1.0 · August 23, 2026"); an ad-hoc `tip pdf`/`tip epub`
carries no stamp, so a casual build never masquerades as a numbered
release. Deleting a bad release stays a manual act:
`gh release delete v1.0 --cleanup-tag`.

Deliberately excluded from `verify_targets.py`'s smoke test, alongside
`tools-upgrade` and friends: it tags the repo and publishes to GitHub.

## search_index.py

Builds `search-index.json`, which the site's `search.js` fetches and
searches in the browser. There is no server, so the whole index ships to
the reader, fetched lazily the first time someone opens the search box.
`build_site.py` calls this, so `tip site` covers it.

A record is one *section*: the text under a single `##` or `###` heading,
plus the chapter's opening text, which sits under no heading and links to
the page itself. Each carries the page, anchor, chapter title, and section
heading needed to deep-link to it. Anchors come from
`heading_links.pandoc_anchor()`, the same function the gate checks links
with, so a link the gate accepts and a link a search result produces
resolve to the same heading.

## serve.py

Serves `build/site/` over HTTP for local preview. `tip serve` runs it as-is;
`tip local` builds the site first, then runs it with `--open --watch`. Use
`--port N` for another port. It builds nothing on startup, so run a site build
first if `build/site/` is missing.

`--watch` turns it into an edit loop. A daemon thread compares modification
times every second across `Chapters/*.md` and the few files the whole site
renders from (`template.html`, the static assets, `build_site.py`,
`search_index.py`). A changed chapter goes through
`build_site.rebuild_chapter()`, roughly 0.3s here; a changed template or tool
rebuilds every page, roughly 5s. Served pages carry an injected script that
polls `/__reload` for a token the watcher bumps after each rebuild, so the
open page refreshes on its own. A rebuild holds a lock the request handler
also takes, so no request can read `build/site/` while a full build is
deleting and rewriting it. Polling beats a filesystem-watch library here
because it needs no new dependency, and 50-odd `stat()` calls a second cost
nothing.

### Publishing to GitHub Pages

The `deploy` job in `.github/workflows/ci.yml` publishes the site to GitHub
Pages at <https://bruceeckel.github.io/ThinkingInPython> on every push to
`master`. It uses the GitHub Actions Pages flow: `actions/upload-pages-artifact`
uploads `build/site/`, then `actions/deploy-pages` deploys it. The site is built
fresh in CI, so the generated HTML is never committed (`build/` stays
git-ignored). All in-page links are relative, so the project subpath
(`/ThinkingInPython/`) just works. See "Continuous integration" below for how
the build and publish steps relate to the opt-in test gates.

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `master`, every pull request,
and manual `workflow_dispatch`. The full example/test suite already runs on your
machine before you push (and Actions can be slow), so **the default CI path only
builds and publishes the site**. The workflow has these jobs:

* **`site` (always runs):** installs uv (`astral-sh/setup-uv`, Python 3.15,
  cached) and pandoc, runs `uv sync --locked`, and builds the static site. On a
  push to `master` it hands the site to the `deploy` job, which publishes it to
  GitHub Pages. Pull requests build the site but do not deploy.
* **`gates` (opt-in only):** the full suite, the same one `tip ci` runs
  locally: the drift check (`extract_examples.py`), the example run
  (`run_examples.py`, all must pass), the pytest examples
  (`pytest build/examples`), the type check (`ty check build/examples`,
  zero diagnostics), and the lint (`ruff check build/examples`, zero
  findings), followed by the same five checks for `Solutions/`
  (`extract_solutions.py`, `validate_output.py --tree build/solutions`,
  `ty check build/solutions`, `ruff check build/solutions`, and
  `pytest build/solutions`). Deliberate lint exceptions live in
  `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`.
* **`prose` (opt-in only):** the same checks as `tip spell` and `tip prose`.
  codespell spell-checks `Chapters/` (config in `[tool.codespell]`, ignore list
  in `tools/data/codespell-ignore.txt`) and fails on a spelling error. It then
  installs the Vale binary and runs the house-style rules in `styles/House/`;
  Vale fails the job on an em-dash (error level) and prints the filler
  findings as warnings. Shares the gates trigger.

`deploy` depends only on `site`, not on `gates` or `prose`, so publishing is
never blocked by the opt-in checks. The trade-off is that a push can publish even if an example
would fail a gate, which is why you run `tip ci` locally first.

### Requesting the full gates in CI

The `gates` job runs only when you ask for it, in either of two ways:

* **Manually:** on the repo's **Actions** tab, select **CI**, click **Run
  workflow**, and leave the `run_gates` input at its default of `true`. From the
  command line that is:

  ```
  gh workflow run ci.yml -f run_gates=true
  ```

* **From a push:** include the marker `[full-ci]` anywhere in the commit message
  of the push, for example:

  ```
  git commit -m "Rework the Visitor example [full-ci]"
  ```

Either way, treat CI as a second opinion: run `tip ci` locally first.

### Suggested workflow

Day to day:

1. Make your changes by editing `Chapters/` (the source of truth for prose and
   code alike) or `Solutions/` (worked exercise answers).
2. Run `tip verify site`: it pushes any code-block edits out to
   `Examples/` and `SolutionsCode/`, then runs the full gate (drift, run,
   pytest, ty, ruff, plus the same for `Solutions/`) and builds the site.
   Use plain `tip ci` when you want to confirm there is no drift rather
   than paper over it.
3. When it is green, commit and push, including any updated `Examples/` or
   `SolutionsCode/` files. The default CI path just rebuilds and publishes the
   site; it does not re-run the gates, so the push is fast.
4. Only when you want CI to re-check the suite itself (an environment-specific
   change, say, or a release) request the gates: add `[full-ci]` to the push
   commit message, or trigger the workflow manually as shown above.
