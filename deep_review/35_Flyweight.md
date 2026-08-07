When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter-level: the chapter argues memory and never shows a number.**

Every claim about what Flyweight buys is stated, never measured.
"A map can hold millions of cells, but only a handful of tile kinds."
"Memory proportional to the number of distinct values, not the number of uses."
The only real number in the chapter is `24 3`, an object count.
The one place the book actually weighs a shared map against an unshared one is
`Solutions/35_Flyweight.md` exercise 2, which the reader reaches only after
finishing the chapter and only if they do the exercise.

The deep-review skill's "front-load the payoff" test applies:
the most convincing artifact is outside the chapter entirely.

Proposed change, recommended form:
a short listing immediately after `tile_map.py`'s commentary that measures the
same 24-cell grid two ways, using `sys.getsizeof()` rather than `tracemalloc`
so the number is deterministic and the marker is stable.
Something like:

```python
# tile_memory.py
import sys
from tile_map import Tile, parse_map

def footprint(cells: list[Tile]) -> int:
    unique = {id(t): t for t in cells}
    per_object = sys.getsizeof(next(iter(unique.values())))
    per_dict = sys.getsizeof(next(iter(unique.values())).__dict__)
    return len(unique) * (per_object + per_dict)
```

I have deliberately not drafted this as a finished listing, because where it
goes and whether the chapter wants a measurement at all is a pacing decision.
Two things to know if you take it:
`sys.getsizeof(Tile(...))` is 48 bytes and its `__dict__` another 280 on the
pinned 3.15 build, so a shared 24-cell grid costs 3 x 328 against an unshared
24 x 328, which is a clean 8x with no timing involved;
and the alternative (drop it, and instead point at exercise 2 from the prose)
costs one sentence and no listing.

---

[] Reject

**"Intrinsic and Extrinsic State": the typing discussion is a 19-line
digression inside the chapter's flagship section.**

Between `tile_map.py` and its test sits a block that starts at
"`Symbol` names the closed set of valid map characters" and ends at
"`cast()` is believed rather than verified."
It is good material and chapter 08's `cast(T, x)` table row links directly to
this section for it.
But it is about `Literal`, boundary functions and narrowing, not about
intrinsic versus extrinsic state, and a reader following the pattern has to
push through it to reach "Because `Tile` is frozen, sharing is invisible to
clients," which is the section's actual conclusion.

Proposed change: give it its own `###` heading, e.g.
`### Typing the Symbol Set`, placed exactly where the block already begins.
Price of the rearrangement: nothing moves, so no listing or test is affected;
the existing `#intrinsic-and-extrinsic-state` anchor is unchanged, so chapter
08's link and `heading_links.py` stay green; the new heading only adds an
anchor.
The alternative is to move the block after the test listing so the frozen
paragraph follows the code directly, but that separates the typing prose from
the code it describes, which is worse.

---

[] Reject

**`tile_map.py`: a memory chapter whose shared object still carries a
`__dict__`.**

`thinking-in-python-skill.md` says to pair `@dataclass(frozen=True)` with
`slots=True` "for the memory and access-speed win (the dropped `__dict__`)."
`Tile` does not.
Neither do the other 86 `frozen=True` dataclasses in `Chapters/`, so this is
not drift, it is a book-wide default, and I did not change it.

It is conspicuous *here* specifically, though, because this is the chapter
about object memory, and the two techniques are complementary in a way worth
one sentence: Flyweight cuts the number of objects, `slots=True` cuts the size
of each one. Measured on the pinned 3.15 build:

    @dataclass(frozen=True)              48 bytes + 280 byte __dict__
    @dataclass(frozen=True, slots=True)  40 bytes, no __dict__

There is also a genuine trap at the intersection of the chapter's own two
techniques, which nothing in the book currently mentions:

    @dataclass(frozen=True, slots=True)
    class Symbol:
        name: str
    ...
    _pool[name] = found
    TypeError: cannot create weak reference to 'Symbol' object

