[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/23_Iterators.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest (16 tests) are clean on
`build/examples/23_Iterators`, and all 12 scripts run. The one
threshold boolean, `tee.py`'s `buffered > listed * 0.9`, is memory
rather than time and measured stable, 5 of 5 `True` standalone.
Probes confirmed the chapter's checkable claims: `ty` refuses
`twice_collection(gen(3))` with "Expected `Collection[int]`, found
`Iterator[int]`", as the prose says it must; ruff with every rule
enabled (`--select ALL`) reports nothing against `list(count(1))`
beyond the comprehension-rewrite rule the prose describes (C416); a
`__getitem__`-only class does iterate under `for`, fails
`isinstance(obj, Iterable)`, and fails an `Iterable[int]` annotation
under `ty`, all three as claimed; `threading.concurrent_tee()` exists
on the pinned 3.15 and chapter 19's linked section covers it; and the
PEP 479 `RuntimeError` is demonstrated live by `asking_costs.py`'s
marker. Cross-references to chapters 5, 14, 16, 19, 20, 21, and 45
all resolve (`heading_links.py` clean). No live blocks this run:
every finding had one defensible answer.

## Applied directly

- The Costs of Laziness: added a short paragraph separating laziness
  from single use (`Countdown` and `range()` are lazy yet survive
  repeated passes; the iterator runs out, not the iterable that made
  it). Without it a reader can leave the section believing lazy
  means one-pass, and `range` then looks like a counterexample.
- Iteration Comes Built In: added the `next(nums)` near-miss to the
  prose after `basic_iteration.py` (a list has no `__next__()`, so
  the call raises a `TypeError` at runtime and the checker rejects it
  before that). Kept out of the listing because `ty` refuses the call
  ("Expected `SupportsNext[Unknown]`, found `list[int]`") and a
  chapter listing must type-check, the same reason `walked_twice.py`
  cannot show `twice_collection(gen(3))`.
- Intro: "It only asks for the next item" is now "It asks only for
  the next item" (the restriction belongs on the item).
- `walked_twice.py`: the comment "# Ty sees nothing wrong" is now
  "# The checker sees nothing wrong". The tool's name is lowercase
  everywhere else in the book, but the comment-caps gate does not
  recognize `ty` as an identifier and demands the capital, so the
  capitalized tool name was traded for the book's usual "the
  checker". `Examples/` resynced.
- The Pattern That Disappeared: "recreating one item by item" is now
  "recreating one, item by item" (the old form parsed as "recreating
  [one item] by item").
- Two "has to" became "must" ("`advance()` must return the value it
  moved to"; "a peekable iterator must buffer").
- Ran `make reflow CH=23` over the edited prose.

## Considered and declined

- `iterators.py` and `yield_from.py` carry top-level demos with
  markers and are imported by their tests, so the demo prints during
  pytest. Declined to split them into library plus demo file: tests
  importing a marker-carrying demo module is the book's standard
  shape (30+ instances across chapters 12-26), and the split
  convention targets an example importing another example.
- "You take only as many as you need ..., which a list cannot do":
  the antecedent of "which" is mildly loose, but the sentence reads
  correctly as "produce on demand with no end". Left as written.
- "The fix is almost never a `try`" keeps its watch-list "never":
  the hedged claim is the point.
- "Whether an iterator ever ends is not something a checker can
  decide" keeps "ever": it carries the termination question.
- The orienting comments inside `iterators.py` ("# Generator
  function", "# __iter__() makes a class iterable. Often a
  generator:") are pre-existing authorial choices; left alone.
- "A *generator* writes them" (for `__iter__()`/`__next__()`):
  considered the more literal "calling a generator function supplies
  them", declined; the pithy form is clear in context and in
  character.
- `OverStream.__init__()` is hand-written rather than a dataclass:
  correct as is, since it transforms its argument (`iter(source)`)
  and seeds derived state, which the dataclass rule exempts.
