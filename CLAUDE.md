# Thinking in Python: working in this repo

This file is loaded every session. It captures how the repo is built and verified,
plus the traps that are easy to rediscover the hard way. Personal writing style
lives in the global `~/.claude/CLAUDE.md`; accrued facts live in project memory.

## Source of truth: Chapters/, not Examples/

`Chapters/NN_*.md` is authoritative. Every fenced ```python block whose first line
is a `# path/slug.py` comment is an extractable example. `Examples/` is **generated
from the Markdown** by `tools/extract_examples.py`, so:

- Edit the code **in the Markdown block**, never in `Examples/` directly.
- After editing, sync the committed trees: `tip sync`
  (= `uv run python -m tools.extract_examples --write -o Examples` and
  the same for `extract_solutions` into `SolutionsCode/`).
- `Examples/` also holds files with no Markdown block (hand-written helpers,
  `.idea/`, `__pycache__`). `tools/extract_examples.py`'s check mode (part of
  `tip check`/`gate`/`verify`/`ci`) flags these automatically: a stray file
  whose name appears nowhere in `Chapters/` is *orphaned* and fails the gate;
  one still mentioned somewhere (a real hand-written helper) is *referenced*
  and only reported, since deleting it needs a human call. `tip prune`
  deletes exactly the orphaned ones, under `Examples/` and `SolutionsCode/`
  both (a `utils/` helper rename orphans a file in each). A rename or
  deletion of a book example is the usual cause, so run this after either.

## Rust examples: rust/, isolated from the main build

Chapter 18's Rust section has real PyO3/maturin crates under `rust/`. Only
the `rust-*` tasks in `tools/tasks.py` enter `rust/` or need a Rust
toolchain, so `verify`/`gate`/`ci` work with no Rust installed. Details:
`rust/CLAUDE.md`.

## Cloud sessions: tools/cloud-setup.sh

A Claude Code cloud session starts from a fresh Ubuntu 24.04 VM whose
stock `uv` (0.8.17) cannot fetch Python 3.15, so nothing that goes
through `uv run` works until the environment's setup script installs
the toolchain. `tools/cloud-setup.sh` (since 2026-09-25) is that
script's source: paste it into the environment's Setup script field,
and paste it again after editing it, since the environment keeps its
own copy. It installs uv and Python 3.15, Vale, an SVG rasterizer,
and pandoc from PyPI, apt, and the Go module proxy, because the
session's GitHub proxy refuses release downloads from any repository
not attached to the session, at every network access level, and
`tip tools-check-full`'s Linux lines for pandoc, typst, and Vale
download exactly those. typst and gh stay out; the script's header
says why. Check a change with `tip tools-check-full` in the first new
session. The VM is Linux, so the seeded-simulation trap below applies
to any `#:` marker a cloud `tip verify` rewrites.

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
pass: it clears `tip prose`'s passive-voice and there-is warnings and
cuts metadiscourse, empty frames, and expletive constructions; new
passive-feeling phrasings Bruce flags accrue in its "Accrued patterns"
section.
`/literal`, `/positive`, `/straighten`, `/cohesion`, and `/antecedents`
are the other prose passes.
`tip rewrite CH=NN` runs these five plus `elements-of-style` and `bruce-edit-apply` by
default; `tip rewrite ARGS=--list` shows the set and the model each
pass runs on. Each pass can name its own model in `tools/rewrite.py`'s
`PASSES`; all resolve to `DEFAULT_MODEL`, Opus 5.5 since 2026-09-25
(Fable 5 before, moved to spare Bruce's Fable usage, not on a new
measurement). `MODEL_NOTES` there records the A/B evidence and the
move, and `MODEL=` forces one model on a run.
Every pass checks any claim it rewrites against the listing it
describes; the 2026-09-01 sweep of chapters 30-47 found nine factual
errors that way, none of them gate-detectable.
`CH="25 28"` or `CH=30-40` runs several chapters in parallel (each chain
edits and checks only its own chapter); `ARGS=--serial` runs them one at
a time.

## Model routing

The session model (whatever `/model` set) reads the request, plans,
gates, and commits. It does not do every kind of work itself: the
project defines agents in `.claude/agents/` whose frontmatter fixes
the model, and a request that matches one is delegated there, one
agent per file, gated and committed by the session afterward. Add a
row here when a new agent lands.

