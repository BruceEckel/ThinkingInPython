> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 46_Effects--Stateless, third review (2026-10-13)

This review follows `~46_Effects--Stateless.r2.md` (2026-09-29) and the
listing-design, fault-search, and outside-review commits made since.
It has no live blocks.

What I checked:

- Every sentence about Stateless against the installed 0.6.1 source,
  all twelve modules (`__init__`, `ability`, `async_`, `console`, `effect`,
  `errors`, `files`, `functions`, `handler`, `need`, `schedule`, `time`).
- Type claims the prose makes without a quote, by `reveal_type()` probe on
  `ty` 0.0.86: `supply(Log())(greet_all)` and the layered `supply(Console())`
  around it, `fallback(chosen)`, `supply(screen)` on an annotated local
  (`Handler[Need[Terminal]]`), the `unused-awaitable` warning on a bare
  `run_async()`, the bare `greet(name)` in `greet_all()`
  (`invalid-return-type`) and in `greet_logged()` (silent), the
  `invalid-yield` after deleting `| Need[Log]` from `greet_all()` or
  `KeyError` from `announce()`, and the alias probe
  (`type Greeting = Depend[...]` still draws `invalid-yield`).
- The Solutions quotes made against edited copies (exercises 7 and 10),
  rerun on 0.0.86: both match line for line. Exercise 1's near-miss
  (`supply(scripted)` without `as_type()`) draws `invalid-argument-type`
  at both `run()` calls and still prints `['Hello, Bob!']`.
- Runtime claims by script: a non-frozen data class subclassing `Time`
  raises `TypeError: cannot inherit non-frozen dataclass from a frozen one`,
  and `run(success(42))` against a plain call (below).
- Cross-chapter claims: chapter 44's `ask_tell.py` and its exercise 2,
  its exception-specification paragraph, and chapter 47's `outcome()`
  boundary function in Composing a Program.

`tip verify-ch CH=46 ISOLATED=1` passed 27 of 27 before and after.
`tip prose CH=46` shows no new stranded-preposition, watch-word, or
positional hits.

## Applied directly

- Built-in Dependencies: the `Time` bullet now names its module,
  `stateless.time`, as the other two bullets do.
- Nothing Runs Yet: "`need(Console)` builds a `Need[Console]`" contradicted
  Why `yield from`, which says `need(Console)` builds a small generator.
  It now builds a generator that yields the `Need[Console]`, and
  `yield from` passes that `Need` out of `greet()`'s body.
- Dependency Injection: "`Any` is the one type its values share" gave the
  wrong reason; every value shares `object`. The paragraph now says why
  `object` fails (probed: `ty` rejects `return DI_CONTAINER[t]` with
  "expected `T@get`, found `object`") and that `Any` passes as a `T`.
- Churn in Every Signature: "Java's checked exceptions, which failed this
  way" left "this way" to the reader. It now states the failure chapter
  44's linked paragraph describes: an exception added three levels down
  meant editing every signature above it.
- Waiting on a Coroutine: "`yield from wait()` accepts any awaitable"
  attributed the argument to the `yield from`. Now `wait()` accepts it, and
  `yield from wait(...)` produces the value. "An `Async` request carries a
  coroutine" became "an awaitable", matching `Async.awaitable`.
- A Clock That Never Waits: "`waited` is a field because `Time` is a frozen
  data class" gave a reason that does not hold (an ordinary subclass of
  `Time` can assign `self.waited`; probed). The sentence now says why
  `Instant` is a record: a data class that inherits from a frozen one must
  be frozen too.
- Where to Call `run()`: "four to five orders of magnitude" overstated the
  ratio. Measured here on Windows, `run(success(42))` took 477 to 809
  microseconds against 33 to 35 nanoseconds for a plain call, ratios of
  14,000 to 24,000; the first review's Linux figures give about 2,400.
  Now "three to four orders". The 650 microsecond figure sits inside the
  measured range and stays.
- Emptying the Channels: "once the last Ability is answered" became "once
  a handler answers the last Ability" (Vale passive, natural actor).
- Solutions exercise 11: "turns the coin flip into a diagnostic" called a
  deterministic argument-order rule a coin flip. Now "the silent choice",
  the exercise's own phrase.
- Solutions exercise 4: "the case for which `as_type()` exists"
  overclaimed; the chapter uses `as_type()` for every interface supply.
  It now says why this case needs it: a bare `supply()` sees one static
  type for the object.

## Considered and declined

- "produces nothing" (The Effect Type, Errors Propagate) beside "produces
  `None`" (Declaring a Dependency): r2 chose the second deliberately in one
  place, and both read correctly where they stand.
- "`catch()`, `throws()`, and `supply()` return decorators over functions
  for the same reason" is a design-intent claim the source neither
  confirms nor contradicts; left as written.
- Vale's "is bound" passive on "The first type parameter is bound to
  `Ability`": "bound" is the type-variable term, not a passive.
- The `run()` timings were taken while other review agents loaded the
  machine. The range brackets the chapter's figure, so no number changed.

## For the session

- `tip prose` reports a stale `internal-names` baseline entry,
  `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`,
  outside this chapter.
- A first timing script (30,000 `run()` calls in one process) printed
  nothing for five minutes and was stopped; a 600-call rerun finished in
  seconds. It fits the Windows event-loop creation hang in `CLAUDE.md`
  and is not a chapter finding.
