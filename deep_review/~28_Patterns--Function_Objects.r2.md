> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 28_Patterns--Function_Objects (2026-10-13)

I read the chapter and its Solutions file against the 2026-09-29 review (`~28_Patterns--Function_Objects.md`), `deep_review_db.md`, the chapters that link into this one (16, 17, 21, 25, 27, 30, 36, 37), and probes under `ty` 0.0.86, Pyright 1.1.414, and the pinned interpreter.
`tip verify-ch CH=28 ISOLATED=1` passes 27 of 27 before and after the edits.
No live blocks.

Probes that hold:

- `[account.deposit(), alert]` as a `list[Command]` draws `invalid-assignment` (`None` is not a `Command`).
- `subscribe(Deposit, on_withdraw)` draws `invalid-argument-type`; `Audit(50).threshold = 1` draws "Property `threshold` defined in `Audit` is read-only".
- Solutions 1: a `Callable` list draws `unresolved-attribute` on `c.undo()`. Solutions 2: a `Callable` chain draws `unresolved-attribute` on both reads of `__name__` under `ty`, and Pyright accepts it, as the prose says.
- Solutions 4: `partial(newton, 0.6)` fails at run time with the `TypeError` the prose describes.

## Applied directly

Chapter:

- Tagged bus: the prose said `Handler` becomes a `Protocol` "because the handlers are now objects rather than functions". That reason is false, and the chapter disproves it: `callable_command.py` shows a `Repeat` instance satisfying the `Callable` alias `Command`. A probe with `type Handler[E] = Callable[[E], None]` in `tagged_bus.py` gives the same `ty` result for the listing, the demo, the tests, an undecorated class, and a lambda. `tagged_bus.py` now keeps `event_bus.py`'s alias, the prose says it accepts callable objects as `Command` accepts `Repeat`, and the paragraph explaining the Protocol's `/` is gone, since a `Callable` parameter has no name. This reverses one line of the last review's applied list. The close alternative was keeping the `Protocol` and giving it a true reason (it names the method `@handler` inspects); I chose the listing with one fewer construct.
- Story figure and its paragraph moved from the middle of the *Chain of Responsibility* section to its end, just before "An Event Bus". The figure summarizes all three patterns, and where it sat it split `chain_demo.py` from the paragraphs about `first_root()`'s `is not None` test.
- "so the command's configuration reads from outside the object": a configuration does not read. Now "so you can read the command's configuration from outside the object."
- "and so does `first_root()` in `chain.py`" named a listing the reader has not met. Now says the next section introduces it.
- `publish()`'s `.get()` paragraph: "Every published event type ... otherwise leaves a stray entry behind" left "otherwise" without a stated condition. Now "Indexing would leave a stray entry behind for every published event type with no handler".
- "The entries in `EVENTS` and `HANDLES` are runtime facts" became "The two decorators fill `EVENTS` and `HANDLES` at run time, where the type checker cannot see them", stating the contrast with `dataclass_transform` in the sentence before it.
- Exercises 4 and 6: `functools.partial` became `functools.partial()`; `tip statements` copied both into the Solutions quotes.

Solutions:

- Exercise 4: `partial(newton, 0.6)` draws two `ty` diagnostics, `invalid-argument-type` on the `0.6` and `invalid-assignment`; the prose named one. It now names both, and the run-time `TypeError` is its own sentence.
- Exercise 6: "`partial(print, n)` passes the value straight to `print()`" gave no reason the value is not private. Now: it stores the value in the `partial` object's public `args` attribute (`by_partial[0].args` is `(0,)`, checked).
- Exercises 1 and 5: dropped "already" twice.

## Considered and declined

- `test_chain.py` imports `Fn` and `RootFinder` from `chain`, which re-exports them from `algorithms`. Importing them from `algorithms` makes the line 65 columns, and a wrapped import needs a per-file `I001` entry in `pyproject.toml`, outside this review's scope.
- "That makes all three patterns largely unnecessary" overstates if read as the patterns' ideas, but the next sentence's "dissolves into the language" is chapter 21's thesis, and the chapter goes on to show each pattern as a function.
- `functools.singledispatch` without parentheses in the tagged-bus closing paragraph matches the book's majority form (seven uses against two `singledispatch()`).

## For the session

- `tip prose CH=28` reports stale baseline entries left by these edits: in `stranded` ("otherwise leaves a stray entry behind") and in `watch-words` (the deleted "positional-only" line and the two removed "already"s). No new hits.
- `tagged_bus.py` under `Examples/` changed through `verify-ch`'s sync.