| Request shape | Agent | Model | Why |
|---|---|---|---|
| clarity pass, straighten, clear passives, "make X clearer", "obscure/unclear sentences" on named files | `prose-clarity` | Opus | judgment work that edits the author's voice and verifies claims against listings; both Opus and Fable did it well in the 2026-09-01 Solutions sweep, Opus's reports were the more careful about what they left alone |
| a list, a count, a location, a gate's output, what a listing prints | `repo-lookup` | Sonnet | read-only, no voice at stake, cheap |
| `tip rewrite` passes | (headless `claude -p`) | per pass, `tools/rewrite.py` `PASSES` | see `MODEL_NOTES` there |
| verify a chapter's factual claims against its listings and against the chapters it names | a fresh agent per chapter, report-only | Opus | verification fails by under-reading, not by over-editing, so `MODEL_NOTES`' result for the rewrite passes inverts here; in the 2026-09-02 calibration Opus found three real errors Fable read past, with zero false positives from either |
| deep review of a chapter, thread audits, anything that decides what a chapter claims | the session model, or a `fork` | session | needs the conversation's context; a fresh agent cannot know what Bruce has already ruled on |

Pass `model:` on an `Agent` call only to override a definition for one
run. A fresh agent costs roughly 70-150k tokens on a chapter-sized
file; a `fork` carries the whole conversation and costs several times
that, so forks are for work that needs the session's history.

## Editing passes: /edit-start and /edit-done

When Bruce says he is starting to edit a chapter, run `/edit-start NN`
(`.claude/skills/edit-start/SKILL.md`). It places a local annotated git
tag `edit-start-NN` on `HEAD`, records the chapter's baseline (`tip
check-ch`, `tip reflow-check`, `validate_output`), and reports; it
writes nothing under `Chapters/`. When he says he is done, run
`/edit-done NN` (`.claude/skills/edit-done/SKILL.md`): it diffs from the
tag to the working tree (so commits he made along the way and
uncommitted edits are one pass), hands that diff to
`/bruce-edit-capture`, runs `tip verify-ch CH=NN` (or `tip verify`
when the pass reached other chapters), commits what the loop changed,
and deletes the tag. The tag is the only state: local, never pushed,
`git tag -l 'edit-start-*'` lists the open passes. A `SessionStart`
hook in `.claude/settings.json` prints the open passes into every new
session's context, so a request that names no file ("fix that sentence
about closures") is looked up in the chapter in progress first, and
its Solutions file second, before asking which chapter he means.

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

Fastest path for one chapter is `tip verify-ch CH=NN`
(`tools/verify_chapter.py`): the same fixers and gates as `verify`,
scoped to that chapter and its Solutions file, in a few seconds. It
reflows the chapter only, since the gate never reflows `Solutions/`,
and it writes no gate stamp; a change that other chapters depend on
(a renamed listing, a `utils/` helper, a linked heading) still needs
the whole-book run. That run is `tip verify`: fix line endings, every
mutating fixer (the comment-style fixers, import sorting, blank-line
cleanup), refresh the `#:` output markers in both trees, sync `Examples/`
and `SolutionsCode/`, build the figure gallery, then every gate but the
site build. Its ordered step list lives in `tools/verify.py`
(`VERIFY_TARGETS`), and `tip verify ARGS=--help` lists it without
running anything. Until 2026-09-24 this was two targets, `verify` without
the fixers and `all` with them; `all` is gone, since every fixer repairs
something the gate would otherwise fail on. The marker refresh runs
*before* the sync, not after: `gate`/`solutions-gate` refresh markers
too, but only after their own prior sync step already copied the Markdown,
so a marker that needed fixing would otherwise stay one sync behind until
the next run caught it up. When iterating on one chapter, the manual
sequence is:

1. `uv run python -m tools.extract_examples --write -o Examples`  # sync committed tree
2. `uv run python -m tools.extract_examples`                      # drift check ("In sync")
3. `uv run python -m tools.extract_examples --write`              # (re)build build/examples/
4. `uv run python -m tools.validate_output Chapters/NN_*.md`      # `#:` markers match stdout
5. `(cd build/examples && uv run ty check NN_Chapter)`            # types
6. `uv run ruff check build/examples/NN_Chapter`                 # lint
7. `uv run pytest build/examples/NN_Chapter`                      # tests
8. `uv run python -m tools.run_examples NN_Chapter`               # runs scripts, honors norun.txt

