---
name: tool-upgrade
description: >-
  Procedure and history for a ty, ruff, pyright, or Stateless upgrade in this repo: what breaks in both directions, the version-pinned probes to re-run, the quoted-diagnostic sweep, and reading the pyright delta. Use after tip tools-upgrade or a Stateless bump, or when running tip pyright-review.
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
  Solutions ch34). After `tip tools-upgrade`, run
  `uv run ty check build/examples` **and** `uv run ty check build/solutions`
  before assuming the first failure is the only one: `tip verify` stops
  at the first failing gate, and `solutions-gate` runs first, as `gate`'s
  prerequisite.
  The 0.0.75 to 0.0.77 upgrade (2026-09-02, alongside Python 3.15.0b3 to
  3.15.0rc2) was the first with **no fallout at all**: `tip sweep` green
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
  0.16.8) was a quiet one: `tip sweep` green on both trees, the
  pyright delta empty, all six version-pinned claims re-probed
  unchanged, and all 40 quoted diagnostics matching. The quote recheck
  ran as one `verify-claims-opus` agent (about 130k tokens, seven minutes),
  and reading that closely it found two stale Solutions passages no
  upgrade caused: Solutions 46 naming line 28 under a quote that points
  at line 29, and Solutions 17 showing a `try`/`except` the listing had
  long since replaced with `with expected(TypeError):` (then named `ignore`).
  The 0.0.81 to 0.0.82 upgrade (2026-09-17) had one gate failure, and
  it retired a claim. 0.0.82 reports instantiating an abstract class
  (`error[call-non-callable]: Cannot instantiate abstract class`),
  directly or through a subclass that leaves an abstract method out.
  The gate: ch25 `proxy_interface.py`'s `Proxy(Partial())` now carries
  a `# type: ignore`, with a sentence saying the checker reports it
  before the runtime refuses it. The claim: Solutions 24 exercise 4
  said `ty` had no such rule and named Pyright and mypy as the
  checkers that report it; it now says the type checker reports the
  construction. Chapter 17's "`@abstractmethod` makes the checker
  report an abstract instantiation" became true of `ty` that day. The
  pyright delta was one GONE, the same line, because pyright honors
  the `# type: ignore` too. The five remaining pinned claims and the
  `record(cls)` gap re-probed unchanged, and all 40 quoted diagnostics
  matched (two `verify-claims-opus` agents, about 80k and 130k tokens).
  The 0.0.84 to 0.0.86 upgrade (2026-10-11, the day Python 3.15.0 final
  replaced rc2, with ruff 0.16.9 to 0.17.0, numpy 2.5.3 to 2.5.4,
  hypothesis 6.168.3 to 6.169.0, and uv 0.12.20 to 0.13.0) had no gate
  failure and one prose casualty. Python first, alone: `tip
  python-upgrade` needed the new uv to see the 3.15.0 download, and the
  whole-book verify was green with no marker or reflow drift; chapter
  10's shutdown transcript and the small-int cache note re-verified.
  Then `tip tools-upgrade`: `tip sweep` green, the pyright delta empty,
  all 43 quoted diagnostics matching (one `verify-claims-opus` agent,
  about 130k tokens, four minutes), and the "Python 3.15 is under
  development" warning gone. The new noise: typeshed deprecates the
  `Iterator` overload of `contextmanager`, so every `@contextmanager`
  generator annotated `-> Iterator[T]` drew `warning[deprecated]` (17
  listings in chapters 15 and 47 and their Solutions); a warning does
  not fail the gate, and the fix was `-> Generator[T]` and
  `-> AsyncGenerator[T]` throughout (PEP 696 defaults make the one-
  argument form valid). The casualty: chapter 09's "`ty` enforces less
  than the declaration states" paragraph. 0.0.86 reports a subclass's
  `sides = "four"` under a base `sides: ClassVar[int]` as
  `invalid-assignment`, and a redeclared `sides: ClassVar[str]` as
  `invalid-attribute-override`; it still accepts a narrowing
  `sides: ClassVar[bool] = True`, which Pyright rejects, and still
  needs no value from a subclass. The paragraph now states those two
  gaps. The other six pinned claims and the `record(cls)` gap re-probed
  unchanged (one `verify-claims-opus` agent, about 90k tokens). Two
  traps from the run: the probing agent's cleanup, `find build -name
  'probe_*.py' -delete`, also removed 46 older scratch files under
  `build/claims-scratch/` (gitignored, so harmless, but delete by
  listed path); and a Python `write_text()` on Windows turns `\n` into
  CRLF, so a script that rewrites Markdown passes `newline="\n"` or
  `tip fix-eol` runs before the commit. winget's pandoc step failed to
  uninstall 3.11 (exit 1603), so pandoc stays at 3.11 with 3.12.1
  available; typst 0.15.1 and vale 3.24.0 were current.
  The 0.0.86 to 0.0.87 upgrade (2026-10-13, with hypothesis 6.169.0
  to 6.169.1; ruff, pyright, uv, and the libraries unchanged) had no
  gate failure and one prose casualty, the same chapter 09 paragraph
  as the upgrade before. `tip sweep` green on both trees; the pyright
  delta was three GONE lines in Solutions 31 `exercise_9.py`, caused by
  that day's typed-rules rewrite of the listing rather than the
  upgrade (pyright had not moved), and accepted. 0.0.87 adds
  `invalid-mutable-override`: a subclass's `sides: ClassVar[bool] =
  True` under a base `sides: ClassVar[int]` is now rejected, so the
  narrowing gap closed and chapter 09's "Two mistakes pass the checker"
  became "One mistake", the missing value; the Pyright contrast and
  the issue 2158 pointer (still open that day, its title is the
  general LSP rule) came out. The other nine probes held (one
  `verify-claims-opus` agent, about 80k tokens, two minutes) and all
  43 quoted diagnostics matched (one agent, about 130k tokens, four
  minutes; it also ran every probe under `uv tool run --from
  ty==0.0.86 ty check` and found the two versions print the same, a
  faster answer to "did the upgrade move a quote" than reading each
  one). Trap: `tip pyright-review` re-extracts both build trees, so
  running it while a probe agent works deletes the agent's scratch
  files mid-run; run it before launching the agents.
  The 0.0.89 to 0.0.90 upgrade (2026-10-22, with Python 3.15.0rc2 to
  3.15.1, uv 0.12.18 to 0.13.5, and hypothesis 6.170.1 to 6.170.5;
  ruff, pyright, and the other libraries unchanged) was a quiet one.
  `ty` had already moved 0.0.87 to 0.0.89 on 2026-10-17 through a bare
  "Update uv.lock" commit with no pin sweep, so the whole-book review
  of 2026-10-21 re-probed every pinned claim on 0.0.89 first. Then, in
  order: `uv self update` alone, because the old uv could not see the
  3.15.1 download; `tip python-upgrade`, whole-book verify green with
  no marker or reflow drift; `tip tools-upgrade`, `tip sweep` green on
  both trees; `tip pyright-review` with one NEW, chapter 03's
  `chain_map.py`, where pyright infers `dict[str, int]` for
  `user = {"zoom": 125}` and rejects `user["theme"] = "dark"` while
  `ty` accepts it (accepted; the chapter makes no checker claim
  there); `tip quoted-diagnostics-probe` 42 of 42 MATCH; and all ten
  pinned probes HOLD, including `record(cls)` still mistyped (one
  report-only Opus agent, about 90k tokens, 70 seconds). Then
  `tip version-pins ARGS=--write`. winget's pandoc step failed to
  uninstall again (exit 1603), so pandoc stays where it was.
  The 0.0.90 to 0.0.91 upgrade (2026-10-22 again, that afternoon on the
  Windows machine, with ruff 0.17.1 to 0.17.2 and hypothesis 6.170.5 to
  6.170.8) was quiet too. The morning's run happened in another clone,
  so this machine pulled the lockfile with uv still at 0.13.1 and its
  managed Python still at 3.15.0: a pull moves `uv.lock`, never uv or
  the interpreter, so each machine runs `uv self update` and
  `tip python-upgrade` on its own. The trigger was `tip` itself failing
  with "did not find executable at 'C:\Python\python.exe'": the tool
  environment `uv tool install` builds keeps the interpreter it was
  built on, and a python.org install that the new Python install manager
  replaced had taken that interpreter away. `uv tool install --reinstall`
  fails on such an environment, because it queries the old interpreter
  first; `uv tool uninstall thinking-in-python`, then `uv tool install
  --managed-python --python 3.15 -e .`, rebuilt it on uv's managed
  Python. Then `tip python-upgrade` (verify green, no drift) and
  `tip tools-upgrade` (`tip sweep` green, pandoc 3.12.1 and typst and
  vale current); `tip check output-check` clean; the pyright delta
  empty; `tip quoted-diagnostics-probe` 42 of 42 MATCH; and all 13
  probes and the 7 pinned sentences HOLD, each byte-identical under
  0.0.90 and 0.0.91 (one report-only Opus agent, about 90k tokens, under
  two minutes).
  The 0.0.91 to 0.0.95 upgrade (2026-10-30, with Python 3.15.1 to
  3.15.2, uv 0.13.5 to 0.13.6, ruff 0.17.2 to 0.17.3, pytest 9.1.1 to
  9.2.0, hypothesis 6.170.8 to 6.170.14, time-machine 3.5.1 to 3.6.0,
  numba 0.68.0 to 0.68.1; pyright, Stateless, and numpy unchanged) was
  quiet across four `ty` releases. In order: `uv self update` (the old
  uv could not see 3.15.2), `tip python-upgrade`, then a second verify
  under `TIP_FULL=1`, because the first one refreshed no markers: the
  stamp digest covered `uv.lock` and `.python-version` and a patch
  upgrade changes neither, so `skip_stamps.marker_context()` hashes
  `sys.version` since that day. Then `tip tools-upgrade` with `tip
  sweep` green on both trees, `tip check output-check` clean, the
  pyright delta one renamed message (chapter 17's `events.py` now says
  `Hour` where it said `int`, from the alias added 2026-10-28, not
  from pyright, which did not move; accepted), `tip
  quoted-diagnostics-probe` 43 of 43 MATCH, no `ty` warnings in either
  tree, and all 13 probes HOLD, byte-identical under 0.0.91 and 0.0.95
  (one report-only Opus agent, about 105k tokens, two and a half
  minutes; its brief is the shape to reuse, in
  `build/upgrade-2026-10-30/PROBES.md` while that directory lasts: one
  numbered probe per pinned claim, both versions through `uv tool run
  --from ty==OLD`, scratch files deleted by listed path). Then `tip
  version-pins ARGS=--write` bumped the ten pins. winget's pandoc
  uninstall failed with 1603 for the third time, so pandoc stays at
  3.12.1 with 3.13 available; vale moved to 3.25.1. The small-int
  cache still reaches 1024 on 3.15.2. Then, on Bruce's "check to see
  if there are any things we can improve with the new ty", a second
  pass the earlier upgrades never made: `uv run ty check build/examples
  --warn unused-ignore-comment` (and `build/solutions`; the printed
  rule name is `unused-type-ignore-comment`, so grep for that) found
  none of the 90 `# type: ignore` lines unused; `redundant-cast` is on
  by default and was silent, and the three `typing.cast()` calls each
  convert an `object` or a `Callable` the next line needs. The four
  changelogs (0.0.92 to 0.0.95) add no rule and change no default:
  narrowing fixes for `match` captures, enum comparisons, and
  `LiteralString`, ParamSpec and TypeVarTuple inference, Django
  support, a preview `baseline` setting, SARIF output. Four
  report-only Opus agents (about 125k tokens and three and a half
  minutes each) then read the 107 unpinned prose lines that say what
  `ty` cannot do, misses, or accepts (`grep -rn -i '`ty` \(does
  not\|cannot\|misses\|accepts\|has no\|reports nothing\|still\)\|the
  type checker \(does not\|cannot\|...\)' Chapters Solutions`), probed
  each under both versions, and found every one still true, and the
  prose beside each of the 70 ignores in those chapters still names
  the diagnostic it suppresses. One imprecision surfaced that no
  version caused: Solutions 12 exercise 8 passes three values through
  one loop, so the suppressed report names `True` beside the two
  values the checker rejects; a sentence now says so. That pass is
  the shape to repeat when a `ty` release adds a rule or a narrowing
  change, since the gate cannot see a "cannot see" sentence turn false.
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
  `tip quoted-diagnostics-probe` (`tools/quoted_diagnostics_probe.py`)
  now does that sweep, so it replaces the report-only agent on an
  upgrade. It rebuilds the listing behind each of the 42 quotes in
  `Chapters/` and `Solutions/` (the edit for each, such as a stripped
  `# type: ignore` or a deleted `match` block, lives in
  `tools/data/quoted_diagnostics_probes.txt`), runs `uv run ty check`
  on it, and prints MATCH or STALE per quote with the quoted and actual
  text side by side. The run takes a few seconds and exits nonzero on
  any STALE. Read each STALE against its prose: requote a changed
  message, or fix the spec entry if the book's own edit moved. A new
  quote with no spec entry also fails, so you add its edit when you add
  the quote. The probe is report-only like `tip pyright-review`, and
  joins no gate.
  `tip version-pins` (`tools/version_pins.py`, 2026-10-14) lists every
  pin behind the installed `ty`: the chapters, Solutions, CLAUDE.md, and
  the coding-style skill's two copies. `tools-upgrade` prints that list
  at the end of its run. `tip version-pins ARGS=--write` rewrites the
  stale pins; run it after the probes pass and never before, since a
  bumped pin asserts that someone re-checked the claim on that version.
  Chapters 46-47 and Solutions 43 pin five behavior claims to a
  ty version ("under `ty` 0.0.82"; `grep -rn '0\.0\.[0-9]' Chapters
  Solutions` finds them): the `type`-alias probe (46), the
  chained-`supply()` order and the `Never`/`Unknown` asymmetry, the
  `nested_handle.py` reveal, and the `fork(bad)` reveal (47), and the
  `float | Unknown` without `@final` (Solutions 43). Re-probe on each
  upgrade and update those version strings; the alias probe is a
  scratch generator annotated with a `type X = Depend[...]` alias whose
  `yield from need(Undeclared)` must still draw `invalid-yield`. The
  Since 2026-09-26 `utils/record.py` is a dual-form decorator (two
  `@overload`s, `cls is None` branch) under `@dataclass_transform`, and
  `ty` 0.0.82 reads both forms as frozen data classes; re-probe that
  too: a scratch `@record(slots=False) class Q: x: int` must still
  draw `invalid-argument-type` on `Q("bad")` and `invalid-assignment`
  on `q.x = 4`, and a bare `@record` class the same. If the called form
  loses either, every Stateless Ability in chapters 46-47 and the
  Memento version-skew listings are unchecked.
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
  `float | Unknown`. A sixth claim, Solutions 24 saying `ty` had no
  rule for instantiating an abstract class, was retired by 0.0.82,
  which added the rule.
