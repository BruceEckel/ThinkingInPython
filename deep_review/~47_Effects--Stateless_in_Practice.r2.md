> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 47_Effects--Stateless_in_Practice, second review (2026-09-29)

The first review is `~47_Effects--Stateless_in_Practice.md` (2026-09-25).
Its applied list, its two accepted blocks, and its three declined items all stand,
and nothing here proposes any of them again.
That review ran in a cloud session without the global watch list,
so this one reads the prose against it for the first time.
It also reads the six commits made to the chapter after the first review closed
(the fix triage, the `@record(slots=False)` conversion, the prose move, and three prose commits).

Nothing here needs your decision, so the file has no live blocks.
Three of the applied changes touch a fix-triage decision of yours;
they are marked below, and each is a one-line revert.

Checked against the installed Stateless 0.6.1 source (every module read),
`ty` 0.0.84, Pyright 1.1.414, the ZIO documentation, and the text of
*Effect Oriented Programming* at `C:\git\book-published\Chapters`.
`tip verify-ch CH=47` passes 24 of 24, and the whole-book `tip verify` passes.

## Applied directly

### Chapter: damage from edits made after the first review

- **Opening list (touches the triage).** The triage cut "The rest of the chapter applies the machinery:",
  which left the eight bullets with no sentence to belong to.
  The list now follows "The rest of the chapter adds:".
- **Bakery section (touches the triage).** The triage cut
  "This example rebuilds the `Bread` sequence from Effect Oriented Programming, where ZIO wires the same graph with `ZLayer`s".
  Two later sentences depended on it: "ZIO makes both of them a `HeatSource`" and "`Bread.homeMade` is a `ZLayer`".
  Neither name appears anywhere else in the book, so both read as facts about ZIO.
  The cut sentence stays cut. The two later sentences now name their source:
  "[Effect Oriented Programming] builds this same toast in ZIO, where both appliances are a `HeatSource`..."
  and "In that book's version, `Bread.homeMade` is a `ZLayer`".
- **`outcome()`'s annotations (touches the triage).** The triage cut "`outcome()`'s parameter annotations also do a job.",
  so "Declaring the parameters as `Feed` and `Encyclopedia`" had no function to point at.
  Now "Declaring `outcome()`'s parameters as...".
- "Here the binding is a call to `choose()`" followed a sentence ending "and here the right answer changes with the hour".
  The second is now "In `microgrid.py` the binding is...".

### Chapter: corrections

- *Abilities Are Not Special*: "That second channel in the signature is the one Effect Management says an EMS needs"
  linked `#tracking-and-management`, which has no "second channel" in it.
  The sentence it cites closes `#effects-by-hand`. Anchor changed.
- Same section: "`next()` on `greet("Alice")`" sat six lines under "`greet()` takes no arguments".
  The call belongs to chapter 46's `hand_driven.py`. Now "does with that chapter's `greet("Alice")`. `next()` on that Effect...".
- *Composing a Program*: "A full Effect system calls each pair of bindings a *scenario*."
  ZIO has no such term. `Scenario` is a teaching device in Effect Oriented Programming (its chapter 3).
  The sentence now credits the book, with the link.
- Same section: "`research()`'s signature is also the only place its dependencies and failures appear"
  is false for the dependencies, since the body calls `need(Feed)` and `need(Encyclopedia)`.
  Now "the only place its failures appear, and the body requests each dependency by its type."
- Same section: "`@throws` decorates a function returning an Effect" read as the general rule,
  one paragraph after three `@throws` functions that return ordinary values.
  Now "`@throws` also decorates a generator function".
- Resource lifetime, both statements: "You cannot acquire a resource in one Effect and release it after a later one finishes"
  is false as written, because an `ExitStack` supplied as a `Need` does it,
  and the second statement goes on to recommend `ExitStack`.
  Both now say what is true: Stateless provides no way to do it.
  (The first review declined to merge the two statements. They are still two.)
