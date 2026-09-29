> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 41_Functional--Toolkits, second round (2026-09-29)

This run follows the 2026-09-25 review (`~41_Functional--Toolkits.md`) and the
five commits made to the chapter since: the `stranger`/`host` rename, the
two-sentence opener, its blockquote form, the 2026-09-27 fix triage, and
c9db3b8c, which split the demos out of `student_pairs.py`.
Nothing here needs your decision, so the file has no live blocks.

Every quoted message and count was probed on the pinned 3.15.0rc2 and `ty`
0.0.84: the `reduce()`, `batched(strict=True)`, `zip(strict=True)`, `islice()`,
and `min()` errors, `partial(pad, 5)` failing with the `AttributeError` the
prose quotes, `list(groupby(data))` giving three empty groups, `del x.squared`
recomputing, and exercise 3's fifteen integers.
The `tee()`, `product()`, `cycle()`, `cached_property`, and cache claims were
read against the 3.15 documentation.
No claim in the chapter was false at runtime; one overstated the documentation
(`tee()`), and one instruction was wrong as written (`groupby()`).
`tip verify-ch CH=41` passes 24 of 24.

## Applied directly

Corrections:

- `groupby`: "`sorted(data, key=keyfunc)` before `groupby(data, key=keyfunc)` is the fix" passes the unsorted `data` to `groupby()`, since `sorted()` returns a new list. Now `groupby(sorted(data, key=keyfunc), key=keyfunc)`, with a sentence saying why.
- `tee`: "handing them to separate threads corrupts it" overstated the 3.15 documentation, which says simultaneous use may raise a `RuntimeError`. Now says that, matching the wording chapter 23's review gave the same sentence.
- `singledispatch`: "A keyword-only argument cannot select the implementation either" missed the failure a reader meets. The dispatch argument must be passed by position: `describe(value=5)` raises `TypeError: describe requires at least 1 positional argument` (probed).
- `cache`: "runs those effects on the first call and never again" is true per set of arguments, not per function. Now says so.
- `zip(strict=True)`: the quoted message is the one for a shorter second argument; a longer one reads "longer than". The sentence now ties the message to the two lists in the listing.
- Opening roadmap: "A case study closes it" was not true, since "Choosing From the Toolkits" follows the case study. Now "A case study then puts...".
- `cache`: the *lapsed listener* link pointed at the H2 "The Pythonic Observer"; the leak is taught in its subsection. The link now goes to `#lapsed-listeners`.

Damage from edits made after the first review:

- The end of the `functools` section: "`itertools` does the same for iteration" follows the `singledispatchmethod` paragraph, so "the same" read as dispatch. Now "`itertools` does for iteration what `functools` does for functions".
- Case study opening: the triage rewrite left "A small program solves it", with no noun for "it". Now "solves this scheduling problem by combining several of the chapter's tools".
- After the split (c9db3b8c), the `small_roster.py` paragraph describes lines of `group_rounds()`, which now sits three listings back. It names the function.
- Same commit: "the same join-instead-of-sit-out choice `pair_rounds.py` makes" credited the demo with a choice `group_rounds()` makes. Now "the choice `pair_rounds.py` shows for pairs".
- `partial`: the triage cut the sentence that linked chapter 40's `Placeholder` section, which left `Placeholder` named with no example and no pointer. The term is now the link, with no added sentence.

Teaching additions:

- `cache`: the entry never said arguments must be hashable, though exercise 5 and the case study both depend on it. Added, with the `TypeError` message.
- `cached_property`: a reader who has used `@record` since chapter 18 would put `cached_property` on one and get a `TypeError` (probed). A short paragraph says so, links `slots_limits.py`, and says why `Lazy` is a `@dataclass`.
- `cmp_to_key`: the demo's ordering has a simpler form, `sorted(words, key=len, reverse=True)`. The entry now says so and says when a comparator is the right tool.
- `starmap`: the lookalike is `map()` with two iterables, which the `repeat` entry uses. One sentence contrasts `map(pow, [2, 3], [5, 2])` with arguments that arrive paired.
- Recursion: chapter 18 links here for "tail-call optimization of Python functions, which CPython does not do", and the positive pass had removed the term. It is back, as the name for what other languages do with a call in tail position.
- Solutions 5: the listing carries two `# type: ignore` comments the prose never mentioned. `ty` reports `invalid-argument-type` ("Expected `Hashable`, found `list[Nested]`") on both calls, so the checker catches the mistake before the run. A paragraph says so and says why the comments are there.

House style:

- `functools_partialmethod.py`: `Text` is never mutated, so it is now a `@record` (probed: `partialmethod` and `partial` both work on a slotted frozen class, and `partial(pad, 5)` fails with the same `AttributeError`).

Prose:

- `wraps`: "`wraps()` is what copies" is now "`wraps()` copies"; "a tool that wants the original" is now "needs".
- `cached_property`: "find an empty slot" is now "find no stored value". "Slot" next to `cached_property` reads as `__slots__`.
- `islice`: "Give it an iterator, and that iterator resumes..." was an imperative followed by its consequence. Now "An iterator you pass to `islice()` resumes...".
- Pipeline: "that one value was a batch" is now "is".
- `history` Is Mutable State: "which pair sits where in round `r` follows from `r` alone" now opens with "in the circle method", since the clause before the colon names both methods.
- Solutions 4: "everything `groupby()` is buying" is now "the streaming `groupby()` provides". Solutions 6: dropped "exactly" from "exactly as before".

## Considered and declined

- The triage also cut "[Classes](07...#cached-property) covers it alongside `@property`" from the `cached_property` entry. The entry stands without it, and the new paragraph links chapter 18 for the one failure the reader needs. Not restored.
- `total_ordering`: the Python documentation says "all six rich comparison methods", counting `__ne__`. The chapter's "five" was settled in the 2026-09-14 claims sweep (`__ne__` comes from `__eq__` by default). Left.
- `singledispatch` follows the MRO, so `describe(True)` takes the `int` implementation. Chapter 33 teaches "Dispatch follows inheritance", and this entry links it. Not repeated here.
- `lazy.py`'s output cannot tell lazy evaluation from computing five values eagerly, since all five `computing` lines print before the list. The `list(squares())[:5]` paragraph carries the contrast. Left.
- `count`, `cycle`, `pairwise`, `compress`, and `filterfalse` have one line of prose or none. They are catalog entries, and each listing makes its point.
- "These tools are already written and already correct" and its `itertools` twin use "already" twice each. The repetition is the rhetoric of both openings. Left.