- **A Stateless upgrade is a book-wide event too.** The libraries the
  listings import (`libs_check.LIBRARIES`: Stateless, numpy, hypothesis,
  time-machine) sit in the same dev group as the tools, so
  `tip tools-upgrade` moves them along with `ty` (`uv lock --upgrade`
  upgrades everything), and their constraints are floors. `tip
  tools-status` (read-only, no gate) says when a release is waiting,
  for them and for uv and the tools, and notes a library that moved
  since the last stamp. Stateless was 0.6.1 on 2026-09-17, the
  newest on PyPI since 2025-11-11; work on its repository that has no
  release is invisible to uv, and the book does not track it, because a
  reader installs the PyPI release.
  Take a Stateless release alone, never alongside a `ty` bump, so a
  failure has one cause: `uv lock --upgrade-package stateless`, then
  `uv sync`. Then, in this order: `tip sweep`; the five version-pinned
  probes above, since the revealed types come from Stateless's
  annotations as much as from `ty`'s inference; the two quotes that
  list the library's overloads verbatim (nine for `supply()` in
  Chapters 47, four for `fork()` in Solutions 47), which a new overload
  makes stale with no gate reading message text; and one
  `verify-claims-opus` agent each over Chapters 46 and 47 and their
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
  added or removed, and run `tip pyright-review`.
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

