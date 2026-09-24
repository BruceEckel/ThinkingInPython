# Thinking in Python: working in this repo

This file is loaded every session. It captures how the repo is built and verified,
plus the traps that are easy to rediscover the hard way. Personal writing style
lives in the global `~/.claude/CLAUDE.md`; accrued facts live in project memory.

## Source of truth: Chapters/, not Examples/

`Chapters/NN_*.md` is authoritative. Every fenced ```python block whose first line
is a `# path/slug.py` comment is an extractable example. `Examples/` is **generated
from the Markdown** by `tools/extract_examples.py`, so:

- Edit the code **in the Markdown block**, never in `Examples/` directly.
- After editing, sync the committed trees: `make sync`
  (= `uv run python -m tools.extract_examples --write -o Examples` and
  the same for `extract_solutions` into `SolutionsCode/`).
- `Examples/` also holds files with no Markdown block (hand-written helpers,
  `.idea/`, `__pycache__`). `tools/extract_examples.py`'s check mode (part of
  `make check`/`gate`/`verify`/`ci`) flags these automatically: a stray file
  whose name appears nowhere in `Chapters/` is *orphaned* and fails the gate;
  one still mentioned somewhere (a real hand-written helper) is *referenced*
  and only reported, since deleting it needs a human call. `make prune`
  deletes exactly the orphaned ones, under `Examples/` and `SolutionsCode/`
  both (a `utils/` helper rename orphans a file in each). A rename or
  deletion of a book example is the usual cause, so run this after either.

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
`/literal`, `/positive`, `/straighten`, `/cohesion`, and `/antecedents`
(each under `.claude/skills/`) are the other prose passes: figures of
speech become the mechanism they stand for, a passage that makes the
reader cancel one image after another gets restated in positive form, a
sentence the reader must read twice gets its actor named or splits at
the seam, paragraphs get old-before-new order and one topic string, and
every ambiguous "this"/"it"/"which" gets its noun. `make rewrite CH=NN`
runs these five plus `elements-of-style` and `bruce-edit-apply` by
default; `make rewrite ARGS=--list` shows the set and the model each
pass runs on. Each pass can name its own model in `tools/rewrite.py`'s
`PASSES`; all resolve to `DEFAULT_MODEL` (Fable 5) today, `MODEL_NOTES`
there records the A/B evidence behind that, and `MODEL=` forces one
model on a run.
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
| `make rewrite` passes | (headless `claude -p`) | per pass, `tools/rewrite.py` `PASSES` | see `MODEL_NOTES` there |
| verify a chapter's factual claims against its listings and against the chapters it names | a fresh agent per chapter, report-only | Opus | verification fails by under-reading, not by over-editing, so `MODEL_NOTES`' result for the rewrite passes inverts here; in the 2026-09-02 calibration Opus found three real errors Fable read past, with zero false positives from either |
| deep review of a chapter, thread audits, anything that decides what a chapter claims | the session model, or a `fork` | session | needs the conversation's context; a fresh agent cannot know what Bruce has already ruled on |

Pass `model:` on an `Agent` call only to override a definition for one
run. A fresh agent costs roughly 70-150k tokens on a chapter-sized
file; a `fork` carries the whole conversation and costs several times
that, so forks are for work that needs the session's history.

## Editing passes: /edit-start and /edit-done

