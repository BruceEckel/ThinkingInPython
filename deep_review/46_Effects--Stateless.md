> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 46_Effects--Stateless, second review (2026-09-29)

This review follows the one completed on 2026-09-25 (`~46_Effects--Stateless.md`)
and the nine commits made to the chapter since then.
Nothing here needs your decision, so the file has no live blocks.

What I checked:

- Every sentence about Stateless against the installed 0.6.1 source
  (`effect.py`, `handler.py`, `need.py`, `async_.py`, `functions.py`,
  `time.py`, `console.py`, `files.py`, `schedule.py`).
- Every quoted `ty` diagnostic in the chapter and in Solutions, rerun on
  `ty` 0.0.84 against the listing or the edited copy it describes.
  All eleven match.
- The type claims the prose makes without a quote, by `reveal_type()` probe:
  the layered `supply()` types, `fallback(chosen)`, `supply(screen)` on an
  annotated local, `Depend[Console, None]`, `return success(n)` inside a
  generator function, `as_type()` against `cast()`, the `unused-awaitable`
  warning, and the two dropped-`yield from` cases.
  All hold on 0.0.84.
- The alias probe from the `tool-upgrade` skill.
  A generator annotated with `type Greeting = Depend[Need[Console], None]`
  still draws `invalid-yield` on `yield from need(Undeclared)`.
- Runtime claims by script: a class that is both an `Ability` and an
  `Exception` counts as a failure, a structural double for the library's
  `Console` draws `MissingAbilityError`, and `inside_a_loop.py` prints the
  `RuntimeWarning` on standard error.
- The diff from the first review's closing commit to `HEAD`,
  for damage left by later passes.

`tip verify-ch CH=46` passes 24 of 24, and Vale reports nothing on either file.

## Applied directly

Damage from edits made after the first review:

- Forgetting to Supply: the fix-triage cut "The expected type in that message
  names two things that come later in this chapter:",
  which left two bullets with no subject and "those two" with nothing to point at.
  The lead-in is back in a form that states content:
  "The expected type in that message names `Async` and `Exception`:".
- Declaring a Failure with `@throws`: the same triage cut
  "`ty check scores.py` reports what it becomes:",
  so the quoted diagnostic followed the prose with no source.
  The sentence now ends "as `ty check scores.py` shows:".
- Declaring a Dependency: commit 89350d18 changed "produces nothing" to
  "returns `None`". Calling `greet()` returns a generator, as Nothing Runs Yet
  says two sections later, and the alias table's verb is "produces".
  Now "produces `None`", which still ends on what happens.

Corrections:

- Retrofitting an Effect: the version pin reads `ty` 0.0.84.
  The alias probe holds on that version.
- An Interface Instead of a Base Class: "fails with a `MissingAbilityError`
  whatever static type `as_type()` gives it" described a call the type checker
  rejects. `as_type(Console)(double)` draws `invalid-argument-type`
  (probed), and the runtime failure needs a `cast()` to reach.
  The passage now says both.
- Catching Is Not Handling: "`throw()` raises the exception in the innermost
  suspended frame, where the `except` clause runs" put the `except` clause in
  the wrong frame. The innermost frame belongs to the Effect the `yield from`
  delegates to, and the exception propagates out to the `except`.
  The passage now says that, names `throw()` as the generator's method
  (Stateless exports a `throw()` function too, which chapter 47 teaches),
  and links chapter 45's section on `throw()` reaching the innermost generator.
- Where to Call `run()`: "one of the few mistakes in this chapter that the
  type checker cannot report" undercounted.
  The chapter shows at least seven: a discarded Effect, a spent Effect,
  an inherited method in a double, argument order in `supply()`,
  an `except` behind a handler, a default that hides a missing binding,
  and this one. The clause now gives the reason instead of a count.
  Solutions exercise 9 made the same claim and got the same fix.
- The Effect Type: "Each one fills in `Never` for an unused type parameter"
  was true of two aliases; `Success` fills in two. Now "the type parameters
  it leaves out".