## Probe: `record(cls)` on a `type[E]` parameter

Moved from the root `CLAUDE.md` (2026-09-29).

  Separately, `ty` 0.0.82 mistypes a direct call to a
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

## Probe: a `type()`-built class checked against `EventMaker`

Added 2026-09-29, when chapter 17 dropped its two `cast(EventMaker, ...)` calls.

  `ty` 0.0.84 reads a `type(name, (Event,), {"__init__": init})` call
  whose namespace is a dict literal, takes the constructor from `init()`,
  and checks the class against the `EventMaker` alias
  (`Callable[[int, int], Event]`). Since 2026-10-13 the call lives in
  one place, `make()` in chapter 17's `events.py`, which
  `eager_event_classes.py` and `greenhouse.py` import. So `make()`'s
  `return new_cls` passes with no cast, and chapter 17's "A Family of
  Generated Classes" says `ty` verifies the signature, where a cast
  would state it unchecked. Re-probe on each `ty` upgrade: in a scratch
  copy of `events.py` in `build/examples/17_*/`, add a third parameter
  `x: int` to `init()`. It must draw `invalid-return-type` on
  `return new_cls` with an `info:` line naming the unexpected extra
  parameter `x`. The unedited listing must stay clean. If `ty` stops
  following the call, the listings fail the gate (the class becomes an
  unknown type that is not an `EventMaker`), and the fix is to restore
  the cast and the paragraph's old wording. If `ty` still accepts the
  listing but misses the extra parameter, the gate stays green while
  the prose turns false. Pyright gives the class `Event`'s
  three-argument constructor and rejects `make()`; that is one
  `pyright_baseline.txt` entry in `events.py` (three before the move,
  one in `eager_event_classes.py` and two in `greenhouse.py`).