When Bruce says he is starting to edit a chapter, run `/edit-start NN`
(`.claude/skills/edit-start/SKILL.md`). It places a local annotated git
tag `edit-start-NN` on `HEAD`, records the chapter's baseline (`make
check-ch`, `make reflow-check`, `validate_output`), and reports; it
writes nothing under `Chapters/`. When he says he is done, run
`/edit-done NN` (`.claude/skills/edit-done/SKILL.md`): it diffs from the
tag to the working tree (so commits he made along the way and
uncommitted edits are one pass), hands that diff to
`/bruce-edit-capture`, runs `make verify-ch CH=NN` (or `make verify`
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

Fastest path for one chapter is `make verify-ch CH=NN`
(`tools/verify_chapter.py`): the same fixers and gates as `verify`,
scoped to that chapter and its Solutions file, in a few seconds. It
reflows the chapter only, since the gate never reflows `Solutions/`,
and it writes no gate stamp; a change that other chapters depend on
(a renamed listing, a `utils/` helper, a linked heading) still needs
the whole-book run. That run is `make verify`: fix line endings, every
mutating fixer (the comment-style fixers, import sorting, blank-line
cleanup), refresh the `#:` output markers in both trees, sync `Examples/`
and `SolutionsCode/`, build the figure gallery, then every gate but the
site build. Its ordered step list lives in `tools/verify.py`
(`VERIFY_TARGETS`), and `make verify ARGS=--help` lists it without
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
about its own chapters); all three are in `make verify`. So is
`check_quoted_diagnostics.py`: every quoted `ty` diagnostic's gutter
lines are compared with the extracted listing, and the dozen quotes
the book deliberately makes against an edited copy of a listing live
in `tools/data/quoted_diagnostics_baseline.txt`. A NEW entry after a
listing edit is a stale quote to requote, or a fresh deliberate edit
to accept with `make quoted-diagnostics-accept`; `--all` lists every
hit. `exercise_refs.py` (in the gate since 2026-09-20) does the same
for prose that names an exercise by number: each "exercise N", "the
second exercise", or "the previous exercise" in `Chapters/` and
`Solutions/` is paired with the Solutions title under that number,
and the pairs live in `tools/data/exercise_refs_baseline.txt`.
Inserting or reordering an exercise changes the title under every
later number, so every reference to one turns NEW and fails the gate.
Reread each NEW sentence against the title printed beside it, fix the
number or `make exercise-refs-accept`, and never accept without that
read: chapter 30 carried five stale numbers for a day after commit
a2cc5a98 inserted an exercise at 2, with every gate green. A new
reference is NEW too, until accepted. `make verify-ch` sees only the
references its two files make, so after moving an exercise run
`make exercise-refs` over the book. `make verify`'s gate also
runs `validate_output.py --update` over all of `Chapters/` now, so a stale
`#:` marker anywhere self-heals (rewriting `Chapters/`) instead of failing
the build, the same way `fix-eol`/`sync` already self-heal other drift.
Check `git diff Chapters/` afterward: a chapter you did not touch can
still land in the diff if its output actually changed. An exception
raised where none is expected still fails the gate; only marker text is
auto-corrected. A lone bare `#: ` with nothing after it is always treated
as a not-yet-filled-in placeholder and filled in, even without `--update`.

## Pyright: a periodic review, never a gate

`ty` is the only checker the gates run. Pyright is a pinned dev
dependency with its config in `pyproject.toml` (`[tool.pyright]`), and
its value is the list of places where it disagrees with `ty`, kept in
`tools/data/pyright_baseline.txt`. `make pyright-review` runs it over
both extracted trees and prints only the delta: NEW for a diagnostic
the baseline lacks, GONE for one that no longer fires. It exits
nonzero on NEW. `make pyright-accept` rewrites the baseline once every
line in the delta has an explanation. `tools/pyright_review.py` has
the details; `pyright_experiment.md` has the 2026-09-14 measurement
that led here.

Three rules, all deliberate:

- **Nothing pyright-related joins `verify`, `gate`, `sweep`, or `ci`.**
  A green pyright run is not the goal; the changed delta is the
  information.
- **No listing carries a pyright suppression.** A `# pyright: ignore`
  in a book listing explains nothing to a reader using `ty`, so every
  accepted disagreement is a baseline entry instead. (The two checkers'
  comments do coexist, `# ty: ignore[rule]` and `# pyright: ignore[rule]`
  each invisible to the other, but the book does not use that.) The ten
  listings pyright cannot parse (PEP 798 comprehension unpacking) are
  baseline entries too, not an exclude list.
- **"The type checker" in prose means `ty`.** The review's first
  catch was chapter 12 claiming "a type checker" never compares a bare
  `default_factory` with its field, which Pyright does. The 2026-09-14
  sweep of 195 such sentences found fourteen that hold for `ty` alone;
  each now names `ty` and says what the other checkers do. When a NEW
  entry names a listing, reread the nearest "the type checker" sentence
  next to it. mypy is not a candidate for the book: it cannot parse the
  PEP 798 or PEP 661 helpers and rejects a dozen committed Stateless
  listings on its own limitations.

