When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/35_Flyweight.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on `build/examples/35_Flyweight`
(5 tests), and both runnable scripts run. Every runtime and checker claim
was probed individually on the pinned 3.15.0b4 interpreter and all hold:
the small-int cache's first uncached positive value is 1025, matching
"caches up to 1024" and the choice of `100000`; literal `100000 is 100000`
compiles to `True` via constant pooling (with the `SyntaxWarning` the
prose mentions); four threads missing on one `@cache` key each ran the
function and each kept their own object (4 distinct results), matching
the thread-race paragraph and exercise 8's `4 4` marker in
`Solutions/35_Flyweight.md`; an enum that sets `_value_` in `__init__`
instead of `__new__` leaves the value-lookup table keyed by the member
tuples (`Tile(".")` fails with `ValueError`, `Tile((".", True))` works),
matching the "must happen in `__new__()`" paragraph; a
`slots=True` dataclass without `weakref_slot=True` makes the
`WeakValueDictionary` insert raise a `TypeError`, matching the collision
note; and `sys.intern()`'s no-lifetime-extension claim matches the
documented behavior (interned strings are not immortal; keep a reference
to benefit). The `to_symbol()` boundary idiom is in its current
post-ty-0.0.63 form (guard, no `cast()`) and checks clean on the pinned
0.0.70. The figure `resources/images/flyweight_tiles.svg` exists, the
three anchors other chapters target (`#python-uses-flyweights`,
`#typing-the-symbol-set`, `#interning-in-the-constructor`) are intact,
and the Solutions file covers all eight exercises. No finding needs a
decision, so this file has no live blocks; everything found was either
applied directly or recorded below as considered and declined.

## Applied directly

- "Intrinsic and Extrinsic State": named `[*row for row in field]` as
  the comprehension unpacking from chapter 16, with a link to its
  Unpacking in Comprehensions section. This chapter is the book's only
  use of the PEP 798 form outside chapter 16, and it appeared
  unremarked.
- Same section: "The listing can show the object count" is now "shows";
  the modal added nothing to the contrast the semicolon already draws.
- Frozen discussion: "`frozen=True` has to hold all the way down" is now
  "must hold" (watch-list "has to").
- "Interning in the Constructor": added the sentence explaining why
  `Color(220, 20, 60)` survives with no `__init__()` defined: the call
  still reaches `object.__init__()`, which accepts and ignores the three
  arguments because the class overrides `__new__()` and not
  `__init__()`. Probe-verified in both directions (a `__new__`-only
  class tolerates the extras; a class overriding neither raises a
  `TypeError`). The question the paragraph raises ("where do the
  arguments go, then?") previously went unanswered here and in
  Singleton.
- Same section: rewrote the `defaultdict` sentence to give the real
  reason it cannot replace `_pool` (its `default_factory` is called with
  no arguments, so it cannot see the components the missing `Color`
  needs). The old wording, "needs the three color components, not just
  the key that names them," misled twice over: the factory does not
  receive the key either, and the key here is the three components.
- "A Pool That Does Not Leak": replaced "bounded memory with fixed
  construction cost" (unclear on first and second reading) with "a
  bounded pool," and added the probe-verified caveat that eviction
  weakens the sharing guarantee: a value rebuilt after eviction is equal
  to any surviving original but not the same object, a pair the weak
  pool cannot produce because its entry lives as long as anyone holds
  the object. Without this, the paragraph recommends
  `lru_cache(maxsize=n)` right after the chapter taught readers to
  trust `is` for pooled types.
- Same section: "The two techniques in this chapter collide at one spot"
  is now "They collide at one spot"; `slots=True` is chapter 18's
  technique, not this chapter's.
- Ran `make reflow CH=35` over the edited prose.

## Considered and declined

- "Equal means identical, so `==` collapses to a pointer check": for
  *unequal* interned strings CPython still runs a length check, so the
  collapse is strictly the success path. The sentence states the
  property that matters (equality between interned strings is decided by
  identity), and qualifying it would blur the point it makes.
- "Calling `int("...")` on a string, not a literal, matters here" is
  compressed, but the two sentences that follow unpack it fully;
  rewording adds words without adding clarity.
- The heading "Which Pool Should You Use?" contains a modal, which the
  heading-style rule frowns on, but "Which X Should You Use?" is the
  book's established decision-section convention (chapters 22, 24, 27,
  31); renaming one instance would break the set.
- Section order: "Which Pool Should You Use?" before "Flyweights in the
  Wild". Both orders are defensible; the decision guide closes the
  four-mechanism arc and the wild sightings read as a widening coda, so
  a swap buys nothing.
- `print(len(Color._pool))` reads a private attribute from module-level
  demo code, as does `test_weak_pool.py` with `_pool`. Inspecting the
  pool is the demo's point; a public accessor would be machinery the
  chapter would then have to explain.
