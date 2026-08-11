[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/15_Context_Managers.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` and ruff are clean on `build/examples/15_Context_Managers`,
all 3 tests pass, and all 16 scripts run. The chapter's runtime claims
were re-verified with probes on the pinned toolchain: reusing a
`@contextmanager` manager in a second `with` raises the quoted
`AttributeError: '_GeneratorContextManager' object has no attribute
'args'` verbatim; every manager `@contextmanager` produces is an
instance of `ContextDecorator`; and `utils/exceptions.py` needs no
import for `sentinel` because it is a builtin on the pinned 3.15
(chapter 5 says so, and the probe confirms it). One probe surfaced a
near-miss the chapter did not cover: a generator that reaches a second
`yield` makes the manager raise a `RuntimeError` (`generator didn't
stop`), now taught next to the single-use caution. The structure needed
no work: the pool teaser front-loads the payoff, the sections escalate
cleanly, and "Choosing a Form" closes on guidance rather than a rehash.
No findings met the bar for a live block.

## Applied directly

- "A Basic Context Manager": extended the single-use caution with the
  loop near-miss. A reader who hits the single-use limit plausibly puts
  a loop around the `yield`; the single `yield` is enforced, and a
  second `yield` makes the manager raise a `RuntimeError` (`generator
  didn't stop`) when the block ends (verified on the pinned
  interpreter).
- Cut "The `@contextmanager` form relies on the generator and decorator
  machinery from [Decorators] and [Iterators]" after the `finally`
  paragraph: the section opener already links `23_Iterators` for
  generators, and the sentence was a dangling aside inside a paragraph
  about `finally`.
- "Wrap the `yield` in `try`/`finally` in every `@contextmanager`
  generator, without exception" drops the "without exception" pun; in a
  chapter about exceptions it can be misread as "when no exception is
  raised".
- "the cleanup runs on the way out" (under `exit_on_error.py`) is now
  "on the exception path", echoing the intro's phrasing; "unwinds them
  in reverse on the way out" (ExitStack) is now "when the block ends"
  (watch-list "the way out").
- Intro: "the borrower writes nothing to make that happen" is now
  "writes nothing to arrange it" (watch-list "happen").
- "instead of spelling it out at every use" (the `Types` alias) is now
  "writing it out" (watch-list "spelling").
- "`suppress()` with no argument suppresses nothing, because no type is
  there for the raised exception to match" is now "because a raised
  exception has no listed type to match" (expletive "is there").
- Toolkit list: "`nullcontext(value)` is a do-nothing manager that
  yields `value`" is now "whose `__enter__()` returns `value`"; the
  chapter spends two sections separating the generator's `yield` from
  `__enter__()`'s return, and this bullet used "yields" for a class
  manager.
- `emit()` explanation: "the `nullcontext` wrapper lets one `with`
  block serve both cases" said the outcome without the mechanism, and
  "both cases" collided with the three cases established one paragraph
  up. Now: "exiting a `nullcontext` does nothing, so the same `with`
  block closes the file in the `Path` branch and touches nothing in the
  other two."
- Object Pool: merged "So you can hand the same pool to several
  threads. The pool becomes the throttle..." into one gerund-subject
  sentence ("Handing the same pool to several threads makes it the
  throttle that limits concurrent use"); the old pair opened with a
  second consecutive "so".
- Ran `make reflow CH=15` over the edited prose.

## Considered and declined

- A warning that cleanup code after the `yield` (or in `__exit__()`)
  can raise an exception of its own and replace the block's exception:
  real behavior, but every cleanup in this chapter is a `print()`, the
  topic belongs with exception handling rather than the manager
  protocol, and the chapter's `finally` lesson stays sharper without
  it.
- The toolkit bullet "suppress(*exceptions) ignores the listed
  exceptions, replacing the `ignore` class above" slightly overclaims:
  `suppress` does not print what it swallowed. Left alone because the
  print is a demo artifact and the bullet's point is "prefer the
  stdlib".
- Teaching the variant `RuntimeError: generator didn't stop after
  throw()` (a generator that catches the thrown exception and then
  yields again): too niche once the main single-`yield` enforcement
  note exists.
- An exercise using `async with`: the async section is deliberately a
  bridge to [Concurrency](../Chapters/19_Concurrency.md), which owns
  the practice.
- An explicit `{#id}` anchor for "The `__exit__()` Arguments" heading:
  no link targets it, so the ugly auto-slug breaks nothing.