Read the delta at three moments: after editing a chapter's listings
(a NEW entry is a fresh disagreement worth a sentence), after `make
tools-upgrade` moves pyright (GONE means pyright caught up, NEW means a
new strictness), and after a `ty` upgrade (a disagreement that
disappears because `ty` now reports it too is a listing that may need
an ignore).

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
has no reason to mention. `make self-reference-report` reads it, the same
bargain `make claims` strikes. Do not promote it into the gate without
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
registers"). `tools/pattern_names.py` checks it (`make pattern-names`)
and `make fix-pattern-names` rewrites the unambiguous cases; the names
and the excluded phrases (`!State Machines`) are in
`tools/data/pattern_names.txt`. State/Command/Bridge at a line start
are listed only with `--sentence-start`, for a human to judge; the
three in the book ("State the rule...") are the verb. The check has
been in `GATE_CHECKS` since 2026-09-16, so `verify`, `gate`, and
`verify-ch` fail on a plain name.

## Diagrams: the figure labels, the caption names, the prose explains

A figure is a hand-authored SVG in `resources/images/`, referenced from
the prose as `![caption](_images/<name>)` with no extension.
`build_site.py` and `build_epub.py` resolve it (the EPUB rasterizes the
SVG to PNG, so a rasterizer must be on PATH: `resvg`, `rsvg-convert`,
`magick`, or `inkscape`). There is no Mermaid, Graphviz, or PlantUML
anywhere in the repo, and a diagram written as a fenced block renders
as nothing.

Three rules about what text goes where, from Bruce's 2026-09-18 ruling
on chapter 30's `observer_broadcast.svg`:

- **No caption inside the SVG.** A drawing carries labels on its
  parts, nothing else. A sentence summarizing the figure, set in small
  type along the bottom, is a caption in the wrong place: pandoc
  already prints the Markdown alt text as a `<figcaption>` under the
  image, so an embedded one shows up twice, in two type sizes.
- **The Markdown caption is one short sentence** naming what the figure
  shows. Chapter 30's is "One call to set_celsius() becomes one
  update() call on every observer in the list."
- **Everything else goes in the prose after the figure**, as ordinary
  sentences with the usual code spans. The second clause cut from
  chapter 30's caption became the paragraph under it: "`Thermometer`
  holds the list and names no observer type, so a `Plot` and a `Table`
  would attach the way `Display` does."

The existing diagrams share a visual vocabulary worth matching, since
nothing enforces it: a `viewBox` with no width or height,
`font-family="'JetBrains Mono', Consolas, monospace"`, a `<title>` for
screen readers, and the cover palette from `tools/make_cover.py`,
`#1a1612` for ink and text, `#c8bfb0` for ordinary box strokes,
`#7a6e62` for muted text, `#8b1a1a` to mark the one class the figure
is about. A dashed stroke marks a box that the listing does not
contain (`surrogate.svg`'s "Etc.", `observer_broadcast.svg`'s `Plot`
and `Table`). Before committing a new one, rasterize it the way the
EPUB does and look at the PNG; text that fits in a browser can collide
once rasterized. `make figures` (in `make verify` since 2026-09-24,
`tools/figure_gallery.py`) builds `build/figures/index.html`: every
figure in book order, numbered, with its file name, chapter, line,
and caption, switchable between the live SVG and the EPUB's PNG,
and a style line per figure (colors, stroke widths, dashes, fonts,
arrowhead markers) that marks anything outside the palette. Bruce
names a figure by its number there or its file stem; it fails on a
reference with no file and only reports a file no chapter references.

The one family of generated figures is the coupling-notation panel at
the top of each pattern chapter, 23 through 36
(`resources/images/coupling_NN.svg`, merged 2026-09-23). Chapter 21's
Coupling section (merged from Appendix C on 2026-09-24) defines the
notation: a heavy edge names a
concrete class, a thin edge names an interface, a dashed hollow-headed
edge satisfies one, a solid hollow-headed edge inherits, and the red
box is the part the pattern keeps free of change. `tools/coupling_panels.py`
holds a `Panel` spec per chapter, in that chapter's own class and
function names, plus the `CAPTIONS` dict with the Markdown captions
(code spans on the identifiers, because the pattern-name gate reads a
bare "Proxy" or "Observer" in a caption as an unitalicized pattern
name). Edit the spec and run `make fix-coupling-panels`; never edit
one of these SVGs by hand. `make coupling-panels` (in `gate`,
`verify-ch`, and `sweep`) fails when a committed SVG differs from what
the spec draws, so a listing rename that misses the spec is loud. The
2026-09-23 verification of all fourteen found two recurring mistakes
worth checking a new panel for: drawing the GoF shape instead of the
listing's (chapter 26 had a `Service` protocol no listing declares),
and counting a call through `Any` as naming a class (chapter 32's
`eval_*()` methods). A panel's note counts the heavy edges drawn and
says when demo or wiring code is left out.

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

