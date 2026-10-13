> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 41_Functional--Toolkits, third round (2026-10-13)

This run follows `~41_Functional--Toolkits.r2.md` and carries forward its
rejections and declined items, and those of the first round.
Every listing ran under `uv run` (Python 3.15.0 final, `ty` 0.0.86).
I re-probed the quoted messages (`batched(strict=True)`, `zip(strict=True)`,
`islice()` with a negative index), the default recursion limit (1000),
bare `@lru_cache`'s `maxsize=128`, the `partial(pad, 5)` failure on the
`@record` `Text`, `dataclasses`' generated `__le__()`, and the `ty`
diagnostics Solutions 3 and 5 quote. All of them hold.
A scratch copy of `group_rounds()` with a cached `met()` confirmed the
"schedule gets worse" claim: seven pair rounds cover 20 of the 21 pairs.
`tip verify-ch CH=41 ISOLATED=1` passes 27 of 27 before and after.
No live blocks.

## Applied directly

Chapter:

- `lru_cache`: added the near-miss a reader writes. A bare `@lru_cache` keeps `maxsize=128` and starts evicting; `@cache` is `lru_cache(maxsize=None)`.
- `partialmethod`: added that the type checker catches `partial(pad, 5)` before the run (`invalid-argument-type`, expected `Text`, found `Literal[5]`; probed).
- `wraps`: "copies the same metadata onto a wrapper that is a class instance" made `update_wrapper()` sound class-only. Now says `@wraps(func)` runs `update_wrapper()`, which a class-based decorator calls directly.
- `wraps`: the paragraph after the listing said "Both names refer to a function called `wrapper`" between two claims about different functions. Restructured: both decorators return a `wrapper`, `wraps()` renames `greet`'s, `greet_bare` keeps `wrapper - None`. The `__wrapped__` sentence is its own paragraph.
- `total_ordering`: the speed example showed the generated `__lt__()`, but `Weight`'s `__lt__()` is hand-written, so it compared nothing `total_ordering` synthesizes. Now contrasts the two `__le__()` methods: `total_ordering`'s calls `__lt__()` and then `__eq__()`; the dataclass's compares tuples and calls nothing.
- `islice`: "an iterable may have none" had an unclear "none". Now "an iterator may have no end".
- `chain`: "the iterables themselves arrive as one lazy sequence" did not match the listing, which passes a list. Now says the iterables arrive inside one outer iterable, read lazily, so a generator works too.
- Lazy Evaluation: "the program stalls before the slice" was inaccurate, since `list()` keeps printing. Now says it prints and grows its list until memory runs out, with the slice waiting.
- Recursion: the loop's length was stated twice in consecutive paragraphs. The first now gives only the one-frame point.
- Recursion: "Self-similar problems ... are a different reason to recurse" read as if the tree walk did not branch, right after `nested_sum.py` was cited as branching. Now: a tree walk branches too, with no repeated subproblem, and the reason to recurse is shape.
- Case study: dropped "exactly" from "solves the pairs-only version exactly"; the next sentences state the result.
- `history` Is Mutable State: "the schedule gets worse" now gives the measured result: 20 of the 21 pairs.

Solutions:

- 2: "that conversion is the whole of what `maxsize` controls" overstated, since `currsize` changes too. Now "One extra slot turns that miss into a hit."

## Considered and declined

- "Pairs are the only group size where that question has a tidy rotation-based answer." Some Kirkman triple systems have cyclic constructions, but "tidy" carries the claim, and the next sentences say why trios are hard. Left.
- `lazy.py` and `recursion.py` keep their explanatory comments. They label the trace and the two cases in place, and no earlier review flagged them.
- "the extra elements are genuinely surplus" (`zip_longest`): "genuinely" marks the contrast with data in the next choice. Left.

## For the session

- `deep_review_db.md`'s standing exemption "41_Functional--Toolkits: `recursion.py` teaches two things on purpose" describes `sys.getrecursionlimit()` and an `import sys` the listing no longer has. It now uses `expect(RecursionError, factorial, 5000)`. The exemption is stale and can go.
- `tip watch-words` reports two stale baseline entries for this chapter (`exactly` and `only` on the circle-method sentence) because of the edit above. Pruning them is a baseline change, outside this run's files.
