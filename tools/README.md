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

A file can span several blocks. A later block whose path line is
`# trace.py (continued)` appends to `trace.py`, after one blank line, with
its path line kept as a comment, so every Markdown line maps to one line
of the file and prose can follow each part. `tools/extract.py` does the
join and reports a `(continued)` block with no earlier block of its file
in the same chapter. `validate_output.py` and `marker_placement.py` run
the parts in order in one namespace, marked or not; `fix_imports.py`
splits the fixed file back into its parts (`split_parts()`); the listing
id and the prose links go to the first part; every per-block check sees
each part as a listing of its own.

`Examples/` is the curated copy committed to git. `build/examples/` is a
throwaway tree (git-ignored) regenerated from the Markdown for running.

`Solutions/*/README.md` (worked exercise answers) go through the exact same
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
  execs every book listing in its own process, and chapter 23 has a
  listing called `config.py`, so a bare `config` module on `sys.path`
  would be found by that chapter's `import config` through the
  `sys.modules` cache. `tools.config` is a key no listing can collide
  with. See `tools/repo.py`'s docstring.
* **`data/`** holds the word lists, allowlists, and glob lists the checks
  read (`wordlist.txt`, `norun.txt`, `banned_phrases.txt`, ...), so this
  directory lists code and nothing else.