`tools/record_check.py` gates both directions (`make records`, in
`GATE_CHECKS` and in the Solutions checks since 2026-09-17): a
`@dataclass(frozen=True)` whose bases are all slotted fails unless
`tools/data/record_exceptions.txt` lists it, and a `@record` under a
base with no `__slots__` fails. A base it cannot see (imported from
another listing) draws no finding, so it under-reports by design. The
exceptions file is keyed by chapter *name* (`Rethinking_Objects`), not
number, so a renumbering leaves it alone and a chapter rename does not.
Run alone, `make records` also fails on an entry that matches nothing.
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
- **`tools/*.py` is not linted by any gate.** Only `build/examples` is checked by
  `make lint`/`make ci`, so a `tools/` script can exceed the 70-char limit with
  nothing catching it (several already do). `ty` still matters there; run it
  directly, e.g. `uv run ty check tools/whatever.py`.
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
  each, so a burst lands on both. 2026-08-30: the listing (and every
  other wall-clock boolean) is registered in `tools/data/timing.txt`,
  so the gate retries a mismatch toward the committed `True` instead of
  rewriting it; a flip now surfaces as a loud validate failure after
  three misses, never as a silent diff in the generated copy. 2026-08-30: do not shrink the loop to make the
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
  Orphaned python processes cause the same error: on 2026-09-03,
  worker/load-test processes left behind by subagents (ProcessPool
  workers, synthetic-load loops) held `build/examples/<chapter>` long
  after their agents finished, and `make verify` died at the extract
  step. After a multi-agent run that executed listings, check
  `Get-Process python` before a verify and kill strays rooted in this
  repo's `.venv`. Also: piping make through `tail` swallows its exit
  code; capture `$?` or redirect to a log instead.
- **`run_examples.py` and `validate_output.py`: never pass a relative
  `--tree`.** It goes on `PYTHONPATH` and breaks once an example changes cwd.
  `validate_output.py` manifests this as `ModuleNotFoundError` on a `utils/`
  helper (`No module named 'greeter'` across every block that imports one),
  which reads as a broken listing rather than a bad flag; an absolute
  `--tree` fixes all of them at once. GUI/interactive examples are skipped via
  `tools/data/norun.txt` (keep those paths current when chapters are renumbered).
- **Renumbering or renaming a chapter** touches, in all four trees
  (`Chapters/`, `Solutions/`, `Examples/`, `SolutionsCode/`): the filenames, every
  `NN_*.md` cross-reference and its link text, `build_site.py` `PARTS`,
  `tools/data/norun.txt`, `tools/data/timing.txt` (since 2026-09-18 the
  gate's `skip-lists` step, `tools/check_skip_lists.py`, fails on a
  pattern in either that matches no file under `Examples/` or
  `SolutionsCode/`, so a missed one is loud; renaming one *listing*
  trips it the same way),
  `tools/data/record_exceptions.txt` and
  `tools/data/exercise_refs_baseline.txt` (both keyed by chapter name,
  so a rename only; after one, `make exercise-refs` shows each pair as
  GONE plus NEW, and `make exercise-refs-accept` settles it), the
  `README.md` tracking table,
  `deep_review_db.md`/`readability_db.md`/`bruce_edit_db.md`, and any
  `tools/tests/` fixture naming a chapter. Appendices use letter prefixes
  (`A_...`); build_site labels them "Appendix X".
  The ones that hide, both in `pyproject.toml`: **`per-file-ignores` keys a few
  entries by chapter directory** (`"**/46_Effects--Stateless/exercise_8.py"`), so
  a rename silently drops the waiver and the listing fails `I001` at
  `solutions-gate`, several steps after the rename looked done; and
  **`[tool.ty.environment] extra-paths` names one**
  (`build/examples/06_Foundations--Modules_and_Packages`), where a stale entry
  makes `ty` refuse to start with "does not point to a directory". Grep
  `pyproject.toml` for the old directory name before running `verify`.
  Renaming the *chapter title* additionally means the H1, the Solutions H1
  (`<Title>: Solutions`), and every link whose text was the old title.
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
  **A regex that matches chapter filenames must allow `-`.** `check_solutions.py`'s
  `BARE_CHAPTER_LINK` was `\d{2}_[A-Za-z_]+\.md` and stopped matching every chapter
  the moment the `--` landed, so the check reported nothing instead of failing.
  Its own unit test caught that one. Grep `re.compile` for `\.md` before adding a
  character to a filename.
  Only `[\w./-]` is safe in a filename, because that is the character class in
  all three link regexes (`build_site.MD_LINK`, `build_epub.ANCHOR_TARGET`,
  `heading_links.ANCHOR_TARGET`). A character outside it fails *silently*, which
  is why brackets were tried and rejected: with `43_[Functional]_Confidence.md`,
  `heading_links` reported "Anchor links OK" for a link to a nonexistent anchor,
  and `build_site` emitted un-rewritten `.md` hrefs (404s on the site). No gate
  went red. Also avoid `[`/`]` because `norun.txt` and `timing.txt` patterns are
  `fnmatch` globs, where brackets are a character class.
