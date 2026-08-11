When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/32_Multiple_Dispatching.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty` and ruff are clean on `build/examples/32_Multiple_Dispatching`, all 30
tests pass, and all six runnable scripts run. The operator-dispatch claims
were probed individually on the pinned toolchain and all hold: a class with
only `__radd__()` gets `TypeError` adding to its own kind, same-type operands
skip the reflected call, a right-operand subclass's overriding reflected
method runs before the left operand's `__add__()`, and `int.__add__(4, obj)`
returns `NotImplemented` for an unknown type. The typing paragraph was
verified two ways: typeshed's `types.pyi` defines
`class NotImplementedType(Any)` and annotates `timedelta.__add__()` as
returning `timedelta` (confirmed via `reveal_type` under `ty`), and `ty`
accepts `return NotImplemented` under any declared return type, in dunders
and plain functions alike, while rejecting the sentinel in an ordinary
assignment, so the claim as scoped to return position is right. Incoming
links from chapters 13, 20, 27, 33, 34, 37, 39, 41, 44 and `Solutions/34`
target `#one-type-or-many` and `#operators-dispatch-twice`, both intact;
outgoing anchors into 20, 31, 33, and 34 resolve; the `double_dispatch`
diagram's labels match the listing; and chapter 33's "the same gap the `Any`
in `paper_scissors_rock.py` left" still points at the methods version, which
kept its `Any`. `Solutions/32_Multiple_Dispatching.md` covers all ten
exercises; one factual error surfaced there (solution 2's method count) and
one in the chapter (the conclusion's "available for arithmetic and nothing
else"), both fixed below. No finding needed a decision, so this review has
no live blocks.

## Applied directly

- Table listing: `compete(self, item: Any)` is now `compete(self, item:
  Item)`, and the `Any` import is gone. `Item` declares `compete()`, so the
  opponent has a precise type; the methods version's `Any` is the one the
  prose and chapter 33's cross-reference price. Solutions exercises 1, 4,
  and 6 updated to match.
- `Any`-cost paragraph: "the table version gets the same guarantee for free"
  overstated the case, since a missing row is still the runtime `KeyError`
  the next section prices, not a static check. It now says the table needs
  neither `Any` nor a `Protocol`: no method for a class to forget, and its
  one method typed `item: Item`.
- Conclusion: cut "and it is available for arithmetic and nothing else",
  which contradicted the chapter's own "every arithmetic and bitwise
  operator"; "the one case" plus the following "Everywhere else" already
  carry the exclusion.
- Moved "Testing Both Versions" above "Operators Dispatch Twice": the tests
  compare the two versions and now sit beside them, and the Operators
  section flows directly into the conclusion that synthesizes it and into
  the chapter-34 handoff. Both section anchors are unchanged, and no
  cross-reference depends on the old order.
- New paragraph after the follow-one-duel walkthrough: the `item` argument
  every `eval_*()` method ignores is the original caller, passed along as
  `self` by `compete()`; this answers why `self` is passed at all, and notes
  a game with richer state would read it.
- New sentence after `arena.py`: `duel()` settles for `Any` because the two
  versions define separate `Item` hierarchies and the file serves both,
  while `item_pair_gen()` stays generic.
- Operators section: "This is how an `int` on the left can learn..." now
  sits directly after the reflected-form naming, before the in-place aside
  that had separated it from its referent; "Do not confuse this" is now
  "Do not confuse the reflected forms".
- "a type that inherits `Any`" is now "inherits from `Any`" (typeshed:
  `class NotImplementedType(Any)`).
- `functools.singledispatchmethod()` dropped its parens, matching
  `functools.singledispatch` two paragraphs earlier and the bare-decorator
  convention in chapters 33 and 41; "so the first dispatch never happens" is
  now "so the resolution on `self` no longer distinguishes them", which is
  more precise (the resolution still runs; it stops mattering).
- "the size of the behavior never forces the choice" is now "does not force
  the choice"; "The test imports neither hierarchy by name" is now "imports
  the two modules, not their classes" (it does import the modules); the
  fail-fast sentence now says exercise 1 "puts you in that situation" rather
  than claiming the exercise demonstrates the `KeyError`, which it never
  shows.
- Exercise 7: dropped "using *Multiple Dispatching*" and added "Single
  dispatch is enough here; the next exercise adds the second dispatch". The
  solution deliberately implements single dispatch and says so, deferring
  the second dispatch to exercise 8; the exercise now matches that staging.
  The alternative, rewriting solution 7 into real double dispatch, would
  duplicate exercise 8.
- Solution 2's counts corrected against the code: `Lizard` needs a
  `compete()` plus *four* `eval_*()` methods (not "three more"), the classes
  encode *sixteen* answers (not "the same nine numbers"), and the method
  version's cost is five new methods on `Lizard` plus the retrofits.
- Solution 4: `item_pair_gen()` regains `arena.py`'s generic signature
  (`[T](base: type[T], ...) -> Iterator[tuple[T, T]]`), since the exercise
  modifies `arena.py` in place and the solution had silently degraded it to
  `type`/`Any`.
- Ran `make reflow CH=32` over the edited prose.

## Considered and declined

- No listing for `singledispatchmethod` or the `isinstance()` ladder: "One
  Type or Many" is a comparative section, and a third and fourth
  implementation of the same game would cost more than the prose warnings
  teach.
- Comparison operators also swap operands (`__lt__`/`__gt__` mirror each
  other), but they have no `r`-prefixed forms; the chapter's "every
  arithmetic and bitwise operator" claim is accurate as scoped, and adding
  comparisons would widen the section past its point.
- "The match is on classes exactly" keeps "exactly": a precise match claim,
  and solution 6 quotes the phrase.
- Exercise 6's "say which of the two properties ... you have just given up"
  stays singular even though the fail-fast property erodes too: the direct
  answer is exact matching, and the solution derives the erosion as a
  consequence, which is the right teaching order.
- The trace comments' past tense ("self was Paper") stays: they narrate the
  dispatch that just resolved.
- `duel()` keeps `Any` rather than gaining a `Competes` protocol: the
  Protocol option is priced one listing later in the `Any`-cost paragraph,
  and a protocol in the first helper file would front-load machinery.