* **`tests/`** holds the harness's own unit tests, run by `tip tools-test`
  every time and by `tip gate` after its `solutions-gate` prerequisite.
  The gate skips them while `tools/` is unchanged since they last passed
  (`tools/skip_stamps.py` has the policy). They are separate from the book's
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
them. It is deliberately not an inventory of every file: `tip help`
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
tip verify     # every fixer, refresh markers, sync Examples/ and Solutions/, then the full gate but the site
tip ci         # the full local gate: check, ty, ruff, run, pytest, site
```

`tip verify` is the loop to repeat after editing a chapter: every
mutating fixer (the comment-style fixers, import sorting, blank-line
cleanup), then a refresh of the `#:` output markers in both trees, then
a sync of your Markdown changes out to `Examples/` and `Solutions/`
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
at that point, so a target that belongs to two jobs (`check-ch` is an
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

The interactive side of `tip help`, built on `prompt_toolkit` (a project
dependency in `pyproject.toml`, which is how `uv tool install` puts it in
`tip`'s environment; without it `tip help` falls back to the static listing
and says so). A full-screen list of the same sections and doc text:
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
. /c/git/ThinkingInPython/tools/menu_history.sh     # Git Bash, in ~/.bashrc
. ~/ThinkingInPython/tools/menu_history.sh          # Linux/WSL clone, in ~/.bashrc or ~/.zshrc
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
cmd.exe has none. The first run in a menu session then ends with a
line naming the wrapper to source and the profile that should load it. When it finishes, a one-line
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
word: `tip run-one grid_view` binds `grid_view` to `F`. Every step runs
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
never touched. A list of targets never runs (`EXCLUDED` in the script,
each with its reason): the upgrades, the servers, the publishing and GUI
targets, the ones that need a `CH=` selector, and the token-spending AI
passes. Logs land in `build/target_test_logs/`. Each passing
target's time is recorded for the help listing, and the run ends by
rewriting `tools/data/target_tiers.txt`, the committed tier per target
that the listing falls back on for a target this machine has not run.
Commit that file when the run changes it.

## everything.py

`tip verify` skips work that cannot find anything new (see
[skip_stamps.py](#skip_stamps.py)), and no gate runs the spelling and
house-style checks or the book builds. `tip everything` covers all of
it. It sets `TIP_FULL=1`, which turns every skip off in each step it
starts, then runs six targets in order: `verify`, `spell`, `prose`,
`preview-check` (the site build and its link-preview test), `epub`,
and `pdf` (`EVERYTHING` in the script). Unlike `verify`,
it keeps going after a failure. At the end it prints every target's
time, names the ones that failed, and exits 1 if any did. Run it before
a release, after a tool upgrade, or when a shortcut's assumptions are in
doubt.

It needs every tool those targets need: pandoc and typst for the builds,
node for `preview-check`, vale for `prose` (`tip tools-check-full` lists them). Left out on
purpose are `links` (network, and link rot is not the book's fault),
`pyright-review` (advisory), the `rust-*` tasks (cargo), `verify-targets`
(it tests the harness, not the book), and anything that publishes.
`verify-targets` runs `everything` in a disposable worktree, since
`verify` rewrites tracked files.

```
tip everything              # every fixer, gate, and build, no shortcuts
tip everything ARGS=--help  # list the targets without running them
```

## by_hand.py

`tip run` skips every listing in `tools/data/norun.txt`. Among them are
the Tkinter views, which open a window that nothing unattended can
close. No gate executes those files, so a view that raises an exception
at startup or on the first click goes unseen. `tip by-hand` is the check
a person runs instead. It starts every example listed under the
`# [by-hand]` header in `norun.txt` (today the four Tkinter views in
chapters 30 and 38), all at once, each as its own process from its own
chapter directory under `Examples/`, with `utils/` on `PYTHONPATH`. Try
each window and close it. The tool prints a line as each process ends,
then the traceback of each one that exited nonzero, and exits 1 if one
did. Ctrl+C stops whatever is still open.

The header is a comment, so `run_examples.py` and `run_one_example.py`
still skip every pattern in the file. The section runs to the next
`# [name]` header or the end of the file, and entries above it (chapter
6's package submodules) stay out. A pattern under the header that
matches no file is reported as stale. `ARGS=--list` prints what would
start, opens nothing, and exits 1 on a stale pattern, so it can serve as
a check. `verify-targets` leaves `by-hand` out, since it waits for a
person.

```
tip by-hand              # open every by-hand example and wait
tip by-hand ARGS=--list  # list them; exit 1 on a stale pattern
```

## tools_tests.py

The gate's first step: the tools' own unit tests under `tools/tests/`.
Every later step trusts these tools, so a broken one makes the rest of
the gate's verdict meaningless. The suite tests the tools, so while
nothing under `tools/`, `pyproject.toml`, or `uv.lock` has changed since
it last passed, a rerun can only repeat the verdict. In that case the
module runs only the tests marked `book`, the few that read a chapter,
which an edit can break with the tools untouched. A run where every test
is deselected counts as a pass. A full pass records the digest of those
files; [skip_stamps.py](#skip_stamps.py) holds the digest, the stamp,
and the policy. The digest is taken before the suite starts, so an edit
made during the run stays unstamped.

`tip tools-test` passes `--always`, which runs the full suite every time
and refreshes the stamp. `TIP_FULL=1` does the same, so `tip gate
RUN=full`, `tip ci`, `tip release`, and `tip everything` run it in full.
`PYTEST_N=` passes extra arguments to pytest. A new test that reads a
chapter rather than a fixture needs `@pytest.mark.book`, or the skip
hides its failures while `tools/` is unchanged.

```
tip tools-test   # the full suite; refreshes the skip stamp
tip gate         # runs it first, with the skip
```

## verify_targets_wsl.py

`tip verify-targets` starts every task as a new process, and on Windows
that run takes most of an hour. The same run in the WSL clone,
`~/ThinkingInPython`, a clone in the Linux filesystem (the root
`README.md`'s Install section says why it belongs under `~` and not
under `/mnt/c`), took seven minutes on 2026-10-10, because Linux starts a
process about ten times faster. The clone normally pulls from GitHub,
which would mean a push before every smoke test. `tip
verify-targets-wsl` skips the push. It fetches this checkout's `master`
into the clone over `/mnt/<drive>/...`, fast-forwards the clone to it,
and runs `verify_targets.py` there. The output streams here, with the
summary and each failed target's excerpt at the end. What runs is the
last commit on `master`; uncommitted edits in this tree stay out of it.

The clone is for running, never for editing. The script resets the
clone's tracked files first (`git checkout -- .`), because a
verify-targets run leaves `tools/data/target_tiers.txt` and a
self-healed marker or two behind, and a fast-forward refuses to run over
them. A commit made in the clone fails the `--ff-only` merge loudly
instead of being discarded. The task refuses to start where `wsl` is not
on PATH (exit 2), and kills the run after `LIMIT=` minutes (default 40,
about six times the measured run; exit 1). `ARGS=--dry-run` prints the
bash script the clone would run and starts nothing; other `ARGS=` words
go to verify-targets. `verify-targets` leaves this target out of its own
run.

```
tip verify-targets-wsl                     # every task, in the WSL clone
tip verify-targets-wsl ARGS="--only gate"  # the named targets
tip verify-targets-wsl LIMIT=60            # a longer cap, in minutes
tip verify-targets-wsl ARGS=--dry-run      # print the clone's script
```

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

The full gate spends most of its time executing every listing in the
book, almost none of which is about the chapter you just edited. This
runs the same code-example checks scoped to one:

```
tip check-ch CH=12     # or CH=12_Techniques--Data_Classes_as_Types
```

It rebuilds `build/examples/` whole-book first (cheap, and necessary since
a chapter's listings import their siblings), then narrows the expensive
step, `validate_output.py --update`, to that chapter, and finishes with the
listing gates plus `ty`, `ruff`, and `pytest` over that chapter's directory.

## verify_chapter.py

`tip verify` spends nearly all its time on chapters you did not touch.
`tip verify-ch` runs the same loop scoped to one chapter and its Solutions
file, in a few seconds:

```
tip verify-ch CH=28              # or CH=27_Patterns--Function_Objects
tip verify-ch CH=28 ISOLATED=1   # private build trees, for parallel runs
```

The steps mirror `verify`. It fixes line endings, reflows the chapter
and its Solutions file (the gate reflows both trees since 2026-10-25),
regenerates the exercise statements and solution
steps, and rebuilds both build trees whole-book. Then it refreshes both
files' `#:` markers and checks their placement, syncs and drift-checks,
and runs the Markdown gates and `ty`, `ruff`, `run`, and `pytest` over the
chapter's directory. `tools/tasks.py` passes `GATE_CHECKS` through, so the
Markdown checks are the gate's by construction. Every step after the
rebuild runs whether or not an earlier one fails, so one pass reports
every problem.

It writes no gate stamp. A change that can reach other chapters (a renamed
listing, a `utils/` helper, a heading that other chapters cite) still
needs `tip verify`. Two runs at once wipe each other's `build/examples`,
so parallel runs add `ISOLATED=1`, which extracts into
`build/verify-ch-<NN>/`; deleting `build/verify-ch-*` is safe at any time.
The module docstring lists every step.

## Status stamps: gate_stamp.py and tool_stamp.py

Both write to `build/`, which is gitignored, so neither can enter a commit
or dirty a diff.

**`gate_stamp.py` (`tip gate-status`)** records a pass of the gate along
with a hash of every Markdown file in `Chapters/` and `Solutions/`, so it
answers the question that matters after an editing session, which is not
"when did the gate run" but "has anything changed since it did":

```
gate passed 12 minutes ago (2026-07-25 14:03), at commit d6b9ad6
3 file(s) changed since: Chapters/22_Patterns--Iterators.md, Chapters/23_Patterns--Singleton.md, ...
```

**`tool_stamp.py` (`tip tools-status`)** records when `tip tools-upgrade`
last ran. Upgrading is deliberately manual, since it rewrites the tracked
`uv.lock` and can invoke winget or Homebrew, and the cost of that choice is
drifting quietly for months and then meeting every breaking change at once.
So the gate prints one line when the stamp is old. It never fails and never
touches a tracked file, so it cannot turn a green gate red. That line is a
reminder for the author; nothing should act on it automatically.
Run by hand, `tip tools-status` also compares uv, the locked tools, and
the listings' libraries with the latest release on PyPI and marks each
one that is behind; the gate's one line never reaches the network.
When something is behind, it asks whether to run `tip tools-upgrade`,
but only a person at a terminal: a captured, piped, or CI run is never
asked, so nothing starts the upgrade unattended.

## skip_stamps.py

The gate repeats work that rarely finds anything new, so this library
keeps a stamp in `build/` for each kind of work, recording when it last
passed, and the gate skips the work while the stamp still matches. Three
steps use it. The gate skips the tools' own tests while nothing under
`tools/`, `pyproject.toml`, or `uv.lock` has changed since they last
passed (tests marked `book` read a chapter and always run).
`run_examples --quick` runs the listings without `#:` markers, since the
marker refresh executed the rest, and does a full run once a day.
`validate_output --changed-only` (`tip output`) skips a chapter whose
Markdown, `utils/` helpers, and checker modules match the digest recorded
when its markers last passed, and `marker_placement --changed-only` keeps
the same digest in a stamp of its own.

Setting `TIP_FULL=1` turns every shortcut off. `tip ci`, `tip release`,
and `tip everything` set it, and `RUN=full` sets it for one gate:

```
tip gate RUN=full   # one gate with every shortcut off
```

The module docstring has the policy and what each digest covers.

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

The full tier also compares the local pandoc with `PANDOC_VERSION` in
`.github/workflows/ci.yml`, the pandoc CI builds the deployed site
with. CI stopped testing the link previews on 2026-10-24, so
`tip preview-check` tests them locally, and that test covers the live
site only while the two pandocs match. A mismatch prints a note naming
both versions. It leaves the exit status alone, since the fix is to
update the pin after a local pandoc upgrade, not to undo the upgrade.

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
pipx, Homebrew, or winget rather than its standalone installer). `uv tool
upgrade ty` upgrades the globally installed `ty`, the copy bare `ty` on PATH
resolves to; it is best-effort, since not every machine installed `ty` that
way. `uv lock
--upgrade` then `uv sync` upgrade every uv-managed dev tool (`ty`, `ruff`,
`pytest`, `codespell`, ...) to the latest version `pyproject.toml` allows,
rewriting `uv.lock`; review `git diff uv.lock` before committing. `pandoc`,
`typst`, and `vale` are standalone binaries uv does not manage, so this is
best-effort: it tries winget (Windows) or Homebrew, whichever is on PATH,
and falls back to printing the install link if neither works. `git` is
left alone, the one tool `check_tools.py` treats as assumed. For the pinned Python
version itself, use `upgrade_python.py` below instead.

The `tip tools-upgrade` task then runs `tools-check-full`, writes the
upgrade stamp (see `tool_stamp.py` above), lists the prose pins that name
an older `ty` version, and ends with `tip sweep`.

```
tip tools-upgrade   # update uv, global ty, ty/ruff/pytest/..., (best-effort) pandoc/typst/vale, then sweep
```

## upgrade_python.py

Upgrades the pinned development Python and resyncs the environment. With no
argument, `tip python-upgrade` fetches the latest patch of the minor pinned
in `.python-version` (e.g. the newest 3.15.x). With `TO=3.16`, it first
repins: rewrites `.python-version` and the `requires-python` floor in
`pyproject.toml`, then syncs. Either way it finishes by running `tip
verify`. It runs through `uv run --no-project` so the orchestrating
interpreter is never the venv that `uv sync` is about to rebuild.

```
tip python-upgrade           # latest patch of the pinned minor, then verify
tip python-upgrade TO=3.16   # repin to a new minor, then verify
```

## version_pins.py

Some sentences in the book and in the project's instructions name the
`ty` version on which a claim was last checked, as a code span followed
by a three-part version ("`ty` 0.0.87"). `tip tools-upgrade` moves `ty`,
but nothing rewrites those numbers, so after an upgrade each pin keeps
asserting a version nobody has run. `tip version-pins` finds every pin
in every chapter, every Solutions `README.md`, `CLAUDE.md`,
`tools/CLAUDE.md`, `AGENTS.md`, and both copies of the coding-style
skill. It compares each pin with the version `uv run ty --version`
reports and lists the stale ones. Review files, `archive/`, and the
tool-upgrade skill record history, so it leaves them unscanned. The
`TOOLS` table holds one row per tool; today `ty` is the one row.

The report is a to-do list, never a gate: it exits 0 whether or not pins
are stale, and 2 on an error (the installed version is unreadable, or a
keep entry matches no line). By default it reads and reports.
`ARGS=--write` rewrites each stale pin to the installed version, and
writes a file only when a pin in it changed; while an error stands it
writes nothing. Run `--write` after the probes in the tool-upgrade skill
pass, since a bumped pin asserts that someone re-checked the claim on
that version. A historical sentence keeps its version through an entry
in `tools/data/version_pins_keep.txt`, one `path:substring` per line. A
matching line is reported as KEEP and never rewritten. An entry that
matches no line is the error above, so the list cannot rot. `tip
tools-upgrade` runs the report, without `--write`, after it stamps the
upgrade.

```
tip version-pins               # list the stale pins
tip version-pins ARGS=--all    # current and kept pins too
tip version-pins ARGS=--write  # bump the stale pins
```

## libs_check.py

A library module with no task of its own. The dev group in
`pyproject.toml` holds two kinds of package: the tools that check the
listings (`ty`, `ruff`, `pytest`) and the libraries the listings import
(`LIBRARIES`: Stateless, numpy, hypothesis, time-machine). A library
release can change a listing's behavior, a revealed type, or an overload
list the prose quotes, the same way a `ty` upgrade can. Stateless is the
heavy case, since chapters 46 and 47 describe its API in prose.

`current()` reads each package's locked version from `uv.lock`, and
`rows()` asks PyPI for each one's latest release, all lookups at once
with a 10-second timeout. `tool_stamp.py` is the caller. `tip
tools-status` prints each package against PyPI's latest, and `tip
tools-upgrade` records the libraries' locked versions in its stamp under
`build/`. `libs_check.py` writes no file, and an offline machine is no
failure: an unreachable PyPI gives `None`, and the report line reads
"latest unknown". No gate imports it, because a gate that reaches the
network fails for reasons the book did not cause. A library that is
behind is upgraded alone, with `uv lock --upgrade-package NAME`, `uv
sync`, and `tip sweep`, so a failure afterward has one cause. The
tool-upgrade skill's Stateless entry lists what to re-check.

## extract_examples.py

Default mode is **check**: nothing is written. It reports

* examples present in the book but missing from `Examples/`,
* examples whose book text differs from `Examples/`, and
* conflicting duplicates (the same path tagged twice with different content).

It exits non-zero on any of these, so CI catches prose/code drift. Pass
`--write` to materialize `build/examples/` (use `-o DIR` for another target).

Check mode also looks the other way, at *strays*: a file under `Examples/`
that no current block generates, typically left by a rename or deletion.
A stray whose bare filename appears nowhere in the chapter that generates
its directory (the whole of `Chapters/` for a directory with no chapter
behind it, such as `utils/`) is
*orphaned* and fails the check; one still mentioned there (a hand-written
helper) is *referenced* and only reported, since deleting it needs a human.

```
tip sync    # write Examples/ and the .py files in Solutions/ from the Markdown
tip check   # verify the Markdown matches Examples/, Solutions/, rust/, and effects/
tip prune   # delete the orphaned strays check flags, in both trees (never Markdown)
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
tasks that build or run anything in `rust/` or need a Rust toolchain.

```
uv run python -m tools.extract_rust            # check vs rust/
uv run python -m tools.extract_rust --write     # update rust/
```

## extract_effects.py

A third extractor of the same shape, for chapter 44's
[Effect Management](../Chapters/44_Effects--Effect_Management.md)
programs in Koka, Flix, Scala (ZIO), and TypeScript (Effect). A block in
one of those four fence languages whose first line is a `//` comment
naming the file (relative to `effects/`, e.g. `// koka/greet.kk`, the
same `slash_slug` the Rust extractor reads) extracts there; a block in
one of those languages with no path line is a fragment. Default mode is
**check** against the committed `effects/` tree, run by `tip check` and
the gate; pass `--write` (`tip effects-sync`) to update it. It never
touches the project files beside the programs (`package.json`,
`tsconfig.json`, `project.scala`, `expected.txt`).

```
uv run python -m tools.extract_effects            # check vs effects/
uv run python -m tools.extract_effects --write    # update effects/
```

## effects_run.py

Builds and runs the four programs under `effects/`, each with its own
toolchain, feeds each the same name on stdin, and compares its stdout
with `effects/expected.txt`. A toolchain that is not installed is a
skip in the final table, never a failure, unless `--require` (CI's
`effects` job). `--fetch` downloads the pinned `flix.jar` and runs
`npm ci` in `effects/ts`, both into gitignored paths. On Windows it
finds MSVC through `vswhere` for Koka's C step. `effects/README.md` has
the per-toolchain setup; the `effects-*` tasks (`tip effects-all`) are
the only tasks that build or run anything in `effects/`.

```
uv run python -m tools.effects_run                 # what is installed
uv run python -m tools.effects_run --only flix,ts  # a subset
uv run python -m tools.effects_run --fetch         # flix.jar and node_modules
```

## run_examples.py

Runs every `.py` under `build/examples/`, each in its own directory so the
examples' relative data paths resolve. Reports passed / skipped / timed-out /
failed and exits non-zero if anything fails or times out.

`test_*.py` and `conftest.py` are skipped here: they are pytest files, run by
`tip test` (`uv run pytest` over `build/examples` and `build/solutions`), not
as standalone scripts. See the Testing chapter.

* Narrow the run: `uv run python -m tools.run_examples 31_Patterns--State_Machines`
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
tip deque_timing
tip run-one deque_timing
uv run python -m tools.run_one_example Examples/03_Foundations--Containers/deque_timing.py
```

The argument is a path, a file name (`.py` optional), or pieces of the
path: each piece before the last is found, in order, inside a directory
name, the tree's included, so `18/exercise_1` and
`Solutions/47/research_by_hand` each pick one file. A spec matching several
files lists them and exits 2. It reads `Examples/` and `Solutions/`, the
committed trees, so it needs no extract step, and falls back to
`build/examples/` and `build/solutions/`. A Solutions answer gets
`Examples/utils` on its path, since its own tree has no `utils/`.

`tip NAME` reaches it directly when `NAME` is no task: a word ending in `.py`
always, and a bare word or path when it names a listing exactly, so a
mistyped task still gets tip's "no task named" message. Every word after the
name goes to the program.

It supplies the same two things `run_examples.py` does for every example,
the example's own directory as the working directory and the tree's `utils/`
on `PYTHONPATH`, and prints the equivalent `cd` and `PYTHONPATH` commands before running. That
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
uv run python -m tools.run_examples --baseline        # fail only on NEW breakage
uv run python -m tools.run_examples --write-baseline   # regenerate the baseline
```

The book is now fully modernized, so the baseline is **empty** and every run
is a strict pass: every example must run. CI by default only builds and
publishes the site; it runs the examples only when you request the gates
(see "Continuous integration" below). The `--baseline` mechanism remains for
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
tip output         # rewrite stale markers in Chapters/ and Solutions/, changed chapters only
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

## marker_placement.py

A `#:` run belongs directly after the statement that printed it.
`validate_output.py` cannot see a misplaced run. It compares each run with
everything printed since the previous one, so markers gathered at the end
of a listing pass as long as their text is right. `marker_placement.py`
runs each marked block the way `validate_output.py` does, one top-level
statement at a time, and reports every run that sits below a statement
other than the one that printed it.

```
tip marker-placement                # report, both trees
tip marker-placement ARGS=--write   # move the runs
```

Both gates run it with `--changed-only` right after the marker refresh,
and `verify-ch` runs it on its two files; a finding fails the build. In
the gates it reports and leaves the Markdown as it is, because a move can
need a human's eye. `ARGS=--write` rewrites each block with the same
marker text in the new layout. Output from an import goes below the blank line that
closes the import block, since a marker hugging an import fails ruff's
`I001`. A block whose total output differs from its markers is reported
and left alone, so run `tip output` first. The module docstring has the
layout rules.

## check_skip_lists.py

`tools/data/norun.txt` names the listings `tip run` skips.
`tools/data/timing.txt` names the listings whose `#:` markers are
wall-clock claims, which `validate_output.py` must leave as written. Both
hold `fnmatch` patterns over a listing's path, and both go stale when a
listing is renamed or deleted, or a chapter is renumbered. A stale timing
entry is the dangerous one. The listing's timing boolean stops being a
claim, so the gate rewrites its next flip into the chapter with
everything green.

```
tip skip-lists   # fail on a pattern that matches no listing
```

The check matches each pattern against `Examples/` and `Solutions/`; one
file serves both trees, so a match in either passes. The gate runs it
right after the drift check, so the committed trees it reads equal what
the Markdown generates. To clear a finding, correct the pattern to the
listing's new path, or delete it.

## extract_solutions.py

The exact counterpart of `extract_examples.py`, pointed at `Solutions/`
instead of `Chapters/`; it imports and reuses that module's `extract()` and
`is_derived()`, and `tools/extract.py`'s `check_against()` and `write_tree()`,
rather than duplicating them. `Solutions/` is the committed tree (like `Examples/`): each
`Solutions/<chapter>/` holds the authored `README.md` beside the `.py`
files extracted from it. `build/solutions/` is the throwaway tree used for running (like
`build/examples/`). Same two modes: check (default, compares against
the `.py` files in `Solutions/`) and `--write` (materializes a tree, default
`build/solutions/`, or `-o DIR`).

Check mode reports strays the same way `extract_examples.py` does, using
that module's `find_strays()` and `report_strays()`. A file under
`Solutions/` that no block generates is *orphaned* when its name
appears nowhere in that chapter's `README.md` (fails the check) and *referenced*
when it still does (reported for a human). The authored `README.md`
files are the source, so they are never strays, and `--prune` refuses to
delete any Markdown file. A renumbered exercise is the
usual source. The grep covers the solutions alone: a leftover named only
by a chapter is still orphaned here, since no solution block generates it
and the chapter's own copy lives under `Examples/`.

The `tip` targets that cover `Examples/` cover this tree in the same
run: `sync`, `check`, `prune`, `extract`, `output`, `output-check`,
`ty`, `lint`, `run`, and `test` each take both trees (until 2026-09-24
each had a `solutions-*` twin). These targets are Solutions-only:

```
tip solutions-numbering      # every exercise has a solution (below)
tip fix-solutions-links      # insert or correct the chapter's Solutions link
tip statements               # copy each exercise under its solution heading
tip statements-check         # report a statement that differs from its chapter
tip steps                    # fold each hinted solution into steps (below)
tip steps-check              # report steps that differ from what `tip steps` writes
tip hint CH=30 N=3           # reveal the next step of one solution
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
prose has no exercises and needs no `Solutions/` file. And one heading may answer several
exercises at once, written `## 1 & 2. ...`, `## 1, 2. ...`, or `## 1-3. ...`,
which is the right form when two exercises share one worked answer; a heading
with no leading number at all (`## Shared code: the microgrid`) is a preamble
and counts as no answer.

What it cannot see is a solution that answers the wrong exercise under the
right number, which still needs a human reading the two side by side. It runs
first in `solutions-gate`, being the cheapest step and the only one that
notices a missing answer.

It also checks how a solution cites its chapter, which is a trap the layout
sets. A link copied from a chapter, `](23_Patterns--Singleton.md#state)`,
resolves inside the chapter's solutions folder, and the one-level form
`](../Chapters/23_Patterns--Singleton.md#state)` resolves inside `Solutions/`;
both miss, with no warning from anything. Seventeen links were wrong this way
before anything looked. The correct form is
`](../../Chapters/23_Patterns--Singleton.md#state)`, and a leading `./`
marks a deliberate link to a neighboring file.

The check runs the other way too. Each chapter with exercises links its own
Solutions folder from the Exercises section, so a reader browsing `Chapters/` on
GitHub can click through: `Try each exercise before opening its
[solution](../Solutions/<chapter stem>/).` (The hint, shape, and answer
steps are described once, in the Introduction.) The check reports a chapter with
no such link between the last `## Exercises` heading and the first exercise, and
a link that names another folder, which a chapter rename leaves behind. It holds
the link target only, so the author may reword the sentence. `tip
fix-solutions-links` inserts the default sentence where the link is missing and
corrects a stale target, keeping the wording; it is not part of `verify`, since
no tool rewrites `Chapters/` prose on its own. The builders rewrite the link in
`build_site.link_solutions()`, which `load_chapter()` calls: on the site it
points at the chapter's `<stem>.solutions.html`, and in the EPUB and PDF,
which carry no Solutions pages, at the GitHub URL.

`heading_links.py` covers the other half. The gate now runs its `anchors`
check over `Solutions/` as well (see `GATE_DOCS` in `tools/tasks.py`), which
catches an anchor that names no heading in whatever file it does reach; three
of those were dead in `Solutions/` for the same "nothing looked here" reason.
Neither check sees an anchorless link to a file that exists, so the two
together are the coverage: `check_solutions.py` for the missing prefix,
`heading_links.py` for the anchor.

## exercise_statements.py

A solution with no exercise above it sends the reader back to the chapter,
and a solution that answers the wrong exercise under the right number is hard
to see. `check_solutions.py` compares the numbers alone.

This copies each statement from the chapter into `Solutions/` as a block
quote directly under the matching `## N.` heading. The chapter is the single
source of truth: the quote is generated, and every run rewrites it. A combined
heading (`## 1 & 2.`) quotes each exercise it names, kept as the list item
the chapter writes, with a bare `>` line between them. Headings with no
leading number, and numbers that name no exercise, get nothing.

```
tip statements                 # rewrite every Solutions file
tip statements ARGS=19         # only chapter 19
tip statements-check           # report drift, change nothing
```

Two edits happen inside the copy. A chapter-relative link gets the
`../../Chapters/` prefix that `Solutions/<chapter>/README.md` needs
(`](#anchor)` and a bare
`](17_Techniques--Metaprogramming.md#x)` both resolve from the new place), and
a footnote reference `[^label]` is dropped, since its definition stays in the
chapter. A statement ends at the next item, a heading, or any line in column
0, so the footnote definitions that follow the last exercise in some chapters
stay out of it.

`gate` runs `tip statements` twice, so the copy self-heals the way reflow and
the `#:` markers do: once before the `anchors` check, which reads `Solutions/`
and would otherwise fail on a link a renamed heading left stale, and once
after the reflow, which can rewrap a chapter's exercise lines.
`verify-ch` runs it for its chapter. `exercise_refs.py` skips the generated
lines, so the baseline counts each reference once.

## solution_steps.py

A solution gives everything away at once. This folds each solution that
carries a `Hint:` paragraph (the first paragraph after the generated
exercise quote) into a ladder of nested HTML `<details>`, which GitHub and
the site render collapsed: "Where to look" (the hint), then "The shape"
(each listing reduced to its imports, aliases, constants, classes, and
signatures, every function body replaced by `...`), then "Solution"
(everything else, as authored). Nesting orders the steps: each toggle
stays hidden until the step above it is open. A solution with no
`Hint:` paragraph is left as it is.

A paragraph beginning `Done when:` directly after the hint adds a fourth
step, "Done when", between "The shape" and "Solution". It states what you
can check to know your attempt is finished: a test file to run, the
output to match, a `ty` diagnostic that must disappear. The criterion is
authored; a `Done when:` paragraph anywhere else is ordinary prose.

Every "Solution" step ends with a generated paragraph, `DIAGNOSIS`, that
asks you to name what separates your attempt from the model solution: a
different design, a detail, or an equivalent alternative. Readers handed
a model solution match its surface features unless something forces a
judgment, and the three categories are the ones `AGENTS.md` gives a
reviewing agent.

```
tip steps                      # rewrite every Solutions file
tip steps ARGS=30              # only chapter 30
tip steps-check                # report drift, change nothing
tip hint CH=30 N=3             # the next step, at the command line
```

The tags and the shape blocks are generated and replaced on every run,
the way `exercise_statements.py` replaces the quote; `gate` and
`verify-ch` run it, so they self-heal. The authored prose and listings
round-trip byte for byte: a run strips the tags, the shape blocks, and
the diagnosis paragraph, restores the `Hint:` and `Done when:` prefixes,
and nests the section again. A shape block's
first line is `# The shape of <path>`, which no extractor reads as a path,
and it carries no `#:` marker, so `extract_solutions.py` and
`validate_output.py` leave it alone; a `test_*.py` listing gets no shape.

`hint.py` prints the same ladder one step per run, keeping its place in
`build/hints.json`; `--reset` starts over and `--all` prints every step.
On the site, `resources/static/solutions.js` remembers which steps a
reader opened and offers to hide them all, and `solutions.css` draws the
summary rows as steps; without the script the native elements do the
same job without the memory.

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

Runs the AI editing passes over one chapter's prose, in place, or over
several chapters in parallel (`CH="25 28"`, `CH=30-40`). Each pass is
one headless `claude -p "/<skill> <chapter>"` run of a skill (from
`.claude/skills/` or an installed plugin) with `--permission-mode
acceptEdits`, scoped by an appended system note to the chapter's prose
(never a fenced block or a `#:` marker, never git). After every pass the
chapter is reflowed and the cheap prose gates run (`banned_phrases.py`,
`heading_links.py`, the `extract_examples.py` drift check), so a pass that
touched a listing or broke a link fails right there. The chain stops at the
first failure.

```
tip rewrite CH=25                        # the seven default passes (ARGS=--list shows them)
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

Several layers, all optional and not part of the default CI gate. The local
gate runs one of them, prose_lint.

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
one blank line in a row, a period or comma left outside a closing quote,
trailing whitespace (a two-space hard break is allowed), "fix" meaning "set"
(`SET-FIX`), and a "raises" with no object (`BARE-RAISE`). It shares the
`tools/prose.py` classifier with `reflow_prose.py`, so fenced and indented code,
tables, blockquotes, and HTML are skipped, and inline code spans and footnotes
are ignored inside a prose line; headings and list-item text are checked but
their markers are not. It exits non-zero on any finding, and it runs in the
gate (`prose-lint` in `GATE_CHECKS`). Run
it directly with `uv run python -m tools.prose_lint Chapters` (or a single file).

The quote check reads a quoted *literal* differently from quoted prose. The book
puts the mark inside a quoted phrase (`"easier to ask forgiveness than
permission,"`) but outside a literal, where moving it in would put a comma into
a `pytest -k` substring or a period into an error message the reader matches
against. A quote holding an inline code span, and a single-token quote whose
token also appears in a code span on the same line (`"overdraft"` beside
`pytest -k overdraft`), are therefore skipped. A multi-word literal fits neither shape,
so write that one as an inline code span rather than as a quotation.

**House style: Vale (`tip prose`).** Vale is a standalone binary, not a Python
package, so install it once (`winget install errata-ai.Vale`,
`brew install vale`, or see <https://vale.sh/docs/install>). Vale parses Markdown
and checks only text, never code spans or fenced code, so the rules never fire on
identifiers or examples. Spelling is left to codespell; Vale enforces house style
only. The nine rules live in `styles/House/` and are wired up by `.vale.ini`:

* `EmDash` (error): no `—`, `–`, or `--` used as a dash.
* `Filler` (warning): throat-clearing phrases ("this is the whole idea", and so on).
* `InOrderTo` (warning): "in order to" where a bare "to" says the same.
* `NoChain` (warning): a "no X, no Y, no Z" chain of three or more.
* `Nominalization` (suggestion): an action hiding in a noun ("performs a lookup").
* `UsedTo` (warning): a past-habitual "used to" in place of a dated earlier state.
* `WeakVerb` (warning): a weak-verb frame ("is used to preserve").
* `Weasel` (warning): the words that are vague in this book.
* `WholePoint` (warning): an "is the whole/entire X" closer.

The community packages for usage checks are listed in
`.vale.ini` (`Packages = write-good, proselint`); `tip prose` runs `vale
sync` to download them into the gitignored `styles/` the first time, when
that directory has no `write-good`. write-good's `Passive` rule is off in
`.vale.ini`; `tip passive` replaces it.

After Vale, `tip prose` runs twelve report-only scans, each with a
baseline of judged keeps: stranded prepositions, stranded possessives,
watch words, positional references, italics, trailing tags, subject gaps,
sentence shapes, passive voice, past tense, expletives, and internal names.
Each has an entry below, under "Report-only prose scans" and "The spaCy
parse".

## Report-only prose scans

`tip prose` runs Vale and then a family of literal scans, each aimed at
one shape the style guide rules out. No gate runs them. A word-pattern
heuristic finds false alarms beside real faults, which a human tells
apart. Vale runs first. A Vale error stops `tip prose` before the scans,
so each scan also has a task of its own. `tip everything` includes
`tip prose`. The parse-based scans that `tip prose` runs after
these (subject gaps, sentence shapes, passive voice, past tense,
expletives) share one spaCy parse and have an entry of their own.

Each scan keeps a baseline in `tools/data/` of the hits a human read and
judged keeps, so a run prints the new hits, then any `stale` entry (a
baseline entry for a scanned file that matches no current hit), then a
summary line, `N new, M accepted`, with a stale count when there is one.
An entry holds the path and the clause or sentence with its whitespace
normalized and no line number, so a reflow leaves it in place. An edit to
the clause retires the entry, and the rewritten clause reports as NEW.
To act on a hit, fix the prose, or judge it a keep and run
`tip <name>-accept`, which appends every NEW hit to the baseline and
drops the stale entries.

`CH=` picks a chapter by number or stem prefix and passes that chapter
and its Solutions file (`Chapters/<CH>*.md`, `Solutions/<CH>*/README.md`)
to the scan; with no `CH=` a scan reads all of `Chapters/` and
`Solutions/`. The `-accept` tasks pass the same files. A run given
paths compares against those files' baseline entries alone, so
`tip stranded-accept CH=33` adds and drops entries for chapter 33
and its Solutions file and leaves every other file's entries alone.
`ARGS=--all` on a report task lists every hit, marked NEW or accepted,
and `ARGS=--fail` exits 1 on a NEW hit. `tip prose` passes no `ARGS` to
the scans.

```
tip prose CH=30             # Vale, then every scan, on one chapter
tip stranded CH=30          # one scan alone
tip stranded CH=30 ARGS=--all
tip stranded-accept CH=30   # baseline the new hits after reading them
```

## stranded_prepositions.py

Lists a clause that ends on a preposition whose object moved or went
missing ("the field they sit on", "what it is for"). The scan joins each
paragraph's lines, splits the text into clauses at `.`, `,`, `;`, `:`,
`?`, and `!`, and reports a clause whose last word is in `PREPOSITIONS`.
It skips a phrasal verb whose pronoun object sits before the particle
("turn it on", "passes `x` through") and the idioms in `IDIOMS` ("and so
on", "as before"). Inline code spans become the placeholder `CODE`, so
"refers to `x`" is no hit. Fenced listings, headings, block quotes,
tables, HTML, link definitions, and `#:` lines are skipped. The
possessive, watch-word, italics, and trailing-tag scans reuse this
module's paragraph reader, so they skip the same input. The
module docstring lists the false-positive shapes left for a human (an
infinitive marker closing a clause, a phrasal verb with no pronoun).
Front the preposition, restructure the sentence, or use a transitive
verb. The baseline is `tools/data/stranded_baseline.txt`.

```
tip stranded CH=30          # new hits
tip stranded-accept CH=30   # baseline the judged false positives
```

## stranded_possessives.py

Lists a possessive whose head noun is elided ("the subclass's type, not
the base's"), the possessive cousin of the stranded preposition (a style
rule since 2026-10-14). A word ending in `'s` or `s'` is a hit when clause
punctuation, the end of the paragraph, or a function word from
`FUNCTION_WORDS` follows it; the contractions in `CONTRACTIONS` ("it's",
"let's") are skipped. A code span after the possessive counts as its noun
("the wrapper's `__dict__`"). Restore the noun or restate the sentence.
The baseline is `tools/data/stranded_possessives_baseline.txt`.

```
tip possessives CH=30          # new hits
tip possessives-accept CH=30   # baseline the judged false positives
```

## watch_words.py

Lists the words in the style guide's three watch tiers, matched as whole
words and phrases, case-insensitively, with the tier label on each
hit. `[T3]` ("Don't use": `ships`, `lands`, `wants`, and the other
metaphors) is a defect unless a human reads it as literal. `[T2]`
("Avoid if possible": `already`, `even`, `never`, the commerce family,
and the who-does-it family `by hand`, `manually`, `explicit`,
`explicitly`, since 2026-10-25)
stays where the word changes the meaning. Tier 1 ("Consider
rewriting": `only`, `itself`, `once`, `names`, and the rest) is
advisory. A default run
leaves it out of the report, the `new` count, and `--fail`. Two literal
senses are skipped: the arithmetic `even` and a `hook` near `git`,
`pre-commit`, `SessionStart`, or `Claude`. `ARGS="--tier 3"` prints one
tier, `ARGS="--tier 1"` or `ARGS=--all` shows Tier 1, and `ARGS=--fail`
exits 1 on a new Tier 3 hit alone. `tip watch-words-accept` baselines
the new Tier 2 and Tier 3 hits. That task passes no `ARGS`, so
baselining Tier 1 hits takes the module's `--accept --tier 1` directly.
The baseline is `tools/data/watch_words_baseline.txt`.

```
tip watch-words CH=30                    # new Tier 2 and 3 hits
tip watch-words CH=30 ARGS="--tier 1"    # the advisory tier
tip watch-words-accept CH=30             # baseline the judged keeps
uv run python -m tools.watch_words --accept --tier 1 Chapters/30_*.md
```

## positional_refs.py

Lists prose after a listing that points at a line by position ("the
second `print()`", "the last line", "line 3") or by a construct the
listing holds more than once ("the `for` loop" beside two `for`s), the
shapes the `# [n]` tag convention replaces (see `listing_tags.py`). A
listing's region runs from its closing fence to the next fence or
heading, as in `listing_tags.py`. A sentence that cites a `` `[n]` ``
tag is skipped. Six patterns match; the construct pattern counts the
keyword in the listing's code and reports the count (`construct x3`).
The noun list leaves out "argument", "version", and "element", so an
ordinal naming a parameter, a variant, or data draws no hit. A runtime
order ("the second `run()`") still matches and goes in the baseline as
a keep. Tag the line, or name the construct when the listing holds
one. The baseline is `tools/data/positional_refs_baseline.txt`.

```
tip positional CH=30          # new hits
tip positional-accept CH=30   # baseline the judged keeps
```

## italics.py

Lists italics that break the rule that italics introduce a term once.
`[EMPHASIS]` is a span made of function words ("*is*", "defers *how*"),
`[REPEAT]` a term italicized again in the same file, and `[EARLIER]` a
term italicized after the file's prose used it without italics, with a
trailing "s" or "es" tried both ways. All three rules skip pattern
names, which are italic on every mention. `[REPEAT]` and `[EARLIER]`
also skip capitalized titles and spans under three letters. Run over
the 15 chapters as they stood before the 2026-10-23 hand sweep (commit
cd9c4045), the scan flagged 32 of the 38 lines that sweep changed; a
verb or adjective stressed at first use is beyond it. Remove the
italics, or baseline a defining sentence for a term the earlier prose
used loosely. The baseline is `tools/data/italics_baseline.txt`.

```
tip italics CH=45          # new hits
tip italics-accept CH=45   # baseline the judged keeps
```

## trailing_tags.py

Lists two shapes from rules R32 and R35 in `bruce_edit_db.md`, marked in
chapter 31 on 2026-10-18, with the rule label at the front of each hit.
`[R32]` is a clause whose last comma-separated segment is a past
participle plus a measure or place from `MEASURES` ("belongs in that
state's row, written once"), the word "unchanged", or "the same" plus a
few words. `[R35]` is a transactional connective from `CONNECTIVES`
anywhere in a clause ("in return", "the trade-off", "the cost of").
Every "the cost of" and "the price of" is reported, and the baseline
holds the measured ones. Clauses split at `.`, `;`, `:`, `?`, and `!`,
since R32 reads the segment after the last comma. A participle that
describes the noun before it is a typical keep. The baseline is
`tools/data/trailing_tags_baseline.txt`.

```
tip trailing CH=31          # new hits
tip trailing-accept CH=31   # baseline the judged keeps
```

## overclaims.py

Lists clauses that bound a set with a count or exclusivity word (`[BOUND]`):
"one restriction", "the only way", "nothing else", "all it does", "alone".
The test a reader applies is whether the text can point at a second member
of the set; if it can, the bound is an overclaim. The patterns live in
`PATTERNS` and `NOUNS`. The baseline is `tools/data/overclaims_baseline.txt`.

```
tip overclaims CH=45          # new hits
tip overclaims-accept CH=45   # baseline the judged keeps
```

## internal_names.py

Lists public class names that nothing outside their class uses, each a
candidate for a leading underscore. Unlike the rest of the family it
reads code: every class under `Examples/<chapter>/` and
`Solutions/<chapter>/`, collecting each method, property, class
attribute, class-body annotation, and `self.x` store. A name counts as
used when `.name` or `name=` appears in the chapter's code outside the
class's own lines, or when the name sits in a code span of the
chapter's Markdown or its Solutions README. Record fields (class-body
annotations of a `@dataclass`, `@record`, or `NamedTuple` class) are
skipped by design. A hit prints as
`path:line: Class.name (kind, N references inside the class)`. The baseline,
`tools/data/internal_names_baseline.txt`, keys an entry as
`path::Class.name` and holds the judged keeps: stored constructor data,
table-driven names, double-dispatch legs, introspection demos. Add the
underscore in the listing's Markdown block (`Examples/` and `Solutions/`
are generated from it), or accept the hit.
The scan always reads the whole book, so neither task takes `CH=`.

```
tip internal-names          # new hits, whole book
tip internal-names-accept   # baseline the judged keeps
```

## bare_raise.py

Lists a "raise" word with no object in the prose of `Chapters/` and
`Solutions/` (or the files given in `ARGS`): "raise", "raises",
"raised", "raising", and "re-raise", followed by clause punctuation or
a word from `NOT_AN_OBJECT`. It joins each sentence across line breaks
first, so a verb at a line end whose object opens the next line is no
hit. A verb after an article and one whose object comes first ("the
exception it raises", "what they raise") are skipped. `tip bare-raise`
runs it. The task sits under "Style gates" in `tip help`, but neither
a gate nor `tip prose` runs it. It keeps no baseline. The gated form of
the same rule is `prose_lint.py`'s `BARE-RAISE` (since 2026-10-21),
which the gate runs over `Chapters/` through `check_all.py` and
`tip spell` runs over both trees. The two matchers differ. `BARE-RAISE`
skips "raised" as passive and excuses a verb at a line end, while
`bare_raise.py` reads "raised" and joined sentences, so it finds
"raised inside" and similar shapes the gate passes, beside false alarms
of the non-exception sense ("the limit raised to"). Read each hit and
give the verb an object where it means raising an exception.

```
tip bare-raise                               # both trees
tip bare-raise ARGS=Chapters/42_Functional--Error_Handling.md
```

## The spaCy parse: spacy_parse.py, parsed_prose.py, parse_check.py

Seven report-only prose checks read a dependency parse instead of matching
word patterns. Five run in `tip prose` against a baseline, and two are
surveys that run alone. A whole-book parse takes about 24 seconds, so the
seven share one, and these three modules hold what they have in common.

**`spacy_parse.py`** is the parser half. The book pins a Python for which
spaCy publishes no wheel, so this file runs in a separate environment:
`parsed_prose.py` starts it with `uv run --no-project --python 3.12 --with
spacy ...` (`PARSER_CMD`, which pins spaCy 3.8 and the `en_core_web_sm`
3.8.0 model wheel). It reads paragraph texts as JSON on stdin and writes
each sentence's token table (text, lemma, part of speech, tag, dependency
label, head, character offset, morphology) as JSON on stdout. Since it
runs outside the project, it imports nothing from `tools/`. uv caches the
environment. The first run downloads an interpreter, spaCy, and the
model, which takes a minute or so, and later runs start in a few seconds.

**`parsed_prose.py`** is the half the checks call. `parsed()` reads each
document's paragraphs through `stranded_prepositions.py`'s reader
(listings, headings, block quotes, tables, HTML, and `#:` lines are
skipped, an inline code span becomes the placeholder `CODE`, and a
paragraph's lines are joined), parses them, and returns typed `Paragraph`,
`Sentence`, and `Token` records. Each document's parse is kept in
`build/parses/`, one JSON file per document named for its path
(`Chapters__31_Patterns--State_Machines.md.json`), with a hash of the
document's paragraph texts. A document whose hash matches is read from
its file. Every paragraph of the other documents goes to one parser call,
so a run with stale documents starts one subprocess, and a run with none
starts no subprocess. The hash covers the text alone, so a spaCy or model
upgrade leaves the cache looking current: delete `build/parses/` after
one. The directory is derived, so deleting it is always safe. The module
also holds the token-table helpers the rules share (`finite()`,
`children()`, `subtree()`, `subject_of()`, `conj_verbs()`,
`coordinator()`).

When the environment cannot start (no `uv` on `PATH`, or no network on a
first run), `parse()` raises `ParserUnavailable`. Each check catches it,
prints `<name>: parser unavailable (...); nothing checked` to stderr, and
exits 0, so `tip prose` goes on to the next scan.

**`parse_check.py`** holds the rest. `run()` is a baselined check's whole
default run: read the files, call the check's rule, apply the baseline,
then print the report or, under `--accept`, rewrite the baseline. The
baseline mechanics are the ones the section above describes.
`build_arg_parser()` gives every check the same command line: paths,
`--fail` (exit 1 on a NEW hit, or on any hit for a survey), `--all` and
`--accept` for a baselined check, and `--survey` and `--calibrate` where a
check has them. `PROSE_CHECKS` lists the five checks `tip prose` runs, in
order. The module docstring ends with the steps for adding a check.

Two conventions run through the checks. A survey rule finds a shape that
the author's own rewrites carry about as often as the originals, so each
hit is a question for an editing pass rather than a fault. A baselined
check prints its survey rules under `ARGS=--survey` alone, each line
marked `survey`, never written to the baseline and never counted in
`N new`. `pointer_words.py` and `negation_density.py` are surveys
through and through, with no baseline. `ARGS=--calibrate` shows whether a
rule separates bad prose from good. It parses the `before` and `after`
text of each record in `tools/data/edit_pairs.json` (sentences the author
rewrote) and prints, per label, the pairs where the rule fires on the
before text alone, on both, and on the after text alone. A default rule
should fire on the originals and stay quiet on the rewrites. Most checks
then print their built-in examples with the result each should give, and
`passive_voice.py` and `expletives.py` also compare their hits with a
Vale rule. The edit pairs and examples are parsed without the cache.

The tests start no spaCy. Each `tools/tests/make_<check>_parses.py`
records the real parse of its fixture paragraphs into
`tools/tests/data/<check>_parses.json`, and the tests read it through that
module's `recorded_parser()`. Rerun a recorder after a spaCy or model
upgrade, or after changing its `SOURCES`, then run `tip tools-test`.

```
uv run python -m tools.tests.make_passive_voice_parses  # rerecord
```

## subject_gap.py

Lists a sentence whose subject is held open from its verb: the subject
head carries a relative clause, a participle, a "such as" phrase, a
prepositional chain, or an appositive, and the finite verb arrives nine
or more words later ("an action that must run on every entry into that
state appears once", the chapter 31 sentence that started it on
2026-10-18). The `straighten` skill calls the shape "the subject held
open". A hit prints as `path:line: [kinds] subject .. verb: sentence`,
where `kinds` are the dependency labels of the subject's postmodifiers
(`relcl`, `acl`, `prep`, `appos`, `conj`). The repair moves the modifier
after the verb, turns it into a when-clause, or gives it a sentence of its
own; commit 0fc6e04d has 37 examples. Keeps go in
`tools/data/subject_gap_baseline.txt`: coordinated subjects, a short
appositive, a relative clause that is the claim and reads once, and a
parser misreading. `tip prose` runs it, and no gate does.

```
tip subject-gap CH=31            # new hits, chapter and Solutions
tip subject-gap ARGS="--gap 12"  # a different threshold for one run
tip subject-gap-accept CH=31     # baseline the judged keeps
```

## sentence_shapes.py

Finds four sentence shapes from the style rules. Two are default rules,
held to `tools/data/sentence_shapes_baseline.txt`: `[IMP]`, a command
plus its consequence ("Remove `frozen=True` and the pattern fails"), and
`[COLON+AND]`, a colon followed by a clause whose verb joins a second
clause with its own subject through "and". Two are survey rules: `[AND]`,
an "and" that joins two clauses with different subjects, and `[COLON]`,
a colon followed by an independent clause. A colon after a count or a
demonstrative ("three parts:", "this shape:") is skipped. Two imperatives
in a row ("Try the operation and handle the exception") are no hit, since
the second verb has no subject. In calibration `[AND]` fired on 7 pairs'
before text alone, 1 on both, and 6 on the after text alone, so its hits
are judgments made per sentence. `tip prose` runs the default rules.

```
tip sentence-shapes CH=31                # new default hits
tip sentence-shapes CH=31 ARGS=--survey  # plus [AND] and [COLON]
tip sentence-shapes ARGS=--calibrate     # all four, edit pairs
tip sentence-shapes-accept CH=31         # baseline the judged keeps
```

## passive_voice.py

Lists each passive clause: a verb with a passive auxiliary and a passive
subject, a relative clause ("a value that is written once") and a
get-passive included. `[PASSIVE]` names no actor. `[PASSIVE+BY]` writes
the actor out in a by-phrase, so the sentence could make that actor its
subject; it is the form most often worth turning around. A bare
participle ("a value stored in the class") and an adjective after "be"
("is unchanged") are no hit. Vale's write-good `Passive` rule matches by
word pattern and flags that adjective, so `.vale.ini` turns it off (since
2026-10-19), and this check replaces it. Keeps go in
`tools/data/passive_voice_baseline.txt`: an unknown actor ("Java is
statically compiled"), a quoted diagnostic, a naming convention ("is
called *Multiton*"), and a parser misreading. `ARGS=--calibrate` compares
the check with the edit pairs and with Vale's `Passive` alerts (it runs
`vale` over the book and skips that half when `vale` is missing).

```
tip passive CH=31              # new hits
tip passive ARGS=--calibrate   # edit pairs, then Vale comparison
tip passive-accept CH=31       # baseline the judged keeps
```

## past_tense.py

Holds standing behavior to the present tense. It finds a simple-past
verb, or a participle with a past auxiliary ("was built", "had loaded");
a present perfect ("has loaded") is no hit. `[PAST]` is the past verb of
a main clause ("One design served three jobs in this chapter").
`[PAST-HEADING]` is a past verb in a heading ("What Stayed Constant"),
which the check reads from the heading lines, since the paragraph reader
skips them. Both are held to `tools/data/past_tense_baseline.txt`.
`[PAST-SUB]`, every other past verb, is a survey rule: the first run on
2026-10-19 found 1283 hits, nearly all subordinate ("the function the
caller passed"), which refer back inside present narration. A sentence
with a year, a version number, a PEP number, or the modal "would",
"could", "might", or "should" is skipped, and so are a verb inside
double quotes, a main-clause past whose subject is "I" or "we", and the
subjunctive "were" in a sentence that opens with "If" or "When". Keeps
are a narrated run, a measurement, and history without a year.

```
tip past-tense CH=31                # new [PAST] and [PAST-HEADING] hits
tip past-tense CH=31 ARGS=--survey  # plus [PAST-SUB], for an activate pass
tip past-tense ARGS=--calibrate     # edit pairs and built-in examples
tip past-tense-accept CH=31         # baseline the judged keeps
```

## expletives.py

Lists the empty frames the style rules exclude. `[THERE]` is the
existential "there" in any position ("there is", "if there were",
"there is no X"): a "there" with dependency `expl` whose verb has no
subject of its own. That second test separates it from a place adverb
the parser also labels `expl` ("Caching there is one way"). `[IT-IS]` is
the extraposed frame, "it is easy to add" or "it is true that": "it"
with a form of "be" whose adjective carries an infinitive or a
that-clause. The check has no cleft rule, because the parse cannot tell
"it is X that" from "it is a NOUN that" with a real antecedent.
Vale's write-good `ThereIs` stays on, and it matches a sentence-initial
"There is/are" alone, so this check adds the mid-sentence cases. Keeps go
in `tools/data/expletives_baseline.txt`: an `[IT-IS]` "it" with a real
antecedent, a quotation the quote count missed, and a mislabeled place
adverb with no subject beside it.

```
tip expletives CH=31              # new hits
tip expletives ARGS=--calibrate   # edit pairs, examples, and Vale's ThereIs
tip expletives-accept CH=31       # baseline the judged keeps
```

## pointer_words.py

A survey for the `antecedents` skill, outside `tip prose`, with no
baseline. It lists each sentence that opens with a pronoun used as a
subject, after any opening adverb or conjunction. `[THIS]` is a
demonstrative ("This is the fast path") and always prints. `[IT]` is "it"
or "they", and it prints when the previous sentence of the paragraph
holds two or more nouns of matching number, which the line names as
candidates (`it -> proxy, level`), or when the pronoun opens the
paragraph. The calibration fired about as often on the author's rewrites
as on the originals (`[THIS]` 1 before alone, 0 both, 2 after alone;
`[IT]` 1, 0, 1), so each line is a candidate for that pass to judge. A
pronoun whose target the sentence and the paragraph's topic make clear
stays.

```
tip pointers CH=31             # every hit, to start an antecedents pass
tip pointers ARGS=--calibrate  # edit pairs and built-in examples
```

## negation_density.py

A survey for the `positive` skill, outside `tip prose`, with no baseline.
It counts the style rule's family of negatives per paragraph: the
parse's `neg` dependency; no, none, nothing, never, without, unless, and
cannot; verbs such as omit, lack, fail, and skip; and un-, non-, and -less
words, minus stop lists for words such as "under", "unique", and
"regardless". The restrictive "only" is counted apart. A paragraph at
three or more, "only" aside, prints as `[NEG n +k only] word, word x2:
text`, and a table follows with each file's negatives per 1000 words and
a line `N paragraphs at >= 3 in F files`. A listed paragraph is a
candidate: the `positive` pass keeps a negation that is the claim or half
of a real contrast. `ARGS=--calibrate` sorts the edit pairs into FEWER,
SAME, and MORE negatives after the author's rewrite.

```
tip negatives CH=31                    # paragraphs at 3 or more
tip negatives ARGS="--threshold 4"     # a different threshold
tip negatives ARGS="--top 20"          # the 20 densest paragraphs
tip negatives ARGS=--calibrate         # edit pairs and the rule's examples
```

## check_all.py

The checks below each have their own script and their own `tip` target,
which is what you want when one thing is broken and you are iterating on
it. Running them one at a time means an interpreter startup and a fresh
parse of all 49 chapter files (47 chapters and two appendices) per tool,
and N summaries instead of one answer to
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
its findings were cleared. `tip checks` runs the same registry. The
Vale prose lint is `tip prose`, which the gate leaves out because
Vale is a standalone binary rather than a uv-managed one.

## check_line_endings.py

`.gitattributes` (`* text=auto eol=lf`) already keeps committed blobs LF on
every platform, so the repo and the Linux CI build are always LF. This tool
guards the **working tree**: on Windows an editor can write CRLF into a source
file, which is harmless to git but produces noisy warnings and inconsistent
local files. `tip eol` reads `git ls-files --eol` (so it honors the binary
markers in `.gitattributes`) and fails if any tracked text file has CRLF or
mixed endings. It is part of the `tip ci` gate. The gate converts nothing,
but `tip verify` runs `fix-eol` before it; elsewhere, run the fixer
explicitly when the check flags something:

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
the `tip ci` gate. Like line endings, the gate fixes nothing, but `tip verify`
runs `fix-listings` before it:

```
tip listings       # check, exit 1 on extra blank lines (part of `tip ci`)
tip fix-listings   # remove the offending blank lines
```

Do not run `ruff format` on the examples: it would re-expand to two blank lines
between top-level defs and undo the density. The gate runs `ruff check` (the
linter) only, which is happy with one blank line.

## listing_width.py

Fails if any line of a ```python block in `Chapters/` or `Solutions/` is
wider than 60 characters, so listings fit phones and e-readers. It
measures the Markdown, so it covers fragment blocks, which ruff never
sees, and every `#:` marker. A trailing `# type: ignore` pragma is the one
sanctioned overflow. A marker wider than the limit means the program's
own output needs shortening. It is `widths` in `GATE_CHECKS`, and the gate
runs it over `Solutions/` as well. The fix is a judgment call: wrap the
statement, move a comment to its own line or into the prose, or change
what the program prints.

```
tip widths    # check (part of the gate through GATE_CHECKS)
```

## code_width.py

`listing_width.py` (`tip widths`, and `widths` in `GATE_CHECKS`)
enforces the 60-character limit. `tip code-width` answers a different
question: what would break at another width, when weighing a narrower
limit, an e-reader column, or a code font size. It is a survey, never a
gate, and exits 0 whatever it finds. It measures every line of every
Python block in `Chapters/` and `Solutions/` by its raw rstripped
length, with no pragma exemption, since the question is what a reader's
screen has to fit. `WIDTH=` (default 60) sets the threshold for the
printed count and for `--tsv`, and where the page's slider starts.

By default it writes `build/reports/code_width.html`, a self-contained
page grouped by chapter. Each row gives the extracted file and line
(under `Examples/` or `Solutions/`, or `(fragment)` for a block the
extractor never writes), the Markdown line, the width, and the line with
the overflow highlighted. The page carries every line wider than 40
columns, so its slider (40 to 80) re-filters live without another run.
Lines past the gate's 60 are marked apart from those merely over the
slider's value. One checkbox, on by default, hides the lines the gate
forgives (those that fit once a trailing `# type: ignore` is excluded),
using `listing_width.py`'s own measure so the two agree. A second, off
by default, keeps only the lines that a comment carries over the width.
A `#:` marker counts as program output, never as a comment.

When stdout is a terminal, the script also opens the page in the browser
and stays up as a small HTTP server on 127.0.0.1 until Ctrl+C. A click
on a row asks that server to run the Zed CLI, `zed path:line`, which
opens the chapter at that line; the row's file cell opens the extracted
file instead. The server opens files under the repo and refuses any
other path. It finds Zed through `$ZED`, then `zed` on PATH, then Zed's
per-user install location. Piped or captured, the script writes the
page, prints the count and the path, and exits, which is how
`verify-targets` runs it. `ARGS=--no-open` and `ARGS=--open` override
the terminal test. `ARGS=--tsv` prints one tab-separated row per line
(code location, Markdown location, width, line) and writes no page.

```
tip code-width                  # page of lines over 60; serve and open it
tip code-width WIDTH=50         # what would break at 50
tip code-width ARGS=--no-open   # write the page only
tip code-width ARGS=--tsv       # tab-separated rows, for cut or a sheet
```

## listing_tags.py

Prose that walks a listing line by line points at a line with a numbered
tag: a trailing comment `# [1]`, `# [2]`, and so on, on the code line (or
alone on the line above it, when the line is too long to carry it). The
prose cites the tag as a code span, `` `[1]` ``. `tip listing-tags` fails
on four things: tags that break the 1, 2, ..., n sequence, a tag that the
prose below the listing (up to the next block or heading) leaves uncited, a
`[n]` code span that names no tag in the listing above it, and a bracketed
tag number in prose outside a code span. The last rule exists because the
EPUB and PDF concatenate every chapter, where one stray `[n]:` reference
definition would turn every bare citation in the book into a link.

```
tip listing-tags    # check (part of the gate through GATE_CHECKS)
```

It is `listing-tags` in `GATE_CHECKS`, and the gate runs it over
`Solutions/` as well. An untagged listing whose prose cites nothing draws
no finding. Each finding is a hand edit: renumber the tags, cite the
missing one, or put the citation in a code span.

## record_check.py

From chapter 18's `utils/record.py` on, the book writes a frozen data
class as `@record`, which is `dataclass(frozen=True, slots=True)`.
`tip records` fails on three shapes: a `@dataclass(frozen=True)` whose
bases are all known to be slotted (it could be a record), a
`@record(slots=False)` under bases that are all slotted (the flag drops
slots for nothing), and a bare `@record` under a base with no `__slots__`,
which gives every instance its `__dict__` back. A `record(...)` call with
an argument other than `slots=False` fails too. A base the check cannot
see, such as one imported from another listing, draws no finding, so the
check under-reports by design.

```
tip records    # check (part of the gate through GATE_CHECKS)
```

It is `records` in `GATE_CHECKS`, and the gate runs it over `Solutions/`
as well. To clear a finding, convert the class, give the book's own base
`__slots__ = ()`, or list a deliberate exception with its reason in
`tools/data/record_exceptions.txt`. That file is keyed by chapter name, so
a renumbering leaves it alone. When run standalone, `tip records` also
fails on an entry that matches no class, so the file stays current.

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

The gate checks `Chapters/`, `Solutions/`, and this README (`GATE_DOCS` in
`tools/tasks.py`).
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

## opening_epigraph.py

Chapters 02 onward open with an epigraph, a blockquote of two to four
lines directly under the `#` heading. `build_site.split_epigraph()` finds
it for the site, EPUB, and PDF by matching a blockquote at the start of
the body, so a chapter whose opener loses its `>` markers, or gains a
paragraph above them, builds with no epigraph and no complaint.
`tip epigraph` turns that into a failure. It requires the heading on line
1, a blank line 2, and the blockquote from line 3, followed by a blank
line. Chapter 01 and the appendices open with an ordinary paragraph and
are skipped. It is `epigraph` in `GATE_CHECKS`; restore the blockquote to
clear a finding.

```
tip epigraph    # check (part of the gate through GATE_CHECKS)
```

## check_self_reference.py

`heading_links.py` proves that a cross-chapter link resolves, while the
sentence around the link can still make a false claim about the chapter
it names. Chapter 07 said "[Rethinking Objects] uses it" of `slots=True`,
and chapter 20 contains the string "slot" zero times. `tip self-reference`
checks three literal shapes, each taken from a real error:

* `absence` (gates): a claim that something appears nowhere else, where
  a code span or listing elsewhere in the book holds it.
* `direction` (gates): an ordering phrase ("an earlier chapter") near a
  link that points the other way.
* `grounding`: a sentence that links a chapter containing none of the
  code terms the sentence names. Search cannot tell a misattribution from
  terms that belong to the linking chapter, so `tip grounding-triage`
  asks a model and commits each verdict to
  `tools/data/grounding_verdicts.json`. A misattribution verdict (SR004)
  fails the gate. `tip self-reference-report` lists a finding with no
  verdict yet (SR002), which the gate lets pass.

```
tip self-reference          # the gating rules (part of GATE_CHECKS)
tip self-reference-report   # plus grounding findings with no verdict
tip grounding-triage        # ask about new findings (TYPESAFE_API_KEY)
```

A new misattribution passes the gate until it has a verdict, so run the
triage after editing a sentence that links another chapter. Waivers go in
`tools/data/self_reference_ok.txt`. The rules under-report by design: a
claim with no code term in it is invisible to them. The module docstring
and `tools/CLAUDE.md` have the details.

## Model-backed reviews

Some questions about the prose depend on reading, so no search can
settle them. Does a sentence attribute a name to the chapter it links?
Does the linked section cover what the sentence credits it with? Would
the author rewrite this sentence? The tools in this family put such
questions to a model. Two services answer. TypeSafe takes structured
questions through `judgments.py`: a Choice among named options, a Score
on a scale, or a Noul, the probability of yes. Gemini, reached through
Google's Antigravity CLI (`agy`), reads a whole chapter or a numbered
list of statements. Two members call no model: `check_claims.py`
narrows by search the question `link_support.py` asks a model, and
`sentence_diff.py` is the library that finds the sentences an edit
rewrote.

None of these tools is part of `verify`, `gate`, `sweep`, or `ci`. Each
run uses tokens and can answer differently from the last. A model's
answer reaches a gate in one place: `check_self_reference.py` reads the
grounding verdicts that `grounding_triage.py` stored in `tools/data/`,
offline, so the gate stays deterministic and makes no network call.
`tip verify-targets` smoke-tests `grounding-triage` and `link-support`
on a machine where the TypeSafe key is set and skips them elsewhere. It
excludes `edit-patterns`, `outside-review`, and `prompt-facts`
everywhere. Treat every finding as an observation to test against the
chapter before editing.

## judgments.py

The shared TypeSafe layer, a library with no command. `ask()` sends a
batch of (state, questions) pairs to TypeSafe's `system_one()` call,
eight at a time. It retries a gateway error, a dropped connection, or a
timeout up to four times with backoff; the SDK retries rate limits on
its own. Four tools call `ask()`: `grounding_triage.py`,
`link_support.py`, `prose_calibration.py`, and `edit_patterns.py`.
`check_self_reference.py` imports the module to read
`grounding_verdicts.json`. `fault_review.py` and `fix_triage.py` use its
`load()` and `save()` on `edit_pairs.json`. Those three ask nothing.

Asking needs the `typesafe-sdk` package and a `TYPESAFE_API_KEY`. The
SDK stays out of `pyproject.toml`, because it builds `pydantic-core` from
source on the pinned Python, which a fresh cloud session cannot do. The
`tip` tasks add it for one run with `uv run --with typesafe-sdk`.
`api_key()` looks in the process environment and then, on Windows, in
the user's registry environment (`HKCU\Environment`). The registry
fallback dates from 2026-09-29, when a Claude Code session started from
an older shell inherited no copy of the key. An exit message naming
both places means the key is unset. Reading a store needs neither the
SDK nor the key, which keeps the gate offline.

`key()` hashes everything a question saw, with whitespace collapsed. A
reflow therefore keeps a verdict. An edit to the sentence (or to the
linked section) retires it, leaving that sentence unjudged until the
next run. `save()` sorts a store by file and line, so its diff reads in
book order. `SECTION_LIMIT` (12,000 characters) caps how much of a
linked section a question sees.

## grounding_triage.py

`check_self_reference.py`'s `grounding` rule finds a sentence that links
a chapter containing none of the code names the sentence holds. Search
cannot tell a misattribution (chapter 07's old "[Rethinking Objects]
does with `slots=True`") from a sentence that credits the linked chapter
with an idea while the names belong to the current chapter's example.
All 41 findings on 2026-09-27 were the second kind. `tip
grounding-triage` asks TypeSafe a Choice about each finding that has no
stored verdict, `terms_to_target` against `idea_to_target`. It writes
the probability of `terms_to_target`, with the date asked, to
`tools/data/grounding_verdicts.json`. It also prunes a verdict whose
sentence no longer produces a finding and refreshes the stored line
numbers without asking again.

The gate reads that file offline (see `check_self_reference.py` above).
A verdict at or above `MISATTRIBUTED` (0.4) becomes SR004 and fails the
gate. A finding judged to credit an idea drops out. One with no
verdict stays SR002, which `tip self-reference-report` lists and the
gate lets pass. A new misattribution therefore passes the gate until
the triage runs, so run it after editing a sentence that links another
chapter, and commit the verdict file. An SR004 asks you to correct the
sentence: link the chapter that holds the name, or credit the linked
chapter with its idea alone. The 2026-09-27 calibration scored the 41
real findings 0.00 to 0.11 for attribution and the five planted
misattributions in `CALIBRATION` 0.66 to 0.93. `ARGS=--calibrate`
re-asks the planted cases and every stored one, stores nothing, and
exits 1 when a case falls on the wrong side of 0.4. Run it after a
model or wording change.

```
tip grounding-triage                    # ask about new findings, store the verdicts
tip grounding-triage ARGS=--dry-run     # list what would be asked
tip grounding-triage ARGS=--calibrate   # re-ask the planted and stored cases
tip self-reference-report               # findings still without a verdict
```

## check_claims.py

`heading_links.py` proves that a cross-chapter link resolves.
`check_claims.py` narrows, by search and with no model, the links whose
text might claim something the target does not say. A link whose text
shares at least half its words with the target chapter's title or with
the target heading (`--threshold 0.5`, short function words removed)
asserts nothing the target can contradict. A link text under three words
(`--min-words 3`) is a term link, one word of the running sentence
linked to where the term is taught. What remains is a phrase the author
wrote to describe the target, and the tool lists each one with its
target heading, then a count. It always exits 0. To act on a line, read
the target section; if it says something else, reword the link text or
point the link at the section that does say it. `tip link-support` asks
a model the same question of every anchored link.

```
tip claims               # every chapter
tip claims ARGS=33       # one chapter
tip claims ARGS=--all    # every link, classified as chapter, heading, or term
```

## link_support.py

For every anchored link from one chapter into another, `tip
link-support` gives TypeSafe the sentence, the sentence before it, and
the linked section, and asks a Choice: `supports`, `contradicts`, or
`says_nothing`. A section longer than `SECTION_LIMIT` goes as its
opening plus the subsections that share the most words with the
sentence, in book order, with `[...]` at each gap. `excerpt()`'s
docstring records the false alarms that shaped that rule. Verdicts go to
`tools/data/link_support_verdicts.json`, keyed by the sentence, the
target, the anchor, and the section text the question saw, so an edit at
either end re-asks that one link. A run asks about new links, prunes
stale verdicts, and then reports. Commit the updated file.

The report lists each link whose answer is not `supports`, at a
confidence of 0.5 or more (`CONFIDENT`); `--all` adds the
low-confidence answers. A `says_nothing` is often a link doing its job
loosely, such as an exercise that links "descriptor" to the nearest
descriptor example. The first run's real finding was chapter 42 linking
"put the meaning in the type" to chapter 08's annotation-syntax section,
when chapter 12 makes that argument. Each line asks for a judgment:
retarget the link, reword the sentence, or leave a loose link as it is.
`ARGS=--report` reads the store and needs no key.

```
tip link-support                        # ask about new links, then report
tip link-support ARGS=--report          # report from the store; no key needed
tip link-support ARGS="--report --all"  # include low-confidence answers
```

## sentence_diff.py

A library for `prose_calibration.py` and `edit_patterns.py`. Given the
before and after text of a chapter, `diff()` returns the rewritten
sentences, each paired with the most similar new sentence and its
`difflib` ratio, and the sentences left alone. It collapses whitespace
first, so a reflow is not a rewrite. A sentence whose words still read
straight through the new text also counts as left alone, since a line
break after a colon splits a sentence nobody edited. `prose()` drops
the text no sentence-level judgment covers: table rows,
list items, figure captions, anything under 40 characters, and any
sentence holding a `[[...]]` draft note. Each `Sentence` carries its
neighbors, the nearest heading, and its paragraph (up to 2,000
characters), which is the context the model questions see.

## prose_calibration.py

A study rather than a check: does a model score pick out the sentences
Bruce rewrites? A score should agree with the author before it steers a
prose pass (`/straighten`, `/antecedents`, the clarity agent). Git
holds the evidence. The tool collects the author's editor commits under
`Chapters/` (no Co-Authored-By trailer, a subject such as "Update
30_Patterns--Observer.md" or "more ch 30"). From each it takes the
sentences the commit rewrote, through `sentence_diff.py`, and as
controls an equal number from the same commit and chapter that no
collected commit rewrote. TypeSafe answers eight questions about each
sentence. Four are Scores for one fault each: subject-verb distance,
ambiguous pointers, skipped steps, and overloaded claims. The Noul
`would_rewrite` shows six before/after pairs from `bruce_edit_db.md` and
asks whether the author would rewrite the sentence. Three more Nouls,
`preamble`, `fractal_summary`, and `comma_tail`, ask about the faults
the riff prose linter flags.

The report gives each question's AUC, the chance that a rewritten
sentence outscores a left-alone one (0.5 is no signal), with a standard
error. Longer sentences get rewritten more and score higher on every
question, so it also gives the AUC within length bands, then the
top-scoring rewrites per question. The samples split by commit. The
report reads the half of the commits that supplied none of the six
examples, which keeps `would_rewrite` from scoring its own examples.
Answers cache in `build/prose_calibration.json`, stamped with each
question's wording, so a rerun asks a new or reworded question and
reuses the rest. No `tip` task runs the study. It needs the TypeSafe
setup described under `judgments.py`.

The results, from `tools/CLAUDE.md`, count a rewrite as restructured
below 0.75 similarity. On 2026-09-27 (115 restructured rewrites, 299
controls) `would_rewrite` led at AUC 0.66 ± 0.03, unchanged by length
banding; ambiguous pointers and skipped steps were near 0.58, and
subject-verb distance near chance. On 2026-10-03 (110 restructured
rewrites, 294 controls) the added `overloaded` Score reached 0.59 ±
0.03, 0.58 within bands, behind `would_rewrite` (0.63), pointers (0.62),
and skipped steps (0.61). The three riff Nouls scored 0.54, 0.50, and
0.56. Those numbers are good enough to rank sentences for a human
reader and too weak to justify an edit. Rerun the study before letting
a model score steer a prose pass.

```
uv run --with typesafe-sdk python -m tools.prose_calibration            # ask, then report
uv run --with typesafe-sdk python -m tools.prose_calibration --dry-run  # count samples and questions
```

## edit_patterns.py

`/bruce-edit-capture` turns an editing pass into written rules, applied
after a second sighting. `edit_patterns.py` works from the examples
instead. Each sentence a pass rewrote becomes a before/after pair in
`tools/data/edit_pairs.json`. A pair that carries a one-line `fault`
is searched for across `Chapters/`. A bare `tip edit-patterns` diffs the
open `edit-start-NN` tag against the working tree, whoever made each
edit; with no open tag, or several, it exits and asks for
`ARGS="--since REF"` or `ARGS="--range A..B"`. `/edit-done` step 3b runs
it with `--dry-run`, which records the pairs and asks nothing. The
fault lines come from the review page that `fault_review.py` seeds. Two
filters keep noise out of the store. A pair below 0.6 similarity
(`MIN_SIMILARITY`) is dropped unless it is a deletion. In chapter 31's
pass on 2026-10-19 the pairs at 0.3 to 0.5 were all spurious. A pair
whose every change is a rename, a word swap seen in three or more pairs,
is dropped too.

Then come three TypeSafe steps. A Noul checks each pair: its own before
must score at or above 0.7 (`REPORT`) and its after below 0.7, or the
pair is `unclear` and stays out of the search. A Choice screens every
sentence in the book against up to 20 searchable pairs at once, plus
`none`. A sentence that gives a pair at least 0.15 gets that pair's
Noul, and a hit at or above the pair's `floor` (0.7 by default) goes to
`build/edit_patterns.md`, strongest first. Since 2026-09-27 every
question sees the sentence's paragraph and heading. Answers cache in
`build/edit_patterns.json`, so a rerun asks about new pairs and changed
sentences. A full search takes about five minutes, most of it one
screening question per sentence of the book.

What the runs found, from `tools/CLAUDE.md`: with no fault line the
search matches surface features (chapter 30's metadiscourse cut matched
158 sentences for ending in a colon). With a fault line, the top hits
were real metadiscourse. The fault line's wording sets the precision, so a
loose hit list calls for rewording the fault, not for raising the floor.
On 2026-09-27 Bruce labeled ten sampled hits for each of six faults on a
blind page. Each labeled pair now carries its own `floor` and
`floor_basis`, from 0.62 for R21 to 0.84 for R2. For three of the six
the score did not rank the right hits first, so a floor is a rough
filter and a long hit list is a review batch. `ARGS=--from-rules`
searches for `bruce_edit_db.md`'s promoted rules, with each rule's
title, Test, and Keep-when lines as the fault and, as the example, the
sighting the pair check separates best; 14 of 19 rules were searchable.
The tool reports and edits nothing. A hit asks for a human decision,
made on the page that `fix_triage.py` seeds or in a prose pass.

```
tip edit-patterns                                # the open edit-start pass
tip edit-patterns ARGS="--since edit-start-30"   # REF to the working tree
tip edit-patterns ARGS=--dry-run                 # record the pairs, ask nothing
tip edit-patterns ARGS=--report                  # every stored pair, from the cache
tip edit-patterns ARGS=--from-rules              # search for bruce_edit_db.md's rules
tip edit-patterns ARGS="--pair FILE:LINE"        # one stored pair
```

## outside_review.py

`tip outside-review CH=17` sends one chapter to Gemini through Google's
Antigravity CLI (`agy`) in one headless call: the instructions in
`tools/data/outside_review_prompt.md`, then the chapter's Markdown. The
reply goes to `outside_review/<stem>.md`, tracked like `deep_review/`,
under a first line that records the chapter, the model, and the date.
The default model is `gemini-3.1-pro-high`; `MODEL=` picks another.
`CH="17 18"` or a range such as `CH=30-32` reviews several chapters in
order. `ARGS="--suffix .r2"` keeps a second round beside the first.
It needs an `agy` that is installed and signed in: install it from
https://antigravity.google/docs/getting-started?tab=cli and run `agy`
once. The tool finds it on PATH or under `%LOCALAPPDATA%\agy\bin`. It
refuses to run under `CI`.

A transient failure is rerun up to two more times (`--retries`): an
`ERROR` result for exceeding the output token limit, an empty reply
after `agy` denied a tool call, an interrupted stream with no reply, and
a server error (code 500). An interrupted stream that carries a reply
is saved, with a second header line telling you to check its tail. Any
other failure (a nonzero exit, no reply within 900 seconds, no result
event) is final for that chapter. The run goes on to the next chapter
and exits 1 at the end.

The reply is a set of observations, never instructions. Applying it is
a separate step in a Claude session: test each item against the chapter
and a run under `uv run`, apply what passes, and append a `## Verdicts`
section to the review file, one line per item, applied or rejected, with
the evidence and the commit. The test matters. In the tool's first runs
(2026-10-08) all five items of the first reply were wrong for Python
3.15, and the prompt now lists the 3.12-3.15 features the book uses.
The corrected run's third item claimed a `TypeError` that
`type.__new__()` never raises.

```
tip outside-review CH=17                        # one chapter, default model
tip outside-review CH="17 18" MODEL=gemini-3.8-flash-high
tip outside-review CH=17 ARGS="--suffix .r2"    # a second round beside the first
tip outside-review CH=17 ARGS=--dry-run         # print the command and sizes, call nothing
```

## prompt_facts_probe.py

The outside-review prompt carries a list under "Treat these as valid and
do not flag them:", each bullet a Python 3.12-3.15 fact the reviewer
model tends to get wrong. Every bullet adds tokens to every review, so
each one should earn its place. `tip prompt-facts` sends the bullets to
Gemini through `agy` in one call, without the prompt or its framing,
and asks for TRUE, FALSE, or UNSURE on each, with a one-sentence reason.
It prints a row per bullet. A `no` row (FALSE, UNSURE, or no answer) is
a bullet the model still disputes, so the bullet stays. A `yes` row is a
candidate to drop. Answers vary from run to run, so the task passes
`--save`, which appends the model, the date, and the table to
`tools/data/prompt_facts_runs.md`. Drop a bullet after two runs mark it
`yes`, and commit the log. The default model is `gemini-3.8-flash-high`,
the one whose reviews prompted the bullets. The probe reuses
`outside_review.py`'s `agy` helpers and needs the same sign-in. It makes
one attempt with no retry and refuses to run under `CI`.

```
tip prompt-facts                             # ask, print the table, append it to the log
tip prompt-facts ARGS=--raw                  # the model's reply before the table
tip prompt-facts ARGS=--dry-run              # print the command and the message
tip prompt-facts MODEL=gemini-3.1-pro-high   # another model
```

## pattern_names.py

Every naming of a design pattern is capitalized and italic, on every
mention, in prose and in link text (*State*, *Chain of Responsibility*),
since names like State, Command, and Proxy are ordinary words otherwise.
Headings stay plain, code spans are class names, and the lowercase word
keeps its ordinary sense. `tip pattern-names` reports a capitalized name
outside italics, a bold name, and a lowercase name directly before
"pattern", and `tip fix-pattern-names` wraps each of those in italics. A
name that is also a common verb or noun (State, Command, Bridge) at the
start of a line is ambiguous ("State the rule"), so the tool leaves it
unrewritten and lists it under `--sentence-start` for a human to judge.

```
tip pattern-names        # check (part of the gate through GATE_CHECKS)
tip fix-pattern-names    # italicize the unambiguous ones
uv run python -m tools.pattern_names --sentence-start   # line-start cases
```

The names live in `tools/data/pattern_names.txt`, along with `!` phrases
that contain a name without naming the pattern (`!State Machines`). It is
`pattern-names` in `GATE_CHECKS`, and the gate runs it over `Solutions/`
as well.

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

## quoted_diagnostics_probe.py

Advisory. `check_quoted_diagnostics.py` compares a quote's gutter
lines with the listing, so it catches a moved line but not a `ty`
upgrade that rewords a message, renames a rule, or changes a caret
label. `tip quoted-diagnostics-probe` closes that gap: for each of the
book's 42 quoted diagnostics it rebuilds the listing the quote
describes, runs `uv run ty check` on the copy, and compares what `ty`
prints with what the book shows. It replaces the report-only agent that
used to re-derive every quote by hand after an upgrade.

Many quotes are against an edited copy of the listing: a
`# type: ignore` removed, a `match` block deleted, a line uncommented,
a scratch call appended. `tools/data/quoted_diagnostics_probes.txt`
records the edit for every quote, one tab-separated entry each (the
Markdown file, the quote's ordinal in it, the listing, and one or more
edits). The edits are `none`, `strip-ignore`, `replace`, `delete`,
`delete-range`, `insert-after`, `append`, and `uncomment`, each
anchored on text in the listing so a moved line leaves the spec
intact. The module docstring has the full form. The probe lands in
`build/quoted-probe/`, outside the extracted trees, with the listing's
siblings copied beside it so a local import resolves.

The comparison cuts the quote and `ty`'s output into headline, `info:`
line, location, source line, and caret-label events, normalizes
whitespace so the book's line wrapping does not matter, and requires
every event the quote shows to appear in order in one of `ty`'s
diagnostics. A line the quote leaves out is not a mismatch, because the
book omits trailing `info:` lines by choice. A changed message, rule,
location, source line, or label is. The run prints one line per quote,
MATCH or STALE, then the quoted and actual text for each STALE one, and
exits nonzero if any is STALE, if a quote has no spec entry, or if an
entry names a quote that is gone. `ARGS=--list` prints the spec,
`ARGS=--keep` leaves the probes for inspection, and
`ARGS="--only PATH"` checks one Markdown file.

Run it after `tip tools-upgrade`. It joins no gate, on the same terms
as `tip pyright-review`.

`tip unused-ignores` (a task in `tasks.py`, no module of its own,
2026-10-30) is the third advisory check an upgrade runs, and the one
`tools-upgrade` itself ends with, after the sweep. It is one
`ty check` over both build trees with `--error unused-ignore-comment`,
so a `# type: ignore` that the new `ty` no longer needs fails the run.
The rule is off by default, which is why the gate's `ty` step never
reports one. A hit is a comment to delete and a paragraph to reread:
the prose beside an ignore names the diagnostic it suppresses, and
the release that retired the ignore made that sentence false.

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
lacks, and an exercise of "the previous chapter" or "the next
chapter", which a chapter split retargets silently. Entries are keyed by chapter name, so a
renumbering leaves the baseline alone and a chapter rename does not.
"The last three exercises" and an exercise described without a
number are invisible to it.

## skill_copies.py

The book's coding-style skill exists twice: `thinking-in-python-skill.md`
at the repo root and `.claude/skills/thinking-in-python/SKILL.md`, where
Claude Code loads it. The repo sets `core.symlinks = false`, so the two
are copies. An edit to one leaves the other stale until someone copies it
over. `tip skill-copies` compares them byte for byte and fails, naming
the first line where they diverge. `gate` runs it too. To clear a finding,
copy the edited file over the other. The pairs live in `PAIRS` in the
module, so a second pair of copies is one more line.

```
tip skill-copies    # check (part of the gate)
```

## archive_contents.py

`archive/README.md` describes each finished document in `archive/`, one
bullet per file, opening with the filename in a code span. The check
compares those bullets with the files in the directory and fails on a
file with no bullet and on a bullet whose file is gone. `tip check` and
the gate run it. To clear a finding, add or remove the bullet.

```
tip check    # the drift checks, this one included
```

## readme_coverage.py

Every module in `tools/` needs a name in this file: its filename
(`check_all.py`) or its dotted name (`tools.check_all`). A package,
such as `story_figures/`, needs its name with a trailing slash. The
check fails on each module or package this file never names, so a new
tool arrives with its entry. `tip check` and the gate run it. It reads
names alone, so a module mentioned in passing in another entry passes;
the entry is still worth writing. To clear a finding, add an entry
that says what the tool does, which task runs it, and whether a gate
does.

```
tip check    # the drift checks, this one included
```

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
<!-- TODO(free-threaded-default): if free threading ever becomes
CPython's default build, convert this indented block to a real, fenced,
tested example. -->
```

The tag groups related markers that share one underlying blocker, and
doubles as a plain `grep -rn "TODO(free-threaded-default)" Chapters/` when you care
about only one of them. It always exits 0, being informational.

## Review pages and author reports

Five tools put work in front of the author and gate nothing. Two print a
worklist in the terminal. The other three prepare a review page: a
claude.ai artifact that the session publishes with a database
(`capabilities: {"db": {}}`), where Bruce reads cards or a whole chapter
and records decisions with the mouse. The page tools share one
shape. A `seed` or `load` step writes one JSON file per database
document under `build/<tool>/`, plus `batch*.json` files of 50 writes
each, which the session sends to the page with one `ArtifactData`
`batch` call per file. When Bruce is done, the session reads the
documents back with `ArtifactData` into a `read/` folder, and an `apply`
step turns the decisions into edits. A skill drives each page's round.
The commands in each page entry are steps of that round. None of the
five calls a model.

## chapter_editor.py

The chapter editor shows a whole chapter, one block per paragraph,
heading, list, table, figure, or listing. Bruce selects text and marks
it Rewrite (with an optional note) or Delete, or opens a block's
Markdown and edits it in place. Each mark saves when it is made. After
reading through the chapter, Bruce types `apply` in the terminal. The
`chapter-editor` skill (`.claude/skills/chapter-editor/SKILL.md`) runs
the round. The page template is `chapter_editor.html` beside it. The
Markdown in `Chapters/` stays the source of truth; the page's database
mirrors it.

`tip editor-load CH=NN` parses the chapter into blocks and writes the
documents, the batch files, and a copy of the page titled for the
chapter, all under `build/chapter_editor/NN/`. The first load writes
every block. A later load compares the chapter with the snapshot the
previous load left in `state.json` and writes only what changed. A
changed block keeps its id and records its old text as `previous`, so
the page outlines the change. A block gone from the chapter is
deleted. `load` refuses to start a round over one that was never
applied, since that would drop its marks; `ARGS=--force` overrides it.
`ARGS=--refresh` stays in the open round instead, for a change made to
the chapter while the page shows no marks.

`tip editor-apply CH=NN` reads the saved documents from
`build/chapter_editor/NN/read/`. It writes the in-place edits and the
Delete cuts into the chapter, prints each cut with its surroundings, and
saves the Rewrite marks to `round-R.json` beside the state, since a
rewrite is the session's work. A marked block whose chapter text changed
during the round (an edit made in Zed) is a conflict. `apply` lists it
and leaves that block for the session. The store refuses a write to an
existing document unless the write names its current version, so `load`
pins each write from a ledger, `versions.json`, of the versions its own
batches leave behind. `tip editor-pin` sets a pin by hand for a write the
store refused. `tools/data/chapter_editor.json` maps each chapter number
to its page's artifact URL, so a chapter keeps one page across rounds.
Every other piece of state lives in `build/`. A wiped `build/` makes the
next load a first load.

```
tip editor-load CH=30                    # start the next round
tip editor-load CH=30 ARGS=--refresh     # update the open round
tip editor-apply CH=30                   # edits and cuts; list rewrites
tip editor-pin CH=30 ARGS="blocks/b0011=4"  # pin a refused write
uv run python -m tools.chapter_editor page 30  # page copy only
```

## fault_review.py

`/edit-done` step 3b (`.claude/skills/edit-done/SKILL.md`) asks Bruce to
approve a one-line `fault` for each sentence the editing pass rewrote,
because `edit_patterns.py` searches the book only for a pair that
carries one. The fault-review page shows one card per rewrite, the
session's proposed line editable in place, with Approve or Local edit on
each. The same page carries the rule proposals from
`/bruce-edit-capture`, each decided with Approve, Narrow, or Reject
and a note. The template is `.claude/skills/edit-done/fault_review.html`.
Each pass publishes its own copy as a new artifact.

`seed --since REF` records the pass's rewrites in
`tools/data/edit_pairs.json` and writes the cards from the session's
`--proposals` file, a JSON object from pair key to fault line, and the
rule proposals from `--rules`. Three filters keep the page small.
A pair below the similarity floor (0.6, `--min-similarity` overrides it)
is dropped. So is a pair whose changes are all renames, a word replaced
the same way in three or more pairs. A proposal the session marks
`"local": true` makes no card. `seed` marks that pair local. The
page lists the local pairs in one collapsed row, each with a Disagree
button. `seed` also clears `build/fault_review/read/`, since a read-back
adds files there and deletes none. A stale card left there could
overwrite a newer decision.

`apply` reads the cards back and writes each decision into
`edit_pairs.json`. An approved line, edited or not, becomes the pair's
`fault`. A Local edit clears the `fault` and marks the pair local.
Undecided cards are listed and left alone. With `--rules-dir` it prints
one line per rule proposal with Bruce's decision and note. It never
writes `bruce_edit_db.md`; the session writes that file from the printed
lines, in Bruce's words. No `tip` task runs the module.

```
uv run python -m tools.fault_review seed --since edit-start-30 \
    --proposals build/fault_review/proposals.json \
    --rules build/fault_review/rules.json   # write the page's documents
uv run python -m tools.fault_review apply \
    build/fault_review/read/cards \
    --rules-dir build/fault_review/read/proposals  # record decisions
```

## fix_triage.py

`edit_patterns.py` searches the book for sentences that share a fault
Bruce fixed once. A list of a hundred hits in a terminal goes unread. The
fix-triage page (`.claude/skills/edit-done/fix_triage.html`, offered in
`/edit-done` step 3b) shows one card per hit: the sentence in its
paragraph, a proposed rewrite editable in place, and four choices. Apply
rewrite and Delete sentence change the chapter. Skip keeps a sentence
that has the fault. Not this fault marks a false hit. `apply` counts
those last two per fault, so a pair's floor can be revisited.

`export PAIR ...` writes `build/fix_triage/hits.json`, every hit at or
above each pair's floor. It reads the verdicts `tip edit-patterns` cached
in `build/edit_patterns.json` and asks no model, so that run comes
first. The session then writes `build/fix_triage/proposals.json`, a
rewrite or a deletion for each hit id. `seed` joins the two into cards
and batch files. `apply DIR` edits the chapters, finding each sentence
by its words with any whitespace between them, and exits 1 when a
sentence is no longer there. It refuses a directory that holds a card
outside the current `hits.json`. Reflow is left to `tip verify-ch`.

A pair marked `"direct": true` in `tools/data/edit_pairs.json` skips the
page; the flag is set after a page where Bruce applied a fault's
proposals wholesale. `direct` applies the proposed rewrites and lists
the deletions for the session, which reads the next sentence for a lost
antecedent. With `--commit` it runs `tip verify-ch CH=NN ISOLATED=1` on
every edited chapter and commits one chapter per commit. One failed
gate holds every commit, so a batch is never half committed. The
top-level `--dir` option moves the working directory away from
`build/fix_triage`. No `tip` task runs the module.

```
uv run python -m tools.fix_triage export KEY      # hits for a pair
uv run python -m tools.fix_triage seed            # cards and batches
uv run python -m tools.fix_triage apply build/fix_triage/read/cards
uv run python -m tools.fix_triage direct --commit --trailer "..."
```

## comment_report.py

A comment in a listing belongs there when it says something the code
does not. No rule can tell a comment that restates its own line from one
that teaches. `tip comment-report` narrows the reading instead.
It lists the listing comments in `Chapters/` and `Solutions/` that are
new since a git ref, one per line as `path:line: [listing] source`, so
you read the comments you wrote and delete the ones that repeat their
line. It tokenizes each block, so a `#` inside a string stays out, and
it skips the `# slug.py` line, `#:` markers, and tool directives. A
comment counts as new when its listing holds more copies of that text
than it did at the ref, so a reworded comment is new and a moved one is
not. Moving a listing to another chapter reports all its comments as new
in the receiving file. Inserting an unmarked fragment renumbers the
fragments after it, so their comments read as new too. It is report-only
and exits 2 on a usage error (an unknown ref, a missing file).

```
tip comment-report                 # new since HEAD (uncommitted edits)
tip comment-report SINCE=v0.5.9    # new since a tag or commit
tip comment-report ARGS=--all      # every comment in the book
```

## exercise_coverage.py

A chapter's exercises tend to cluster on one section and leave others
with nothing for the reader to do. `tip exercise-coverage` lists, per
chapter, the `##` sections that no exercise reaches. An exercise reaches
a section when it names a listing the section owns, names a function or
class those listings define, links the section's anchor, or quotes its
heading (one longer than 12 characters). The matching is literal, so it
under-reports coverage. Confirm a reported section by eye before writing
an exercise for it, since a table, an aside, or a conclusion needs none.
The tool reads `Chapters/` and exits 0 unless `--strict` is given, which
exits 1 on any gap. No gate runs it.

```
tip exercise-coverage                    # every chapter
tip exercise-coverage ARGS="19 31"       # chapters by number
tip exercise-coverage ARGS=--deep        # count ### sections too
tip exercise-coverage ARGS=--covered     # list practiced sections too
```

## Figures

Every figure is an SVG in `resources/images/`, referenced from the prose
as `![caption](_images/<name>)`. Most are drawn by hand. Two sources are
generated, and their SVGs are never edited by hand: the 22 figures that
`tools/story_figures/` draws (each pattern chapter's story figure, plus
body figures in chapters 14, 16, 26, 32, 34, 36, 37, and 38), and chapter
21's `coupling_gallery.svg`, which `coupling_panels.py` draws. To change
one, edit its module or spec and run its `tip fix-*` task. The `figures`
skill (`.claude/skills/figures/SKILL.md`) holds the rules for drawing a
figure: captions, palette, arrowheads, placement, and what `tip figures`
checks. Read it before creating or changing any SVG.

The gate runs the two drift checks, `tip story-figures` and `tip
coupling-panels`, and so do `verify-ch` and `sweep`. `tip figures` runs
in `verify` alone. `arrowheads.py` and `svg_text.py` are libraries that
the other three call.

## story_figures/

A package with one module per generated figure, named `chNN_<name>.py`.
Each module defines `STEM`, the SVG's name in `resources/images/` without
`.svg`, and `render()`, which returns the SVG source as a string. Its
docstring says which listings its names come from, so read it before
changing the figure. `__init__.py` holds the vocabulary the figures
share: the cover palette, `SHADE` (`#eeeeee`, the one fill for a shaded
region, since the EPUB's PNG8 conversion turned every pale warm tint
yellow), the book font, `text()`, `rect()`, `line()`, `arrow()`,
`cross()`, and `svg()`. An `arrow()` takes its head from `arrowheads.py`
and stops `TIP_GAP` (4 units) short of the target's border. An outer
shape that encloses an arrow's target is a `region()` path rather than a
`rect()`, because `arrowheads.tight_tips()` would read a tip on the inner
box as buried in the outer rect.

`__main__.py` discovers every `chNN_*` module and writes each SVG whose
committed copy differs. With `--check` it writes nothing and fails on a
committed SVG that differs from its module, or on any flag `tip figures`
would report for that figure (`lint()`, which calls
`figure_gallery.read_style()`). That makes the check stricter than the
gallery: a color outside the palette, a missing `<title>`, or another
font fails a generated figure, where the gallery marks it and passes a
hand-drawn one. `--only NN` limits a run to one chapter's modules, and
`--png DIR` also rasterizes each figure with the EPUB's rasterizer, since
text that fits in a browser can collide once rasterized. `--png` exits
with a message when no rasterizer is on PATH. `tip story-figures` runs
the check in `gate`, `verify-ch`, and `sweep`. To clear a drift finding,
run `tip fix-story-figures` and commit the SVG; to clear a lint finding,
change the module.

```
tip story-figures                         # drift and lint check (gated)
tip story-figures ARGS="--only 30"        # one chapter's figures
tip fix-story-figures                     # regenerate every SVG
tip fix-story-figures ARGS="--only 30 --png build/story"   # and look
```

## coupling_panels.py

Generates chapter 21's `coupling_gallery.svg`: six patterns, three to a
row, drawn in the coupling notation that chapter's Coupling section
defines. A heavy edge names a concrete class, a thin edge names an
interface, a dashed hollow-headed edge satisfies one, and the red box is
the part the pattern protects from change. The spec is `GALLERY`, one
`Cell` per pattern with its title, position, nodes, and edges. The
section's other three figures (`coupling_edges.svg`,
`coupling_ladder.svg`, `coupling_reach.svg`) are hand-drawn. From
2026-09-23 to 2026-09-29 the module also drew a panel at the top of each
pattern chapter; the story figures replaced them.

`--check` regenerates in memory and fails when the committed SVG
differs. Every run, writing or checking, also checks each cell's edges
(`edge_problems()`): a head's tip must sit `TIP_PAD` (4 units) from its
target's rounded outline, within `TIP_SLACK` (1), and no edge may cross a
box other than its own two. `edge_points()` slides every tip onto that
line, so a new edge finding usually means two boxes need moving. `--png
[DIR]` rasterizes every `resources/images/coupling_*.svg` into
`build/coupling/` by default, with the EPUB's rasterizer, and writes
nothing else. `tip coupling-panels` runs the check in `gate`,
`verify-ch`, and `sweep`.

```
tip coupling-panels        # drift and edge check (gated)
tip fix-coupling-panels    # regenerate coupling_gallery.svg
tip coupling-panels-png    # rasterize into build/coupling/ to look
```

## arrowheads.py

The book's four arrowheads as SVG markers, with the geometry an edge
needs to carry one. `filled`, a swept head, marks anything that points;
`hollow`, an open triangle, marks inherits or satisfies; `open`, a V,
marks a return; `diamond` marks aggregation at the owning end. Each head
has a fixed size in user units, so heavy and thin edges carry the same
head. The open shapes have no fill, since a paper-colored fill shows as a
patch on the EPUB's white page. Instead the edge stops short by the
head's `trim`, and the head, anchored at its back, reaches the target.
`marker_def()` writes a `<marker>` in a given color. `shorten_line()`,
`shorten_path_end()`, and `shorten_path_start()` shorten a hand-drawn
edge by the trim, cutting a curve at its arc length.

The module also holds the checks the other figure tools run on any SVG:
`marker_kinds()` (a marker outside the four), `mismatched_heads()` (a
head whose color differs from its line's), `short_edges()` (a marked line
shorter than `MIN_LINE`, 8), `tight_tips()` (a tip closer than `MIN_GAP`,
3, to its box or circle), `stray_tips()` (a tip farther than `MAX_GAP`,
6, from every shape, legend samples excepted), and `crossed_boxes()` (an
edge through a box that holds neither end). `figure_gallery.py` runs
them all; `coupling_panels.py` and `story_figures/` write their markers
with `marker_def()`. No task runs it directly.

## svg_text.py

Finds text that runs off a figure's canvas or into other text, without
rendering anything. Every figure sets its text in JetBrains Mono, whose
characters all advance 0.6 em, so a `<text>` element's box follows from
its position, `font-size`, `text-anchor`, and character count, with the
box running from 0.75 em above the baseline to 0.2 em below it.
`clipped()` names text that crosses the `viewBox` edge, which every
renderer cuts off, and `collisions()` names pairs of text boxes that
overlap by more than one unit. `figure_gallery.py` fails on either, so
`tip figures` and the story-figure check report them. The estimate
handles no `transform` or `<g>`, which no figure uses today, and knows
nothing of lines and shapes: text lying across a line still needs the
gallery's PNG view and an eye. No task runs it directly.

## figure_gallery.py

Builds `build/figures/index.html`, every figure the prose in `Chapters/`
and `Solutions/` references, in book order and numbered, each under its
file name, chapter, line, and caption, so a figure can be named by its
number or its stem. The page shows the live SVG from `resources/images/`
and can switch to the PNG the EPUB draws, rasterized into
`build/figures/png/` with the first rasterizer on PATH and redrawn only
when its SVG is newer. With no rasterizer the page shows SVGs alone. A
style line under each figure lists its colors, stroke widths, dashes,
fonts, and markers, and marks anything outside the cover palette or the
book font.

The run fails on a reference to a figure with no file, on any arrowhead
or edge finding from `arrowheads.py`, and on any text finding from
`svg_text.py`. A color or font outside the palette is marked on the page,
and a file no chapter references is listed and reported; neither fails.
`TIP_GAP_EXEMPT` and `STRAY_TIP_EXEMPT` would name a figure excused from
the tip checks, with the reason; both are empty. `tip figures` runs it
and `tip verify` runs that, so the gallery tracks the working tree; the
gate does not run it. `tip figures-open` also opens the page in a
browser.

```
tip figures          # build build/figures/index.html (part of verify)
tip figures-open     # build it and open it in a browser
```

## build_site.py

Renders `Chapters/*.md` into a browsable site under `build/site/` (git-ignored).
Pandoc converts each chapter; the script adds the title page, an ordered
contents list, a sidebar, previous/next links, and syntax-highlighting CSS.

The book's **Part dividers are generated here, not written in the Markdown.**
The `PARTS` map names Part I (Foundations, before chapter `02`), Part II
(Techniques, before `11`), Part III (Patterns, before `20`), Part IV
(Functional, before `40`), Part V (Effects, before `44`), and the
Appendices (before `A`); the builder
emits each heading in the table of contents before its starting chapter, with
the Introduction standing alone above Part I. So a chapter file with no "Part"
heading is correct: to move or rename a Part, edit `PARTS`, not the chapters.

Book images are referenced in the Markdown as `_images/<name>` with no
extension. The builder resolves each to the real file in `resources/images`
(`decorator_pattern` to `decorator_pattern.svg`), copies the referenced ones into
`build/site/images/`, and warns about any reference with no matching file.

Cross-references between chapters use standard relative Markdown links to the
target chapter's `.md` file, for example
`[Factory](26_Patterns--Factory.md)`.
These render correctly on GitHub; the builder rewrites intra-book `.md` links to
`.html` so they also resolve in the site. External links (which carry a scheme)
are left alone.

Requires `pandoc` on PATH. Run `uv run python -m tools.build_site` (or `tip site`);
use `-o DIR` to build elsewhere. `tip serve` serves the
existing `build/site/` at <http://localhost:8000>, watching for edits and
copying selections; `tip local` builds the site first and also opens a
browser at it.

Each `Solutions/<stem>/README.md` becomes `<stem>.solutions.html` beside
the chapter's page (`write_solutions_page()`), carrying the chapter's
label, a link back to the chapter, the step assets (`solutions.css`,
`solutions.js`), and the listing links into the chapters. The chapter's
`../Solutions/` link and the index's `solutions` link beside each chapter
point at it; the EPUB and PDF keep the GitHub URL, since they carry no
Solutions pages.

`rebuild_chapter()` is the incremental entry point `serve.py --watch` uses:
it re-renders one chapter and its Solutions page (two pandoc runs, against
the ~95 of a full build: 49 chapter pages, about 45 Solutions pages, and the
book index) plus the index page and the search index, both of which a changed
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
the book's anchors ambiguous: 45 chapters end in `## Exercises`, and
`#immutability` and six other anchors each appear in
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
| `[x](23_Patterns--Singleton.md)` | `[x](#ch23)` |

The `ch` prefix is not decoration: an EPUB is XHTML, where an id may not start
with a digit. The old ids come from `heading_links.pandoc_anchor()`, the
function the `anchors` gate checks links with, so a link the gate accepts is a
link this build resolves; its per-file de-duplication is mirrored too, so a
chapter with two identical headings keeps pandoc's `-1` suffix inside its own
namespace. A link naming a chapter's *own* title heading is aliased to the
chapter's root id, since `load_chapter()` lifts that heading out into the
title. Anything that still resolves to nothing is reported and left unlinked.

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

## send_to_kindle.py

`tip kindle` hands a built EPUB to Amazon's Send to Kindle desktop app.
The app takes a file path on its command line, the same call its
Explorer context-menu entry makes, and opens its dialog with the file
queued. The device choice and the Send click belong to the app, so the
script starts it and returns without waiting for the upload. It also
opens a file-manager window (Explorer, or Finder on macOS) with the EPUB
selected, for drag and drop if the app starts empty. On Windows it
expects the app under `Program Files (x86)\Amazon\SendToKindle\` and
names the download page when the app is missing. Linux has no app, so
there the script exits with a message pointing to email delivery or the
web uploader.

The e-ink EPUB is the default (a Paperwhite is the target), and
`VARIANT=color` sends the other. Before sending, the script compares the
EPUB's modification time with its inputs: everything under `Chapters/`
and `resources/`, plus `build_epub.py`, `build_site.py`, and
`config.py`. A missing or
older file is rebuilt with the same `build_epub.build()` call `tip epub`
makes, so the file sent is current with the Markdown. A current file
goes as it is, and its age is printed either way. `tip epub` always
rebuilds, so this is the one place the inputs are compared. A rebuild
needs pandoc. `verify-targets` leaves `kindle` out because it opens a
GUI.

```
tip kindle                # send the e-ink EPUB, rebuilt first if stale
tip kindle VARIANT=color  # send the color EPUB
```

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
page (of a page's listing line-number anchors, the first
`CODE_LINES_PER_PAGE`), taps the first link of each kind on each page, and fails on a
link into the book with no panel, a navigation link with one, or a
panel with an id, a back-link, or a stray `#place` link in it. It
needs node, which no gate does, and its first run installs jsdom
(major version pinned in the script) under `build/node/` from the
network, so it is in no gate and `verify-targets` skips it.
`tip release` runs it after `verify`, and `tip everything` runs it in
place of a bare site build. CI ran it before the Pages upload until
2026-10-24, when it took 4m40s of a 5m44s run; the workflow now pins
pandoc to the local version (`PANDOC_VERSION` in `ci.yml`), so a
local run tests the HTML the deploy publishes. It reads the script from `resources/static`
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
on the site (template.html) and the PNG in the EPUBs
(injected by build_epub.py's shared assembly, which also places the
cover art on each Part divider page). The PDF draws its own band in
typst (`build_pdf.py` passes the assembly `ornament=False`). And `chapter-snake.png`: the
line-drawn serpent from `resources/chapter-snake-source.png`, 320 px
wide, which template.html sets to the left of each chapter title on
the site (and above it on a narrow screen). `snake_from_drawing()`
makes it in either mode with Pillow alone: each pixel's darkness
becomes its opacity and its color the site's ink, so the paper drops
out and the drawing's anti-aliased edges survive, and the image is
cropped to what remains; `--snake` writes it alone. It replaced a
cutout of the cover art's serpent on 2026-09-30, which read too dark
beside a title. The EPUBs set it on its own line under each
chapter title, above the ornament, and the PDF under the typst
ornament band that underlines the title. The index page does
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
there anyway: ruff caps listing lines at 60 characters, which fits the
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

## Index: book_index.py and index_seed.py

The book's index is data plus code, with no markers in `Chapters/`
(`INDEXING.md` has the survey and the decisions).
The entries live in `tools/data/index_terms.toml`,
one `[[entry]]` table each:
the heading, its `kind` (`concept`, `pattern`, `python`, `pep`),
the `match` patterns that count as a mention,
and optional `under`, `see`, `see_also`, and `code`.
`index_seed.py` wrote the first version of the file on 2026-10-16
from the book's conventions (italic terms, pattern names,
Python names in code spans, PEP numbers).
It is a one-time seed: from then on the file is edited by hand.

`book_index.py` matches the entries against the chapters on every build.
An entry gets one locator per `##` or `###` section,
principal (first, and bold) when the section's heading holds the term
or the section italicizes it where it defines it.
A locator names a paragraph.
The builds inject an id at the start of that paragraph in the text in memory,
`[]{#ix-12-34}` for chapter 12's paragraph 34.
The site writes `book-index.html`, linked from the header and the contents page;
the EPUB adds an Index chapter of links;
the PDF adds the same chapter as typst, which looks up each id's page number.
`tip index` writes `build/index/index.md` and prints the counts.
`tip index-report` lists italic terms with no entry, dead entries,
broken cross-references, near-duplicate entries, and entries over eight locators.
Neither is in a gate. The module docstring has the matching rules.
Tests live in `tools/tests/test_book_index.py`.

## release.py

Publishes a GitHub release whose uploaded assets are the fresh
PDF, the two EPUB variants (`-color` and `-eink`), and the reader guides
in `GUIDES`, shipped as-is from `resources/`. Run
`tip release VERSION=1.0`; the tag is the version
with a `v` prefix (`v1.0`), created on origin at the branch tip. Needs
`git` and an authenticated `gh` (`gh auth login`).

The order is preflight, verify, preview check, build, publish,
cheapest first. The
preflight refuses a dirty tree, a detached HEAD, a branch whose tip
does not match origin, and a tag that already exists (locally or on
origin): the tag must point at the pushed commit the assets were built
from. Then `tip verify` runs the full gate, so a book that fails it
can never ship. If verify's self-healing fixers rewrite tracked files,
the run stops and asks for a review-commit-push before trying again,
since the tree no longer matches the pushed commit. `tip
preview-check` then builds the site and tests its link previews,
which CI no longer does. Only then are the
PDF and EPUBs rebuilt (both builders wipe their output directory first,
which is what makes the assets fresh) and handed to `gh release
create`. All are built with the `--release` stamp, so their title
pages tell the reader which release they hold and when it was made
("Release 1.0 · August 23, 2026"); an ad-hoc `tip pdf`/`tip epub`
carries no stamp, so a casual build never masquerades as a numbered
release. A final prune step deletes every release older than the newest
two (the git tags stay), and `tip release-prune` runs that step alone.
Deleting a bad release stays a manual act:
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
heading needed to deep-link to it. Solutions pages are sources too, with
one record per exercise. Anchors come from
`heading_links.pandoc_anchor()`, the same function the gate checks links
with, so a link the gate accepts and a link a search result produces
resolve to the same heading.

## serve.py

Serves `build/site/` over HTTP for local preview. `tip serve` runs it with
`--watch --copy-on-select`; `tip local` builds the site first, then adds
`--open`. Use
`--port N` for another port. It builds nothing on startup, so run a site build
first if `build/site/` is missing.

`--watch` turns it into an edit loop. A daemon thread compares modification
times every second across `Chapters/*.md`, `Solutions/*/README.md`, the
figures in `resources/images/`, and the few files the whole site
renders from (`template.html`, the static assets). A changed chapter goes
through `build_site.rebuild_chapter()`, roughly 0.3s here; a changed template
or asset rebuilds every page, roughly 5s. A change to the build code itself
(any `tools/` module the server imports) restarts the server under its
supervisor process, and the new server rebuilds every page with the new code;
the module docstring says why a rebuild alone is not enough. Served pages carry an injected script that
polls `/__reload` for a token the watcher bumps after each rebuild, so the
open page refreshes on its own. A rebuild holds a lock the request handler
also takes, so no request can read `build/site/` while a full build is
deleting and rewriting it. Polling beats a filesystem-watch library here
because it needs no new dependency, and about 130 `stat()` calls a second cost
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
  cached) and pandoc, runs `uv sync --locked`, and builds the static site.
  The pandoc is the release `.deb` at `PANDOC_VERSION`, set at the top of
  the workflow; keep it equal to the local `pandoc --version`, so the
  deployed HTML is the HTML `tip preview-check` tests locally. On a
  push to `master` it hands the site to the `deploy` job, which publishes it to
  GitHub Pages. Pull requests build the site but do not deploy.
* **`gates` (opt-in only):** a subset of what `tip ci` runs
  locally: the drift check (`extract_examples.py`), the example run
  (`run_examples.py`, all must pass), the pytest examples
  (`pytest build/examples`), the type check (`ty check build/examples`,
  zero diagnostics), and the lint (`ruff check build/examples`, zero
  findings), followed by the same five checks for `Solutions/`
  (`extract_solutions.py`, `validate_output.py --tree build/solutions`,
  `ty check build/solutions`, `ruff check build/solutions`, and
  `pytest build/solutions`). It does not validate the `#:` markers in
  `Chapters/`. Deliberate lint exceptions live in
  `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`.
* **`prose` (opt-in only):** codespell and Vale over `Chapters` only, the
  CI-safe part of `tip spell` and `tip prose`.
  codespell spell-checks `Chapters/` (config in `[tool.codespell]`, ignore list
  in `tools/data/codespell-ignore.txt`) and fails on a spelling error. It then
  installs the Vale binary and runs the house-style rules in `styles/House/`;
  Vale fails the job on an em-dash (error level) and prints the filler
  findings as warnings. Shares the gates trigger.
* **`effects` (opt-in only, on its own switch):** builds and runs chapter
  44's Koka, Flix, Scala (ZIO), and TypeScript (Effect) programs with
  `tip effects-test REQUIRE=1`, after installing the four toolchains. It runs
  when the `run_effects` input is `true` on a manual run, or when a push's
  commit message holds `[effects-ci]`.

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
   `Examples/` and `Solutions/`, then runs the full gate (drift, run,
   pytest, ty, ruff, plus the same for `Solutions/`) and builds the site.
   Use plain `tip ci` when you want to confirm there is no drift rather
   than paper over it.
3. When it is green, commit and push, including any updated `Examples/` or
   `Solutions/` files. The default CI path just rebuilds and publishes the
   site; it does not re-run the gates, so the push is fast.
4. Only when you want CI to re-check the suite itself (an environment-specific
   change, say, or a release) request the gates: add `[full-ci]` to the push
   commit message, or trigger the workflow manually as shown above.
