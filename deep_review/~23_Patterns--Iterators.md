> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 23_Patterns--Iterators (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the chapters it links (5, 14, 16, 18, 19, 20, 21, 41, 45), the committed `#:` markers, `ty` 0.0.84 and Pyright 1.1.414 probes, `ruff` with every rule selected, the GoF text, and the 3.15 `itertools.tee()` documentation.
`tip verify-ch CH=23` passes 24 of 24.

## Applied directly

Chapter, corrections:

- `generator_memory.py`: `lazy_peak, _ = tracemalloc.get_traced_memory()` bound the current size, since the call returns `(current, peak)`. Both measurements now unpack `_, lazy_peak` and `_, eager_peak`, so the names and the prose ("the generator's peak") match what is measured. The marker is unchanged (488 bytes against 40 million).
- `tee.py`, lockstep block: the reading was the current size after the loop ended, when both branches are spent and the buffer is free, so it could not show that `tee` "never buffers more than the gap". It now reads the peak (4,768 bytes against the list's 4 million). The drained-branch reading stays the current size, which is what `tee` holds at that moment.
- "What `tee()` Buffers": "handing them to separate threads corrupts it" overstated the 3.15 documentation, which says simultaneous use may raise a `RuntimeError`. The sentence now says that.
- "Iteration Comes Built In": "the one case where the loop and the type checker disagree" was wrong for `ty`, which accepts the `for` loop over a `__getitem__()`-only class and rejects it as an `Iterable[T]` argument. Now "the one case where an object a `for` loop accepts fails an `Iterable` annotation."
- "An Exhausted Generator Is Silently Empty": "`Collection[T]` and `Sequence[T]` ask for more than iteration, and no iterator supplies it" is false for an iterator class that defines `__len__()`. Now names the requirement: they "also require `__len__()`, which no generator has."
- "A Type-Checking Iterator": two wrappers over one source share one cursor, so "each sits at a different point in the stream" was wrong. Now "each has delivered different items" (verified: the two compare equal).
- `test_iterators.py` comment: "`__iter__` yields a fresh generator" is now "`__iter__()` builds a fresh generator". The method returns the generator; the generator yields.
- Exercise 5 pointed to "the rule that closes that section", but the section now closes on the threading paragraph. It points to "that section's rule for what `tee` buffers."

Chapter, teaching:

- "Asking Consumes an Item": added the near-miss `"c" in letters` to `asking_costs.py` and two sentences of prose. A membership test on an iterator consumes every item up to and including the match.
- "The Pattern That Disappeared": the prose now gives GoF's own names (`First()`, `Next()`, `IsDone()`, `CurrentItem()`) and says why the listing calls `Next()` `advance()`.
- `generator_memory.py` lead-in: `squares()` returns a generator expression in a section that has taught only `yield`. The lead-in now names the form and links chapter 16. It replaces "Measure it:".
- "The Protocol Answers Nothing": the closing line "The protocol costs you nothing, and tells you nothing" contradicted "Each question costs an item" two sections earlier. It is now "The protocol stores nothing, so it answers nothing in advance," followed by one sentence tying the buffers of `tee`, `OverStream`, and the peekable wrapper to that rule. Revert this one from the diff if you want the original line back.

Chapter, prose:

- "The `print` at the top fires" is now "The `print()` at the top runs" (function references carry parentheses; "fires" was a figure).
- `eager_validation.py` comment "Raises now" had no object; now "The check runs now".
- "The infinite `count(1)` never runs away" now states the mechanism: it "produces no more than they pull."
- "`list()` keeps pulling in the hope of another match" named the wrong actor. The generator expression does the pulling.
- "...carries the element type through. So `typed(items, int)`..." joined with a colon; two sentences in a row opened on "so".

Solutions:

- Exercise 9: the last paragraph said `ty` accepts `"ab"` "because it checks a recursive alias of this shape loosely". `ty` rejects a `float` in the same list, so it does enforce the alias. It accepts the string because a `str` is a `Sequence[str]` whose items are again `Sequence[str]`, which satisfies the alias by the same descent that breaks `flatten()`. Pyright rejects the string. The paragraph now says all of that.
- Exercise 5: `N` is `Final[int]`, matching `tee.py`.
- Exercise 3: the Performance link gained its anchor, `#lazy-evaluation-with-generators`.
- Exercises 7 and 8: "*GoF*" in italics is now "GoF"; the chapter italicizes the book title and the pattern name only.
- Exercise 10: "part on the answer" is now "act differently on a no".
- Exercises 2, 7, 8, 10: dropped intensifiers ("itself" three times, "exactly" three times, "plain", "simply", "at all", "buys back"), and two emphasis italics.

## Considered and declined

- `basic_iteration.py` catches `StopIteration` with `try`/`except` instead of `expect()`. The block mirrors the expanded loop printed right after it, which is the mechanism being taught.
- `OverStream` and the Solutions `Peekable` hand-write `__init__()`. Both transform their argument with `iter(source)`; `OverStream` is a standing exemption.
- The many uses of "never" ("never returns", "never stops"). Each states non-termination, which is the subject.
- `TypedIterator`'s field name `imp`. Renaming it touches the Solutions copy and buys little.
- An exercise on `in` consuming an iterator. The listing line and two sentences cover it.
- Reusing one generator twice in a single expression (`zip(g, g)`). A real near-miss, but a fourth instance of "the iterator runs out", which the chapter has made three times.
