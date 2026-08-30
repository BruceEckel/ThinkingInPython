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
  and only reported, since deleting it needs a human call. `make prune`
  deletes exactly the orphaned ones. A rename or deletion of a book example is
  the usual cause, so run this after either.

## Rust examples: rust/, isolated from the main build

Chapter 18's Rust section has real PyO3/maturin crates under `rust/`. The root
`Makefile` never enters `rust/` and never requires a Rust toolchain, so
`verify`/`gate`/`all`/`ci` work with no Rust installed. Details: `rust/CLAUDE.md`.

## Deep-reviewing a chapter

The full deep-review procedure (editing pass, teaching pass, style
audit, prose pass, third-party-library rules, accrued review notes) lives in
the `deep-review` skill (`.claude/skills/deep-review/SKILL.md`).
Invoke it for any chapter review request.
`/annealing` (`.claude/skills/annealing/SKILL.md`) is the follow-up
settling pass, run after a review is applied: it re-runs the same passes
over the whole chapter but applies the confident findings directly and
discards the rest unreported, with no review file.
`/activate` (`.claude/skills/activate/SKILL.md`) is the active-register
pass: it clears `make prose`'s passive-voice and there-is warnings and
cuts metadiscourse, empty frames, and expletive constructions; new
passive-feeling phrasings Bruce flags accrue in its "Accrued patterns"
section.
`/literal`, `/cohesion`, and `/antecedents` (each under
`.claude/skills/`) are the other prose passes: figures of speech become
the mechanism they stand for, paragraphs get old-before-new order and
one topic string, and every ambiguous "this"/"it"/"which" gets its noun.
`make rewrite CH=NN` runs these three plus `elements-of-style` and
`bruce-edit-apply` by default; `make rewrite ARGS=--list` shows the set.
`CH="25 28"` or `CH=30-40` runs several chapters in parallel (each chain
edits and checks only its own chapter); `ARGS=--serial` runs them one at
a time.

## Learning from Bruce's own edits

`/bruce-edit-capture` (`.claude/skills/bruce-edit-capture/SKILL.md`) reads a
diff of Bruce's edits to a chapter, separates the generalizable edits from the
local ones, and proposes editing practices into `bruce_edit_db.md`. It writes
only that file, never `Chapters/`. `/bruce-edit-apply`
(`.claude/skills/bruce-edit-apply/SKILL.md`) applies the promoted rules to a
chapter or the book, reporting per-rule firing counts. The split is deliberate:
capture is cheap and reversible, application rewrites prose that no gate
checks. One sighting logs a candidate; a second sighting in a different chapter
promotes it to a rule; only rules are applied. Rejected rules go to Retired and
are never re-proposed.

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

Prose-only edits still need `heading_links.py` (cross-references) and
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

- **Listing line length is 60** (ruff `line-length` plus the `widths` check
  in `check_all.py`, which also covers fragments and `#:` markers that ruff
  never sees). The one sanctioned overflow is a trailing `# type: ignore`
  pragma, exempted by both ruff and `widths`. A `#:` marker wider than 60
  means the program's own printed output must shrink, not the marker.
  Wrapped imports use packed parentheses with per-file `I001` ignores in
  `pyproject.toml` (ruff would otherwise force one-name-per-line); a new
  over-60 import needs its file added there. A scratch dir's `ruff` uses
  the default 88, so **line length must be verified against
  `build/examples`**, not a temp file.
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
- **A `#:` marker for output an `import` produced cannot hug that import.**
  Markers otherwise sit directly after the statement that produced them, but a
  marker placed after the last import sits *inside* the import block, and ruff's
  `I001` ("Import block is un-sorted or un-formatted") fails the gate.
  `validate_output.py` accepts either arrangement, so this surfaces at `make
  lint`/`make verify`, a step after the edit looked correct. Close the import
  block with its blank line first, then put the marker below it, directly above
  the code it precedes. Chapter 6's `package_only.py` was annealed into the
  hugging form and broke the build; its neighbors `using_packages.py` and
  `from_packages.py` already had the right shape.