- **Splitting a chapter silently invalidates every relative cross-reference in
  the later half.** Nothing greps for prose, so no gate catches this. Splitting
  Generators out of Stateless left chapter 46 with fourteen phrases
  ("the previous chapter", "the previous chapter's second exercise",
  "the previous section") that still meant 44, not the newly-inserted 45.
  After any split, `grep -n "previous chapter\|previous section\|last chapter"`
  the later half and check each hit against the content it names, since some
  will legitimately point at the new neighbor. Prefer a named link
  (`[Effect Management](44_Effects--Effect_Management.md#anchor)`) over a relative
  phrase, so the next split fails loudly at `heading_links.py` instead of
  quietly misleading a reader. Where three references cluster in one section,
  resolve the later ones with "that chapter" against a nearby link rather than
  repeating the same hyperlink.
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
  looks up doc text through it. A `##+ name name` line (since 2026-09-24)
  repeats targets defined elsewhere into the section it sits in, at that
  point in the listing, so one target can appear under every heading where
  someone would look for it; `entries()` skips the repeats, and `make_help`
  exits on a `##+` naming no documented target or one defined in that same
  section. The sections are ordered by how often they are used, Everyday
  first and Cleanup last, and a new target goes in the section for its
  job, with a `##+` in Everyday if it becomes a daily command. Parsed by `tools/make_help.py`,
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
  Chapter 35's `to_symbol()` and `Solutions/35_Patterns--Flyweight.md` were written
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
  before assuming the first failure is the only one: `make verify` stops
  at the first failing gate, and `solutions-gate` runs first, as `gate`'s
  prerequisite.
  The 0.0.75 to 0.0.77 upgrade (2026-09-02, alongside Python 3.15.0b3 to
  3.15.0rc2) was the first with **no fallout at all**: `make sweep` green
  on both trees, no marker or reflow drift, and all four version-pinned
  claims below re-probed unchanged. Record the quiet ones too, so the
  next upgrade knows what a clean one looks like.
  The 0.0.78 to 0.0.80 upgrade (2026-09-14) had one gate failure and one
  prose casualty. The gate: typeshed's `weakref.finalize` no longer
  draws `missing-slot`, so ch10 `finalize_trap.py`'s `# type: ignore`
  became an `unused-type-ignore-comment` warning and was removed. The
  prose: nested handler expressions now infer precisely
  (`handle(scripted)(handle(capture)(greet))` reveals
  `() -> Generator[Never, Any, None]`, the same as the named form, and
  a `Need` left unsupplied stays named through `catch_all()` so `run()`
  rejects it), which emptied ch47's "The type checker can give up
  quietly" section; it was rewritten in present tense as "The type
  checker decides what survives handling" around the one asymmetry
  left (below). All 32 quoted diagnostics re-verified; one pre-existing
  off-by-one in Solutions ch40 was fixed. Two probes were wrong before
  they were right: a module-level `feed: Feed = Wire()` is narrowed to
  `Wire`, so `supply(feed, ...)` subtracts `Need[Wire]`, not
  `Need[Feed]`, and the "lost subtraction" that showed was an artifact.
  Probe `supply()` inside a function whose parameters carry the
  Protocol types, as the chapter's `outcome()` does, or through
  `as_type()`.
  The 0.0.80 to 0.0.81 upgrade (2026-09-16, with ruff 0.16.7 to
  0.16.8) was a quiet one: `make sweep` green on both trees, the
  pyright delta empty, all six version-pinned claims re-probed
  unchanged, and all 40 quoted diagnostics matching. The quote recheck
  ran as one `verify-claims` agent (about 130k tokens, seven minutes),
  and reading that closely it found two stale Solutions passages no
  upgrade caused: Solutions 46 naming line 28 under a quote that points
  at line 29, and Solutions 17 showing a `try`/`except` the listing had
  long since replaced with `with expected(TypeError):` (then named `ignore`).
  The 0.0.81 to 0.0.82 upgrade (2026-09-17) had one gate failure, and
  it retired a claim. 0.0.82 reports instantiating an abstract class
  (`error[call-non-callable]: Cannot instantiate abstract class`),
  directly or through a subclass that leaves an abstract method out.
  The gate: ch26 `proxy_interface.py`'s `Proxy(Partial())` now carries
  a `# type: ignore`, with a sentence saying the checker reports it
  before the runtime refuses it. The claim: Solutions 25 exercise 4
  said `ty` had no such rule and named Pyright and mypy as the
  checkers that report it; it now says the type checker reports the
  construction. Chapter 17's "`@abstractmethod` makes the checker
  report an abstract instantiation" became true of `ty` that day. The
  pyright delta was one GONE, the same line, because pyright honors
  the `# type: ignore` too. The five remaining pinned claims and the
  `record(cls)` gap re-probed unchanged, and all 40 quoted diagnostics
  matched (two `verify-claims` agents, about 80k and 130k tokens).
  **Sweep `Solutions/` for quoted diagnostics too, not just `Chapters/`.**
  The 2026-09-02 exercise pass found ten stale `ty` quotes, every one of
  them in `Solutions/` and not one in `Chapters/`: wrong line numbers,
  wrong diagnostic codes, wrong message text, and twice a claim built on
  the wrong wording that inverts the point being taught (see
  `exercise_review.md` Part 2.1). Earlier upgrade sweeps went through
  `Chapters/` and stopped. Nothing gates this: `output-check`
  validates `#:` markers, and a diagnostic quoted in prose is not a
  marker. `grep -rn "^error\[\|^warning\[\|^info\[" Chapters/ Solutions/`
  finds all 40 in the book (33 errors, 7 `reveal_type` quotes), so the
  sweep is small once you remember it.
  Chapters 46-47 and Solutions 43 pin five behavior claims to a
  ty version ("under `ty` 0.0.82"; `grep -rn '0\.0\.[0-9]' Chapters
  Solutions` finds them): the `type`-alias probe (46), the
  chained-`supply()` order and the `Never`/`Unknown` asymmetry, the
  `nested_handle.py` reveal, and the `fork(bad)` reveal (47), and the
  `float | Unknown` without `@final` (Solutions 43). Re-probe on each
  upgrade and update those version strings; the alias probe is a
  scratch generator annotated with a `type X = Depend[...]` alias whose
  `yield from need(Undeclared)` must still draw `invalid-yield`. The
  ch47 probes run against `build/examples/47_*/`, inside a function
  with `feed: Feed, book: Encyclopedia` parameters: both
  `supply`/`catch_all` orders must reveal the same result union, with
  `supply(feed, book)(catch_all(research))` reading `Never` in the
  Ability channel and `catch_all(supply(feed, book)(research))` reading
  `Unknown`; `supply(feed)(research)` followed by `catch_all()` must
  keep `Need[Encyclopedia]` named and fail `run()`;
  `partial_handling.py` with its `# type: ignore` stripped must still
  report `Generator[Need[Log], Any, None]` against `run()`, nested or
  named; and `handle(scripted)(handle(capture)(greet))` must reveal
  `() -> Generator[Never, Any, None]`, the same as the named `full`,
  with `half` still `() -> Generator[Ask, Any, None]`. Solutions 43:
  strip both `@final` from `describe_isinstance.py` and
  `reveal_type(result.answer)` in the `Ok` branch must read
  `float | Unknown`. A sixth claim, Solutions 25 saying `ty` had no
  rule for instantiating an abstract class, was retired by 0.0.82,
  which added the rule.