A slotted class has no `__weakref__` unless you also pass `weakref_slot=True`,
so slotting `weak_pool.py`'s `Symbol` breaks the weak pool outright.
Verified both, three runs each.

Recommended: leave the listings alone and add two sentences to
"A Pool That Does Not Leak," after the `weak_pool.py` commentary, naming
`slots=True` with a link to [Performance](18_Performance.md#slots) and the
`weakref_slot=True` requirement.
(Chapter 18's `### Slots` subsection already states "`frozen=True` does not
imply `slots=True`", so the two ends would agree.)
Alternatives: (a) add `slots=True` to `Tile` and `slots=True,
weakref_slot=True` to `Symbol` with the prose to explain both, which is the
most honest version but makes this chapter the only one in the book that
slots its dataclasses and puts `Solutions/35_Flyweight.md`'s inline copies out
of step; (b) do nothing, on the grounds that chapter 18 owns `slots`.
I recommend the first because the `weakref_slot` interaction is a real bug a
reader will hit the first time they combine the two ideas this chapter
teaches.

---

[] Reject

**`interned_color.py`: `_pool` is shared across subclasses and keyed only by
RGB, so a subclass can receive a base-class instance.**

Verified on the pinned build against the chapter's own listing:

```
class Warm(Color): pass
c = Color(220, 20, 60)
w = Warm(220, 20, 60)      # -> the existing Color, not a Warm
print(type(w).__name__)    # Color
c2 = Color(1, 2, 3)        # after Warm(1, 2, 3): -> the existing Warm
print(type(c2).__name__)   # Warm
```

Whichever class asks first owns the entry, and every later caller of any class
in the hierarchy gets that object.
`Tile`'s `@cache` factory has no equivalent problem, because `tile()` is a
function with no subclass to inherit it.

The chapter never says `Color` is not designed for subclassing, and the
`__new__()` interning idiom is exactly the one a reader will copy into a class
that *does* get subclassed.
This is also the one place where "the `@cache` factory does the same job with
less machinery" is understated: the factory has one fewer way to go wrong.

Two fixes. I recommend the second.

- Key the pool by class: `key = (cls, red, green, blue)`, with
  `_pool: ClassVar[dict[tuple[type[Color], int, int, int], Color]]`.
  Correct, but it widens the listing's type noise for a case the chapter is
  not otherwise about.
- One sentence of prose after "The cost is bookkeeping by hand.":
  "`_pool` is keyed by the components alone and inherited by every subclass,
  so `Color` here is a leaf: a subclass would collide with it. Key the pool by
  `(cls, red, green, blue)` if you need to subclass."

Reported rather than applied because either one changes what the listing
claims about itself, and the second is a voice call.

---

[] Reject

**"Interning in the Constructor": chapter 39's Multiton row links here, and
the word never appears in the chapter.**

`Chapters/39_Pattern_Catalog.md:150` has

    | [Multiton](35_Flyweight.md#interning-in-the-constructor) | Manage a fixed set of named singletons. |

A reader who follows that link lands in a section that never uses the term, so
the catalog entry resolves to nothing.
The structure genuinely is Multiton (a registry of singletons keyed by value
rather than one global instance), so the fix belongs in 35, not in 39.

Proposed change: one sentence after
"Here the cache is keyed by the constructor arguments instead of a single
fixed key", e.g.

> A pool of singletons keyed this way is sometimes called *Multiton*.

Reported rather than applied because
`thinking-in-python-skill.md` says to name a pattern only when the structure
earns it, and whether this one earns a proper noun in your book is your call.
If you would rather not name it, the alternative is to retarget 39's row at
[Singleton](24_Singleton.md) instead, which I did not do because I may not
edit chapter 39.

---

[] Reject

**"A Pool That Does Not Leak": `weak_pool.py`'s `Symbol` collides with
`tile_map.py`'s `Symbol`, in the same chapter.**

`tile_map.py` has `type Symbol = Literal[".", "~", "#"]`, a type alias naming
map characters.
`weak_pool.py` has `class Symbol` with a `name: str`, a parser's interned
identifier.
Different kinds of thing, same word, ~150 lines apart, both extracted into the
same `Examples/35_Flyweight/` directory.
Nothing breaks (separate modules), but a reader skimming back for "what was a
`Symbol` again" finds two answers.

Proposed change: rename the weak-pool class to `Name`, with `_pool:
Final[WeakValueDictionary[str, Name]]` and `def name(text: str) -> Name`.
Cost: `test_weak_pool.py` in the chapter, plus `Solutions/35_Flyweight.md`
exercise 5, which uses the technique but defines its own `Color`, so it is
probably unaffected. Check before applying.
Alternative: leave the code and add "(this `Symbol` is the parser's, not
`tile_map.py`'s type alias)" to the prose, which is cheaper and uglier.
Reported rather than applied because renaming a listing's public name is not
mine to decide.

---

[] Reject

**"A Fixed Set: Enum": the section shows a second, different `Tile` without
saying it is the same tile.**

`tile_enum.py` defines `class Tile(Enum)`; `tile_map.py` defines a frozen
dataclass `Tile`. The section opens on the general principle
("When you know the full set of shared values as you write the program, you do
not need a pool at runtime") and goes straight into the listing.
The comparison is real and good, but it arrives four paragraphs later, at
"`tile()` could load `SPECS` from a file, while `Tile.GRASS` is source code."

Proposed change: one clause on the section's opening, so the reader knows they
are looking at the same domain rebuilt, e.g.

> Python constructs each member once, at class creation,
> and any reference produces that one object.
> Here is `tile_map.py`'s `Tile` again, with the pool moved into the language:

Reported rather than applied because it is the section's opening line and that
is voice.

---

[] Reject

**"A Fixed Set: Enum", last paragraph: "The constraint is less flexibility."**

The sentence is grammatical but the noun is doing no work; the chapter
elsewhere writes the plain form ("The cost is bookkeeping by hand.").
Suggest "The cost is flexibility." so the two trade-off sentences in the
chapter read the same way.

---

[] Reject

**"Flyweights in the Wild": "equality checks that collapse to identity" is
true of interned strings and not of the chapter's own `Tile`.**

`Tile` is a frozen dataclass, so `==` runs the generated `__eq__()` and
compares three fields; it does not become a pointer check just because the
objects happen to be shared.
The collapse is available (`is` answers correctly for a perfectly interned
type, which the chapter says of `Color`), but it is something the caller opts
into, not something interning does for them.

Proposed change: "...and, for a type where every instance comes from the pool,
equality checks you can write as `is`."
This also closes the loop with the new paragraph in "Interning in the
Constructor" about `tile()` interning only the calls that go through it.

---

[] Reject

**"Flyweights in the Wild" is a catalog, not a conclusion: the chapter never
helps the reader choose between the four pools it taught.**

The chapter shows four mechanisms: a `@cache` factory, a `__new__` pool, a
`WeakValueDictionary` pool, and an `Enum`.
Each is explained where it appears, and the trade-offs are scattered across
four sections.
Nothing gathers them, and the neighbouring chapters do exactly that:
24 "Which Should You Use?", 27 "Which Factory Should You Use?",
30 "What Stayed Constant", 26 "One Surrogate, Two Intents".

The deep-review skill's test is whether the reader can name a new capability
at the end. Right now they can recognize Flyweight; they cannot pick a pool.

Proposed change: a short section before "Flyweights in the Wild", titled for
its content, e.g. `## Which Pool Should You Use?`, four sentences, one per
mechanism, organized by the question that decides it:

- Is the value set known at compile time? `Enum`.
- Must callers keep writing `C(...)`? An interning `__new__()`.
- Is the value set unbounded? `WeakValueDictionary`.
- Otherwise, a `@cache` factory.

Reported rather than drafted, since a new section changes the chapter's pacing.

---

[] Reject

**Exercises: two of the chapter's sections have no exercise, and one of them
is the section a reader is most likely to get wrong in production.**

Coverage today: 1, 2, 3 exercise `tile_map.py`; 4 is a design exercise;
5 and 6 exercise `interned_color.py`.
Nothing exercises "A Fixed Set: Enum", and nothing exercises the thread race,
which is the chapter's only warning about a bug that survives every gate the
book runs.

Proposed additions:

> 7.  Rewrite `tile_map.py` on top of `tile_enum.py`'s `Tile`, so `parse_map()`
>     returns `list[list[Tile]]` of enum members and `to_symbol()` disappears.
>     What does the checker now catch that the `Literal` version caught, and
>     what does it catch that the `Literal` version did not?
>
> 8.  Make `tile()`'s body slow (a `time.sleep(0.05)` before it builds the
>     `Tile`) and call it from four threads with the same, previously unseen
>     symbol.
>     How many `Tile` objects get built, and how many distinct objects do the
>     four threads hold?
>     Fix it two ways: populate the pool eagerly at import, and guard the
>     factory with a `threading.Lock`.

Exercise 8's outcome I verified: with a 0.05s body, four threads on a cold key
built four objects and each thread kept its own, so `is` fails between all
four.

---

## Cross-chapter (not edited, per the review's scope rules)

[] Reject

**`Solutions/35_Flyweight.md`: the two test files are named for the old
chapter number.**

They are `test_ch36_mutation_leak.py` and `test_ch36_out_of_range.py`, in
`Solutions/35_Flyweight.md`.
The convention everywhere else is `test_chNN_` matching the chapter
(`test_ch11_transfer.py`, `test_ch23_filter.py`), so these are leftovers from
the renumbering that moved Flyweight from 36 to 35.

This is not unique to my chapter, so it wants one sweep rather than a local
patch. The full set of mismatches in `Solutions/`:

    Solutions/35_Flyweight.md               test_ch36_mutation_leak.py
    Solutions/35_Flyweight.md               test_ch36_out_of_range.py
    Solutions/36_Memento.md                 test_ch37_erase_mutable.py
    Solutions/36_Memento.md                 test_ch37_erase_frozen.py
    Solutions/42_Functional_Error_Handling.md  test_ch14_combined.py

Renaming touches the fenced `# slug.py` first lines and then needs
`make prune-examples` for the orphaned files under `Examples/`, per CLAUDE.md.

---

[] Reject

**`Solutions/35_Flyweight.md`, exercise 1: an inline copy of `tile_map.py`
that will drift.**

`exercise_1.py` re-declares `Symbol`, `Tile`, `SPECS`, `tile()`, `to_symbol()`
and `parse_map()` verbatim from the chapter, plus two symbols.
Nothing imports the chapter's module, so nothing catches divergence.
None of the edits I applied touch code, so the copy is still accurate today,
and `Solutions/35_Flyweight.md`'s hand-fix for the ty 0.0.63 literal-narrowing
change is intact (`to_symbol()` has the `raise KeyError(char)` guard and no
`cast()`).
Flagging it only because any future change to `tile_map.py`'s listing — the
`slots=True` proposal above is the live candidate — has to be mirrored here by
hand, and there is no gate that will tell you.

---

[] Reject

**`Chapters/08_Static_Typing.md:614`: the `cast(T, x)` table row points at a
section that argues against `cast()`.**

    | `cast(T, x)` | Tells the checker to treat `x` as `T`, see [Flyweight](35_Flyweight.md#intrinsic-and-extrinsic-state) |

The linked section contains no `cast()` call.
It contains `to_symbol()`, which exists to demonstrate the guard you write
*instead* of a `cast()`, and closes with "Keep `cast()` for the cases where no
guard exists, because `cast()` is believed rather than verified."
That is a useful destination, but the row promises an example of the thing.

Change I would make in `Chapters/08_Static_Typing.md`: say what the reader
will find, e.g. "Tells the checker to treat `x` as `T`; [Flyweight](
35_Flyweight.md#intrinsic-and-extrinsic-state) shows the runtime guard to
prefer over it."
If the `### Typing the Symbol Set` subsection above is adopted, retarget the
link at that anchor at the same time.
I did not touch chapter 08, per the scope rules.

---

[] Reject

**MANIFEST — not a proposal. Applied to `Chapters/35_Flyweight.md` in this
pass, in reading order. All prose; no listing, marker or test changed.**

1.  "Python Uses Flyweights", after "builds a fresh one": added four lines
    explaining that the small-integer cache range is build-dependent (`-5`
    through `256` is the usual quote, this build caches to 1024) and that this
    is why the uncached example is `100000` and not `257`. Verified: `257`,
    `1000` and `1024` all return cached objects here; `1025` and up do not.
2.  After `tile_map.py`, following "Twenty-four cells, three objects": added
    four lines on why the listing counts `id(t)` and not `len(set(cells))` —
    `Tile`'s generated `__eq__()` compares field values, so a plain set
    collapses to three whether the tiles are shared or not. Verified: adding
    an unshared `Tile("~", "water", False)` to the cells leaves
    `len(set(...))` at 3 while the id-set goes to 4.
3.  End of the `to_symbol()` paragraph: rewrote "so `char not in SPECS`
    failing to raise an exception leaves `char` narrowed to `Symbol` on the
    line below" as "so reaching the line below means `char not in SPECS` was
    false, which narrows `char` to `Symbol`". The old phrasing made the
    expression, rather than the `if` body, the thing that raises.
4.  End of "Intrinsic and Extrinsic State", after "Mutating the grass tile in
    one cell changes every grass cell in the map": added a paragraph that
    `frozen=True` has to hold all the way down, with a link to
    `20_Rethinking_Objects.md#the-immutability-solution` (where `frozen_leaky.py`
    lives), and a note that every `Tile` field is already immutable.
5.  `interned_color.py` commentary: replaced "This rules out `@dataclass`,
    whose generated `__init__()` reintroduces that re-run" with a version that
    says when the re-run actually bites — invisible while it re-assigns the
    same components, a real bug once a field has a `default_factory` or
    `__post_init__()` has a side effect. Verified: `@dataclass(frozen=True)`
    plus a pooling `__new__()` interns correctly, and a `default_factory` list
    field loses its accumulated contents on the second construction.
6.  Same paragraph: replaced the `@dataclass(init=False)` parenthetical
    ("at the price of still more care with the by-hand field assignment")
    with the two concrete costs — the generated `__eq__()` sets `__hash__` to
    `None` unless you also pass `frozen=True`, and `frozen=True` then forces
    `object.__setattr__()` inside `__new__()`. Verified both.
7.  New paragraph before "Unless you need the constructor syntax": `tile()`
    interns only the calls that go through it, so `Tile("~", "water", False)`
    still builds a separate object, while `Color(...)` has no such gap.
    Reworded the closing sentence to "the constructor syntax or that
    guarantee". Verified: the direct `Tile(...)` is `==` to the pooled water
    tile and not `is` it.
8.  Thread-safety paragraph: added that `@cache` is not exempt — the lookup,
    the call and the store are three steps, so threads that all miss on the
    same key each keep their own result. Verified: four threads, one cold key,
    a 0.05s function body, four objects built and four distinct objects
    returned.
9.  "A Pool That Does Not Leak": `weakref.WeakValueDictionary` now carries a
    named link to [Cleanup](10_Cleanup.md#reliable-alternatives), where
    `weak_value.py` introduces it, instead of appearing as if new.
10. "Flyweights in the Wild": "Column stores such as Pandas and Polars" ->
    "Dataframe libraries such as Pandas and Polars". Pandas is not a column
    store; the term means a database.

After the edits, `reflow_prose.py --diff` reports the file clean,
`heading_links.py` and `banned_phrases.py` pass, and against
`build/private/35`: `validate_output.py` 1 ok / 0 failed, `ruff` clean,
`ty` clean, `pytest` 5 passed.
No `#:` marker was rewritten by the gate at any point.
