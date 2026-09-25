> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Deep review of chapter 47, run 2026-09-25 in a cloud session after the six
`make rewrite` prose passes (elements-of-style, literal, positive, straighten,
cohesion, antecedents; each committed separately on `claude/prep-47`). The
prose pass ran without the global `~/.claude/CLAUDE.md` watch list, which does
not exist in cloud sessions; it used the skill's own rules, `banned_phrases.py`,
and the repo `CLAUDE.md`. No earlier `~47` review exists; `deep_review_db.md`
was read and nothing in it bears on this chapter beyond the standing "do not
narrate tool-version history" rule, which the chapter obeys.

Every library-behavior sentence was checked against the installed Stateless
0.6.1 source (`.venv/lib/python3.15/site-packages/stateless/`), and the
chapter's type claims were probed with the installed `ty` 0.0.83. Everything
checked held except the items fixed below.

## Applied directly

- Rewrite passes, corrected on review: the elements-of-style pass turned "`Obstacle.blocks()` could be named `name()`" into an ambiguous "calling its method `name()`" (now "You could rename `Obstacle.blocks()` to `name()`"); the literal pass said "the type checker limits how many actors one `supply()` call can take" (the library's nine overloads set the limit; now "One `supply()` call can type-check at most nine actors"); the positive pass deleted "it prints nothing", which sets up "Output is an Ability" (restored as "It prints nothing itself."); the straighten pass changed `midnight.py`'s second reading to "one second after it", which contradicts `LATE + timedelta(seconds=2)` (now "one second after midnight"); the straighten pass left "Two of those same four overloads accept one" with no antecedent for "one" (now "accept an Effect that declares one").
- Rewrite passes, claims they corrected and I verified: the bakery paragraph now conditions `ty`'s `run()` rejection on leaving `Oven(220)` out (the committed listing type-checks); "Three appliances, one of them reached through another Effect" is now "two of them reached through `bread()`" (`Dough` and `Oven`); the `RetryError` paragraph now states that `retry()` builds `RetryError(tuple(errors))`, so `outcome.errors` raises `AttributeError` (confirmed in `functions.py`).
- *A Clock That Crosses Midnight*: "the window for the mistake is one second wide" became "only as wide as the gap between the two reads". The listing's reads are two seconds apart, and in production the gap is microseconds; "one second" matched neither.
- *Composing a Program*: `DeadWire.latest()` "raises `Unavailable` before printing" became "without printing anything"; `DeadWire` has no print to come before. Exercise 6's "fails before printing" changed to match.
- `catch_everything.py` paragraph: "the same two handlers, and the order changes the reading" became "the same two calls in the other order"; `catch_all()` is not a handler.
- *`run()` Builds a Loop per Call*: "hundreds of times the cost of `run_async()`" became "at least fifty times the cost of `run_async()`, by the listing's own measure". The marker claims 50x; this VM measured 46x to 76x across three runs, so "hundreds" is at best machine-specific. See the `run_cost.py` block below.
- *Nothing stops an undeclared Effect*: "`@throws` lifts only the exception types it names, and `ratio()` names none" became "`ratio()` carries no `@throws`"; `ratio()` has no decorator to name anything.
- ZIO defect sentence: "There `sandbox()` can recover it" (an orphaned "There" left by the straighten split) became "`sandbox()` can recover a defect".
- *Handlers cannot capture the continuation*: "Stateless's documentation calls it an algebraic effect system" named the library explicitly ("calls the library"); "it" could have been the `Effect` monad of the sentence before.
- *`fork()` drops the error channel*: "`fork(catch_all(bad))` matches the overload ..." applied `catch_all()` to the `bad` in the listing, which is already `@fork`-decorated. Now: "Apply `catch_all()` before `@fork`: with `bad` left undecorated, `fork(catch_all(bad))` matches ...", and "returns the union" became "returns `Boom | int`". Probed with `ty` 0.0.83: an undecorated `Try[Boom, int]` function under `fork(catch_all(...))` reveals `(n: int) -> Generator[Need[Executor], Any, Task[Boom | int]]`, and `wait()` on its task reveals `Boom | int`.
- Exercise 3: "put it between solar and the battery in `controller()`" became "in the `sun_first` order"; `controller()` takes the order as an argument and contains none. Solutions 47 exercise 3 already does it this way.
- Heading "Two More Doors" became "A Second Way In and Out". The literal pass removed every door from the section's prose, leaving the heading the only figure; nothing in the book links to its anchor.

## Probes of the version-pinned claims (`ty` 0.0.83)

All three sentences that pin a behavior to "`ty` 0.0.82" still hold under the
installed 0.0.83. The version strings were left alone, per `CLAUDE.md`, for the
book-wide update that goes with a `ty` bump. Probes ran in
`build/examples/47_Effects--Stateless_in_Practice/`, inside a function with
`feed: Feed, book: Encyclopedia` parameters where `CLAUDE.md` asks for one.

1. Chained `supply()` order: `supply(feed, book)(catch_all(research))` reveals `() -> Generator[Never, Any, Unavailable | NotInteresting | NoArticle | str]`; `catch_all(supply(feed, book)(research))` reveals the same result union with `Unknown` in the Ability channel. Same result type; `Never`/`Unknown` asymmetry unchanged.
2. `catch_all(supply(feed)(research))` keeps `Need[Encyclopedia]` named, and `run()` rejects it with `invalid-argument-type`. Unchanged.
3. `partial_handling.py` with its `# type: ignore` stripped: `run()` reports `Generator[Need[Log], Any, None]`, both for the named `half` and nested inline. Unchanged.
4. `nested_handle.py`: `nested` and `full` reveal `() -> Generator[Never, Any, None]`, `half` reveals `() -> Generator[Ask, Any, None]`. Matches the chapter's quote character for character.
5. `fork_leak.py`: `reveal_type(bad)` reports `(n: int) -> Generator[Need[Executor], Any, Task[int]]`. Unchanged.

Also re-probed and holding: `retried`'s revealed type as quoted in *What Retry
Costs the Signature*; `catch(Crashed)(retried)` accepted with a `str | Crashed`
result and `RetryError[Crashed]` still in the channel; leaving `Time()` out
draws `invalid-argument-type` on `run()`; `Depend[Console, None]` draws
`invalid-type-arguments` at the annotation; yielding an `Ask` directly types
`name` as `str`; and `throw(KeyError())` in `fetch_nonempty()` draws
`invalid-yield`. Library claims confirmed in source: `Ability` declares no
`__slots__` (no `__slots__` anywhere in the package); `fork()`'s thread target
is `run(f(*args, **kwargs))` with no `try`/`except`; `supply()` returns the
first instance that passes `isinstance()`; `catch_all` is absent from
`stateless/__init__.py`; `schedule.py` has exactly `spaced()` and `recurs()`;
`handle()` raises `ValueError` for an unannotated handler; a `StopIteration`
raised by a handler lands in the `except StopIteration` that ends `Handler`'s
driver loop, which is the silent `None` the coin-toss section describes.

## Exercise 6 asks for a trace the chapter already prints

`scenarios.py`'s second run supplies `WEATHER = Wire("mild and cloudy")`, a feed
that succeeds with a headline no topic matches, and prints its trace. Exercise 6
asks the reader to write a `DullWire` that does exactly that and predict the
trace. Solutions 47 exercise 6 concedes it: "`DullWire` and `WEATHER` produce
identical traces." The prediction is therefore copied, not reasoned out, and the
exercise tests nothing the chapter did not already show. (It likely predates
`WEATHER` in the listing.)

Proposed replacement, which keeps the exercise's place and its "predict the
trace" form but makes the answer new: "Write a `StaleWire` whose `latest()`
prints `feed: fetching` and then raises `Unavailable`. Predict the trace, then
say why it differs from `DeadWire`'s even though both fail the same way."
The answer is `feed: fetching` then `no headline today`: where a failure
arises inside a supplied implementation decides which trace lines precede it,
the point of the paragraph after `scenarios.py`. The solution (listing,
`feeds.py` helper entry, and prose) would be rewritten to match. The
alternative is to cut exercise 6 and renumber 7 through 14, which drags
exercise 11's "Exercise 5" reference along untouched but moves every later
number in `exercise_refs_baseline.txt`.

[] Reject

## `run_cost.py`'s 50x threshold is thin on a four-core Linux VM

`run_cost.py` prints `run() at least 50x slower: True`. Measured standalone on
this cloud VM (Python 3.15.0rc2, four cores), the ratio came out 74, 46, and 76
in three runs; one of the three would print `False`. The listing is in
`tools/data/timing.txt`, so the gate retries toward `True` rather than
rewriting it, and `make verify` passed here. The chapter's prose now claims
only what the marker does ("at least fifty times"); it said "hundreds", which
may be what your Windows machine measures.

Nothing changed in the listing or marker, per the rules for timing claims. The
decision is whether 50x is the threshold you want the book to assert, given a
Linux ratio that sometimes sits below it. If your machine's ratio is in the
hundreds, a threshold of 20x would keep the claim ("`run()` is much slower")
with headroom on both platforms; if the ratio is itself the lesson, 50x can
stay and the Linux flap is accepted.

[] Reject

## Considered and declined

- "Execution stops there: a driver that receives a failure stops sending." `run_async()` actually throws a yielded exception back into the generator (`effect.throw(error)`), so code after `yield from throw(...)` runs if the author wraps it in `try`/`except`. The sentence is true of every path the chapter shows, and the fuller account belongs to chapter 46's driver discussion; left alone.
- The resource-lifetime claim appears twice (after `microgrid.py` and at the end of *Running Effects in Parallel*). The first defers to the second by link, so the repetition is a deliberate forward reference.
- *The Toolkit* sits between *Running Effects in Parallel* and *`run()` Builds a Loop per Call*, and the latter extends the toolkit's last table. The order reads naturally; no move.
