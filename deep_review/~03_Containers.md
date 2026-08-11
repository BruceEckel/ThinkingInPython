[[Reviewed]]
# Deep review: 03_Containers

> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Chapter 03 is in strong shape: every listing runs clean, every `#:` marker
matches, the section order (lists, tuples, dicts, sets, specialized,
immutability) builds correctly, and the exercises cover every section. The
findings were all small enough to decide, so everything this review found is
in the applied-directly list, and the review's one standing question (the
`deque_timing.py` threshold, carried as an open item in `deep_review_db.md`)
is resolved with measurements from this machine under Considered and
declined. No blocks need a decision.

## Applied directly

- Intro: `in`, `len()`, and slicing were claimed to work on all three
  literals shown; slicing works on neither a `dict` nor a `set`. Reworded so
  slicing applies to the sequences only.
- Lists: added `remove_while_iterating.py` (four lines, `#: [2, 4]`) so the
  remove-while-iterating trap is demonstrated instead of asserted; the prose
  already explained the mechanism, and now the surprising half-survives
  output backs it.
- Dictionaries: gave *hash* a first-use gloss (a small integer derived from
  the key's contents that says where the entry lives); the word previously
  arrived cold and the immutability section leaned on it.
- Dictionaries: the `for name, age in ages` slip now states its consequence:
  `ValueError` for `"Alice"`, and the nastier silent unpack into letters for
  a two-character key.
- Dictionaries (`dict_ops.py`): `zip()` was used before the book teaches it
  (chapter 04); added a sentence saying `dict()` accepts any iterable of
  pairs and pointing `zip()` at [Control Flow](../Chapters/04_Control_Flow.md#loops).
- Sets: added the single-element methods (`add()`, `remove()`, `discard()`)
  with the `remove()`-raises/`discard()`-stays-silent contrast; the chapter
  showed set mutation nowhere, yet exercise 4 asks the reader to call
  `groups.add()`.
- Sets (`membership_cost.py`): `lambda` was used before the book teaches it
  (chapter 05); the `timeit()` intro sentence now glosses `lambda:` and
  links the Functions chapter.
- Sets: noted that the probe value is missing on purpose, the list's worst
  case (a full scan before giving up).
- Sets/deque: moved the `report()`/`--numbers` explanation paragraph from
  after `deque_timing.py` up to `membership_cost.py`, the book's first
  measured listing (checked: no earlier chapter imports `benchmark`), so
  `report()` is no longer used two listings before it is explained.
- deque: added the reverse trade-off, indexing a `deque`'s middle is O(n),
  so it does not replace a `list` you index by position; without it the
  section reads as "deque is a strictly faster list at the ends".
- Immutability: "`frozendict` ... completes the set" now reads "completes
  the trio"; in a chapter where `set` is a type, the pun garden-paths.

## Considered and declined

- **`deque_timing.py`'s `* 20` threshold stays.** This resolves the open
  item in `deep_review_db.md` (a past review proposed `* 50`, pending
  measurement on Bruce's machine). Measured here, five standalone runs:
  list/deque ratios 82, 83, 83, 86, 93. `* 50` would leave under 2x
  headroom on this machine and the self-healing gate would flip the marker
  under load; `* 20` keeps roughly 4x. (`membership_cost.py`'s `* 100` was
  also measured: ratios 5000+, ample.)
- **`heterogeneous.py`'s three same-shape prints stay.** Collapsing them
  into the `for item in person` loop from `mixed_types.py` would be denser,
  but the one-print-per-position form is the point (each position, its own
  meaning and type) and it quietly demonstrates tuple indexing.
- **No `KeyError` demo in the dict listing.** `dict.get()` versus `[]` is
  stated in prose; raising and catching a `KeyError` would repeat the
  exception machinery three listings in a row for no new insight.
- **The set-order sentence does not name the dict contrast.** "The order
  these sets print comes from CPython's hashing, not from any guarantee"
  sits two sections after "A `dict` iterates in insertion order, which the
  language guarantees"; wiring them together adds a cross-reference where
  proximity already does the work.
