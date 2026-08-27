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
Markdown file's stem). So `# trace.py` in `08_Decorators.md` is extracted to
`08_Decorators/trace.py`. The slug carries no chapter prefix; the extractor adds
it. A slug may include a sub-path (`# mouse/mouse_action.py`) to group related
files within one chapter. Renaming or renumbering a chapter therefore moves its
example folder to match. Blocks without such a first line are illustrative
fragments and are ignored. Data files (`.txt`, `.dat`) tagged the same way are
extracted too, so examples that read them can run.

`Examples/` is the curated copy committed to git. `build/examples/` is a
throwaway tree (git-ignored) regenerated from the Markdown for running.

`Solutions/*.md` (worked exercise answers) go through the exact same
extract/validate/ty/ruff/pytest pipeline, via a parallel set of tools and
`make` targets described in [extract_solutions.py](#extract_solutions.py)
below. The one difference is that a Solutions code block is
**self-contained**: it redeclares whatever small piece of book context it
needs (a class, a helper function) rather than importing from `Examples/`,
so the two trees never couple and a change to a book example cannot silently
break a Solutions file.

## How this directory is laid out

`tools/` holds four kinds of thing, told apart by name:

* **Entry points** (`extract_examples.py`, `validate_output.py`, ...) are run
  as scripts, almost always through a `make` target. Each one's module
  docstring is its reference, and `--help` prints it.
* **Shared libraries** are exactly the `tools_*.py` files. They define no
  command and are only imported. The `tools_` prefix is not decoration: an
  entry point imports its siblings by bare name, and `validate_output.py`
  execs every book listing in that same process, so a library named `config`
  or `repo` would be found by a chapter's own `import config` through
  Python's `sys.modules` cache. See `tools_repo.py`'s docstring.
* **`data/`** holds the word lists, allowlists, and glob lists the checks
  read (`wordlist.txt`, `norun.txt`, `banned_phrases.txt`, ...), so this
  directory lists code and nothing else.
* **`tests/`** holds the harness's own unit tests, run by `make tools-test`
  and as the first step of `make gate`. They are separate from the book's
  example tests, which live in the chapters and run from `build/examples/`.

The libraries are worth knowing before reading any entry point, because
together they are why a check is usually thirty lines:

| Module | What it provides |
| --- | --- |
| `tools_config.py` | Paths and the convention regexes. Constants only, no behavior. |
| `tools_repo.py` | Small shared behaviors: walking `Chapters/`, reading a glob list, running a subprocess. |
| `tools_markdown.py` | `Document.parse()`: one parse of a Markdown file into lines, fenced `Block`s, and headings. |
| `tools_prose.py` | Which lines are prose, and which inline spans (code, footnotes) to ignore within one. |
| `tools_pycode.py` | Walking fenced Python and finding a real `#` comment in a line, string-aware. |
| `tools_report.py` | `Finding` and `Check`, the shape every check produces and the reporter that prints them. |
| `tools_extract.py` | Routing blocks to paths, conflict detection, and writing or checking a tree. |

A check is a function from a `Document` to `Finding`s, which is what lets
`check_all.py` run all of them over one parse, and what lets a test build a
document in memory with no filesystem at all.

This README covers the tools you invoke by hand and the conventions behind
them. It is deliberately not an inventory of all forty files: `make help`
lists every target, and each script's `--help` prints its own docstring.

## Commands

Tooling is managed by [uv](https://docs.astral.sh/uv/). One-time setup:

```
uv sync          # create .venv with the dev tools (ty) pinned by uv.lock
```

Run `make tools-check` afterward to confirm everything resolved (`uv`, `ty`,
`ruff`, `pytest`); `make tools-check-full` also checks `pandoc` and `vale`,
needed only for `make site`/`make local` and `make prose`. See
[check_tools.py](#check_tools.py) below. If something you expect to work
doesn't, `make doctor` (see [doctor.py](#doctor.py)) checks for the couple
of environment problems that look like a bug in the book but aren't.

To run GNU Make natively on Windows, install it with winget, which ships with
modern Windows and is the quickest setup. In Command Prompt or PowerShell, run:

```
winget install ezwinports.make
```

Restart the terminal to refresh the PATH, then run `make --version` to confirm.

Run targets with `make` (they go through `uv run`); `make help` prints the
complete, categorized list, generated from the Makefile itself so it never
drifts out of date (see [make_help.py](#make_help.py) below). The everyday ones:

```
make all        # every everyday fixer, refresh markers, sync, then the full gate but the site
make verify     # refresh markers, sync Examples/ and SolutionsCode/, then every gate but the site
make sync-ci    # like verify, plus the site build (the full gate)
make ci         # the full local gate: check, ty, ruff, run, pytest, site
```

`make all` is the loop to repeat after editing a chapter: every mutating
fixer (`reflow`, the comment-style fixers, import sorting, blank-line
cleanup), then a refresh of the `#:` output markers, then a sync of the
generated trees, then the full gate; see [run_all.py](#run_all.py) below.
`make verify` is the lighter everyday command: it skips the fixers and
just refreshes markers and pushes your Markdown changes out to
`Examples/` (so the drift check passes) and your `Solutions/` changes out
to `SolutionsCode/`, then runs every gate except the site build. `make
sync-ci` does the same and also builds the site. Both `verify` and
`sync-ci` refresh markers (`output`/`solutions-output`) *before*
syncing, on purpose: `gate`/`solutions-gate` also refresh markers, but
only after whatever sync step ran ahead of them already copied the
Markdown, so a marker that needed fixing would otherwise stay one sync
behind until the *next* run caught it up. `make ci` runs the gate (with
site) without syncing first, so it still fails on drift, the way GitHub
Actions does.

## make_help.py

Prints the `make help` listing, in two levels. In the Makefile, a target
line ending with a `## text` comment becomes one entry; a `##@ Name`
comment line starts a new section. Bare `make` prints the everyday
commands and the section list; `make help NAME` expands one section,
where `NAME` is the first word of that section's heading, lowercased.
A `##-` comment marks a target secondary: documented and smoke-tested,
but folded out of the listing because a sibling's doc text names it
(each `fix-*` under the check it repairs). It replaces a `grep | awk`
one-liner so `make help` has no dependency on a POSIX toolchain being on
PATH: every other target already requires Python (via `uv run`), and this
keeps `help` consistent with that.

Doc text wraps to the terminal width (capped at 100, falling back to 80
when the output is piped), with continuation lines indented under the doc
column so the target names stay in one column. A backticked command and a
hyphenated target name both wrap as one unit.

```
make help         # everyday commands, then the section list
make help style   # one section's targets

uv run python tools/make_help.py --width 72   # wrap to a fixed width
```

## run_all.py

Runs `make all`: the everyday edit-and-check loop, as an ordered list of
`make` targets (`ALL_TARGETS` in the script) run one at a time as their own
subprocess, stopping at the first failure. Add or remove a target name in
that list to change what `make all` runs; its `--help` text comes straight
from that target's own `## text` comment in the Makefile (the same one
`make help` reads), so nothing else needs updating.

```
make all               # run every target in ALL_TARGETS, in order
make all ARGS=--help   # list them, with their doc text, without running
```

## sweep_checks.py

`make gate` stops at its first failing step, which is right when you broke
one thing. It is wrong right after a tool upgrade, when the question is not
whether something broke but how much did. Worse, `gate` declares
`solutions-gate` as a *prerequisite*, so the whole Solutions half runs
first and can hide every `Chapters/` failure behind it, the opposite of the
order the recipe reads in.

`make sweep` runs each check to completion and summarizes which failed:

```
make sweep     # every check over both trees, all failures, exit 1 if any
```

`make tools-upgrade` ends with it, so an upgrade's damage arrives attached
to the upgrade that caused it. The list is `SWEEP_TARGETS` in the script,
and each row's description is read from that target's own `## text` in the
Makefile. It sweeps `gate-checks` (the gate's Markdown selection) rather
than `checks`, since `checks` also runs Vale, a standalone binary the sweep
would then require. The `#:` markers
are deliberately not swept: `make verify` rewrites a stale marker instead
of failing on it, so a nondeterministic listing would report a difference
here every run.

## verify_targets.py

Smoke-tests every target in `make help`, so a target that broke stays
broken for one run rather than until someone happens to use it. Read-only
and idempotent targets run directly; a target that bakes `--fix`/`--write`
into its recipe runs in a disposable git worktree, so this working tree is
never touched. `tools-upgrade`, `python-upgrade`, `serve`, and `local`
never run at all, being network or environment mutations or a server that
blocks forever. Logs land in `build/target_test_logs/`.

## check_chapter.py

The full gate spends most of its time executing every listing in all 44
chapters, almost none of which is about the chapter you just edited. This
runs the same code-example checks scoped to one:

```
make check-ch CH=12     # or CH=12_Data_Classes_as_Types
```

It rebuilds `build/examples/` whole-book first (cheap, and necessary since
a chapter's listings import their siblings), then narrows the expensive
step, `validate_output.py --update`, to that chapter, and finishes with the
listing gates plus `ty`, `ruff`, and `pytest` over that chapter's directory.

## Status stamps: gate_stamp.py and tool_stamp.py

Both write to `build/`, which is gitignored, so neither can enter a commit
or dirty a diff.

**`gate_stamp.py` (`make gate-status`)** records a pass of the gate along
with a hash of every `Chapters/` and `Solutions/` file, so it answers the
question that matters after an editing session, which is not "when did the
gate run" but "has anything changed since it did":

```
gate passed 12 minutes ago (2026-07-25 14:03), at commit d6b9ad6
3 files changed since: 23_Iterators.md, 24_Singleton.md, ...
```

**`tool_stamp.py` (`make tools-status`)** records when `make tools-upgrade`
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
`make` and `git` are checked too but marked "assumed" (you already needed
both to get this far), so their absence doesn't fail the exit code. `--full`
adds the tools a book maintainer needs for the rest of `make help`: `pandoc`
(`make site`, `make local`) and the standalone `vale` binary (`make prose`).

```
make tools-check        # uv, ty, ruff, pytest (make/git checked, assumed)
make tools-check-full   # the above, plus pandoc and vale
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
that makes `uv sync` — and so `make python-upgrade` — fail with "Access is
denied" removing `.venv\Scripts`. Every check prints ok/WARN and, on WARN,
the exact fix command; nothing is installed, upgraded, or killed.

```
make doctor
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
and falls back to printing the install link if neither works. `make` and
`git` are left alone, same as `check_tools.py`. For the pinned Python
version itself, use `upgrade_python.py` below instead.

```
make tools-upgrade   # update uv, ty/ruff/pytest/..., and (best-effort) pandoc/vale
```

## upgrade_python.py

Upgrades the pinned development Python and resyncs the environment. With no
argument, `make python-upgrade` fetches the latest patch of the minor pinned
in `.python-version` (e.g. the newest 3.14.x). With `TO=3.15`, it first
repins: rewrites `.python-version` and the `requires-python` floor in
`pyproject.toml`, then syncs. Either way it finishes by running `make
verify`. It runs through `uv run --no-project` so the orchestrating
interpreter is never the venv that `uv sync` is about to rebuild.

```
make python-upgrade           # latest patch of the pinned minor, then verify
make python-upgrade TO=3.15   # repin to a new minor, then verify
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
make sync    # write Examples/ from the Markdown
make check   # verify the Markdown matches Examples/
make prune   # delete the orphaned strays check flags
```

A block whose slug starts with `rust/` (e.g. `# rust/fastcount/demo.py`)
is skipped here on purpose: see `extract_rust.py` below.

## extract_rust.py

A second, separate extractor for the Rust/PyO3 examples in
[Converting a Slow Function to Rust](../Chapters/18_Performance.md#converting-a-slow-function-to-rust),
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
done by the main build; see `rust/README.md` and `rust/Makefile` (run
`make` from inside `rust/`).

```
python tools/extract_rust.py            # check vs rust/
python tools/extract_rust.py --write     # update rust/
```

## run_examples.py

Runs every `.py` under `build/examples/`, each in its own directory so the
examples' relative data paths resolve. Reports passed / skipped / timed-out /
failed and exits non-zero if anything fails or times out.

`test_*.py` and `conftest.py` are skipped here: they are pytest files, run by
`make test` (`uv run pytest build/examples`), not as standalone scripts. See
the Testing chapter.

* Narrow the run: `python tools/run_examples.py 16_State_Machines`
* Adjust the kill timeout: `--timeout 20` (default 15s)
* Parallelism: runs on all cores by default (`-j auto`); each example is its
  own subprocess, so this is safe. Use `-j 1` for serial, or `-j N` for a fixed
  count. (pytest runs serially by default; enable xdist with
  `make test PYTEST_N="-n auto"`.)

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
python tools/run_examples.py --baseline        # fail only on NEW breakage
python tools/run_examples.py --write-baseline   # regenerate the baseline
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
make output-check   # verify markers, no rewrite
make output         # rewrite stale markers in Chapters/
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

```
make solutions-sync           # write SolutionsCode/ from Solutions/*.md
make solutions-check          # verify Solutions/*.md matches SolutionsCode/
make solutions-prune          # delete the orphaned strays solutions-check flags
make solutions-extract        # write build/solutions/ (for the checks below)
make solutions-output-check   # verify #: markers in Solutions/*.md, no rewrite
make solutions-output         # rewrite them
make solutions-ty             # type-check build/solutions/
make solutions-lint           # ruff-check build/solutions/
make solutions-test           # pytest build/solutions/ (test_*.py)
make solutions-numbering      # every exercise has a solution (below)
make solutions-gate           # all of the above in one go
```

`solutions-gate` runs as part of the main `gate` (and therefore `verify`,
`sync-ci`, and `ci`), so a Solutions regression fails the same build a book
regression would. There is no Solutions counterpart to `run_examples.py`:
every extractable Solutions block already carries a `#:` marker (checked by
`solutions-output`, which executes the block to compare), and a block with
none is a deliberately-unrun illustrative fragment (no `# file.py` slug), the
same convention `Chapters/` uses for code that only makes sense narrated in
prose (a type error, a race outcome).

`validate_output.py` needs an **absolute** `--tree` when pointed at
`Solutions/`: a block runs with its cwd inside `build/solutions/<chapter>/`,
and a relative tree argument stops resolving once cwd changes underneath it
(the `run_location()` gotcha `run_examples.py`'s own `--tree` warning
already describes). The Makefile passes `$(CURDIR)` for this reason; do the
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
make solutions-numbering            # every chapter
make solutions-numbering ARGS=19    # only chapter 19
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
copied from a chapter, `](24_Singleton.md#state)`, resolves to
`Solutions/24_Singleton.md`: a real file, wrong content, no warning from
anything. Seventeen links were wrong this way before anything looked. The
correct form is `](../Chapters/24_Singleton.md#state)`, and a leading `./`
marks a deliberate link to a neighboring solution.

`heading_links.py` covers the other half. The gate now runs its `anchors`
check over `Solutions/` as well (see `GATE_DOCS` in the Makefile), which
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
make reflow-check        # report which chapters would change, no write
make reflow              # rewrite the whole book
make reflow CH=02        # rewrite one chapter (by number, name part, or path)
make reflow-check CH=02  # preview one chapter, no write
uv run python tools/reflow_prose.py --diff Tour   # diff a chapter by name part
```

A positional argument (or `CH=`) may be a file path or a chapter selector
matched against `Chapters/`: a number or stem prefix (`02`, `02_A_Python`) or a
substring (`Tour`). With no argument the whole book is processed.

## Spelling and prose style

Several layers, all optional and not part of the default CI gate.

**Spelling: codespell (`make spell`).** A uv-managed dev tool, so it runs through
`uv run`. It prints one line per suspected misspelling and exits non-zero if it
finds any, so **no output means clean** (a silent return to the prompt is a
pass). It matches a curated misspelling dictionary rather than a full one, so it
stays low-noise even over code comments and examples, but it will not catch an
unusual typo that is not on its list ("fixted" for "fixed"); for that there is
the full-dictionary check below. Configuration lives in `[tool.codespell]` in
`pyproject.toml`; words it flags wrongly (design-pattern terms like `adaptee`,
foreign-language quotes, deliberate code strings) are listed in
`tools/data/codespell-ignore.txt`. Scope it with `CH=`, for example
`make spell CH=02`.

**Full-dictionary spelling: spellcheck.py (`make spell`).** Where codespell
knows only a curated list, `tools/spellcheck.py` (using the uv-managed
`pyspellchecker`) checks every prose word against a real English dictionary, so
a novel typo is caught. It checks prose only: code blocks, inline code,
footnotes, and link URLs are stripped via `tools_prose`, so identifiers do not
flood it. Two more things are not prose either, and both once produced findings
that looked like typos: a heading's explicit `{#anchor}`, whose slug splits into
words that are not (`sys-monitoring` gives "sys", `dont-start-the-engine` gives
"dont"), and the continuation lines of a multi-line HTML comment, which the
stateless classifier cannot see past its opening line. Accepted terms
(technical words, names, coined words) live in
`tools/data/wordlist.txt`, one lowercase word per line. When it flags a real term,
add it there; when it flags a typo, fix the prose. Use
`uv run python tools/spellcheck.py --summary` to see the unique unknowns by
count, which makes seeding the word list quick. `make spell-add` automates the
"add it there" step: it accepts every unknown word into the wordlist, sorted
and deduplicated. It cannot tell a real term from a typo, so always review
`git diff tools/data/wordlist.txt` before committing.

**Mechanical prose: prose_lint (`make spell`).** `tools/prose_lint.py` runs
alongside codespell and catches small mechanical slips a spell checker ignores:
more than one space between words, a space before `.`/`,`/`;`/`!`/`?`, more than
one blank line in a row, a period or comma left outside a closing quote, and
trailing whitespace (a two-space hard break is allowed). It shares the
`tools_prose.py` classifier with `reflow_prose.py`, so fenced and indented code,
tables, blockquotes, and HTML are skipped, and inline code spans and footnotes
are ignored inside a prose line; headings and list-item text are checked but
their markers are not. It is report-only and exits non-zero on any finding. Run
it directly with `uv run python tools/prose_lint.py Markdown` (or a single file).

The quote check reads a quoted *literal* differently from quoted prose. The book
puts the mark inside a quoted phrase (`"easier to ask forgiveness than
permission,"`) but outside a literal, where moving it in would put a comma into
a `pytest -k` substring or a period into an error message the reader matches
against. A quote holding an inline code span, and a single-token quote such as
`"overdraft"`, are therefore skipped. A multi-word literal fits neither shape,
so write that one as an inline code span rather than as a quotation.

**House style: Vale (`make prose`).** Vale is a standalone binary, not a Python
package, so install it once (`winget install errata-ai.Vale`,
`brew install vale`, or see <https://vale.sh/docs/install>). Vale parses Markdown
and checks only text, never code spans or fenced code, so the rules never fire on
identifiers or examples. Spelling is left to codespell; Vale enforces house style
only. The rules live in `styles/House/` and are wired up by `.vale.ini`:

* `EmDash` (error): no `—`, `–`, or `--` used as a dash.
* `Filler` (warning): throat-clearing phrases ("this is the whole idea", and so on).

To add the community packages for passive-voice and usage checks, list them in
`.vale.ini` (`Packages = write-good, proselint`) and run `vale sync` once.

## check_all.py

The checks below each have their own script and their own `make` target,
which is what you want when one thing is broken and you are iterating on
it. Running them one at a time means an interpreter startup and a fresh
parse of all 45 chapters per tool, and N summaries instead of one answer to
the question "is the book clean?"

This runs them together: every file is parsed once into a `Document` and
handed to each check, and all findings land in one list sorted by file and
line, so the report reads top to bottom through the book rather than
grouped by which tool noticed.

```
make checks                # every Markdown check, one pass
make checks ARGS=--list    # their names and descriptions
make fix-checks            # apply every fix they can make
make gate-checks           # just the subset `gate` enforces
```

The registry is the explicit `CHECKS` list in the script, deliberately not
directory discovery: an explicit list is greppable, and it cannot surprise
the interpreter that also execs book listings. Adding a check means
importing it and adding it there, after which it appears in `--list`, in
the default run, and as a selectable name.

`gate` runs the selection named by `GATE_CHECKS` in the Makefile, which is
now the whole registry: `prose-lint` was the last holdout and joined once
its findings were cleared. `make checks` runs the same registry plus the
Vale prose lint, which the gate leaves out because Vale is a standalone
binary rather than a uv-managed one.

## check_line_endings.py

`.gitattributes` (`* text=auto eol=lf`) already keeps committed blobs LF on
every platform, so the repo and the Linux CI build are always LF. This tool
guards the **working tree**: on Windows an editor can write CRLF into a source
file, which is harmless to git but produces noisy warnings and inconsistent
local files. `make eol` reads `git ls-files --eol` (so it honors the binary
markers in `.gitattributes`) and fails if any tracked text file has CRLF or
mixed endings. It is part of the `make ci` gate. There is no auto-convert in the
build; run the fixer explicitly when the check flags something:

```
make eol       # check, exit 1 on CRLF (part of `make ci`)
make fix-eol   # convert any offenders to LF
```

## listing_format.py

The book favors dense listings: at most one blank line in a row, and no blank
line between import groups. Ruff's isort config (`no-lines-before`,
`lines-after-imports = 1`) enforces the import layout, but only on the extracted
`.py` files: it cannot rewrite the `Chapters/` source, and it does not check
blank-line counts between defs at all. This tool closes both gaps by checking
the Markdown directly. It is string-aware, so blank lines inside triple-quoted
strings are never touched, and it only looks at ```python blocks. It is part of
the `make ci` gate; like line endings, there is no auto-fix in the build:

```
make listings       # check, exit 1 on extra blank lines (part of `make ci`)
make fix-listings   # remove the offending blank lines
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
it against a built tree (`make fix-imports` depends on `extract`).

```
make fix-imports    # rewrite the listings' import blocks
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
ignored). It is part of the `make ci` gate.

```
make banned    # fail if any banned phrase is in the book (part of `make ci`)
```

## comment_periods.py

Enforces the comment-period policy in ```python listings: a one-line comment
ends without a period; only a multiline comment (two or more consecutive
full-line `#` comments) reads as sentences and keeps its periods. So it flags a
trailing period on an inline comment or a lone full-line comment, but leaves
multiline blocks alone. It is string-aware (a `#` inside a string is not a
comment) and skips an ellipsis (`...`). It is part of the `make ci` gate.

```
make comment-periods       # check (part of `make ci`)
make fix-comment-periods   # strip the trailing periods
```

## capitalize_comments.py

Enforces that a prose comment in a ```python listing starts with a capital. The
prose-vs-code judgment is a heuristic, so it skips code-identifier first words,
single letters, and keywords, and continuation lines of a multiline comment. Its
unavoidable false positives (program output like `# total = 7`, an identifier
reference like `# n is the counter`, schematic notation like `# name -> subclass`)
are listed by comment text in `tools/data/comment_caps_allow.txt` and skipped. It is
part of the `make ci` gate.

```
make comment-caps       # check (part of `make ci`)
make fix-comment-caps   # capitalize the flagged comments
```

When the checker is wrong, add the comment's text to the allowlist; when it is
right, capitalize the comment (or run `make fix-comment-caps`).

## comment_spacing.py

Enforces that an inline comment in a ```python listing (code precedes it on
the same line) starts exactly two spaces after the code ends. A full-line
comment and a `#:` output marker have no code on their line to measure the
gap from, so both are left alone. It is string-aware (a `#` inside a string
is not a comment) and collapses any gap, including one used to
column-align several comments, to two spaces. It is part of the `make ci`
gate.

```
make comment-spacing       # check (part of `make ci`)
make fix-comment-spacing   # collapse the gaps to two spaces
```

## heading_links.py

Verifies that every heading-anchor link resolves to a real heading, so a typo
does not ship as a dead in-page link. Markdown can link to a heading with
`[text](#id)` (same file) or `[text](07_Static_Typing.md#id)` (another chapter).
The tool reproduces pandoc's anchor rule (lowercase, spaces to hyphens,
punctuation and backticks removed, leading non-letters dropped), honors an
explicit `{#id}` on a heading, collects every id, and checks each `#anchor`
link against it. A bad cross-file link also reports a missing target file. It is
part of the `make ci` gate; there is nothing to auto-fix.

```
make anchors    # check (part of `make ci`)
```

To make an anchor stable against rewording, give the target heading an explicit
id: `## Heading {#stable-id}`, then link `(chapter.md#stable-id)`.

The gate checks `Chapters/` and this README (`GATE_DOCS` in the Makefile).
Two links in here were dead for a while precisely because nothing looked
outside `Chapters/`. Only the anchors check runs over this file: `banned`
would fire on the worked example in
[banned_phrases.py](#banned_phrases.py) above, which names a banned phrase
in order to explain the tool.

## Advisory checks: check_links.py and list_todos.py

Neither is part of `verify`/`gate`/`ci`. Run them now and then.

**`check_links.py` (`make links`)** requests every unique external
`http(s)://` URL in the book and reports connection errors, timeouts, and
statuses at or above 400. HEAD is tried first, with one GET retry for
servers that treat HEAD differently. It stays out of the gate on purpose:
the network is flaky, sites rate-limit, and a dead external link should
never block a build. Internal cross-references are `heading_links.py`'s
job, not this one.

**`list_todos.py` (`make todos`)** lists `TODO(tag): ...` markers left in
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
target chapter's `.md` file, for example `[Factory](18_Factory.md)`.
These render correctly on GitHub; the builder rewrites intra-book `.md` links to
`.html` so they also resolve in the site. External links (which carry a scheme)
are left alone.

Requires `pandoc` on PATH. Run `python tools/build_site.py` (or `make site`);
use `-o DIR` to build elsewhere. `make serve` builds nothing and serves the
existing `build/site/` at <http://localhost:8000>; `make local` builds, serves,
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
color as given. Run `make epub`; `-o DIR` builds elsewhere, and
`--keep-source` leaves the generated pandoc input under `<out>/src/` when
you need to see what pandoc was handed. Needs `pandoc`, like `site`.
`make clean-epub` removes the directory.

Chapter discovery, titles, the Part dividers, and the image map all come from
`build_site.py`, so the EPUB's contents match the site's rather than drifting
from it. What differs is linking. The site keeps one HTML page per chapter, so
a cross-reference stays a link between files and the builder only rewrites
`.md` to `.html`. An EPUB is a single document, and merging the chapters makes
the book's anchors ambiguous: 44 chapters end in `## Exercises`, and
`#immutability`, `#generators`, `#lambdas` and six other anchors each appear in
two to four chapters. Pandoc's own de-duplication numbers repeats in document
order, so `[Immutability](12_Data_Classes_as_Types.md#immutability)` would
quietly open chapter 3.

So every heading gets an explicit id namespaced by chapter number, and every
link is rewritten to match:

| Markdown | In the EPUB |
| --- | --- |
| `## Immutability` | `## Immutability {#ch12-immutability}` |
| `[x](12_Data_Classes_as_Types.md#immutability)` | `[x](#ch12-immutability)` |
| `[x](#immutability)` (same chapter) | `[x](#ch12-immutability)` |
| `[x](24_Singleton.md)` | `[x](#ch24)` |

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

`--release VERSION` (what `make release` passes) stamps the title page
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

## make_cover.py

Generates the covers and favicon. Two modes, chosen by whether
`resources/cover-source.jpg` exists. **Art mode** (the usual one):
that image, whatever its size, is composited with the book's
typography; the page background is sampled from the image's corners
and the art's edges are feathered into it, so any art on its own
paper color drops in seamlessly. To restyle the book, replace
`cover-source.jpg` and run `make cover`. **Drawn mode** (no source
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
cover art on each Part divider page). `--preview` writes a small `cover-preview.png` for quick
iteration.

## build_pdf.py

Renders the same `Chapters/*.md` into one PDF at
`build/pdf/ThinkingInPython.pdf` (git-ignored). Run `make pdf`; `-o DIR`
builds elsewhere, and `--keep-source` leaves the generated pandoc input
under `<out>/src/`. Needs `pandoc` plus `typst`, the PDF engine pandoc
drives (`winget install Typst.Typst`; `make tools-check-full` verifies
both). `make clean-pdf` removes the directory.

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
`make release VERSION=1.0`; the tag is the version
with a `v` prefix (`v1.0`), created on origin at the branch tip. Needs
`git` and an authenticated `gh` (`gh auth login`).

The order is preflight, verify, build, publish, cheapest first. The
preflight refuses a dirty tree, a detached HEAD, a branch whose tip
does not match origin, and a tag that already exists (locally or on
origin): the tag must point at the pushed commit the assets were built
from. Then `make verify` runs the full gate, so a book that fails it
can never ship. If verify's self-healing fixers rewrite tracked files,
the run stops and asks for a review-commit-push before trying again,
since the tree no longer matches the pushed commit. Only then are the
PDF and EPUBs rebuilt (both builders wipe their output directory first,
which is what makes the assets fresh) and handed to `gh release
create`. All are built with the `--release` stamp, so their title
pages tell the reader which release they hold and when it was made
("Release 1.0 · August 23, 2026"); an ad-hoc `make pdf`/`make epub`
carries no stamp, so a casual build never masquerades as a numbered
release. Deleting a bad release stays a manual act:
`gh release delete v1.0 --cleanup-tag`.

Deliberately excluded from `verify_targets.py`'s smoke test, alongside
`tools-upgrade` and friends: it tags the repo and publishes to GitHub.

## search_index.py

Builds `search-index.json`, which the site's `search.js` fetches and
searches in the browser. There is no server, so the whole index ships to
the reader, fetched lazily the first time someone opens the search box.
`build_site.py` calls this, so `make site` covers it.

A record is one *section*: the text under a single `##` or `###` heading,
plus the chapter's opening text, which sits under no heading and links to
the page itself. Each carries the page, anchor, chapter title, and section
heading needed to deep-link to it. Anchors come from
`heading_links.pandoc_anchor()`, the same function the gate checks links
with, so a link the gate accepts and a link a search result produces
resolve to the same heading.

## serve.py

Serves `build/site/` over HTTP for local preview. `make serve` runs it as-is;
`make local` builds the site first, then runs it with `--open --watch`. Use
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
* **`gates` (opt-in only):** the full suite, the same one `make ci` runs
  locally: the drift check (`extract_examples.py`), the example run
  (`run_examples.py`, all must pass), the pytest examples
  (`pytest build/examples`), the type check (`ty check build/examples`,
  zero diagnostics), and the lint (`ruff check build/examples`, zero
  findings), followed by the same five checks for `Solutions/`
  (`extract_solutions.py`, `validate_output.py --tree build/solutions`,
  `ty check build/solutions`, `ruff check build/solutions`, and
  `pytest build/solutions`). Deliberate lint exceptions live in
  `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`.
* **`prose` (opt-in only):** the same checks as `make spell` and `make prose`.
  codespell spell-checks `Chapters/` (config in `[tool.codespell]`, ignore list
  in `tools/data/codespell-ignore.txt`) and fails on a spelling error. It then
  installs the Vale binary and runs the house-style rules in `styles/House/`;
  Vale fails the job on an em-dash (error level) and prints the filler
  findings as warnings. Shares the gates trigger.

`deploy` depends only on `site`, not on `gates` or `prose`, so publishing is
never blocked by the opt-in checks. The trade-off is that a push can publish even if an example
would fail a gate, which is why you run `make ci` locally first.

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

Either way, treat CI as a second opinion: run `make ci` locally first.

### Suggested workflow

Day to day:

1. Make your changes by editing `Chapters/` (the source of truth for prose and
   code alike) or `Solutions/` (worked exercise answers).
2. Run `make sync-ci`: it pushes any code-block edits out to `Examples/` and
   `SolutionsCode/`, then runs the full gate (drift, run, pytest, ty, ruff,
   site, plus the same for `Solutions/`). Use plain `make ci` when you want to
   confirm there is no drift rather than paper over it.
3. When it is green, commit and push, including any updated `Examples/` or
   `SolutionsCode/` files. The default CI path just rebuilds and publishes the
   site; it does not re-run the gates, so the push is fast.
4. Only when you want CI to re-check the suite itself (an environment-specific
   change, say, or a release) request the gates: add `[full-ci]` to the push
   commit message, or trigger the workflow manually as shown above.