## Probe: a misspelled keyword through `Unpack[TypedDict]`

Added 2026-09-29, with chapter 08's "Typing `**kwargs` with a `TypedDict`".

  `ty` 0.0.84 does not check a keyword's name against an unpacked
  `TypedDict` when the key is optional. In a scratch file in
  `build/examples/08_*/`: `class TD(TypedDict): fill: NotRequired[str]`,
  `def f(**kw: Unpack[TD]) -> None: ...`, and the call `f(fil="*")`.
  `ty` reports nothing; Pyright reports `No parameter named "fil"`
  (`reportCallIssue`). Keep `fill` optional in the probe: with a
  required `fill`, `ty` reports the missing argument, which hides the
  question. Chapter 08's `#typed-kwargs` section says, pinned to
  `ty` 0.0.84, that `ty` accepts the misspelled call. The day `ty`
  reports it, rewrite that paragraph (the checkers then agree, and the
  sentence about `fil` becoming an extra key in `style` at run time is
  the part that stays) and drop the version string.
  If `ty` keeps accepting it, bump the version string to the new release.

## Probe: a subclass under a bare `ClassVar` declaration

Added 2026-10-11, when `ty` 0.0.86 started reporting half of what
chapter 09 said it missed.

  Chapter 09's "A Base Class Declares, a Subclass Supplies" pins to a
  `ty` version what the checker enforces of `sides: ClassVar[int]` in a
  base. On 0.0.87: a subclass `sides = "four"` draws `invalid-assignment`
  against the declared type; `sides: ClassVar[str] = "four"` draws
  `invalid-attribute-override`; `sides: ClassVar[bool] = True` draws
  `invalid-mutable-override` (new in 0.0.87; on 0.0.86 it passed, and
  the chapter named Pyright's `reportIncompatibleVariableOverride` and
  `ty` issue 2158 as the contrast); and a subclass with no `sides`
  draws nothing. Probe all four in a scratch copy of
  `required_classvar.py` in `build/examples/09_*/`. The day a missing
  value is reported, rewrite the paragraph's "One mistake passes the
  checker" and drop the version string; otherwise bump it.

## Pyright: a periodic review, never a gate

`ty` is the only checker the gates run. Pyright is a pinned dev
dependency with its config in `pyproject.toml` (`[tool.pyright]`), and
its value is the list of places where it disagrees with `ty`, kept in
`tools/data/pyright_baseline.txt`. `tip pyright-review` runs it over
both extracted trees and prints only the delta: NEW for a diagnostic
the baseline lacks, GONE for one that no longer fires. It exits
nonzero on NEW. `tip pyright-accept` rewrites the baseline once every
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
(a NEW entry is a fresh disagreement worth a sentence), after `tip
tools-upgrade` moves pyright (GONE means pyright caught up, NEW means a
new strictness), and after a `ty` upgrade (a disagreement that
disappears because `ty` now reports it too is a listing that may need
an ignore).
