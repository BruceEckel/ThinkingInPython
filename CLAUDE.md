# Thinking in Python: working in this repo

This file is loaded every session. It captures how the repo is built and verified,
plus the traps that are easy to rediscover the hard way. Personal writing style
lives in the global `~/.claude/CLAUDE.md`; accrued facts live in project memory.

## Source of truth: Chapters/, not Examples/

`Chapters/NN_*.md` is authoritative. Every fenced ```python block whose first line
is a `# path/slug.py` comment is an extractable example. `Examples/` is **generated
from the Markdown** by `tools/extract_examples.py`, so:

- Edit the code **in the Markdown block**, never in `Examples/` directly.
- After editing, sync the committed tree: `make sync`
  (= `uv run python tools/extract_examples.py --write -o Examples`).
- `Examples/` also holds files with no Markdown block (hand-written helpers,
  `.idea/`, `__pycache__`). `tools/extract_examples.py`'s check mode (part of
  `make check`/`gate`/`verify`/`ci`) flags these automatically: a stray file
  whose name appears nowhere in `Chapters/` is *orphaned* and fails the gate;
  one still mentioned somewhere (a real hand-written helper) is *referenced*
  and only reported, since deleting it needs a human call. `make prune-examples`
  deletes exactly the orphaned ones. A rename or deletion of a book example is
  the usual cause, so run this after either.

## Rust examples: rust/, isolated from the main build

Chapter 18's "Converting a Slow Function to Rust" section has real,
buildable PyO3/maturin crates under `rust/` (currently `rust/fastcount/`),
extracted from the same `Chapters/*.md` by `tools/extract_rust.py`, a
separate tool from `tools/extract_examples.py`. Two marker conventions,
both first-line comments in a fenced block:

- A ` ```rust ` block marked `// <crate>/src/<file>.rs` extracts to
  `rust/<crate>/src/<file>.rs`.
- A ` ```python ` block marked `# rust/<crate>/<name>.py` is the Python
  caller for that crate. The `rust/` prefix is what makes
  `tools/extract_examples.py` skip it entirely (never written to
  `Examples/`/`build/examples/`, never run by `pytest`/`ty`/`ruff`/
  `run_examples.py`), since the compiled module it imports does not exist
  in the main build's environment.

This is deliberate: the root `Makefile` never enters `rust/` and never
requires a Rust toolchain, so `verify`/`gate`/`all`/`ci` all work with no
Rust installed. Only `cd rust && make` (a separate `Makefile` there) syncs,
builds, and runs the crates for real; see `rust/README.md`. A crate
directory also holds real, hand-maintained project files
(`Cargo.toml`, `pyproject.toml`, `.python-version`, `.gitignore`,
scaffolded once by `maturin new --bindings pyo3 <name>`) that
`extract_rust.py` never touches, only `src/lib.rs` and the paired demo
file are book-generated.

## The verify loop after editing a chapter

Fastest path is `make verify` (fix line endings, refresh `#:` output markers,
sync, then every gate but the site build). `make all` is the heavier version:
it also runs every mutating fixer (`reflow`, the comment-style fixers, import
sorting, blank-line cleanup) before the marker refresh and sync; its ordered
target list lives in `tools/run_all.py` (`ALL_TARGETS`), and `make all
ARGS=--help` lists it without running anything. In both, the marker refresh
runs *before* the sync, not after: `gate`/`solutions-gate` refresh markers
too, but only after their own prior sync step already copied the Markdown,
so a marker that needed fixing would otherwise stay one sync behind until
the next run caught it up. When iterating on one chapter, the manual
sequence is:

1. `uv run python tools/extract_examples.py --write -o Examples`  # sync committed tree
2. `uv run python tools/extract_examples.py`                      # drift check ("In sync")
3. `uv run python tools/extract_examples.py --write`              # (re)build build/examples/
4. `uv run python tools/validate_output.py Chapters/NN_*.md`      # `#:` markers match stdout
5. `(cd build/examples && uv run ty check NN_Chapter)`            # types
6. `uv run ruff check build/examples/NN_Chapter`                 # lint
7. `uv run pytest build/examples/NN_Chapter`                      # tests
8. `uv run python tools/run_examples.py NN_Chapter`               # runs scripts, honors norun.txt

Prose-only edits still need `check_anchors.py` (cross-references) and
`banned_phrases.py`; both are in `make verify`. `make verify`'s gate also
runs `validate_output.py --update` over all of `Chapters/` now, so a stale
`#:` marker anywhere self-heals (rewriting `Chapters/`) instead of failing
the build, the same way `fix-eol`/`sync` already self-heal other drift.
Check `git diff Chapters/` afterward: a chapter you did not touch can
still land in the diff if its output actually changed. An exception
raised where none is expected still fails the gate; only marker text is
auto-corrected. A lone bare `#: ` with nothing after it is always treated
as a not-yet-filled-in placeholder and filled in, even without `--update`.

