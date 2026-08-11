When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/47_Stateless_in_Practice.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty` (0.0.70) and ruff are clean on `build/examples/47_Stateless_in_Practice`,
the three tests pass, and `run_examples.py` runs every script clean.
The library claims were verified against the installed `stateless` 0.6.1
source, not its docs: `Ability.__iter__` matches the stripped version the
chapter prints; `handle()` raises a `ValueError` at decoration when the
handler parameter is unannotated; `catch()` matches yielded values by
`isinstance` and a handler's driver passes error values upward untouched;
`throw()` is declared `Try[E, Never]`; `catch_all` lives in
`stateless.effect` and the package root does not export it; `supply()`
carries the one-through-nine overloads over a variadic implementation and
matches instances by `isinstance`; `fork()` has the four overloads the
chapter counts and runs the Effect with `run()` inside the worker;
`retry()`/`repeat()` add `Need[Time] | Async` and only `spaced()` and
`recurs()` exist; `RetryError` declares an `errors` attribute that nothing
assigns, so the chapter's `args[0]` rough edge is right; `memoize()` wraps
the Effect in a replaying `Memoize` object over `lru_cache`;
`Files.read_file()` opens and closes within one call. The silent-`None`
trap was probed at runtime: six tosses from a five-value script make
`run()` return `None` with no exception (the handler's `StopIteration` is
caught by the driver's own except clause), and the indexed variant raises
the `IndexError` the prose names. Every quoted `ty` diagnostic was reproduced
verbatim on 0.0.70 with matching line and column numbers
(`bakery.py:34:23`, `partial_handling.py:18:9`, the ten-argument `supply`
overload failure, the `Success[str]` report rejection), and every
version-pinned inference claim re-probed: the direct Ability yield still
reveals `Unknown`, nested handlers still infer `Unknown` while named
stages recover `Depend[Ask, None]` / `Success[None]`, both catch/supply
orders infer the same result union while both nested forms fail as
described, and the stale `catch(Crashed)` after `retry()` still
type-checks into a dead `str | Crashed` branch. The ZIO `divide` example
is verbatim in ZIO's Defects reference doc, and the defect/`Cause`/
`sandbox()` description matches it. Cross-references were checked at both
ends: every 44/45/46 anchor resolves and the content it names
(`ask_tell.py`'s two-parameter signatures, the ZIO accessor object,
`hand_driven.py`'s trace, `two_way_generator.py`'s `drive()`,
`score()`/`Recorder`/`test_greeter.py`, `student_pairs.py`'s `seed`,
chapter 27's `GameElementFactory`/`KittiesAndPuzzles`) says what this
chapter claims. Nothing in `deep_review_db.md` touches this chapter.
One finding needs a decision (below); the rest was applied directly.

## Applied directly

- Three "under `ty` 0.0.69" references are now 0.0.70; each claim they pin
  was re-probed on 0.0.70 before the bump (all behave identically).
- Intro: "collects every tool in one table" is now "in one place" (The
  Toolkit has three tables).
- Intro bullet: "code they never edit" is now "code they do not edit"
  ("never" watch list).
- Accessor paragraph: "That is what the `answer: str` inside `ask()` is
  doing" is now "The `answer: str` inside `ask()` does that job"
  (pseudo-cleft).
- "which is what `hand_driven.py` ... did" is now "which
  `hand_driven.py` ... did"; same cut for "which is what the `Never` in
  its type records" ("is what" deletion test passes in both).
- "has to change" / "has to sit" are now "must change" / "must sit"
  ("has to" watch list).
- `wallet.py` prose: "two functions closed over one `Cell`" is now
  "sharing one `Cell`"; the handlers read a module global, and a global
  reference is not a closure.
- `scenarios.py` trace: "`need(Encyclopedia)` ... never ran" is now
  "did not run"; "`DeadWire.latest()` raises before printing" is now
  "raises `Unavailable` before printing" (house rule: raise names its
  object).
- Cast section: "Printing was never in the engine to intercept" is now
  "The engine holds no printing to intercept" (parallels "the pipeline
  holds no output of its own" earlier).
- Retry section: "the program does not build" is now "`ty` rejects the
  `run()` call" (Python has no build step; the rejection was probed and
  matches the partial-handling diagnostic shape).
- Limits section 5: "constructing a dependency can never be an Effect" is
  now "cannot be an Effect", matching the bakery section's own "a
  constructor cannot be an Effect".

## ty 0.0.70 closes the PEP 695 alias gap this chapter cites

The sentence in Supplying a Whole Cast,
"The five-way union appears in full rather than as an alias, for the
reason given in [Retrofitting an Effect](46_Stateless.md#retrofitting-an-effect)",
points at chapter 46's caveat that a `type X = ...` alias as a generator
return annotation disables `ty`'s invalid-yield check.
On `ty` 0.0.70 that gap no longer reproduces: the standing probe from
`CLAUDE.md` (a `type Greeting = Depend[Need[Console], None]` alias over a
body that yields an undeclared `Need[Log]`) now reports `invalid-yield`
through the alias, identical to the spelled-out form.
I left the listing itself alone: the repo instruction says not to fold
that union into an alias, and a gap that closed in one release can
reopen in another, so the spelled-out unions stay right either way.
What does need a decision is the prose, because 46 owns the caveat's
wording and is under concurrent review, so I did not race it.
Proposed change, if this block stays live: reword this chapter's
sentence to one that stays true whichever way 46's caveat goes, e.g.
"The five-way union appears in full rather than as an alias, the
practice [Retrofitting an Effect](46_Stateless.md#retrofitting-an-effect)
recommends." Whoever settles 46's caveat should also update the
`CLAUDE.md` trap entry and the `stateless-partial-handling-ty-support`
memory note, which both still describe the gap as current; the probe
result to record is: `ty` 0.0.70, alias form now reports `invalid-yield`,
identical to the spelled-out form.

[] Reject

## Considered and declined

- **The five numbered limit headings are sentence-case clauses** ("2. The
  checker can give up quietly") while the book's headings are otherwise
  title-case noun phrases. Read as deliberate: they are a list of claims,
  and two in-text links name one of them verbatim mid-sentence, where a
  title-case noun phrase would read worse. Left as is.
- **`wallet.py` could build its handlers from a closure factory**
  (`def cell_handlers(cell: Cell)`) to literally match the "a test builds
  its own pair from a fresh `Cell`" suggestion, the way `at()` does for
  the clock. The listing is already the longest in its section and the
  prose fix ("sharing one `Cell`") removes the inaccuracy at no size
  cost. Left as is.
- **Exercise 11's "Repeat it with `catch_everything.py` in the build"**
  is compact to the point of terseness, but the exercise is
  understandable and the solution file disambiguates it. Left as is.