- *The Toolkit*: "every tool from both chapters" omitted the three accessors chapter 46 names
  (`print_line()`, `read_line()`, `read_file()`). One sentence now says `need()`'s row covers them.
- `ty` version: all three pinned claims hold on 0.0.84, so the three "0.0.82" now read "0.0.84".
  Probes are listed under "Verified and left as written".

### Chapter: teaching

- *Abilities Are Not Special*, the near-miss. "You can skip the accessor and yield the Ability directly" did not say which `yield`.
  `yield from Ask(...)` types the answer `str`. A bare `yield Ask(...)` runs the same and types it `Any`,
  so `name + 1` passes the check (probed). The paragraph now names `yield from` and warns about the bare form.
  Solutions exercise 12 had written its accessor the bare way.
- `run_cost.py` calls `report(per_run=..., per_run_async=...)`, so `--numbers` prints both costs,
  as chapter 18 says every measured listing does. One sentence after the listing says so, with the link.
  Markers and the `timing.txt` entry are unchanged. On this machine: 525 microseconds against 1.

### Chapter: listings

- `parallel.py` and `fork_leak.py`: the `from stateless import (...)` block is packed,
  as in `fetch_guarded.py` and chapter 46's `catch_score.py`. 13 lines became 3, and 12 became 2.
  Two `I001` entries added to `pyproject.toml`.

### Chapter: prose against the watch list

- "spelling" three times and "spells" once, all meaning form: "one form nesting them", "the two forms", "either form", "writes the union out".
- "`ask_tell_stateless.py` still binds `half` and `full`": "still" implied a reason that had expired. Cut, per the no-history ruling.
- "That `Unknown` loses no unsupplied `Need`" is now "hides no unsupplied `Need`".
- Stranded prepositions: "depletes when drawn from", "everything the program depends on", "the error you started with",
  "the only thing `memoize()` keys on", "the version of this limit to watch for", "what that function can fail with".
- "a third-party function that returns a value or raises" now "raises an exception"; "instead of raising" now "instead of raising the `Boom`".
- Dropped: "has to" (payload), "as itself" (now "unchanged"), "itself" twice, "ever", "anyway".

### Solutions: corrections

- Exercise 1: "Without [`nonlocal`], `moment += step` binds a local name, and every request answers the same instant."
  It raises an `UnboundLocalError` at `current = moment`, on the first request (run).
- Exercise 7: "three fetches and two sleeps". `retry()` sleeps after every failed attempt, the last included, so three
  (counted with a `Time` subclass).
- Exercise 10: the exercise says to raise `Empty` in the body and lift it with `@throws(Empty)`.
  The solution raised it in a separate `nonempty()` function. `lifted()` now does what the exercise asks:
  `@throws(Empty)` on the generator function, annotated with the undecorated shape, as `fetch_effectful.py` does.
  The "prefer" paragraph named `nonempty()`, so it is rewritten around what the type checker verifies.
- Exercise 11: "With no declared return type, `ty` infers one from the body" is true of Pyright and false of `ty`,
  which reveals `-> Unknown`. The two paragraphs now say what each checker does.
- Exercise 12: `roll()` was `return (yield Random(low, high))`, the bare form. Now the chapter's accessor form.
  "An Ability is a dataclass rather than a marker" contradicted `Flip`, `Now`, and `Get`; now "this Ability is a record with fields".
  "One frame away from the code that made it": the traceback names `real()` and the library, and neither `roll()` nor `game()` (run).
- Exercise 14: the edit counts listed three edits for "four" and six for "seven".
  Each list now names the missing one (the line that uses the new actor; the `from quest import` line).

### Solutions: house style and prose

