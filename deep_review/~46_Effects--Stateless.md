When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Deep review of chapter 46, run after the elements-of-style, literal,
positive, straighten, cohesion, and antecedents passes (one commit each on
`claude/prep-46`). Every sentence about Stateless's behavior was checked
against the installed 0.6.1 source (`effect.py`, `handler.py`, `need.py`,
`async_.py`, `console.py`, `files.py`, `time.py`, `functions.py`); the
chapter's three absence claims (no registration, no container, `Time` has
no special status) hold. Type claims were re-probed under `ty` 0.0.83:
`supply(Log())(greet_all)` still reveals `Depend[Need[Console], None]`,
`Depend[Console, None]` draws `invalid-type-arguments`, the annotated
local `screen: Console = Terminal()` narrows to `Terminal`, and dropping
`KeyError` from `announce()` draws `invalid-yield` at the `yield from
score(name)` line. Solutions 46 exercise 7's silent drop was rerun: `ty`
reports nothing and the script prints only the log entries. No relative
chapter reference ("previous chapter", "last chapter") remains in either
file. The prose pass ran without the global `~/.claude/CLAUDE.md` watch
list, which the cloud session does not have; `banned_phrases.py`, Vale,
and the repo's rules stood in for it.

**Alias probe (`ty` 0.0.83).** A scratch generator annotated with
`type Greeting = Depend[Need[Console], None]` whose body does
`yield from need(Undeclared)` still draws `invalid-yield`
("expression of type `Need[Undeclared]`, expected `Need[Console]`"),
identical to the written-out signature. The chapter's "Under `ty` 0.0.82"
string stays as written, for the book-wide version bump.

## Applied directly

- The Effect Definition: "`E`'s bound is `Exception`, so a class that
  subclasses both satisfies each bound at once" was a non sequitur after
  "two bounds ... do that instead." It now says the bounds do not exclude
  each other, and that such a class would count as a failure at runtime
  (the driver matches `case Exception()` first, in `run_async()` and in
  `Handler.__call__`).
- Forgetting to Supply: "an Effect whose Ability channel has narrowed to
  those two" became "yield channel", since `Exception` is not an Ability.
- Retrofitting an Effect: chapter 44's second exercise asks how many of the
  edited signatures *use* the `Log` they name, not just how many you edit;
  the description now says so.
- No Container, consequence 2: "DI has one flat registry" became "A typical
  DI container has one flat registry"; hierarchical injectors (Guice child
  injectors, scoped containers) exist.
- Where to Call `run()`: "Picking the wrong one is a runtime error rather
  than a type error" was half wrong. A bare `run_async(...)` in synchronous
  code draws `ty`'s `unused-awaitable` warning (probed). The sentence now
  names `run()` inside a coroutine as the runtime error and says what `ty`
  does with the opposite mistake.
- Turning an Error Into a Value: "the result type omits the `Console`"
  became "the result type stays as it was"; the result type never held a
  `Console`, and the contrast with `catch()` is that `supply()` adds nothing
  to it.
- Emptying the Channels: "forgetting either is a type error" contradicted
  the bullet two lines up (`error_escapes.py`: an unhandled failure is
  accepted by `run()`). It now reads "forgetting to declare either".
- Prose passes, adjusted before commit: elements-of-style's "`A` has the
  bound `Ability[Any]`" became "`A`'s bound is". The literal pass's
  duplicated handler sentence was merged, its "Every Effect here is an
  object a driver answers one `send()` at a time" (a restatement of the
  line above) became "Every Effect in this chapter is such a generator",
  its `greet`/`bound` reveal sentence was rewritten, and exercise 10's
  "say where each failure surfaced" was restored to match Solutions 46.
  The positive pass's "runs once something drives it" (which reads as "runs
  one time") went back to "runs nothing until something drives it", its
  "asks one thing, an answer for every `Need`" became "rejects every
  unanswered Ability except `Async`" (true of `Effect[Async, Exception, R]`),
  and `success()` again "builds no generator".

## `run()` cost figures are platform-specific

"Where to Call `run()`" says one machine measured `run(success(42))` at
about 650 microseconds, "roughly four orders of magnitude" above a plain
call. On this session's Linux VM (Python 3.15.0rc2, Stateless 0.6.1) the
same call takes about 44 µs and a plain `f(21)` about 0.018 µs, a ratio
near 2,400, three orders of magnitude. The 650 µs figure is plausibly
Windows, where `asyncio.run()` builds a `ProactorEventLoop`, which is
slower to set up. The point of the paragraph (call `run()` once, at the
edge) survives either number, but the sentence states one number as if it
were the cost.

I would keep a measured figure and say where it came from: "On Windows,
`run(success(42))` measured about 650 microseconds (about 45 on Linux),
three to four orders of magnitude above a plain function call." Only you
can confirm the 650 figure is still what your machine shows.

[] Reject

## Considered and declined

- `default_console.py`'s `Console` could be a `@record`; it is never
  mutated. Left as `@dataclass`: `make records` flags only frozen classes,
  and the listing's one new thing is layered handlers.
- Layering Handlers cites `greet_all()`'s types from Retrofitting an Effect,
  a later section. The link names it, and the types are readable without
  the listing, so no move.
- "Constructor injection answers the complaint ..." followed by "An EMS
  requires more" reads as though constructor injection keeps dependencies
  out of signatures. The following sentence (intermediate functions pass
  the parameter onward) carries the distinction; left alone.