- The Error Channel: the `Result` link pointed at chapter 42's section on
  `@safe`. It now points at "A Result Type", and `@safe` carries the link to
  "Turning Exceptions into Results".

Teaching:

- Declaring Is Not Handling: added the near-miss for `@throws`.
  The decorator lifts the types it names, and an exception of any other type
  leaves as an ordinary raised exception with no signature declaring it
  (probed: `@throws(KeyError)` on `read_score()` reveals `Try[KeyError, int]`
  and `"Bob"` raises a `ValueError` out of `run()`).
  Chapter 47 covers a body with no `@throws`; nothing covered a `@throws`
  that names too few.
- Waiting on a Coroutine: the opening sentence said `Async` appeared
  "inside error messages, where `run()` answers it", which reads as though
  the answering happens in the message. Split into three sentences.

House style:

- `unsupplied.py` used `try`/`except`/`print(e)` to show the exception.
  It now uses `with expected(MissingAbilityError):`, which keeps the call
  visible for the quoted diagnostic. The marker gained the `[Type]` prefix
  and the quote moved from line 7 to line 8.
- "ships" (two uses) became "provides".
- "built-in Ability" became "builtin", matching the chapter's heading and
  its four other uses.
- Solutions exercise 6: `Console` and `Clock` carried `@dataclass` with no
  fields. Both are ordinary classes now, as in the chapter's `greeter.py`.

Solutions:

- Exercise 8: "`retry()`'s type is `Callable[P, Effect[...]] ->
  Callable[P, Effect[...]]`" gave the decorator's type as `retry()`'s.
  The exercise words it correctly, and the solution now matches.
  "Hands back a function of the same signature" was also false:
  `retry()` adds `Need[Time]` and `Async` and replaces the error with
  `RetryError`. The paragraph now says the arguments stay and the Effect's
  type widens.
- Exercise 11: "no object satisfies both" `Protocol`s is false in general
  (exercise 4's `Recorder` satisfies two at once).
  Now "neither implementation satisfies both".
- Exercise 11: "One honest limit." became "One limit remains.", and
  "exactly this case" lost its intensifier. Exercise 8's "looks exactly like"
  became "looks the same as".

## Considered and declined

- The Effect Type says the three parameters "answer the three questions"
  chapter 44 "asked of an Effect signature". Chapter 44 states three facts
  about a ZIO signature and asks nothing. The link leads to the right
  paragraph and the list that follows is correct, so the wording stays.
- Solutions exercise 11's `Terminal` also carries a fieldless `@dataclass`.
  Removing it moves the quoted diagnostic from line 40 to 39, and that quote
  has an entry in `tools/data/quoted_diagnostics_baseline.txt`, a file the
  parallel review branches share. Left for a later pass.
- `hand_driven.py` keeps its `try`/`except StopIteration`.
  The handler prints a message of its own, so `expect()` does not fit.
- "Nothing has printed at that point, because `greet()` has suspended at the
  `yield` inside `need()`": the `yield` is in `Ability.__iter__()`, which
  `need()` reaches through `yield from`. The sentence is accurate at the
  level the section works at.
- Dependency Injection names FastAPI's `Depends` as built on constructor
  injection. `Depends` injects into an endpoint function's parameters.
  The paragraph's next sentence says "at the endpoint or the constructor",
  which covers it.
- No Container, consequence 2, cites `ambiguous_supply.py` for two bindings
  of one type live at once. `default_console.py`'s `fallback` and `chosen`
  would show separate handlers, but the cited listing does hold two
  `Console` bindings at once.
- The `run()` cost figures (650 microseconds on Windows, 75 on Linux) were
  not remeasured. Twenty review forks were loading the machine during this
  run, and a reading taken then would be noise.
- "itself" in "Nothing in the union itself" and "matches the yielded value
  itself": each draws a contrast with what follows, so both stay.