- **A Stateless upgrade is a book-wide event too.** The libraries the
  listings import (`libs_check.LIBRARIES`: Stateless, numpy, hypothesis,
  time-machine) sit in the same dev group as the tools, so
  `make tools-upgrade` moves them along with `ty` (`uv lock --upgrade`
  upgrades everything), and their constraints are floors. `make
  libs-check` (read-only, no gate) says when a release is waiting;
  `make tools-status` lists the locked versions and notes one that
  moved since the last stamp. Stateless was 0.6.1 on 2026-09-17, the
  newest on PyPI since 2025-11-11; work on its repository that has no
  release is invisible to uv, and the book does not track it, because a
  reader installs the PyPI release.
  Take a Stateless release alone, never alongside a `ty` bump, so a
  failure has one cause: `uv lock --upgrade-package stateless`, then
  `uv sync`. Then, in this order: `make sweep`; the five version-pinned
  probes above, since the revealed types come from Stateless's
  annotations as much as from `ty`'s inference; the two quotes that
  list the library's overloads verbatim (nine for `supply()` in
  Chapters 47, four for `fork()` in Solutions 47), which a new overload
  makes stale with no gate reading message text; and one
  `verify-claims` agent each over Chapters 46 and 47 and their
  Solutions files, told to check every sentence about the library's
  behavior against the installed source in
  `.venv/Lib/site-packages/stateless/`. Those sentences carry no
  version string, so no grep finds them: `fork()` running `run()` in
  the worker with no `try`/`except`, `supply()` answering a `Need` with
  the first matching instance, `Async` being one more Ability, no
  defect channel. The absence claims are the exception, and a release
  falsifies one by adding the thing: `grep -n "Stateless has no\|Stateless
  provides no" Chapters/4[67]*` finds them (nine on 2026-09-17: no
  registration, no container, no scoping mechanism, no defect channel,
  no timeout, no `race`, no fallback combinator). Finish by
  updating project memory `stateless-api-surface` with what the release
  added or removed, and run `make pyright-review`.