Prose-only edits still need `heading_links.py` (cross-references),
`banned_phrases.py`, and `check_self_reference.py` (claims the book makes
about its own chapters); all three are in `tip verify`. So is
`check_quoted_diagnostics.py`: every quoted `ty` diagnostic's gutter
lines are compared with the extracted listing, and the dozen quotes
the book deliberately makes against an edited copy of a listing live
in `tools/data/quoted_diagnostics_baseline.txt`. A NEW entry after a
listing edit is a stale quote to requote, or a fresh deliberate edit
to accept with `tip quoted-diagnostics-accept`; `--all` lists every
hit. `exercise_refs.py` (in the gate since 2026-09-20) does the same
for prose that names an exercise by number: each "exercise N", "the
second exercise", or "the previous exercise" in `Chapters/` and
`Solutions/` is paired with the Solutions title under that number,
and the pairs live in `tools/data/exercise_refs_baseline.txt`.
Inserting or reordering an exercise changes the title under every
later number, so every reference to one turns NEW and fails the gate.
Reread each NEW sentence against the title printed beside it, fix the
number or `tip exercise-refs-accept`, and never accept without that
read: chapter 30 carried five stale numbers for a day after commit
a2cc5a98 inserted an exercise at 2, with every gate green. A new
reference is NEW too, until accepted. `tip verify-ch` sees only the
references its two files make, so after moving an exercise run
`tip exercise-refs` over the book. `tip verify`'s gate also
runs `validate_output.py --update` over all of `Chapters/` now, so a stale
`#:` marker anywhere self-heals (rewriting `Chapters/`) instead of failing
the build, the same way `fix-eol`/`sync` already self-heal other drift.
Check `git diff Chapters/` afterward: a chapter you did not touch can
still land in the diff if its output actually changed. An exception
raised where none is expected still fails the gate; only marker text is
auto-corrected. A lone bare `#: ` with nothing after it is always treated
as a not-yet-filled-in placeholder and filled in, even without `--update`.

## Pyright: a periodic review, never a gate

`ty` is the only checker the gates run.
Pyright's disagreements with `ty` live in `tools/data/pyright_baseline.txt`,
and `tip pyright-review` prints the delta;
the `tool-upgrade` skill has the workflow and the history.
Three rules hold everywhere:

- **Nothing pyright-related joins `verify`, `gate`, `sweep`, or `ci`.**
- **No listing carries a pyright suppression.**
  An accepted disagreement is a baseline entry instead.
- **"The type checker" in prose means `ty`.**
  A sentence that holds for `ty` alone names `ty` and says what the other checkers do.

## What the book says about itself

`check_self_reference.py` gates the shape that produced the most errors
in the 2026-09-02 correctness sweep: prose asserting something about
another chapter, or about the book, that reading the named place
disproves. Chapter 07 said "[Rethinking Objects] uses it" of
`slots=True`, and chapter 20 contains the string "slot" zero times. The
link resolved, the anchor was fine, every gate was green.

Two rules gate, because a substring search settles them. `absence`
catches "X appears nowhere else" where X is used elsewhere, searching
code spans and listings only, since the book's type names are also
English words ("a more complex design" must not disprove a claim about
`complex`). `direction` catches an ordering phrase that names a chapter
("an earlier chapter") within 80 characters of a link pointing the other
way.

