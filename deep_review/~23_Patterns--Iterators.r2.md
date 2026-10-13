> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 23_Patterns--Iterators (2026-10-13)

This review has no live blocks.
I checked each claim against its listing and against the chapters it links (5, 14, 16, 18, 19, 20, 21, 41, 45), and I ran every extracted listing directly and compared it with its `#:` markers.
The `tee.py` and Solutions `exercise_5.py` byte counts came from three `--numbers` runs.
The tools were `uv run python` 3.15.0, `ty` 0.0.86 (probes for `next(nums)`, `twice_collection(gen(3))` and `twice_collection(Countdown(3))`, `TypedIterator(items, int)`, `typed(items, list[int])`, `reveal_type(typed(items, int))`, the `__getitem__()`-only class, the generator slice, and the Solutions 9 and 10 diagnostics), and `ruff --select ALL` for the `C416` claim.
I also read `threading.concurrent_tee` and the `itertools.tee()` docstring, the previous review, `deep_review_db.md`, and the outside review's verdicts.
`tip verify-ch CH=23 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.

## Applied directly

Chapter, corrections:

- "What `tee()` Buffers": the lead-in said `tee()` "rarely saves memory over collecting a list". The section's own lockstep block shows when it does, so the lead-in now says it "saves memory over a list only when the two branches advance together".
- "What `tee()` Buffers": the measured list size was 3,999,992 bytes and is now 3,999,904 on this machine (the `tee` figure, 4,096,992, matched).
- "Delegating with `yield from`": "the `True` ... shows the substitution is exact" overstated one equal result on one input, and the next paragraph lists three ways the two forms differ. It now says "shows that both produce the same values".
- "Delegating with `yield from`": "the hand-written loop has no way to forward them" is false, because a longer hand-written loop can forward `send()` and `throw()`. It now says "the hand-written loop forwards neither".
- "An Exhausted Generator Is Silently Empty": "raises `StopIteration` at the first `next()`" collided with the section above, where "the first `next()`" means the call that starts the body. It now says "answers every `next()` with `StopIteration`".
- `first()` and `current_item()` section: `gof_iterator.py` used `next(self.source, DONE)` about 90 lines before the chapter explains the two-argument `next()`. The `seen` paragraph now explains it where it first appears.

Chapter, teaching and prose:

- Opening: `*iterator*` was italicized twice as a new term, and only the definition in "Iteration Comes Built In" keeps the italics. "does not name the container's type" became "leaves the container's type unnamed".
- `basic_iteration.py`: the line tagged `[2]` also carried a second comment ("An iterator returns itself") that restated the prose sentence for `[2]`. The comment is gone, matching the `[1]` line.
- "Generators": "pausing and resuming its own state" (state does not pause) is now its own sentence, "The generator pauses after each value and resumes with its local variables intact."
- `iterators.py` lead-in named only the class half of a listing that opens with `fibonacci()`. It now names both.
- "Generators are lazy": "so it works on streams" had `fibonacci(1_000_000)` as its subject. It now says "so a generator works on streams".
- Heading "The Costs of Laziness" is now "What Laziness Hides" (the commerce rule; both surprises are silent). The two links to it, in the conclusion and in Solutions exercise 3, follow. No other chapter links the anchor.
- `eager_validation.py` lead-in: split "removes it as a plain function that ..." into two sentences, keeping "plain" for the contrast with a generator function.
- `tee.py`: `for x, y in zip(...)` bound two unused names over two lines. It is now `for _ in zip(first2, second2, strict=True):`, as in Solutions exercise 5. The output is unchanged.
- "`tee()` is also single-threaded" became "The branches of one `tee()` call also belong in a single thread."
- Functional Toolkits pointer: "the sorted-input trap `groupby()` sets for an unwary caller" is now "why `groupby()` needs sorted input".
- "The one rule that touches this code" now names it, `C416` (verified with `ruff --select ALL`).
- "A Type-Checking Iterator" opening: the *Decorator* Pattern does not wrap an iterator; "Applied to an iterator, the *Decorator* Pattern wraps the existing iterator ...".
- Class-or-generator paragraph: "Use the generator when it does not" pointed two sentences back. It is now "Otherwise, use the generator." The paragraph held three topics, so it is split into choosing a wrapper, the `Iterable`/`Iterator` input difference, and `type[T]` carrying the element type.
- "The listing names GoF's `Next()` `advance()`" now reads "renames GoF's `Next()` to `advance()`".
- `seen` paragraph: "`seen` is how." and "The interface needs more than a buffer. It rebuilds the list." are now "The `seen` list makes that rewind possible" and "Supporting the four methods takes more than a small lookahead buffer: `OverStream` rebuilds the list." The pointer is `print(stream.seen)`, not "the last line of output".
- "Asking Consumes an Item": "swallows" became "absorbs", the word the rest of the chapter uses. "neither restores the free query of the GoF *Iterator*" now says what happens: "either way the question consumes an item, where the GoF *Iterator*'s `is_done()` consumes nothing".
- After `asking_costs.py`, "Nothing in the protocol looks ahead without advancing" is now positive ("Every way the protocol offers to look ahead also advances"). "`tee()` buffered a whole stream" is now present tense and says when. The membership-test sentences start their own paragraph.
- After `escaped_stop.py`, the paragraph is split between the PEP 479 explanation and the fix (`yield from` against a `for` loop).

Solutions:

- Exercise 3: the link follows the renamed heading, and "asks for exactly ten" drops "exactly".
- Exercise 5: "about 9,400 bytes at `k` of 100" was stale. Three runs measured 9,824, so it is now "about 9,800". The 416,000 figure and the 41 bytes per item still hold.
- Exercise 6: "Only `takewhile()` stops" ignored the `islice()` test in the same file. It now says "`takewhile()` stops at the first failure".
- Exercise 8: "the type checker passes that version" became "accepts". "`tee()`, `OverStream`, and this chapter's other lookahead pull early the same way" was wrong for `tee()`, which pulls only when a branch asks. It now names `OverStream`, whose `is_done()` reads the next item before `current_item()` asks for it.
- Exercise 9: "`str` is the one built-in exception" read as an `Exception`. It now says "the one built-in sequence whose items are again strings".
- Exercise 10: "The consumer receives the `1` ... The caller gets an exception instead of a list" contradicted itself. It now separates a consumer that iterates item by item from a caller that wraps the iterator in `list()`.

## Considered and declined

- The outside review's items 2 (retrieving the return value through `StopIteration.value`) and 3 (`takewhile()` discarding the boundary item) stay rejected per its verdicts. Chapters 45 and 41 cover both, and both are linked from here.
- Vale's passive warning on "every item it pulled is gone": "gone" works as an adjective there, and rewriting it would weaken the sentence.
- Exercise 7's "What has `first()` cost you on an infinite source?" and Solutions 7's "Measure what rewinding costs": the cost is memory, measured as `len(endless.seen)`, which the commerce rule keeps.
- `DONE = sentinel("DONE")` without `Final`: the book writes every sentinel this way, and the value is used as a type in `T | DONE`.

## For the session

- `tee.py` changed (an unused `x, y` became `_`), so `Examples/23_Patterns--Iterators/tee.py` needs `tip sync`.
- Recommended rename that I did not make, because it orphans a generated file: `asking_costs.py` (chapter 23, the listing under "Asking Consumes an Item") to `asking_consumes.py`. "Costs" stands in for "consumes", which the section's heading already says. Renaming the fence's first line, then `tip sync` and `tip prune`, removes `Examples/23_Patterns--Iterators/asking_costs.py`. No prose or other file names the listing.
- Stale baseline entries left by these edits (no new hits): `watch_words_baseline.txt` has four stale entries for chapter 23 and its Solutions file ("The Costs of Laziness" twice, "exactly ten", "Only `takewhile()` stops"), and `positional_refs` has one ("The last line of output shows that by the time ...").
