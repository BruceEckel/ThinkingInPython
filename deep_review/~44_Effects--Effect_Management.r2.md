> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 44_Effects--Effect_Management, second review (2026-09-29)

This run follows the completed review of 2026-09-25 (`~44_Effects--Effect_Management.md`)
and the eight commits made to the chapter since then.
Nothing here needs your decision, so the file has no live blocks.
The earlier review's applied list and its four declined items were read first, and none is raised again.

What I checked:

- Every sentence about another chapter, against that chapter as it reads today:
  18 (242,785 calls against 26), 19 (`async_mechanics.py`), 20, 30 (`recolored()`, `Thermometer`, `announce()`),
  32, 34, 40 (`double()`, `withdraw()`, the captured `factor`), 42 (*Total Function*, `@safe`),
  43, 46 (`audit_log.py`, the `Success[None]` diagnostic), 47 (`ask_tell_stateless.py`), and both appendices.
- The Solutions' checker claims, on `ty` 0.0.84:
  `CoroutineType[Any, Any, float]` is what `ty` reveals,
  and a `tell()` that returns a `str` draws `invalid-argument-type` at the `greet(...)` call.
- The external claims, on the web:
  Flix writes `Unit \ {Ask, Tell}` and calls `Ask.ask(...)` with no `do`;
  Pact's README shows `needs` and `using`; Lumen's page shows `bind effect` and `.lm.md` sources;
  `eff` describes itself as algebraic effects for Python.
- `tip verify-ch CH=44` passes 24 of 24.

## Applied directly

Damage from the 2026-09-27 fix triage.
Five "Here is ..." sentences were cut as metadiscourse, and three of them carried facts the chapter stated nowhere else.
Each fact is back, in a sentence that states content.
These reverse part of a cut you approved, so they are the edits to check in the diff.

- "Native Effect Management": the Koka listing had no language name before it, and the link to Koka was gone,
  while later prose says "Koka's Effect row" and "In Koka".
  Added "The first is Koka, a research language with native Effects.
  Its greeting program has the same `ask` and `tell` as `ask_tell.py`:".
- "Library Effect Management": the Scala listing had no introduction, and nothing said ZIO is a Scala library or gave its link,
  while the prose after it says "the ZIO runtime".
  Added "ZIO is such a library, for Scala. In ZIO, "Hello, World!" is a description first and a run second:".
  The second sentence also tells the reader that the program changed from the greeting to "Hello, World!",
  which "All of that, to print one string" relies on.
- "Return a Result Type": with the sentence about `result.py` and `safe.py` cut,
  "If you decorate the original `slope()`" named no decorator until after the listing.
  Now "with that chapter's `@safe`".
- "Two Phases", last line: the triage rewrite "Effect management systems replace it" was lowercase and plural,
  where the chapter writes "Effect Management System" everywhere else. Now "An Effect Management System replaces it."
- Closing roadmap: with "The next three chapters build the library version:" cut,
  "supplies the mechanism" had nothing to be the mechanism of. Now "supplies the mechanism a library needs".

Damage from the prose passes:

- "Effect Management Systems" opened with "Return to the failing test from the chapter's opening",
  and then said nothing about the test.
  The original second sentence was "Most functions in most programs have that hidden life",
  where "that" tied the test to the claim; a pass rewrote it and the tie went.
  The opener is now "The helper behind the failing test in the chapter's opening is the ordinary case."

Corrections:

- "Effect Management for Python?": "In Python, no tool reports the call" is contradicted by the book.
  Appendix B's checker maps `builtins.print` to `Console` and reports a declared row that leaves it out.
  Now "neither Stateless nor the type checker reports it", which is the claim the paragraph needs.
- Same section: the chapter pointed to Appendix A for "an analysis of the tool" and never mentioned Appendix B, which builds it.
  Added one sentence linking An Effect Checker, in the words of that appendix's opening.
- Same section: "`async` succeeded because it arrived with the language" reads as "was there from the start".
  `async def` arrived in Python 3.5. Now "arrived as part of the language: the interpreter enforces it".
- "[Concurrency] opened with the same demonstration" is now "gives", present tense.
  I checked the claim: `async_mechanics.py` prints `coroutine` before any "started" line.

Solutions:

- Exercise 5: the listing changes `sum(... for ...)` to `sum([... for ...])`, and the prose never said why.
  A reader who adds `await` and keeps the generator expression gets an asynchronous generator:
  `ty` reports `no-matching-overload` and the call raises a `TypeError` (both probed).
  The first paragraph now names the brackets as one of the four forced changes.
  Before, its four were hard to count, since the first was a consequence and not a change.
- Exercise 5: "The Effect travels outward automatically" contradicted the paragraph above it,
  in which you make each change by hand. Now "one caller at a time ... and you cannot leave a caller out".
  "Welded to the call site" is now "fixed at".
- Exercise 3: the exercise asks which of the three conversions applies to the exceptions, and the answer covered two.
  Added that a `Result` applies to both as well.
- Exercise 3: "that pairing is what makes it interesting" cut; "wearing a design pattern" is now "inside a design pattern".
- Exercise 1: two imperative-plus-consequence sentences now state the condition,
  and the `tell()` sentence names the diagnostic and says why it appears at the call.
  The `Console` docstring is gone from the listing; the prose under it says the same thing.
- Exercise 2: "Three of five is the number worth sitting with" is now "Three of the five never use the `Log` they name."
- Exercise 4: "that is the whole of what `slope()` is ever supposed to do" is now "Only the division remains."

## Considered and declined

- The TypeScript listing uses `Context.Tag`, which Effect 4 removes (`Context.Service`, with the arguments in a different order).
  Effect 4 is at release candidate 118 as of 2026-09-28 and the stable line is still 3.x, so the listing is correct today.
  Revisit when 4.0 is released; the change is to the `class Tell` declaration alone.
- The introduction says a system that verifies purity "is an *Effect Management System*",
  and "Tracking and Management" later calls that much *Effect tracking*, one part of three.
  The introduction is a first approximation, and the later section says "The first item can stand alone."
  Tightening the introduction would put the three-part definition ahead of its motivation.
- "*Total Function*" is italic here though chapter 42 introduces the term.
  The sentence is a definition in its own right, with a link, for a reader who skipped chapter 42.
- "Catching by hand covers exactly the exceptions you know a callee can raise" and
  "looks exactly like one that computes nothing": both uses of "exactly" state a precise match, so both stay.
- The C++ and Java paragraph calls both mechanisms "exception specifications".
  Java's name is checked exceptions, but the paragraph's claims (written by hand, never inferred, widened to avoid the work,
  C++ reduced to `noexcept`) hold for the pair as described.
- No exercise covers the description/action split of "Library Effect Management".
  Exercise 5 covers it through `async`, the one form of it the reader can run before chapter 46.
