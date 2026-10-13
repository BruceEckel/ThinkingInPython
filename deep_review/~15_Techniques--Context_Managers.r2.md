> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 15_Techniques--Context_Managers (2026-10-13)

This review has no live blocks.
I ran every extracted listing directly on `uv run python` 3.15.0 and compared each run with its `#:` markers.
All of them match, and `pool_contention.py` printed a peak of 2 on three runs.
I probed these claims at runtime: the single-use `AttributeError`, that `suppress` is a class,
that `suppress()` with no arguments lets a `KeyError` through,
and that a comma-separated `with` never constructs the managers after a failing one.
I probed `ty` 0.0.86 for three diagnostics:
`invalid-return-type` when an `__exit__()` annotated `-> None` returns a value,
`too-many-positional-arguments` for the Solutions exercise 2 near-miss, and `invalid-argument-type` for the exercise 6 near-miss.
The 3.15 `ContextDecorator` change for generator functions is confirmed against the 3.15 `contextlib` source and its documentation's "Changed in version 3.15" note.
An unlimited stand-in pool printed a peak of 8 on three runs, which supports the chapter's "a peak of eight".
Chapter 19 uses `async with` for `TaskGroup`, a lock, and a semaphore, as this chapter says.
`tip verify-ch CH=15 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.

## Applied directly

Chapter:

- "A Basic Context Manager": "the message it prints names nothing useful" now says the message is about a missing `args` attribute and gives no hint of the real cause.
- "The Protocol": the longhand-`__init__()` sentence ended on "reads as ordinary Python", which a dataclass also does.
  The sentence now says the constructor sits in the listing beside the two protocol methods.
- "Guaranteed Cleanup": "the managers listed after it are left alone" (passive, vague) now says the statement stops before Python evaluates them, which a probe confirmed.
- "Guaranteed Cleanup": "Python keeps `original`" named a string as if it were a variable.
  The sentence now says Python keeps the `KeyError` as `error.__context__`, the chaining it applies when an `except` block raises an exception.
  The old "a nested `except`" was vague.
- "The `expected` Manager": "The block is expected to raise" is now "The block under it should raise", to clear the passive.
- "Context Manager as Decorator", teaching: the chapter said the parentheses in `@banner("report")` matter without saying what happens when they are missing.
  I added the near-miss: `report` becomes a manager object, calling it raises a `TypeError`, and the type checker flags the decorator line.
- `decorated_generator.py` prose: the context closed "after the generator's last `yield`", which is imprecise.
  It now closes "when the generator finishes or its `close()` method runs", matching `gen_inner()` in 3.15's `contextlib`.
- `decorated_generator.py` prose, teaching: "stays open each time the body resumes" was replaced.
  The new sentence says the banner stays open while the generator waits at each `yield`, so the consumer loop's `got` lines print inside the banner.
  That is the mechanism the output shows.

Solutions:

- Exercise 2: the closing "Note the double parentheses" paragraph repeated the solution's opening paragraph.
  It is cut to its one new point: a `*types` signature would accept the unparenthesized form, the design `contextlib.suppress` chose.

## Considered and declined

- The 3.15 change also keeps a `ContextDecorator` context open across `await` in a decorated coroutine function or async generator.
  Coroutines are not taught until the async section and chapter 19, so the decorator section stays with generators.
- An exercise building the stale-reference guard from "What the Skeleton Leaves Out" would need a `Connection`-specific pool, or a forwarding *Proxy* from chapter 26, to keep "invisible to every `with pool.lease()`" true.
  Either one is larger than the chapter's other exercises.
- "write `__exit__()` methods that fail only for reasons worse than the original exception" reads as unusual advice, but it is a judgment the chapter makes deliberately, so it stays.
- `demo_expect.py`'s `[1]` names `TypeError` in a tuple although only a `ValueError` occurs.
  The call exists to show the tuple form, and the prose says so.
- Everything in the 2026-09-29 review's declined list still holds, and none of it is re-raised here.

## For the session

- `tip positional` reports two NEW hits in this chapter, both re-hits of sentences I reworded whose old forms were in the baseline (now listed as stale):
  line 683 "the first `next()`" (a runtime call) and line 716 "the `for` loop" (the consumer loop; "asks for the first value" disambiguates it from the loop inside `rows()`).
  Both are keeps; `tip positional-accept` after a read.
- Solutions line 98 "were given" (Vale passive) quotes Python's own `TypeError` message and stays.