## Traps (learned the hard way)

- **Ruff line length is 70.** Long inline comments are the usual culprit; move the
  comment to its own line or wrap the statement. A scratch dir's `ruff` uses the
  default 88, so **line length must be verified against `build/examples`**, not a
  temp file.
- **Run `ty`/`ruff`/`pytest` against `build/examples/`** (via `uv run`), never a
  loose scratch file, or config/imports resolve differently.
- **Bare `python`/`ty`/`pytest` on PATH can be a different, older tool than
  `uv run`'s.** On this machine bare `python` is 3.14.6 while `uv run python`
  (and `python3`) is the pinned 3.15 beta, and bare `ty` is 0.0.46 against
  `uv run ty`'s 0.0.56. Running `validate_output.py` with bare `python`
  produced false failures on 3.15-only syntax (`sentinel`, `lazy import`,
  the PEP 798 comprehension-unpacking chapter) that vanished once invoked
  via `uv run`. Always go through `uv run` for anything that executes
  example code; never assume bare `python`/`ty`/`pytest` matches it.
- **CPython's small-int cache is wider on the pinned 3.15 beta than the
  textbook `-5..256` range.** Confirmed cached up to at least 1024 on this
  build. An example meant to show an "uncached" int needs a value safely
  above that (100000+), not just above 256, or the demo silently proves the
  opposite of what the prose claims. See project memory
  (`small-int-cache-extended-py315`) for the chapter-36 case this broke.
- **`tools/*.py` is not linted by any gate.** Only `build/examples` is checked by
  `make lint`/`make ci`, so a `tools/` script can exceed the 70-char limit with
  nothing catching it (several already do). `ty` still matters there; run it
  directly, e.g. `uv run ty check tools/whatever.py`.
- **`#:` output markers must equal stdout exactly.** For nondeterministic output,
  round floats (`f"{x:.6f}"`) or print `type(e).__name__` instead of a message.
  Since the gate now runs `validate_output.py --update`, a genuinely
  nondeterministic listing no longer fails the gate: it silently rewrites the
  marker to whatever this run happened to produce, and can thrash between
  values across runs with nothing to flag it. Don't assume a marker mismatch
  is repo drift; run the extracted script directly first
  (`build/examples/<chapter>/<file>.py`) to check whether the value is
  actually stable before accepting an auto-fix.
- **`validate_output.py` on the whole tree can leak `__del__` output between
  chapters.** It `exec()`s every block's code against a fresh `namespace` dict
  reused as that block's globals. A class defined there forms a reference
  cycle with its own globals (`SomeClass.method.__globals__ is namespace`),
  so plain refcounting never frees it; CPython's cyclic collector runs on its
  own schedule and can finalize it while a *different*, later block's stdout
  is being captured, corrupting that block's output. The fix lives in
  `validate_output.py` itself: drop the last reference to a block's
  `namespace` and call `gc.collect()` (see `collect_now()`) right after the
  block finishes, before moving on. Chapter 10 (Cleanup)'s `cleanup.py` is
  the example that demonstrates this (it deliberately relies on `__del__`
  timing being unpredictable), so it is the usual trigger if this regresses.
- **`build/` is derived and gitignored.** `extract_examples.py --write` now wipes
  the target under `build/` first, so a fresh sync is the fix for weird drift or a
  stale tree. A stale `build/examples/` was behind "phantom" timeouts/import errors.
- **Windows dir-lock on the wipe.** If the persistent shell's cwd sits inside
  `build/examples/<chapter>`, that open handle blocks the rmtree and
  `extract_examples.py --write` dies with `PermissionError [WinError 32]`. Keep the
  shell at the repo root and run chapter-dir commands in a subshell, e.g.
  `(cd build/examples && uv run ty check NN_Chapter)`.
- **`run_examples.py`: never pass a relative `--tree`.** It goes on `PYTHONPATH`
  and breaks once an example changes cwd. GUI/interactive examples are skipped via
  `tools/norun.txt` (keep those paths current when chapters are renumbered).
- **Renumbering a chapter** touches: `Chapters/` and `Examples/` filenames, every
  `NN_*.md` cross-reference, `build_site.py` `PARTS`, `tools/norun.txt`, and the
  `README.md` tracking table. Appendices use letter prefixes (`A_...`); build_site
  labels them "Appendix X".
- **Anchors:** pandoc auto-slugs a heading (backticks/punctuation dropped, but `.`
  is kept). Give headings an explicit `{#id}` when the auto-slug would be ugly
  (e.g. anything containing `type[...]` or `__init__`). `check_anchors.py` gates it.
- **`make help` is self-documenting, not hand-written.** A target needs a trailing
  `## text` comment on its own line (and to sit under the right `##@ Category`
  heading) or it will not appear in `make help`. Parsed by `tools/make_help.py`,
  deliberately not `grep`/`awk`, since GNU Make on Windows can fall back to
  `cmd.exe` as `SHELL` when no POSIX shell is on PATH.
  `tools/README.md`'s own "Commands" section deliberately does not re-list every
  target either (it did once, and went stale); it shows only the everyday few and
  points to `make help` for the rest. Don't re-expand it into a full manual copy.