A third rule, `grounding`, reports and never gates: a sentence links to a
chapter that contains *none* of the code terms the sentence names. It
finds the real thing (it catches chapter 07's case), and it also fires on
31 sentences whose terms belong to the *linking* chapter, which a target
has no reason to mention. `tip self-reference-report` reads it, the same
bargain `tip claims` strikes. Do not promote it into the gate without
first getting that count to zero.

The rules are literal and under-report by design: a claim with no code
term in it is invisible to them. They are a floor, not a substitute for
reading.

## Pattern names: *Capitalized* and italic, every mention

Every naming of a design pattern is written capitalized and in italics,
on every mention, in prose and in link text: *State*, *Chain of
Responsibility*, `[*Template Method*](25_...)`. Names like State, Command,
Bridge, and Proxy are ordinary words otherwise, so this is the exception
to the global "italics only to introduce a term" rule. Headings stay
plain, and the lowercase word keeps its ordinary sense ("an observer
registers"). `tools/pattern_names.py` checks it (`tip pattern-names`)
and `tip fix-pattern-names` rewrites the unambiguous cases; the names
and the excluded phrases (`!State Machines`) are in
`tools/data/pattern_names.txt`. State/Command/Bridge at a line start
are listed only with `--sentence-start`, for a human to judge; the
three in the book ("State the rule...") are the verb. The check has
been in `GATE_CHECKS` since 2026-09-16, so `verify`, `gate`, and
`verify-ch` fail on a plain name.

## Diagrams: hand-authored SVGs, some generated

A figure is an SVG in `resources/images/`, referenced as `![caption](_images/<name>)`.
Never hand-edit a generated one:
chapter 31's `stateMachine.svg` comes from `tools/state_machine_figure.py`,
and every `coupling_*.svg` from `tools/coupling_panels.py`;
edit the spec and run its `tip fix-*` task.
Load the `figures` skill (`.claude/skills/figures/SKILL.md`) before drawing or editing any figure.
It holds the caption rules, the palette, the arrowheads, and what `tip figures` checks.

## `@record`: the book's frozen data class, from chapter 18 on

`utils/record.py` (chapter 18, `#record`) is
`dataclass(frozen=True, slots=True)` under
`dataclass_transform(frozen_default=True)`. From that section on, a
frozen data class in a listing is written `@record` with
`from record import record`, and the prose noun is "record". Chapters
12, 13, and 15 come before the definition and keep
`@dataclass(frozen=True)`. Bruce's rulings from 2026-09-17:

- **A class keeps `@dataclass(frozen=True)` when `@record`'s slots
  would not hold or would break it.** That means `order=True` or any
  other option `record()` lacks, a weak reference (`weak_pool.py`), a
  `cached_property`, a listing that reads an instance `__dict__` or
  pickles across versions (chapter 36's `sketch_v1.py`/`sketch_v2.py`),
  and any class whose base has no `__slots__` (the `Ability` and `Time`
  subclasses in chapters 46-47, chapter 34's `expr.py` nodes under
  `Operators`). Do not put `@record` on a class and then let a base
  take the slots back.
- **One listing slots a base for its records, as the teaching
  example:** chapter 20's `shapes_oo.py` gives `Shape(ABC)` an empty
  `__slots__ = ()`. Do not add a second.
- **Reword a sentence before keeping a listing long-form for its
  sake.** A sentence that names `frozen=True` about a converted class
  says "record" instead. The exceptions are listings whose subject is
  `frozen=True`: chapter 20's `immutable.py` and `frozen_leaky.py`,
  Solutions 20 exercise 2, chapter 18's `slots_dataclass.py`. Chapter
  22's `still_a_tuple.py` (and Solutions 22 exercise 6) stays long-form
  too: its `Frozen*` classes sit beside `order=True` twins, and the one
  added option is the point of the comparison.
- **A Solutions copy of a chapter class follows its chapter listing.**
- Slots make an instance smaller, so a marker that measures memory
  moves when a class becomes a record. Solutions 35 `exercise_2.py`
  went from a ratio near ten to near six.

`tools/record_check.py` gates both directions (`tip records`, in
`GATE_CHECKS` and in the Solutions checks since 2026-09-17): a
`@dataclass(frozen=True)` whose bases are all slotted fails unless
`tools/data/record_exceptions.txt` lists it, and a `@record` under a
base with no `__slots__` fails. A base it cannot see (imported from
another listing) draws no finding, so it under-reports by design. The
exceptions file is keyed by chapter *name* (`Rethinking_Objects`), not
number, so a renumbering leaves it alone and a chapter rename does not.
Run alone, `tip records` also fails on an entry that matches nothing.
Its `UNSLOTTED_LIBRARY` names Stateless's `Ability` and `Time`, and
chapter 47 says in prose that `Ability` declares no `__slots__`; recheck
both against `.venv/Lib/site-packages/stateless/` on a Stateless
upgrade.

Project memory `record-sweep-classification` has the per-class survey
and how it was measured.

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
  `uv run`'s.** They matched on 2026-09-13 (both `python` 3.15.0rc2, both
  `ty` 0.0.78), but they have diverged before: bare `python` was 3.14.6
  while `uv run python` was the pinned 3.15, and bare `ty` was 0.0.46
  against `uv run ty`'s 0.0.56. Running `validate_output.py` with the
  older bare `python` produced false failures on 3.15-only syntax
  (`sentinel`, `lazy import`, the PEP 798 comprehension-unpacking
  chapter) that vanished once invoked via `uv run`. Always go through
  `uv run` for anything that executes example code; never assume bare
  `python`/`ty`/`pytest` matches it. Bare `python` is also a different
  *build* of the same version: `C:/Python/python.exe` is the python.org
  installer's CPython, with the JIT compiled in
  (`sys._jit.is_available()` is `True`), while `uv run` uses uv's
  managed build, where it is `False`. `[tool.uv] python-preference =
  "only-managed"` in `pyproject.toml` (2026-09-17) keeps a fresh clone
  or worktree's `uv sync` off the PATH interpreter; before that, uv's
  default preference picked `C:/Python`, and a scratch worktree
  reported two JIT markers as changed for that reason alone.
  `sys.version` tells the builds apart: "tags/v3.15..." is python.org,
  "main, ..." is managed. There is no `python3` on PATH:
  the Microsoft Store app-execution stub that answered to that name
  (printing "Python was not found" and exiting 9009) was disabled on
  2026-09-13, so a `python3` command now fails as "not recognized".
- **CPython's small-int cache is wider on the pinned 3.15 beta than the
  textbook `-5..256` range.** Confirmed cached up to at least 1024 on this
  build. An example meant to show an "uncached" int needs a value safely
  above that (100000+), not just above 256, or the demo silently proves the
  opposite of what the prose claims. See project memory
  (`small-int-cache-extended-py315`) for the chapter-36 case this broke.
- **`#:` output markers must equal stdout exactly.** For nondeterministic output,
  round floats (`f"{x:.6f}"`) or print `type(e).__name__` instead of a message.
  A wall-clock threshold boolean is the exception: register it in
  `tools/data/timing.txt`, and `validate_output.py` treats its markers as
  claims, never auto-rewritten. On a mismatch it reruns the block, up to
  three runs in all, and passes as soon as one matches the committed
  marker; only a marker that misses every run fails, loudly, and the fix
  is then a human decision. Any *other* genuinely nondeterministic
  listing still self-heals silently under `--update` and can thrash
  between values, so don't assume a marker mismatch is repo drift: run
  the extracted script directly (`build/examples/<chapter>/<file>.py`)
  to check the value is stable, and if it's a timing boolean, add it to
  `timing.txt` instead of accepting the auto-fix.
- **A `#:` marker for output an `import` produced cannot hug that import.**
  Markers otherwise sit directly after the statement that produced them, but a
  marker placed after the last import sits *inside* the import block, and ruff's
  `I001` ("Import block is un-sorted or un-formatted") fails the gate.
  `validate_output.py` accepts either arrangement, so this surfaces at `tip
  lint`/`tip verify`, a step after the edit looked correct. Close the import
  block with its blank line first, then put the marker below it, directly above
  the code it precedes. Chapter 6's `package_only.py` was annealed into the
  hugging form and broke the build; its neighbors `using_packages.py` and
  `from_packages.py` already had the right shape.
- **A seeded simulation can still print differently on Linux.** Solutions
  38's `exercise_8.py` seeds its `random.Random`, and the gate in the WSL
  clone rewrote one of its `#:` readings anyway (`0.012` on Windows,
  `0.010` on Linux, 2026-09-24). The seed fixes the random draws; the
  C library's `cos` does not agree to the last bit between Windows and
  glibc, and a chaotic run (a kick that throws a grain across the plate
  each step) multiplies that last bit by about ten a step until a
  three-decimal reading moves. The chapter's own `chladni_plate` marker,
  at the default kick, matched on both. The fix was two decimals in that
  one listing, which both platforms print alike; do not reseed, and do
  not accept the Linux rewrite, which the next run's drift check then
  fails on. A `git diff` on a simulation marker after a Linux run is
  this until proven otherwise.
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
  bought no speedup," and `tip verify` runs during back-to-back gates
  (including inside `tip release`, twice in a row) rewrote it to `False`,
  contradicting the prose one line below. Do not widen the band to make it
  robust: at `0.7` a genuinely 30%-faster threaded run would still report "no
  faster," hiding the exact regression the listing exists to catch. The fix
  is in `thread_compare.py`'s `compare()`, which the neighboring I/O
  listing also uses: the two variants are timed alternately, five rounds,
  `min` of each, so a load burst lands on both.
  The listing is registered in `tools/data/timing.txt`,
  so a flip fails validation loudly instead of rewriting the marker.
  Do not shrink the loop to make the script faster. At 200,000 iterations each timed round is ~0.075 s,
  about five Windows scheduler quanta (~15 ms), so one lost quantum is
  a 20% error and the boolean flipped inside a quiet `tip verify`;
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
- **`build/` is derived and gitignored.** `extract_examples.py --write` now wipes
  the target under `build/` first, so a fresh sync is the fix for weird drift or a
  stale tree. A stale `build/examples/` was behind "phantom" timeouts/import errors.
- **Windows dir-lock on the wipe.** If the persistent shell's cwd sits inside
  `build/examples/<chapter>`, that open handle blocks the rmtree and
  `extract_examples.py --write` dies with `PermissionError [WinError 32]`. Keep the
  shell at the repo root and run chapter-dir commands in a subshell, e.g.
  `(cd build/examples && uv run ty check NN_Chapter)`.
  Orphaned python processes cause the same error: on 2026-09-03,
  worker/load-test processes left behind by subagents (ProcessPool
  workers, synthetic-load loops) held `build/examples/<chapter>` long
  after their agents finished, and `tip verify` died at the extract
  step. After a multi-agent run that executed listings, check
  `Get-Process python` before a verify and kill strays rooted in this
  repo's `.venv`. Also: piping `tip` through `tail` swallows its exit
  code; capture `$?` or redirect to a log instead.
- **`run_examples.py` and `validate_output.py`: never pass a relative
  `--tree`.** It goes on `PYTHONPATH` and breaks once an example changes cwd.
  `validate_output.py` manifests this as `ModuleNotFoundError` on a `utils/`
  helper (`No module named 'greeter'` across every block that imports one),
  which reads as a broken listing rather than a bad flag; an absolute
  `--tree` fixes all of them at once. GUI/interactive examples are skipped via
  `tools/data/norun.txt` (keep those paths current when chapters are renumbered).
- **Renumbering, renaming, or splitting a chapter** touches files and prose that no single gate covers.
  Follow the `rename-chapter` skill (`.claude/skills/rename-chapter/SKILL.md`).
- **Every chapter filename carries its part name, set off by `--`:**
  `NN_<Part>--<Chapter_Name>.md`, as in `08_Foundations--Static_Types.md`,
  `18_Techniques--Performance.md`, `34_Patterns--Composite_and_Interpreter.md`,
  `42_Functional--Error_Handling.md`, `47_Effects--Stateless_in_Practice.md`.
  The part name is the one in `build_site.PARTS`, so renaming a part renames its
  chapters' files. `01_Introduction.md` stays bare: `PARTS` starts Part I at 02,
  so chapter 01 belongs to no part. The H1 carries only the chapter name
  (`# Static Types`), so the filename and the URL say which part a chapter is in
  while the book's own title stays short. Filename stem and H1 therefore never
  match; do not "fix" one to the other.
  Keep `_` as the separator right after the number: `build_site.py` and
  `check_solutions.py` both pull the chapter number with `split("_", 1)[0]`.
  The link regexes restrict which characters a filename may use;
  the `rename-chapter` skill lists them and says why brackets fail silently.
- **Footnote labels are book-wide.** The EPUB and PDF concatenate every
  chapter, and pandoc keeps a `[^label]:` definition's first occurrence,
  so two chapters sharing a label show the first chapter's note in the
  second; the site, one page per chapter, hides it. `footnotes` in
  `GATE_CHECKS` (`tools/footnote_labels.py`) fails on it since
  2026-09-16, after release 0.5.9 went out with chapter 17 showing
  chapter 11's `parametrize` note.
- **Anchors:** pandoc auto-slugs a heading (backticks/punctuation dropped, but `.`
  is kept). Give headings an explicit `{#id}` when the auto-slug would be ugly
  (e.g. anything containing `type[...]` or `__init__`). `heading_links.py` gates it.
- **`tip help` is generated from `tools/tasks.py`, not hand-written.** A
  task is a function under `@task("one-line doc")`, placed after the
  `section("Name")` call it belongs under; the decorator's doc is the
  listing row, the docstring is the long-form help the picker's `?`
  shows, and the body is the recipe shown under it. Bare `tip`
  and `tip help` both list every section; `tip help style` lists
  one section (the slug is the heading's first word, lowercased, and
  two sections may not share one).
  A task whose Python name would shadow a step helper takes `name=`
  (the `run` task is `def run_all(...)` with `name="run"`, since
  `run()` is the helper that runs a command).
  A new task goes in the section for its job, with an `also()` in Everyday if it becomes a daily command.
  `secondary=True` folds a task out of the listing when a sibling's doc names it.
  `tools/tip_help.py`'s docstring covers the listing and the time column,
  `tools/help_picker.py`'s the picker.
  `tools/README.md`'s own "Commands" section deliberately does not re-list every
  target either (it did once, and went stale); it shows only the everyday few and
  points to `tip help` for the rest. Don't re-expand it into a full manual copy.
- **A new third-party dependency may not install on the pinned Python.**
  `requires-python` tracks a bleeding-edge version (currently 3.15, a beta at
  the time this was written), so a package can lack a wheel for it (source
  build then fails) or refuse outright (its own installer version-guards).
  Before committing a new dev dependency: add it to `pyproject.toml`, run
  `uv sync`, and if it fails, revert (`git checkout -- pyproject.toml uv.lock`)
  and re-sync rather than fighting the build. See project memory for the
  numpy/numba case and the workaround for illustrating a chapter example
  anyway.
- **A `ty` or Stateless upgrade is a book-wide event.**
  New inference breaks listings, and lost inference breaks them too.
  The `tool-upgrade` skill (`.claude/skills/tool-upgrade/SKILL.md`) holds the procedure,
  the version-pinned probes, and what each past upgrade broke.
  Follow it after any upgrade, which you never start yourself (see below).
- **A decorator that registers a class must register what a slotted
  `dataclass()` returns, and under `ty` it cannot build that class by
  calling `record(cls)` on its `type[E]` parameter.** `slots=True` makes `dataclass()` create and
  return a new class, since a class's slots are fixed at creation, so
  `EVENTS.add(cls)` before the call files a class that no instance
  belongs to. Chapter 28's `tagged_bus.py` builds first and registers
  `built`; the one-word swap to `slots=True` without that died at import
  with "Announce: not an @event". The same goes for any registering
  decorator stacked *under* `@record`: it would see the pre-slots
  class. None exists in the book, and `tip records` would not catch
  one. Separately, `ty` 0.0.82 mistypes a direct call to a
  `dataclass_transform` function whenever the argument is typed
  `type[...]` rather than being a class literal: `record(Point)` reveals
  `<class 'Point'>`, but `record(cls)` with `cls: type[E]`,
  `type[Point]`, or bare `type` reveals `<decorator produced by
  dataclass-like function>`, not the declared `type[T]`. The same
  signature without `@dataclass_transform` reveals `type[E]`, so the
  marker is the cause. Inside `event()`, `built = record(cls)` therefore
  draws `invalid-argument-type` on `EVENTS.add(built)` and
  `invalid-return-type` on `return built`. Pyright reveals
  `type[E@event]` for the same call and accepts it. ty's
  `dataclass_transform` tracking issue (astral-sh/ty#1327) did not list
  this on 2026-09-17. Hence
  `tagged_bus.py` calls `dataclass(frozen=True, slots=True)(cls)`
  directly. No sentence in the book states this, so there is no version
  string to bump; re-probe on a `ty` upgrade anyway (a scratch
  `event()` in `build/examples` whose body is `built = record(cls)`,
  `EVENTS.add(built)`, `return built`), and the day it passes,
  `tagged_bus.py` can use `record(cls)`.
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
- **Never auto-run `tip tools-upgrade` or `tip python-upgrade`.** Both mutate
  tracked files (`uv.lock`, and `.python-version`/`pyproject.toml` with `TO=`) and
  can invoke real system package managers (`winget`/`brew`). Only run them when
  the user explicitly asks for that specific run, not to "verify" a change.
  `tip tools-check[-full]`, `tip tools-status`, and `tip sweep` are all
  safe to run freely (the first two are read-only; `sweep` writes only
  `build/`). The nag that `gate` prints when the tools are stale is a
  reminder for the author, not an instruction to you: never act on it by
  running an upgrade.
- **`tip gate` hides half its failures, and not the half you would guess.**
  `solutions-gate` is a *prerequisite* of `gate`, so the entire Solutions
  half runs before gate's own recipe starts. One red `gate` after a
  wide-reaching change therefore shows the Solutions failures and hides
  every `Chapters/` one behind them. Use `tip sweep` (runs every check
  over both trees, reports all failures, exits nonzero if any failed)
  whenever the first failure is unlikely to be the only one. A tool
  upgrade is the standard case, and `tools-upgrade` now ends with it.
- **A green `tip sweep` does not mean the committed trees are current,
  and does not mean the `#:` markers are right.** `sweep` runs checks,
  coupling-panels, solutions-numbering, ty, lint, run, and test, each
  over both build trees. It does *not* run `check` (the `Examples/` and
  `SolutionsCode/` drift check) or `output-check`. Editing a listing in
  either Markdown tree therefore leaves its committed copy stale behind
  a green sweep, and a stale marker survives too. `tip verify` covers
  both, through `sync` and `output`. When iterating with `sweep`, run
  `tip check output-check` before believing the tree is clean.
- **A `#:` marker that measures memory or time is a claim about the
  process the gate runs it in, not about a standalone run.** Chapter
  35's `exercise_2.py` prints a `tracemalloc` peak ratio; standalone its
  first line reports 6.1 every time, and under `validate_output.py`,
  which execs the block alongside everything else, it reports the
  committed 6.2. (Before `Tile` became a `@record` on 2026-09-17 the
  pair was 9.8 and 9.9; the slotted `Tile` is smaller, so the ratio
  fell.)
  The gate's context is the authoritative one. Before "fixing" such a
  marker, reproduce it the way the gate does, or you will correct a
  value that was already right.
- **Appendix B's `check_files.py` marker is a self-check, and the gate
  will rewrite it without complaint.** The listing runs the Effect
  checker on six of its own files and on `utils/result.py`, and its
  `#:` lines show rows for the three edge functions, their module, and
  `result.Ok.bind ['Unknown']`. The prose says every core function is
  absent from that output, which is the appendix's claim that the core
  is pure. An edit to any checker listing (`effect_table.py`,
  `call_names.py`, `function_facts.py`, `infer_rows.py`,
  `row_check.py`) or to chapter 42's `utils/result.py` can add an
  unresolvable call: a method on a loop variable, on a record's field,
  or on an imported constant. `validate_output.py --update` then adds
  the new `Unknown` rows to the marker and the gate stays green while
  the prose turns false. Treat any `git diff` on that marker as a
  finding. The fix is to give the checker a written type (an annotated
  parameter, a small helper), as the appendix's "four changes"
  paragraph describes, and never to accept the changed marker.
  `greeting_check.py` and `third_party_stub.py` carry findings in their
  markers too, with prose tied to each line.
- **Prose in `Chapters/*.md` follows Semantic Line Breaks** (one sentence per
  line; a sentence still too wide breaks further at a top-level `,`/`;`/`:`).
  `gate` (so `verify`/`all`/`ci`) runs `reflow_prose.py --write`, so
  hand-edited prose self-heals (rewriting `Chapters/`) the same way line
  endings and `#:` markers do; expect rewrapped lines in `git diff
  Chapters/` after a verify. A paragraph that fails reflow's round-trip
  check is skipped, reported, and still fails the gate, so a rewrite can
  never silently change rendered output. `tip reflow CH=NN` still
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

- `tools/` is a package: run a tool as `uv run python -m tools.<name>`
  from the repo root, not as `python tools/<name>.py` (a bare script
  cannot import its siblings, which are `tools.config`, `tools.repo`,
  and so on). The `tools_` prefix the shared modules used to carry is
  gone; the package namespace does that job. `tools/README.md` explains.
- `tools/*.py` all have thorough module docstrings; read them before guessing.
- A listing name in backticks in the prose (`registry.py`) becomes a link
  to that listing in the site and the EPUB at build time
  (`tools/listing_links.py`). Never write those links by hand in
  `Chapters/`; a plain code span is the source form.
- `tip` replaces make (branch `explore-python-runner`, 2026-09-26):
  `tools/tasks.py` holds every task and documents every gate
  (`tip help`), and `tools/tip.py` runs them. `uv tool install
  --editable .` puts `tip` on PATH, in its own environment outside
  `.venv`; inside the repo `uv run tip ...` works with no install.
  Variables keep make's form (`tip verify-ch CH=28`), each step runs
  through `uv run` from the repo root and is echoed first, a task's
  `deps` run once per invocation, and the first failing step stops the
  run. Every goal named on the command line ends with
  `tip <goal>: 12.3s`. Steps run with `TIP_NESTED=1`, and a nested
  `tip` prints no timing line, so `verify.py` and `sweep_checks.py`
  (which run each step as `python -m tools.tip NAME`) time their own
  steps.
- Detailed conventions and decisions are in project memory (`MEMORY.md` index).
- `thinking-in-python-skill.md` (repo root) and
  `.claude/skills/thinking-in-python/SKILL.md` are duplicate copies of the
  same Python coding-style skill, not a symlink (this repo has
  `core.symlinks = false`). Edit one, then copy the change into the other;
  nothing enforces sync automatically.