- `research_long.py`: `LIMIT: int = 100` is now `Final[int]`.
- `exercise_7.py`: `THREE` is now `three`, as in the chapter's `retrying.py`.
- Exercise 8 (unnamed, run-only): its import block follows the chapter's packed form.
- "ability" and "effect" in lowercase, three places, now capitalized as the chapter writes them.
- Five imperative-plus-consequence sentences now open with "If you" or "Once".
- "compile-time stop" is now "stops the type check". Python has no compile time in that sense.
- Watch list: "nothing but", "honest", "spells", "has to", "at all" twice, "actually", "buys", "itself", "wants", "in sight", "nothing else to say".
- Bare "raises" twice in exercise 6.

## Verified and left as written

`ty` 0.0.84, probed in `build/examples/47_*/` inside a function with `feed: Feed, book: Encyclopedia` parameters:

- Both `supply()`/`catch_all()` orders reveal the same result union, `Never` one way and `Unknown` the other.
- `catch_all(supply(feed)(research))` keeps `Need[Encyclopedia]` named, and `run()` rejects it.
- `nested_handle.py` prints the chapter's quote character for character.
- `partial_handling.py` without its `# type: ignore` prints the quoted diagnostic.
- `reveal_type(bad)` in `fork_leak.py`, `retried`, the stale `catch(Crashed)(retried)`, a missing `Time()`, `fetch_headline`,
  `Depend[Console, None]`, `throw(KeyError())`, a tenth `supply()` argument, `bakery.py` with `Need[Toaster]` alone,
  a missing `Oven(220)`, `@fork` over a `Need`, `fork(catch_all(bad))`, and `report()` annotated `Success[str]`.
- `@record(slots=False)` and bare `@record` both draw `invalid-argument-type` and `invalid-assignment`.

Runtime: six tosses from the five-value script return `None`; an unannotated handler raises `ValueError`;
a `Blackout` goes past `catch(Blackout)`; retrying `research()` under `WEATHER` fetches three times
and collects three `NotInteresting`; `outcome.errors` raises `AttributeError`.

Source: `Ability` declares no `__slots__`; `supply()` has nine overloads and `fork()` four, two of which take an error;
`fork()` calls `run()` in the worker with no `try`/`except`; `Files.read_file()` opens and closes inside one call;
`catch_all` is absent from `__init__.py`; `run()` is `asyncio.run(run_async(effect))`.

Outside the repo: the ZIO `divide` example is quoted exactly from ZIO's page on defects.
Effect Oriented Programming chapter 4 has `Bread.homeMade`, `Oven` and `Toaster` as `HeatSource`s,
and the ambiguity error. ZIO has `retryWhile`.

Other chapters: the listings and sections cited in 15, 18, 27, 40, 41, 42, 44, 45, and 46 say what this chapter says they do.
`student_pairs.py` still takes `seed` after commit c9db3b8c.

## Considered and declined

- **Five more vertical imports in the chapter, seven in Solutions.** `microgrid.py`, `scenarios.py`, `research_by_hand.py`,
  `catch_everything.py`, and `two_games.py` wrap a local import one name per line. The book has fifteen such blocks.
  Packing them is one sweep with one `pyproject.toml` edit, better made once on `master` than in one chapter's branch.
- **`"**/casts.py" = ["I001"]` in `pyproject.toml` is stale.** `casts.py`'s import fits on one line now. Harmless, and not this review's file to tidy.
- **The opening list repeats the new blockquote opener.** Both are roadmaps. Cutting the list would settle the missing lead-in a different way;
  the list survived the triage, so it stays.
- **`run_cost.py`'s threshold.** This machine measures about 500x against a 20x claim. The first review's block settled the number for Linux; left alone.
- **"It prints nothing itself."** The first review restored it to set up "Output is an Ability". "Itself" carries the contrast with the supplied `Narrator`.
- **Solutions exercise 1 defines its own `Now` and `now()`.** A Solutions listing cannot import a chapter module, so the copy is required.
- **Exercise 8's listing has no name.** A `ProcessPoolExecutor` listing cannot carry markers, and the prose says why the checker skips it.