- **Async timing markers flip silently on Windows timers.** A `#:` trace
  that depends on ordering between asyncio deadlines needs wide margins.
  Chapter 19's `task_group.py` cancellation demo with 0.01/0.02/0.03s
  sleeps let task "a" complete before cancellation landed (b's failure
  and a's deadline fell inside one timer tick), and the self-healing
  gate rewrote the marker to contradict the prose. Use roughly 5-10x
  gaps between competing deadlines (0.01/0.05/0.25), widest where a
  cancellation must propagate, and treat any `git diff` on a timing
  marker as a red flag to investigate, not drift to accept.
- **Chapter 19's `gil_threads.py` boolean flips under machine load, and
  widening its threshold would be wrong.** `thr > seq * 0.9` asserts "threads
  bought no speedup," and `make verify` runs during back-to-back gates
  (including inside `make release`, twice in a row) rewrote it to `False`,
  contradicting the prose one line below. Do not widen the band to make it
  robust: at `0.7` a genuinely 30%-faster threaded run would still report "no
  faster," hiding the exact regression the listing exists to catch. The fix
  is in `thread_compare.py`'s `compare()`, which the neighboring I/O
  listing also uses. 2026-08-23: `min(timeit.repeat(..., repeat=3))` per
  variant. It flipped again on 2026-08-28 during `make verify`, with the
  ratio never dropping below 1.07 in twelve standalone runs (six of them
  under 24 busy loops on 22 cores) or in two whole-book
  `validate_output.py` runs, so it is a rare transient that a burst
  covering all three sequential repeats (about a second) can produce.
  Now the two variants are timed alternately, five rounds, `min` of
  each, so a burst lands on both. The tell of a flip: `Examples/` shows
  `False` while `Chapters/` still says `True`. `verify`'s first marker
  refresh flipped the chapter, `sync` copied it, and the gate's second
  refresh flipped the chapter back with no sync after, so the generated
  copy is the only trace. Revert it (`git checkout -- Examples/...`);
  never commit it. 2026-08-30: do not shrink the loop to make the
  script faster. At 200,000 iterations each timed round is ~0.075 s,
  about five Windows scheduler quanta (~15 ms), so one lost quantum is
  a 20% error and the boolean flipped inside a quiet `make verify`;
  at 1,000,000 a round is ~0.38 s and a quantum is 4%. The ratio
  itself is ~1.02 at either size, so the margin over 0.9 is thin and
  only the long measurement absorbs scheduler noise. The script's
  timeouts under the parallel runner were fixed on the runner side
  instead: `run_examples.py`'s default `--timeout` is 60 s (was 15).
- **Thousands of live `asyncio` tasks in one process can wedge Windows'
  `ProactorEventLoop` for every later `asyncio.run()` call in that process.**
  Chapter 19's `task_vs_thread_memory.py` used to create and cancel 20,000
  tasks. Run standalone (its own process, one `asyncio.run()` ever), that's
  instant. Run through `validate_output.py` (which execs every chapter's
  blocks, including every later `asyncio.run()` block, in one process), it
  triggered a storm of `RuntimeError: loop ... is not the running loop`,
  one per orphaned task, that took minutes to print and looked exactly like
  a hang — the `KeyboardInterrupt`s a human sends to escape it then get
  misattributed to whatever line happened to be executing next, in that or
  a later chapter. Bisected the threshold on this machine: 15,000 tasks ran
  clean, 20,000 didn't. Fixed by dropping `TASKS` to 5,000, comfortably under
  the cliff. If a future example needs a large task count again, verify it
  through `validate_output.py` on the real chapter file (not a standalone
  script run), since only the multi-`asyncio.run()`-per-process path
  reproduces this.
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
- **Kindle listings: only the real book is a valid test bed, and
  line-leading whitespace is half width there.** Send to Kindle (email)
  converts a tiny standalone probe EPUB differently from the full book
  (probes rendered `pre` in Bookerly whatever the CSS said; the book
  renders it monospace), so four probes gave answers the book then
  contradicted. Test a listing change by building the book with a probe
  chapter in front (a scratch script that monkeypatches
  `build_epub.book_markdown`/`epub_css`, then `build()`), never a
  separate small EPUB. Measured in the book on a Paperwhite: spaces or
  `&#160;` at the start of a line draw at ~0.54 of a character; the same
  whitespace after any glyph, even U+200B, draws full width; `ch` is
  unsupported (zero); `6em` came out ~8.4 characters, not 10; a named
  family before `monospace` (`"Courier New", Courier, monospace`) loses
  the monospace entirely. Hence `listing_html()` prefixes each indented
  line with `&#8203;` and keeps plain spaces, and `CODE_FONT` is the
  bare keyword. Project memory `kindle-listing-indentation` has the
  probe script layout.
- **`build/` is derived and gitignored.** `extract_examples.py --write` now wipes
  the target under `build/` first, so a fresh sync is the fix for weird drift or a
  stale tree. A stale `build/examples/` was behind "phantom" timeouts/import errors.
- **Windows dir-lock on the wipe.** If the persistent shell's cwd sits inside
  `build/examples/<chapter>`, that open handle blocks the rmtree and
  `extract_examples.py --write` dies with `PermissionError [WinError 32]`. Keep the
  shell at the repo root and run chapter-dir commands in a subshell, e.g.
  `(cd build/examples && uv run ty check NN_Chapter)`.
- **`run_examples.py` and `validate_output.py`: never pass a relative
  `--tree`.** It goes on `PYTHONPATH` and breaks once an example changes cwd.
  `validate_output.py` manifests this as `ModuleNotFoundError` on a `utils/`
  helper (`No module named 'greeter'` across every block that imports one),
  which reads as a broken listing rather than a bad flag; an absolute
  `--tree` fixes all of them at once. GUI/interactive examples are skipped via
  `tools/data/norun.txt` (keep those paths current when chapters are renumbered).
- **Renumbering a chapter** touches: `Chapters/` and `Examples/` filenames, every
  `NN_*.md` cross-reference, `build_site.py` `PARTS`, `tools/data/norun.txt`, and the
  `README.md` tracking table. Appendices use letter prefixes (`A_...`); build_site
  labels them "Appendix X".
- **Splitting a chapter silently invalidates every relative cross-reference in
  the later half.** Nothing greps for prose, so no gate catches this. Splitting
  Generators out of Stateless left chapter 46 with fourteen phrases
  ("the previous chapter", "the previous chapter's second exercise",
  "the previous section") that still meant 44, not the newly-inserted 45.
  After any split, `grep -n "previous chapter\|previous section\|last chapter"`
  the later half and check each hit against the content it names, since some
  will legitimately point at the new neighbor. Prefer a named link
  (`[Effect Management](44_Effect_Management.md#anchor)`) over a relative
  phrase, so the next split fails loudly at `heading_links.py` instead of
  quietly misleading a reader. Where three references cluster in one section,
  resolve the later ones with "that chapter" against a nearby link rather than
  repeating the same hyperlink.
- **Anchors:** pandoc auto-slugs a heading (backticks/punctuation dropped, but `.`
  is kept). Give headings an explicit `{#id}` when the auto-slug would be ugly
  (e.g. anything containing `type[...]` or `__init__`). `heading_links.py` gates it.
- **`make help` is self-documenting, not hand-written.** A
  target needs a trailing `## text` comment on its own line (and to sit under the
  right `##@ Name` heading) or it will not appear in `make help`. Bare `make`
  and `make help` both list every section; `make help style` lists
  one section. In a terminal both open `tools/help_picker.py` instead
  (arrow keys or mouse, Enter runs the target, `?` shows the target's full help:
  the `#` comment block directly above it in the Makefile plus its recipe,
  so keep that block adjacent to the target line, with no blank line between;
  `prompt_toolkit`, a dev
  dependency); a pipe, `CI`, or `--pick never` gets the static text, so running
  `make help` from a tool or a test never blocks on input. A section's slug is
  the first word of its heading, lowercased, so renaming the heading renames the
  slug with no second list to update. Two rules `make_help.py` enforces by raising
  `SystemExit`: no two sections share a slug, and no slug equals a target name
  (the Makefile neutralizes the word after `help` so `make help style` parses as
  one goal, and a colliding slug would override that recipe). This is why the
  sections are headed "Code examples" and "Writing and spelling" rather than
  "Examples" and "Prose": both of those are targets.
  A `##-` comment instead of `##` marks a target *secondary*: still documented and
  still smoke-tested, but folded out of the listing because a sibling's doc text
  names it (every `fix-*` under its check). Keep `entries()` reporting secondary
  targets, since `verify_targets.py` enumerates through it and `sweep_checks.py`
  looks up doc text through it. Parsed by `tools/make_help.py`,
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
- **`ty` narrows `str` to `Literal[...]` as of 0.0.63,** so the `cast()`
  that used to be required at a boundary function is now flagged as a
  `redundant-cast` warning and fails the gate. `if char not in SPECS:
  raise KeyError(char)` (where `SPECS` is keyed by the literal type) is
  enough; `return char` then satisfies the declared return type.
  Chapter 35's `to_symbol()` and `Solutions/35_Flyweight.md` were written
  against the older behavior and were fixed when 0.0.63 landed. The
  boundary-function idiom itself is still right, only the `cast()` inside
  it went away. Project memory (`typing-construct-hierarchy`) has the
  fuller case study.
- **A `ty` upgrade is a book-wide event, not a tooling detail.** Both
  directions bite. New narrowing power turns a once-necessary `cast()`
  or `# type: ignore` into a `redundant-cast`/`unused-type-ignore-comment`
  warning that fails the gate, and lost inference turns working listings
  into errors. The 0.0.58 to 0.0.63 upgrade did all of these at once:
  literal narrowing (ch35 + solutions), `frozendict` support arriving
  (two of ch03's three ignores went unused), `filter(lambda ...)` no
  longer narrowing its element type (ch16's `map`/`filter` listings broke),
  and higher-order union subtraction starting to work (the caveat that
  invalidated has since been removed from the text). The 0.0.70 to 0.0.75
  upgrade added two more shapes: a new `missing-slot` check that misfires
  on typeshed's `weakref.finalize` (its writable `atexit` property is
  modeled as a plain attribute absent from `__slots__`; ch10's
  `finalize_trap.py` carries the `# type: ignore`), and dict keys inferred
  as literal class objects no longer accepting a `type(e)` lookup (fixed
  by annotating the dict explicitly, `Final[dict[type[Expr], int]]`, in
  Solutions ch34). After `make tools-upgrade`, run
  `uv run ty check build/examples` **and** `uv run ty check build/solutions`
  before assuming the first failure is the only one: `make all` stops at
  the first failing gate and `solutions-gate` runs last.
- **A `type X = ...` alias's right side is lazily evaluated (PEP 695),** so it
  can name a class defined later in the same file with no string quotes, e.g.
  `type Bins = dict[type[Trash], list[Trash]]` above `class Trash:`. Confirmed
  both at runtime and under `ty check`.
- **Effect signatures stay written out in full; don't fold them into
  `type` aliases.** Chapters 46 and 47 spell every Effect signature out
  (47 carries the wrapped five-way union): the union is the information,
  and it stays visible at the point of use. On `ty` 0.0.70 a
  `type X = ...` alias as a generator's return annotation checks the
  same as the spelled-out form (an undeclared Ability draws
  `invalid-yield` through the alias), but an inference gained in one
  release can vanish in another, so re-run the probe on each `ty`
  upgrade (`stateless-partial-handling-ty-support` in project memory
  has it) before trusting an alias there. Chapter 45 has no Effect
  signature, so this entry does not apply there.
- **Never auto-run `make tools-upgrade` or `make python-upgrade`.** Both mutate
  tracked files (`uv.lock`, and `.python-version`/`pyproject.toml` with `TO=`) and
  can invoke real system package managers (`winget`/`brew`). Only run them when
  the user explicitly asks for that specific run, not to "verify" a change.
  `make tools-check[-full]`, `make tools-status`, and `make sweep` are all
  safe to run freely (the first two are read-only; `sweep` writes only
  `build/`). The nag that `gate` prints when the tools are stale is a
  reminder for the author, not an instruction to you: never act on it by
  running an upgrade.
- **`make gate` hides half its failures, and not the half you would guess.**
  `solutions-gate` is a *prerequisite* of `gate`, so the entire Solutions
  half runs before gate's own recipe starts. One red `gate` after a
  wide-reaching change therefore shows the Solutions failures and hides
  every `Chapters/` one behind them. Use `make sweep` (runs every check
  over both trees, reports all failures, exits nonzero if any failed)
  whenever the first failure is unlikely to be the only one. A tool
  upgrade is the standard case, and `tools-upgrade` now ends with it.
- **Prose in `Chapters/*.md` follows Semantic Line Breaks** (one sentence per
  line; a sentence still too wide breaks further at a top-level `,`/`;`/`:`).
  `gate` (so `verify`/`all`/`ci`) runs `reflow_prose.py --write`, so
  hand-edited prose self-heals (rewriting `Chapters/`) the same way line
  endings and `#:` markers do; expect rewrapped lines in `git diff
  Chapters/` after a verify. A paragraph that fails reflow's round-trip
  check is skipped, reported, and still fails the gate, so a rewrite can
  never silently change rendered output. `make reflow CH=NN` still
  targets one chapter when iterating.
  Before writing a script to reflow prose across the book, check
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
