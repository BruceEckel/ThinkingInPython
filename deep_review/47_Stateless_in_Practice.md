When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Intro, the bullet preview: it stops three sections short, and this is the last
chapter in the book.**

The eight bullets map cleanly onto "Scripting an Unpredictable Source" through
"Where the Guarantee Stops", and then stop.
Nothing announces [The Toolkit](#the-toolkit) (the one page a reader will come
back to) or [Costs and Benefits](#costs-and-benefits) (the verdict, and the
book's last section).
A reader arriving at the toolkit table has no idea a consolidated reference was
coming, and a reader who wants the verdict has to scroll for it.

Proposed change: add one line after the last bullet, e.g.

> The chapter then collects every tool in one table and weighs what the whole
> approach costs.

Reported rather than applied because the preview's length is a pacing decision.

---

[] Reject

**"Abilities Are Not Special": the section opens with machinery and the reason
to care arrives a section later.**

The lead-in says a custom Ability "is an ordinary class rather than a special
form", which is reassurance rather than motivation: it tells the reader the
thing is not scary, not what it is for.
`ask_tell_stateless.py` then runs 38 lines before any sentence explains why
you would define `Ask` instead of asking for a `Need[Console]`.
The actual answer sits at the top of the next section — a custom Ability lets a
handler answer *differently at each request*, which `supply()` cannot do — and
the reader decodes the accessor/`__iter__`/type-bound material with no reason to
want it.

Proposed change: one sentence in the section's lead, before the listing, e.g.

> A `Need` asks for an instance and gets whatever was supplied.
> Your own Ability can ask for anything you can name, and the handler answering
> it is an ordinary function, so the answer can differ every time it is asked.

Reported rather than applied because it changes the chapter's opening pacing.
The cheaper variant is to move the two sentences at the top of
[Scripting an Unpredictable Source](#scripting-an-unpredictable-source)
("Every handler so far gave the same answer each time it was asked. ... A
handler is an ordinary function, so it can answer differently at each request.")
up into this section's lead and let that section open on the coin toss.
Price of that move: the "Scripting an Unpredictable Source" `##` section would
then have no prose of its own before `### A Coin Toss`, which reads oddly.

---

[] Reject

**"Abilities Are Not Special", lines 108-119: the type-bound paragraph is
almost verbatim chapter 46.**

46's "Waiting on a Coroutine" already says:

> The channel holds Abilities, and `Async` is one, so it sits there bare.
> `Console` never was one: it is an ordinary class,
> and `Need[Console]` is the Ability that asks for it.
> The first type parameter accepts only `Ability` subclasses,
> so `Depend[Console, None]` is rejected at the annotation.

47 repeats all five clauses. The only new content is
"before any `yield` is examined: `Console` is not assignable to the bound",
which is the part 46 promised ("takes that type bound apart").

I did not cut it, because 46 explicitly forward-links here and a reader who
skipped 46's async section needs the setup.
If you want it tighter, the three-line version is:

> That annotation reads `Depend[Ask, str]`, not `Depend[Need[Ask], str]`,
> the distinction [Waiting on a Coroutine](46_Stateless.md#waiting-on-a-coroutine)
> drew for `Async`.
> `Ask` is an Ability, so it sits in the channel bare, and the bound is what
> makes that more than a convention: `Depend[Console, None]` is rejected at the
> annotation, before any `yield` is examined, because `Console` is not
> assignable to `Ability[Any]`.

Verified against `ty` 0.0.65: the diagnostic is
`error[invalid-type-arguments]: Type \`Console\` is not assignable to upper
bound \`Ability[Any]\` of type variable \`A\``, reported on the annotation.

---

[] Reject

**"Switching Implementations Mid-Run": `microgrid.py` never produces the
`Blackout` the prose spends a paragraph on, and exercise 3 asks the reader to
find out what happens.**

The chapter states the behavior ("it travels through `run()` untracked and no
signature mentions it") and exercise 3 asks the reader to confirm that
`catch(Blackout)` around `run_load()` does not intercept it.
Nothing in the chapter shows it, so a reader who does not do the exercise has
only the assertion.

I confirmed the exercise's answer on the pinned build, so it is on record here
whatever you decide: with
`controller((Solar(), Battery(0), Grid(range(0, 24)), Backup(0)))` and
`guarded = catch(Blackout)(run_load)`, `run(handle(chooser)(guarded)(20, 2))`
raises `Blackout: 20` out of `run()`. `catch()` matches values an Effect
*yields*; `choose()` *raises*, from inside the handler, which is not the Effect
at all.

Two options. I lean toward the first.

- **Leave it as an exercise** and add half a sentence to the existing paragraph
  naming the mechanism rather than only the outcome: "`catch()` matches yielded
  values, and a handler yields nothing," which is the fact that makes the rest
  of the paragraph inevitable.
- **Show it**, with three lines appended to `microgrid.py` that build a
  site with nothing available and let the `Blackout` escape. Costs the listing
  its clean two-run symmetry, and exercise 3 then has nothing left to discover.

---

[] Reject

**"The Success Path": `research_by_hand.py` redefines `topic_of()` and the
chapter does not say why.**

The listing imports `TOPICS` from `research` and then writes `topic_of()` out
again, four lines identical to the original.
It looks like an oversight, and it isn't: `research.py`'s `topic_of()` is
decorated with `@throws(NotInteresting)`, so it returns an Effect and cannot be
called from ordinary `try`/`except` code.
That is the comparison's whole point in miniature — once a function is lifted,
its ordinary callers cannot have it back — and the chapter passes over it.

Proposed change: one sentence after the listing, e.g.

> `topic_of()` is written out again because `research.py`'s version is
> decorated: it returns an Effect, and ordinary `try`/`except` code cannot call
> it. Lifting a function takes it away from its unlifted callers.

Reported rather than applied because it adds a paragraph to a section whose
argument is deliberately compressed.

---

[] Reject

**"Adding Behavior to an Existing Effect", `### Why \`retry()\` Decorates the
Function`: this subsection re-teaches chapter 46's "An Effect Runs Once"
instead of building on it. It is the largest cut available in the chapter.**

46's [An Effect Runs Once](46_Stateless.md#an-effect-runs-once) already
establishes, with `effect_runs_once.py`, every one of this subsection's claims:

| 47, `### Why retry() Decorates the Function` | 46, `## An Effect Runs Once` |
|---|---|
| `spent.py`: second `run()` returns `None` | `effect_runs_once.py`: `print(repr(run(description)))` → `None` |
| "Re-running the spent Effect does not fail loudly" | "The second `run()` ... greets nobody and produces `None`" |
| "The special case is `success()`: it builds a constant" | "`success()` is the special case because it is not a generator" |
| "a retry has to rebuild the description from the function" | "They decorate the function, because the function can produce a second description" |
| "Where ZIO attaches `retryN` to an Effect value it can replay, Stateless attaches it one level up" | "A ZIO or Effect-TS value is an immutable description that can be interpreted as often as you like ... ZIO writes `action repeat policy`" |
| `### repeat() and memoize()`: "That wrapper exists because a generator cannot be replayed" | "`memoize()` is the one concession, and it caches rather than replays" |

`spent.py` is `effect_runs_once.py` with the `bound("Alice")` line removed.
Nothing here is wrong; it is all already known when the reader arrives.

Proposed change: replace the whole subsection (heading, `spent.py`, and its five
paragraphs) with two sentences inside "Adding Behavior to an Existing Effect",
just before `### What Retry Costs the Signature`:

> `retry()` decorates the function, not the Effect.
> `retry(three)(save_user("Morty"))` is not available, for the reason
> [An Effect Runs Once](46_Stateless.md#an-effect-runs-once) gave: the Effect is
> a generator, it is spent after one `run()`, and only the function can build a
> second description.

Price of the cut, checked:

- `#why-retry-decorates-the-function` is referenced from exactly one place, the
  new caution I added in [A Coin Toss](#a-coin-toss) (manifest item 6). That
  link would have to move to `46_Stateless.md#an-effect-runs-once`.
  Nothing outside chapter 47 links to it — I checked every `.md` in
  `Chapters/`, `Solutions/`, and `README.md`.
- `spent.py` would become an orphan in `Examples/47_Stateless_in_Practice/` and
  needs `make prune-examples`.
- `### repeat() and memoize()`'s closing sentence ("which is the same fact that
  made `retry()` decorate the function") still reads correctly.
- The chapter loses ~32 lines, and 46 gains an inbound link, which is the right
  direction: 46 promises the fact and 47 currently reproves it.

Alternative if you want to keep a demonstration here: keep `spent.py` but drop
the four paragraphs of explanation to one line ("The second `run()` returns
`None`, the one-shot behavior of
[An Effect Runs Once](46_Stateless.md#an-effect-runs-once)"). That keeps the
listing where a reader studying `retry()` will see it, and removes the
re-teaching.

---

[] Reject

**"Where the Guarantee Stops", `### 4. Cost`: the heading is a noun where its
four siblings are sentences.**

The five read: "Nothing stops an undeclared Effect", "The checker can give up
quietly", "Handlers cannot capture the continuation", "Cost", "Much of a mature
Effect system is missing".
Four of them state a limit; the fourth names a topic.
Scanning the five headings is how a reader uses this section, and one of them
does not participate.

Proposed change: `### 4. The discipline is all-or-nothing`, which is what the
paragraph actually argues ("An EMS is a decision about a whole codebase, not a
utility you import for one module").

Anchor cost: none. `#cost` is referenced from nowhere in `Chapters/`,
`Solutions/`, or `README.md`; the only chapter-47 anchor any other file links to
in this section is `#nothing-stops-an-undeclared-effect`, from 46.

Reported rather than applied because a heading is voice.

---

[] Reject

**"Costs and Benefits": the book's last section is titled for its middle, and
never names what the reader can now do.**

Two of the deep-review closing questions land here.

*Titled for its content.* The section's argument is not a balance sheet. It
runs: Stateless shows what language-level Effect tracking would look like in
Python today → a signature states dependency, failure, and result before you
read the body → and, the part nothing else in the book says, Python has a
*separate, non-composing mechanism* for each of those concerns while
`Effect[A, E, R]` is one type and `yield from` is one operator → the price →
the direction. The costs occupy four lines of a 34-line section, and one of
them duplicates `### 4` above. Candidate titles that name the payoff:
"One Type for Four Mechanisms", or, taking the closing line,
"What Is Missing Is Not the Capacity".
`#costs-and-benefits` is referenced from nowhere, so the rename is free.

*The capability the reader gained.* The chapter never says it, and it has a
good answer sitting unused at the end of
[A Clock](#a-clock): "Name each contact with the outside as an Ability and bind
it at the edge to whatever the context needs." That is the thing a reader can
do on Monday, in a codebase with no Stateless in it at all — it is what
`at()`, `crossing`, `controller()`, and `Script` all are. Right now that
sentence is buried at the 400-line mark and the last section talks only about
whether to adopt the library.

Proposed change: three sentences before "But the direction is worth watching",
e.g.

> Whatever you decide about the library, the habit survives it.
> Name each contact with the outside — the clock, the feed, the pool, the
> console — and bind it at the edge instead of reaching for it in the middle.
> `at()` and `crossing` and `controller()` are all that habit, and none of them
> needs an Effect type to work.

(Watch the wording if you take this: "reaching for" is in
`banned_phrases.txt`. Use "instead of calling it in the middle".)

Reported rather than applied on both counts: a retitle and a new closing
paragraph are voice and pacing decisions, and this is the paragraph the book
ends on.

---

[] Reject

**Order and pacing: the assumes/introduces table, and what it shows.**

Chapter claim in one sentence: *once every contact with the outside is an
Ability and every failure is lifted into the error channel, a function's
signature is its complete interface — here is what that buys, and here is where
it stops.*

| Section | Assumes | Introduces |
|---|---|---|
| Abilities Are Not Special | 46 (Effect/Depend/handle/run/supply), 45 (return channel) | writing an `Ability[T]`; accessors; `handle()`'s annotation dispatch; Ability vs `Need`; the type bound; naming intermediates |
| A Coin Toss | the above | a handler that answers differently per request; parenthesized `yield from` |
| A Clock | the above | handler factories (`at()`); Effect tests under `pytest`; the twice-read clock |
| Switching Implementations Mid-Run | 46's `@throws`/`catch`; 15 (context managers) | a handler answering with an implementation; mid-run swap; a handler sits outside the channel |
| State as an Ability | the above | paired `Get`/`Put`; the State effect; the unguarded cell |
| Composing a Program | 46 (`need`/`supply`/`as_type`/Protocols) | a three-error signature; scenarios; the boundary function; `catch` + `match` + `assert_never` |
| The Success Path | the previous section's code | the by-hand contrast |
| Two More Doors | the error channel | `throw()`; `catch_all()`; entry/exit symmetry |
| Dependencies That Need Dependencies | `need`, `yield from` composition | nested graphs; `invalid-yield`; the `ZLayer` contrast |
| Supplying a Whole Cast | `supply`, Protocols, 27 (Abstract Factory) | wide casts; the lost matched set; the nine-overload ceiling |
| Adding Behavior to an Existing Effect | Effects, `catch` | `retry()`; schedules; what retry costs the signature; `repeat()`; `memoize()` |
| — Why `retry()` Decorates the Function | 46's An Effect Runs Once | *nothing* (see the block above) |
| Running Effects in Parallel | 46's `wait()`, 19 (executors) | `fork()`; `Task`; the resource-scoping gap |
| The Toolkit | everything | *nothing* (consolidation) |
| Where the Guarantee Stops | everything | the five limits |
| Costs and Benefits | everything | the composition argument; the verdict |

Reading the two columns down: nothing later appears in an earlier "assumes"
column, which is unusual for a chapter this size, and the transitions are all
justified by something other than "it is also about this topic" — deep graph
then wide cast, one channel then the other door on each side, what it does then
what it cannot do. The arc holds.

Two things the table does surface, both already written up as their own blocks:
one subsection introduces nothing (`Why retry() Decorates the Function`), and
one item introduced in the first section ("naming intermediates") is not
justified until `### 2` of the last technical section, about 1800 lines later.
I closed the second with a named link (manifest item 3) rather than a move,
because moving `### 2` earlier costs more than it buys: it is written as one of
three gaps of the same shape, and the other two (the direct-Ability-yield
`Unknown` and 46's `type`-alias hole) genuinely belong at the end, where the
reader has seen enough green checks to be told to distrust them.

If you want the answer nearer the question anyway, the cheap version is two
sentences in "Abilities Are Not Special" stating the rule without the
explanation — "Name each stage. `ty` infers `Unknown` for
`handle(scripted)(handle(capture)(greet))` and the checking stops" — leaving
`### 2` to explain why. That duplicates one fact and closes a 1800-line gap.

---

[] Reject

**Exercises: three sections have none, and two of the three are the chapter's
pattern-book payoff.**

Current coverage: 1 → A Clock; 2 → limit 1; 3, 4 → Switching Implementations;
5, 7 → Composing a Program / The Success Path; 6 → Composing a Program;
8 → Running Effects in Parallel; 9 → State as an Ability;
10, 11 → Two More Doors.

Nothing exercises:

- **Abilities Are Not Special.** The chapter's opening claim is that an Ability
  is an ordinary class you can write, and no exercise asks the reader to write
  one. Every later exercise hands them an Ability that already exists.
- **Dependencies That Need Dependencies.** The nested graph, the union that
  travels up through `yield from`, and the `invalid-yield` that catches an
  under-declared signature.
- **Supplying a Whole Cast.** Including the one honest loss in the chapter — a
  flat `supply()` cannot express a matched family — which is the payoff of the
  comparison with [Abstract Factories](27_Factory.md#abstract-factories) and
  the only place a Part III pattern is weighed against the Effect version.

Proposed additions:

> 12. Write a `Random` Ability whose handler returns an `int` in a range
>     carried on the request, and an accessor `roll(low, high)` for it.
>     Use it to write a dice game as an Effect, then run the game twice: once
>     with a handler that calls `random.randint()`, and once with a handler
>     that walks a scripted sequence. Then delete the `low: int` annotation
>     from the accessor's parameter and say what changes, and delete the
>     annotation on the *handler's* parameter and say what changes.
> 13. Add a `Butter` appliance to `bakery.py` and a `buttered()` Effect that
>     needs it and calls `toast()`. Write `buttered()`'s signature with only
>     `Need[Butter]` first, run `ty`, and read the diagnostic before fixing it.
>     Then remove `Toaster(3)` from `supply()` and say which of the two
>     diagnostics tells you about a dependency two levels down.
> 14. `play()` in `casts.py` accepts any five actors, matched or not.
>     Give `kitties_and_puzzles()` and `warriors_and_weapons()` a shared
>     signature so a caller can pass either one where a cast is wanted, and say
>     what that recovers of the Abstract Factory and what it does not.
>     Then add a sixth actor to `encounter()` and count the lines you edit in
>     `arena.py`, `casts.py`, and `two_games.py`.

Exercise 9 could also earn the race the chapter warns about twice but never
shows, with a second half: "Then `fork()` two `spree()` Effects that share one
`Cell`, run them against a balance that only covers one, and report what
`cell.amount` holds afterward."

Reported rather than applied because the exercise set's size and difficulty
curve are yours.

---

## Cross-chapter

[] Reject

**`Chapters/46_Stateless.md`, "Builtin Abilities": the section calls three
ordinary classes Abilities, and chapter 47 then corrects it.**

46 says "Stateless includes three of its own: `Console` ..., `Files` ...,
`Time` ...", under the heading "Builtin Abilities", and opens with "Every
Ability supplied so far has been one this chapter defined."

None of the three is an `Ability`. I read the source:
`stateless/console.py`, `stateless/files.py`, and `stateless/time.py` all
define plain classes, reached through `need(Console)` / `need(Files)` /
`need(Time)`. The only two `Ability` subclasses in the library are `Need` and
`Async` (`grep "class .*Ability\["` over the package finds exactly those two).
46 half-knows this — the paragraph under the bullets says "All three are
concrete classes rather than interfaces" — but the heading and the lead
sentence still call them Abilities, and everything else in 46 is accurate about
the word (its `Console`/`print_line()`/`read_line()` bullet matches the source
exactly). 47's "Abilities Are Not Special" then draws the line explicitly —
"`Console` never was one. It is an ordinary class, and `Need[Console]` is the
Ability" — so the two chapters disagree about the word within twenty pages.

Change I would make in `Chapters/46_Stateless.md`: retitle the section
"Builtin Dependencies", and change the lead to "Stateless supplies three
classes of its own to depend on", leaving the three bullets alone. The
forward link at 46:762 into 47 keeps working (it names the 47 heading, not
this one), but `#builtin-abilities` would need checking for inbound links
before the retitle. I did not touch chapter 46, per the scope rules.

(I fixed 47's own instance of the same slip: `Running Effects in Parallel`
said "the library's own `Files` Ability", now "the library's own `Files`
class". Manifest item 15.)

---

[] Reject

**`Solutions/47_Stateless_in_Practice.md` answers exercise 1 of eleven.**

The file is 79 lines and stops after "1. An advancing handler, and the fix it
cannot break". Chapters 40, 42, and 43 in this part all carry fuller solution
sets, and this chapter's exercises are the heaviest in the book — several ask
the reader to run `ty` and compare a diagnostic, which is exactly where a
published answer matters, because the diagnostic text changes with the checker
version.

The three with the highest cost of being unanswered, in order: exercise 5
("list every line you had to edit" — a reader cannot check a list against
nothing), exercise 11 (asks for a prediction of `ty` output, then confirmation),
and exercise 2's second half (the `catch(KeyError)`-does-nothing demonstration,
which is the chapter's most important trap).

I did not add them, per the scope rules. One thing worth recording while it is
verified: exercise 7's premise holds under `ty` 0.0.65 —
`retry(recurs(3, spaced(...)))(research)` type-checks and reveals
`() -> Generator[Need[Feed] | Need[Encyclopedia] | Need[Time] | Async |
RetryError[Unavailable | NotInteresting | NoArticle], Any, str]`, so the
exercise's "supply a `Time()`" instruction is right and the `RetryError`
wrapping the union is the thing the reader is meant to notice.

---

[] Reject

**MANIFEST — not a proposal. Changes already applied to
`Chapters/47_Stateless_in_Practice.md` in this pass.**

Every gate re-run and passing after the last edit:
`extract_examples.py --write -o build/private/47`,
`validate_output.py --tree /tmp/tip/build/private/47` (1 ok, 0 failed, no
marker rewritten), `ruff check` (70-col, clean), `ty check` (clean),
`pytest` (3 passed), `heading_links.py` (OK), `banned_phrases.py` (clean),
`reflow_prose.py --diff 47` (0 paragraphs), and `extract_examples.py` reports
chapter 47 in sync. No listing was changed, so `Examples/` needed no sync.

1.  **Intro: corrected two claims in one sentence.** "Every Ability so far has
    been a `Need`" is wrong — 46's "Waiting on a Coroutine" spends a page on
    `Async`, an Ability that is deliberately *not* a `Need` ("The channel holds
    Abilities, and `Async` is one, so it sits there bare"). And "writing a
    `Need` from scratch" contradicts this chapter's own next page, where `Ask`
    is an Ability and `Need[Console]` is a different thing; 46:1206 forward-links
    here as the place that "writes an Ability from scratch". Now: "Every Ability
    so far came from the library: the `Need` that `supply()` answers, and the
    `Async` that `run()` awaits. This chapter opens by writing an Ability from
    scratch".
2.  "Abilities Are Not Special": added what happens when a handler's parameter
    is not annotated. The chapter said the annotation is required and stopped.
    Verified: `handle(f)` raises `ValueError: Handler function <...> was not
    annotated.` at the point of decoration (`handler.py` reads
    `get_type_hints(f)` and raises before returning a `Handler`).
3.  **"Abilities Are Not Special": fixed a forward reference that pointed at the
    wrong section.** "Naming the two stages also matters to the checker, for a
    reason the next section gives" — the next section is "Scripting an
    Unpredictable Source", which says nothing about it. The reason is in
    `### 2. The checker can give up quietly`, 1800 lines later. Now a named
    link, so `heading_links.py` catches it if the section is ever renamed.
4.  "Abilities Are Not Special": "`run()` is the loop at the bottom" →
    "that loop sitting at the bottom of the stack of handlers". In
    `two_way_generator.py` "the bottom" is the `__main__` block, so the
    sentence read as pointing at the wrong part of the listing it names.
5.  "A Coin Toss": "Two handlers answer the same function" → "feed the same
    function". A handler answers a request; "feeds" is the chapter's own word
    for this ("Here is the consumer and the handler that feeds it").
6.  **"A Coin Toss": added the scripted-handler trap, which the chapter teaches
    the idiom for three times and never warns about.** Verified on the pinned
    build: when `next(script)` runs out, the `StopIteration` is caught by
    `Handler.__call__`'s own `except StopIteration: return e.value`, so the
    whole run finishes with `None` and no exception —
    `run(handle(scripted)(count_heads)(6))` against the listing's five-value
    script prints `None`. Any other exception a handler raises propagates
    normally (checked with a custom exception and with an `IndexError` from a
    list-indexing handler, both of which escape `run()` visibly). This matters
    because `crossing` in `midnight.py` and exercises 4 and 9 all ask the reader
    to write more handlers of this shape. Linked to the spent-Effect `None` in
    `Why retry() Decorates the Function`, since it is the same silent value from
    the same protocol.
7.  "Switching Implementations Mid-Run", opening: "Both handlers in the last
    section answered with a value. A handler can also answer with an object" —
    a `datetime` is an object too, so the contrast did not land, and "the last
    section" is a relative reference of the kind CLAUDE.md warns about. Now
    "Every handler so far answered with data: a name, a `bool`, a `datetime`.
    A handler can also answer with an implementation, an object whose methods
    the program then calls".
8.  "Switching Implementations Mid-Run": added why `Source` carries no
    `@runtime_checkable` when `research.py`'s and `arena.py`'s Protocols all do.
    46 states the rule flatly ("`@runtime_checkable` is required because
    `supply()` uses `isinstance()`"), so a reader hitting an undecorated
    Protocol two sections later has a real question. Verified in `handler.py`:
    `handle()` isinstance-checks the *Ability* type (`Outlet`, a concrete frozen
    dataclass), and the `Source` a handler returns is never checked at all.
9.  "State as an Ability": "A test does the same, supplying a fresh `Cell`" was
    not true of the code shown — `read()` and `write()` close over a
    module-level `cell`, so a test has to rebuild the pair, not supply
    anything, and `supply()` is not involved. Now "A test builds its own pair
    from a fresh `Cell`, the way `at()` built a clock from a moment", which
    also points at the handler-factory idiom the chapter already taught.
10. "Composing a Program": "the pattern for reaching ordinary code" →
    "for bringing ordinary code in", matching the chapter's own later phrasing
    ("once `@throws` had brought the ordinary functions in at the boundary")
    and steering clear of the banned "reach for" family.
11. **"Catching the Whole Channel": corrected the explanation of `outcome()`'s
    ordering, which was false under the `ty` version the chapter names.** The
    text said `catch_all()` "cannot split a channel that still holds abilities:
    applied to `research()` directly, the call is rejected". Under `ty` 0.0.65
    it is not rejected: `caught = catch_all(research)` reveals
    `() -> Generator[Need[Feed] | Need[Encyclopedia], Any, Unavailable |
    NotInteresting | NoArticle | str]`, and `supply(feed, book)(caught)` then
    reveals `() -> Generator[Never, Any, Unavailable | NotInteresting |
    NoArticle | str]` and runs correctly (I ran the catch-first version end to
    end; it prints `NotInteresting`). What actually breaks is nesting, in either
    direction: `supply(feed, book)(catch_all(research))` fails with
    `invalid-argument-type` and `catch_all(supply(feed, book)(research))` fails
    with `no-matching-overload` and infers `Unknown`. So the paragraph now says
    both orders work and both need the intermediate name, and links to
    `### 2. The checker can give up quietly`, which is the gap this really is.
    `catch_everything.py` itself needed no change. (CLAUDE.md's note that the
    0.0.58→0.0.63 upgrade made "ch45's documented limitation half-obsolete"
    looks like the same event catching up with this paragraph.)
12. **"Dependencies That Need Dependencies": corrected the location line in the
    quoted `ty` diagnostic.** The block read `--> bakery.py:31:16`, pointing at
    the `def`; `ty` points at the offending yield. Reproduced by editing the
    extracted `bakery.py` to declare only `Need[Toaster]`: the real header is
    `--> bakery.py:34:23`, and the body lines 31-34 in the quote are already
    correct.
13. "Adding Behavior to an Existing Effect": moved "One attempt fails." to the
    front of the paragraph and named what it describes ("The first run is the
    baseline: one attempt, no retry, and it fails"). It sat after two sentences
    about `three`, where its referent had been lost.
14. **"Running Effects in Parallel": added the near-miss.** `squares()` forks
    every task and then waits in a second loop, which is the whole reason five
    50-millisecond sleeps take 50 milliseconds; the chapter showed the result
    and never named the structure producing it. Verified: the one-loop version
    (`task = yield from slow_square(n)` immediately followed by
    `yield from wait(task)`) returns the same list in 0.26s against 0.05s.
15. "Running Effects in Parallel": "the library's own `Files` Ability" →
    "`Files` class" (and "the Ability method owns it" → "the supplied object
    owns it"). `Files` is a plain class reached through `need(Files)`; calling
    it an Ability contradicts this chapter's own definition eight sections
    earlier. See the cross-chapter block about 46 for the other end of this.
16. **"The Toolkit": narrowed an over-claim.** "Here is every tool from both
    chapters" is not true — `as_type()`, `spaced()`, and `recurs()` are all
    tools from these two chapters and none of them is in the tables.
    Now "every tool from both chapters that acts on a description", with one
    line accounting for the three that do not.
17. Five paragraphs reflowed by `tools/reflow_prose.py --write 47` after the
    edits, so Semantic Line Breaks still hold.

Also checked and found clean, so no change was made:

- **The "promise" metaphor does not appear in this chapter at all**, in any
  form (`grep -in promis` returns nothing), and I introduced none. The
  neighbouring family is used literally and correctly throughout: an annotation
  *declares*, a signature *says*, a checker *reports*, `@throws` *lifts*. The
  two metaphor-adjacent uses are deliberate and read right —
  "`Success[int]` claims purity, and this function breaks that claim" needs a
  word that can be false, and "the guarantee" is a defined term with its own
  section. No use shifts subject mid-sentence.
- No "reach for" (`banned_phrases.py` clean); the one "reaching" was rewritten
  anyway, item 10.
- Every `#:` marker matches stdout: `validate_output.py` rewrote nothing, and I
  hand-traced `microgrid.py`'s two power-routing traces, `wallet.py`'s `2` /
  `remaining: 10`, and `retrying.py`'s three attempt sequences against the
  library source rather than trusting the gate. The one threshold boolean
  (`elapsed < 0.15` for five 50ms tasks, measured at 0.05) has the wide margin
  CLAUDE.md asks for.
- The relative-cross-reference sweep CLAUDE.md requires after the
  Generators split: `grep -n "previous chapter\|previous section\|last
  chapter\|earlier chapter"` returns nothing, and the eight named in-chapter
  anchors plus the twenty-odd cross-chapter links all resolve
  (`heading_links.py` OK). The two relative phrases that did exist were
  "the next section" (item 3, wrong) and "the last section" (item 7, replaced).
- No unexplained deviation from `thinking-in-python-skill.md`: no hand-written
  `__init__` anywhere in the chapter (`grep "def __init__(self"` is empty),
  every parameter-assigning class is a dataclass, constants carry the full
  `Final[...]` form, the one `# type: ignore` in `partial_handling.py` is
  required and explained in the following paragraph, the tests use
  `parametrize` and one behavior per test, and no importable module carries a
  top-level demo. The one-line method bodies in `casts.py` and `two_games.py`
  are the density rule, not drift.
- Every claim about the library was checked against
  `.venv/lib/python3.15/site-packages/stateless/`, not its exports: the
  `Ability.__iter__` quote matches `ability.py`; `supply()`'s nine overloads
  and first-match `isinstance()` match `need.py`; `fork()`'s four overloads and
  its `run()`-inside-the-worker match `async_.py`; `spaced()`/`recurs()` are
  the only two combinators in `schedule.py`; and `retry()`'s `RetryError`
  really does leave its declared `errors` attribute unassigned —
  `outcome.errors` raises `AttributeError` and `outcome.args[0]` holds the
  three `Crashed` instances, exactly as the chapter says. The
  `catch(Crashed)(retried)` trap is real too: it reveals
  `... Any, str | Crashed]` with no complaint, and at runtime the `RetryError`
  sails past and is raised out of `run()`.
- The three checker gaps in `### 2` all reproduce on `ty` 0.0.65:
  `handle(scripted)(handle(capture)(greet))` is `Unknown`, a bare
  `yield from Ask(prompt)` binds `Unknown`, and the quoted
  `partial_handling.py` diagnostic matches byte for byte (line 18, column 9)
  once the `# type: ignore` is removed. `run()`'s missing-`Oven` rejection and
  `supply()`'s tenth-argument `no-matching-overload` also reproduce as quoted,
  as does `report()` annotated `Success[str]` naming the `yield from` that
  still carries `Need[Feed] | Need[Encyclopedia]`.