- **A decorator that registers a class must register what a slotted
  `dataclass()` returns, and under `ty` it cannot build that class by
  calling `record(cls)` on its `type[E]` parameter.** `slots=True` makes `dataclass()` create and
  return a new class, since a class's slots are fixed at creation, so
  `EVENTS.add(cls)` before the call files a class that no instance
  belongs to. Chapter 28's `tagged_bus.py` builds first and registers
  `built`; the one-word swap to `slots=True` without that died at import
  with "Announce: not an @event". The same goes for any registering
  decorator stacked *under* `@record`: it would see the pre-slots
  class. None exists in the book, and `make records` would not catch
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
- **A green `make sweep` does not mean the committed trees are current,
  and does not mean the `#:` markers are right.** `sweep` runs checks,
  coupling-panels, solutions-numbering, ty, lint, run, and test, each
  over both build trees. It does *not* run `check` (the `Examples/` and
  `SolutionsCode/` drift check) or `output-check`. Editing a listing in
  either Markdown tree therefore leaves its committed copy stale behind
  a green sweep, and a stale marker survives too. `make verify` covers
  both, through `sync` and `output`. When iterating with `sweep`, run
  `make check output-check` before believing the tree is clean.
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
- The `Makefile` documents every gate and target (`make help`).
  Every goal named on the command line runs in a child make under
  `tools/timed_make.py` and ends with `make <goal>: 12.3s`; the
  real rules sit inside `ifeq ($(TIMED),)`/`else`/`endif`, so a
  new target goes inside that block, and `TIMED=0` bypasses the
  wrapper. A tool that runs `make` from Python inherits `TIMED=1`
  through `MAKEFLAGS` when it was itself started by make, so
  `verify.py` and `sweep_checks.py` time their own steps.
- Detailed conventions and decisions are in project memory (`MEMORY.md` index).
- `thinking-in-python-skill.md` (repo root) and
  `.claude/skills/thinking-in-python/SKILL.md` are duplicate copies of the
  same Python coding-style skill, not a symlink (this repo has
  `core.symlinks = false`). Edit one, then copy the change into the other;
  nothing enforces sync automatically.