- **A new third-party dependency may not install on the pinned Python.**
  `requires-python` tracks a bleeding-edge version (currently 3.15, a beta at
  the time this was written), so a package can lack a wheel for it (source
  build then fails) or refuse outright (its own installer version-guards).
  Before committing a new dev dependency: add it to `pyproject.toml`, run
  `uv sync`, and if it fails, revert (`git checkout -- pyproject.toml uv.lock`)
  and re-sync rather than fighting the build. See project memory for the
  numpy/numba case and the workaround for illustrating a chapter example
  anyway.
- **`ty` does not narrow `str` to `Literal[...]` via `match`/`case` or an
  `in` membership check.** Tried both (`match symbol: case "." | "~" | "#":`
  and `if symbol not in (".", "~", "#"):`); `ty` still reports the narrowed
  variable as plain `str` afterward, unlike pyright's literal-narrowing.
  The only way to satisfy `ty` is an explicit `cast(Literal[...], value)`
  after the runtime check has proven it safe. See project memory
  (`typing-construct-hierarchy`) for the chapter-36 case and the
  boundary-function idiom this led to.
- **A `type X = ...` alias's right side is lazily evaluated (PEP 695),** so it
  can name a class defined later in the same file with no string quotes, e.g.
  `type Bins = dict[type[Trash], list[Trash]]` above `class Trash:`. Confirmed
  both at runtime and under `ty check`.
- **Never auto-run `make upgrade-tools` or `make upgrade-python`.** Both mutate
  tracked files (`uv.lock`, and `.python-version`/`pyproject.toml` with `TO=`) and
  can invoke real system package managers (`winget`/`brew`). Only run them when
  the user explicitly asks for that specific run, not to "verify" a change.
  `make check-tools[-full]` is read-only and safe to run freely.
- **Prose in `Chapters/*.md` follows Semantic Line Breaks** (one sentence per
  line; a sentence still too wide breaks further at a top-level `,`/`;`/`:`),
  enforced by `make reflow` (`CH=NN` for one chapter), not any gate.
  `reflow`/`reflow-check` are standalone `--write`/check-only targets, absent
  from `verify`/`gate`/`ci`, so hand-edited prose can silently drift out of
  compliance. Before writing a script to reflow prose across the book, check
  `tools/reflow_prose.py` first: it already masks inline code/links/footnotes,
  protects an abbreviation list, and greedily packs clauses to fit a width
  instead of breaking every comma (a naive "break at every comma" script
  fragments simple lists like "insights, idioms, and patterns" into three
  lines, a regression, not a fix). Its `SINGLE_LETTER_WORDS` set holds single
  uppercase letters that are real words (`"C"`, the language) rather than
  initials like "B."; extend it if a new one causes a missed sentence split.
- **`ty` narrows a PEP 661 `sentinel()` parameter imprecisely if the
  annotation names the generic `sentinel` class instead of the specific
  value.** `dunder: Sequence[str] | sentinel` lets `ty` narrow the `is
  ALL_DUNDERS` branch, but the other branch keeps a bogus `sentinel &
  ~ALL_DUNDERS` type (some other sentinel value, not `Sequence[str]`), which
  then fails `name in dunder`. Naming the specific value instead,
  `Sequence[str] | ALL_DUNDERS`, fixes it: the union has only two members, so
  ruling one out via `is` leaves exactly `Sequence[str]`. See `display.py` in
  chapter 17 (Metaprogramming); project memory `typing-construct-hierarchy`
  has the fuller case study.
- **Every class, even an empty one, carries compiler-generated dunders that
  always differ from `object`'s own** (`__module__`, `__dict__`,
  `__firstlineno__`, `__annotate_func__`, `__static_attributes__`,
  `__weakref__`, `__doc__`). A filter meant to report "dunders this class
  redefined," built by comparing each dunder to `object`'s version, must
  restrict that comparison to a known allowlist (chapter 17's
  `INTERESTING_DUNDERS`) or it leaks all of this bookkeeping as false
  positives. `__static_attributes__` itself is new in CPython 3.13+: a tuple
  of names assigned via `self.X` anywhere in the class's own methods.

## Pointers

- `tools/*.py` all have thorough module docstrings; read them before guessing.
- The `Makefile` documents every gate and target (`make help`).
- Detailed conventions and decisions are in project memory (`MEMORY.md` index).
- `thinking-in-python-skill.md` (repo root) and
  `.claude/skills/thinking-in-python/SKILL.md` are duplicate copies of the
  same Python coding-style skill, not a symlink (this repo has
  `core.symlinks = false`). Edit one, then copy the change into the other;
  nothing enforces sync automatically.
