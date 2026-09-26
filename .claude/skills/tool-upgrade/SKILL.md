---
name: tool-upgrade
description: >-
  Procedure and history for a ty, ruff, pyright, or Stateless upgrade in this repo: what breaks in both directions, the version-pinned probes to re-run, the quoted-diagnostic sweep, and reading the pyright delta. Use after make tools-upgrade or a Stateless bump, or when running make pyright-review.
---

# Tool and library upgrades

Moved from `CLAUDE.md`, which keeps the rule that you never start an upgrade yourself.

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
