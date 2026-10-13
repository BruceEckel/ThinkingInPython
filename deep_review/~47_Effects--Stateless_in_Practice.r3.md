> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 47_Effects--Stateless_in_Practice, third review (2026-10-13)

This review reads the chapter and its Solutions file after the two completed reviews
(`~47_Effects--Stateless_in_Practice.md`, `.r2.md`) and the eight commits since,
including the Gemini outside-review edits and the listing-design proposals.
Nothing here re-proposes a declined or rejected item from either file or from `deep_review_db.md`.

Checked against every module of the installed Stateless 0.6.1
(`__init__`, `ability`, `async_`, `console`, `effect`, `errors`, `files`, `functions`, `handler`, `need`, `schedule`, `time`),
`ty` 0.0.86, and Python 3.15.0 under `uv run`.
`tip verify-ch CH=47 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.
`run_cost.py` and `parallel.py` ran three times each with `--numbers`:
`run()` cost 566 to 658 microseconds against 1 for `run_async()`, and the five forked tasks took 56 to 58 ms against the 150 ms threshold.

No live blocks: every finding had one sensible answer and is applied below.

## Applied directly

### Chapter

- *Abilities Are Not Special*: "so you decorate an Ability with `@record(slots=False)`" read as a rule for every Ability, and `Flip`, `Now`, and `Get` carry no decorator. Now "an Ability that carries fields".
- Same section: the accessor sentence said "one place to state that answer type" and then named two (the signature and the `answer: str` binding). Now the accessor "keeps its answer type in one function", and the two statements are named in order. The rewrite also drops "one line below", a positional pointer.
- Same section: "compare these two listings to `ask_tell.py` again" named a listing this chapter never shows, and "again" pointed at a comparison that never happened. The sentence now links `ask_tell.py` to its section in Effect Management, and the link two sentences later becomes a plain chapter name.
- *Dependencies That Need Dependencies*: the missing-`Oven` rejection was described as expecting "an empty Ability channel". `run()` expects `Generator[Async | Exception, Any, Unknown]`, and `Async` is an Ability. Now "a yield channel holding only `Async` and errors", matching the Toolkit's wording.
- *Supplying a Whole Cast*: "which `Hero` already declares" is now "declares too" (watch word).
- Heading "What Retry Costs the Signature" is now "What Retry Does to the Signature" (commerce figure, R2). No link in `Chapters/` or `Solutions/` used its anchor.
- *`repeat()` and `memoize()`*, teaching addition: `memoize()` is `functools.lru_cache(maxsize=None)` under a wrapper, so the chapter now says so outright ("through", not "the way ... does"), and a new three-line paragraph gives the two consequences a reader meets first: an unhashable argument raises a `TypeError` at the call, and the default cache has no size limit, with `memoize(maxsize=128)` as the bound. Both probed (a `list` argument raises `TypeError: unhashable type: 'list'`; `memoize(maxsize=128)(save_user)` runs and type-checks).
- *Running Effects in Parallel*: "That restriction is the only one the checker enforces. The restriction says nothing about a declared error." merged into one sentence with "it".
- *The Toolkit*: "it serves as an entry point as well as a transformation" is now "it is both" (Vale `WeakVerb`).
- *`run()` Builds a Loop per Call*: "so it pays that cost on every `run()`" is now "so each of its `run()` calls builds one" (commerce figure).
- *The type checker decides what survives handling*: "`Unknown` in a revealed type is still `ty` not finishing the subtraction" is now "An `Unknown` in a revealed type means `ty` left the subtraction unfinished"; "still" read as a time word.
- Exercise 3: "say where the `Blackout` propagates to" lost its stranded "to". The Solutions quote regenerated.

### Solutions

- Exercise 8: "This book's output checker also skips the listing, for the same reason. `slow_square()` must be picklable by name from an importable module" is false for Stateless. `fork()` has a `ProcessPoolExecutor` branch that serializes `(f, args, kwargs)` with `cloudpickle`, which pickles a `__main__` function by value. Run through `exec()` in a synthetic `__main__` namespace (the validator's shape), the listing printed `[0, 1, 4, 9, 16]`. The paragraph now says what changed around `squares()` (the executor class, the dropped timing, the guard) and why `slow_square()` needs nothing new.
- Exercise 2: "genuinely produces" is now "produces" (flourish).

## Verified and left as written

`ty` 0.0.86 probes, each in the isolated build tree:
`yield from Ask(...)` types the answer `str` and a bare `yield Ask(...)` types it `Any`;
`Depend[Console, None]` draws `invalid-type-arguments` at the annotation;
`fetch_headline` reveals as quoted;
`catch_all(supply(...)(research))` reveals `Unknown` in the yield slot and the reverse order `Never`, with the same result union;
`catch_all(supply(feed)(research))` keeps `Need[Encyclopedia]` and `run()` rejects it;
`retried` reveals as quoted, `catch(Crashed)(retried)` passes with a `Crashed` branch added, and leaving out `Time()` fails at `run()`;
a tenth `supply()` argument draws `no-matching-overload`;
`@fork` over a `Need` lists the four overloads Solutions 8 quotes;
`reveal_type(bad)` in `fork_leak.py` matches, and `fork(catch_all(bad))` gives `Task[Boom | int]`, with `wait()` returning `Boom | int` at runtime;
`report()` annotated `Success[str]` draws `invalid-yield` at its `yield from`;
`throw(KeyError())` under a narrower channel draws `invalid-yield` at that line.

Runtime: six tosses from the five-value script return `None`, and an indexed script raises `IndexError`;
an unannotated handler raises `ValueError` at `handle()`;
a `Blackout` goes past `catch(Blackout)`;
forking and waiting in one loop took 0.268 s against 0.056 s for the two-loop form.

Source: `Handler.__call__` catches `StopIteration` from a handler as the end of the Effect and lets every other exception leave without touching the inner generator;
`retry()` and `repeat()` run each attempt through `catch_all()` and sleep after every pass;
`spaced()` and `recurs()` are the only schedule builders.

Solutions probes: exercise 1 without `nonlocal` draws `unresolved-reference` twice;
exercise 5's three `invalid-yield` stops and the `assert_never` failure appear in the order the solution gives;
exercise 10's two versions reveal the same return type;
exercise 11 without its annotation reveals `-> Unknown`, and with the old annotation draws `invalid-return-type`;
exercise 12's empty `Random` draws `too-many-positional-arguments` and `unresolved-attribute`, and an unannotated `low` lets `roll("a", 6)` pass.

## Considered and declined

- *Abilities Are Not Special*'s `answer: str` bindings in the accessors: under `ty` 0.0.86 the binding's annotation adds nothing that `yield from Ask(...)` lacks, since both type the answer `str`. The accessor still earns its place as the name and the stated signature, which the sentence now says; cutting the annotations from five accessors is a listing change for the author's taste.
- *`repeat()` and `memoize()`*: "Memoize a function only where one environment serves the memoized call for its whole lifetime, the way ... `Cell` does once bound": the comparison is loose, but every rewrite I tried needed a second listing to make it concrete.

## For the session

- `tip watch-words` reports three stale baseline entries for this chapter (`already`, `cost`, `pays`), and `tip positional` one (`one line below`), all for sentences this review rewrote. Pruning them is a baseline edit, outside this agent's scope.
- No cross-chapter errors found. Chapters 18, 41, 44, 45, and 46 say what this chapter cites them for.
