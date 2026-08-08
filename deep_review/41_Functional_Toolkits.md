When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter-level, the largest item: the chapter has no Exercises section and no
`Solutions/41_Functional_Toolkits.md`, and chapter 43 has already borrowed
this chapter's case study for one of its own exercises.**

Every other chapter in Part IV ends with Exercises
(40 has five, 42 has a set, 43 has four).
41 ends mid-case-study, on the sentence
"...when a loop's simple counter is not enough and the problem needs a stack
instead."
`Solutions/` has entries for 40, 42, 43 and nothing for 41.

The gap is visible from outside the chapter:
`Chapters/43_Functional_Assurance.md` exercise 4 is
"Write a property test for `group_rounds()` from
[Toolkits](41_Functional_Toolkits.md#case-study-pairing-rotations)".
Chapter 43 is exercising chapter 41's material because chapter 41 does not.

Proposed set, all answerable from this chapter and verified where they claim a
result:

> ## Exercises
>
> 1.  Rewrite `deep_sum()` from `nested_sum.py` without recursion,
>     using a list as an explicit stack.
>     Compare the two versions for length,
>     and name the places an off-by-one can hide in the loop version that do
>     not exist in the recursive one.
> 2.  `functools_lru_cache.py` prints
>     `CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)`.
>     Change `maxsize` to `3`, predict the four numbers before running it,
>     then run it and account for any difference.
>     (Verified: `hits=2, misses=3, maxsize=3, currsize=3`.)
> 3.  Write `batch_totals(source, n)`, which takes an iterator and yields the
>     sum of each `n`-element batch, built only from `itertools` pieces and a
>     generator expression.
>     Show that it stays lazy by passing it `count(1)` and taking five values.
> 4.  `groupby()` on unsorted input silently returns the same key more than
>     once. Write `grouped(data, key)` returning a `dict[K, list[V]]` that
>     cannot make that mistake, and say what it costs relative to `groupby()`.
> 5.  Decorate `deep_sum()` with `@cache` and explain the exception.
>     (Verified: `TypeError: unhashable type: 'list'`.)
>     What would have to change about the `Nested` alias for caching to be
>     possible at all?
> 6.  `group_rounds()` takes a `seed` and builds its own `random.Random`.
>     Replace that with an `rng: random.Random` parameter.
>     Which property of the function does that preserve,
>     and which one does it hand to the caller?

Reported rather than applied because the size and difficulty curve of an
exercise set is a pacing decision, and because adding one implies creating
`Solutions/41_Functional_Toolkits.md`, which is outside this chapter.

---

[] Reject

**Chapter-level: the chapter has no conclusion. It stops inside the case
study, and the reader is never told what they can now do.**

The last paragraph is an observation about the case study
("That trade, memory for generality, ...").
Nothing gathers the chapter, and nothing hands the reader off to
[Error Handling](42_Functional_Error_Handling.md),
which is the next chapter in the arc.
Chapter 40 ends the same way and I raised it there too;
here it matters more, because 41 is a catalog and a catalog with no closing
argument reads as a reference page rather than a chapter.

The honest answer to "what can the reader do now that they could not before"
is "recognize about thirty standard-library functions."
That is a real gain, and it needs one paragraph to say what to do with them.

Proposed closing section, after the case study:

> ## Choosing From the Toolkits
>
> The rule for both modules is the same:
> before writing a loop, ask whether the loop already has a name.
> A running total is `accumulate()`, a sliding window is `pairwise()`,
> a remainder-safe chunking is `batched()`,
> and a memoized pure function is `@cache`.
> Each of those replaces a small piece of code that works the first time and
> fails on the empty input, the single element, or the last partial batch.
>
> The second rule is that the pieces are meant to be stacked.
> `islice(count(10, 2), 5)` in this chapter is two stages;
> a real pipeline is five or six,
> and it still holds one item in memory at a time.
> [Error Handling](42_Functional_Error_Handling.md) asks what happens to such
> a pipeline when one stage fails,
> which is the question a chain of pure functions leaves open.

Reported rather than applied because a new section changes the chapter's
pacing and shape, which is your call.
A cheaper version is three sentences appended to the case study with no new
heading.

---

[] Reject

**Order: "Recursion" sits between the `itertools` catalog and "Lazy
Evaluation", separating the two sections that are about the same thing.**

Section order today: functools, itertools, Recursion, Lazy Evaluation, Case
Study.
"Lazy Evaluation" is the direct continuation of the `itertools` section (it
opens by combining a generator with `count()` and `islice()`, both taught two
sections earlier), and "Recursion" has nothing to do with either module except
the `@cache` thread this pass just added.

Swapping them gives: functools, itertools, Lazy Evaluation, Recursion, Case
Study, which reads as two toolkits, the property that makes the second one
work, then the one technique that is not a toolkit, then the case study.

Price of the move, checked:

- No chapter outside 41 links to `#recursion` or `#lazy-evaluation`; the only
  external anchors into this chapter are `#lru_cache`, `#cache`,
  `#singledispatchmethod`, `#the-functools-toolkit` and
  `#case-study-pairing-rotations` (from 18, 33, 39, 40, 43, 47). The two
  sections can move freely.
- Two in-chapter links point at `#recursion`: the `cache` entry's new
  forward pointer, and the case study's closing sentence. Both still resolve.
- The `itertools` intro's new pointer to `#lazy-evaluation` says "below" and
  stays true.
- The case study's last sentence reaches back to Recursion, and after the
  swap Recursion is the section immediately above it, which is better, not
  worse.

The argument against: the chapter intro says "two techniques that pair
naturally with them, recursion and lazy evaluation", in that order, and would
need its order flipped too. That is a one-line edit.

Reported rather than applied because reordering sections is a pacing decision
however clear the case.

---

[] Reject

**Case Study: `group_rounds()` raises `ValueError` for any roster smaller than
`size`, and chapter 43 asks the reader to property-test it "for any roster and
any group size".**

Verified on the pinned build:

    group_rounds(["a", "b"], 3)  -> ValueError: min() iterable argument is empty
    group_rounds(["a"], 2)       -> ValueError: min() iterable argument is empty

When `0 < len(students) < size`, the `while len(pool) >= size` loop never
runs, `groups` stays empty, and `min(groups, key=...)` in the leftover loop
raises.
(`group_rounds([], 2)` is fine; it yields `[]` forever.)

`Chapters/43_Functional_Assurance.md` exercise 4 reads
"for any roster and any group size, every student appears in exactly one group
per round. Use a strategy that generates rosters of distinct names."
A Hypothesis strategy over rosters and sizes finds this on its first few
examples, and the reader gets a crash instead of the falsified property the
exercise is about.
`Solutions/43_Functional_Assurance.md` currently holds only exercise 1, so
nothing downstream depends on the present behavior yet.

Recommended fix, two lines, and consistent with the "join instead of sit out"
rule the prose already states:

```python
        for extra in pool:  # Too few left for a full group of `size`
            if not groups:
                groups.append([])
            roomiest = min(groups, key=lambda g: sum(
                history[frozenset((m, extra))] for m in g))
            roomiest.append(extra)
```

Everyone lands in one undersized group, and the "every student appears in
exactly one group per round" property holds for every roster and size.

Alternatives, in case you prefer them:

- Raise deliberately at the top: `if students and len(students) < size: raise
  ValueError(...)`. Honest, but then chapter 43's exercise needs its strategy
  constrained, which is an edit to a chapter I cannot make.
- Leave the code alone and add one sentence saying the function assumes
  `len(students) >= size`. Cheapest, but chapter 43's exercise still crashes.

I did not apply any of these: the first changes the listing's behavior and its
`#:` markers would need re-verifying against a decision only you can make, and
the second and third involve `Chapters/43_Functional_Assurance.md`, which is
out of bounds for this pass. Either way, chapter 43's exercise 4 should be
re-read once this is settled.

---

[] Reject

**Case Study: the section closes the chapter but uses almost none of it.**

`student_pairs.py` imports `combinations` and `islice` from `itertools`, and
nothing at all from `functools`.
Of the eleven `functools` entries and twenty `itertools` entries the chapter
just catalogued, the case study cashes in two.
The intro sentence I rewrote in this pass now names honestly what it does use
(infinite generator, `islice`, `combinations`, seeded RNG), which removes the
overclaim, but the underlying imbalance is still there:
a chapter's closing case study is where its tools are supposed to earn out.

Three ways to close the gap, in increasing cost:

1.  Add `@cache` to the pair-cost helper. Pull the
    `sum(history[frozenset((m, c))] for m in group)` expression into a named
    function and note that it cannot be cached, because `history` changes
    between rounds. That is a one-paragraph point and it teaches the purity
    precondition from the `cache` entry in a place where it bites.
2.  Report the schedule with `batched()` or `pairwise()` in the demo section
    below `group_rounds()`, so at least the presentation layer uses the
    catalog.
3.  Leave it, and change the section's framing from "several of these ideas"
    to a claim about the shape of the solution rather than the tools in it.

I recommend 1: it is the only one that teaches something rather than
decorating the listing, and "here is where caching would be wrong" is a
stronger lesson than another `itertools` call.

---

[] Reject

**"The `itertools` Toolkit" intro promises composition and the section never
shows a pipeline more than two stages deep.**

The intro says "Combine them the way you combine any small function, by
feeding one's output to the next."
The deepest composition anywhere in the section is
`islice(count(10, 2), 5)` and `islice(cycle("AB"), 5)`, two stages, in entries
whose point is `count` and `cycle` rather than composition.
Twenty entries later the claim has not been demonstrated.

Proposed listing (verified on the pinned build: runs, `ruff` clean at 70,
`ty` clean, output exactly as shown):

```python
# itertools_pipeline.py
from itertools import batched, count, islice, takewhile

squares = (n * n for n in count(1))
batches = batched(squares, 3)
totals = (sum(b) for b in batches)
print(list(takewhile(lambda t: t < 500, totals)))
#: [14, 77, 194, 365]
print(list(islice(squares, 3)))
#: [256, 289, 324]
```

Four stages over an infinite source, and nothing runs until `list()` pulls.
The second `print()` is the part that teaches: the source is still alive and
sitting at 16, not 13, because `takewhile()` had to pull and discard the
batch `(169, 196, 225)` to discover that its total exceeded 500.
That one line makes the pull model visible in a way no single entry does.

Where it goes is the decision I am leaving to you.
Two candidates:

- **At the end of the `itertools` section**, as a `### Composing the Pieces`
  subsection, so it reads as the payoff for the catalog. Costs a subsection
  heading at a different level from the twenty function entries around it.
- **Immediately after the section intro**, before `repeat`, as the
  front-loaded payoff the deep-review checklist asks for: the reader sees what
  the catalog buys before decoding twenty entries. Costs forward references to
  `batched`, `count`, `takewhile` and `islice` in the chapter's first
  `itertools` listing, which is the "nothing used before it is taught" rule
  going the other way.

I recommend the first, because the second breaks the escalating-difficulty
rule harder than it fixes the front-loading one.

---

[] Reject

**`recursion.py` teaches two things at once.**

The listing is `factorial()` plus `sys.getrecursionlimit()`, so it carries the
base-case/recursive-case lesson and the depth-limit fact in one block, with an
`import sys` that exists only for the second.
The chapter's own rule elsewhere is one new thing per listing.

Splitting it would mean a two-line second listing, which is probably worse
than the current arrangement.
Recording it as a known, deliberate-looking deviation rather than proposing a
change: the depth limit is discussed in the very next paragraph, so the
proximity earns the extra line.
Reject this block if you agree; it exists so a later review does not raise it
again.

---

[] Reject

**`singledispatch`: the entry does not say what it cannot do, which is the
reader's next question.**

The entry says it "dispatches on the type of its first argument."
A reader who wants two-argument dispatch, or dispatch on a keyword argument,
or dispatch on the return type, finds out by trying.
Chapter 32 (Multiple Dispatching) is the place that answers this, and this
entry does not point there.

Proposed sentence after the listing:

> Only the first argument is examined, so a rule that depends on two types
> needs [Multiple Dispatching](32_Multiple_Dispatching.md), and a keyword-only
> argument cannot be dispatched on at all.

Reported rather than applied because I did not want to add a third
cross-reference to a four-line catalog entry that already carries two, and
because the `singledispatch`/Visitor thread is chapter 33's to own.

---

[] Reject

**Two claims in the `itertools` catalog are stated and never shown.**

- `chain`: "`chain.from_iterable(iterables)` does the same when the iterables
  themselves arrive as one lazy sequence" — the listing shows only
  `chain([1, 2], [3, 4])`.
- `accumulate`: "or the running result of any two-argument function" — the
  listing shows only the default sum.

Both would take one line each
(`print(list(chain.from_iterable([[1, 2], [3, 4]])))` giving `[1, 2, 3, 4]`,
and `print(list(accumulate([1, 2, 3, 4], mul)))` giving `[1, 2, 6, 24]` with
`from operator import mul`).
Neither carries a trap, which is why I backed the `groupby` and `batched`
claims in this pass and left these two.
If you want the catalog to be uniform about demonstrating what it asserts,
these are the remaining two.

---

[] Reject

**`repeat`: the entry says "forever or a fixed number of times" and shows only
the fixed form, which is the less useful one.**

`repeat("x", 3)` is a list you would have written as `["x"] * 3`.
The reason `repeat` exists is the infinite form as a constant column:
`map(pow, range(5), repeat(2))`, or `zip(names, repeat(default))`, where it
supplies an argument that never changes without materializing anything.

Proposed second line for `itertools_repeat.py`:

```python
print(list(map(pow, range(5), repeat(2))))
#: [0, 1, 4, 9, 16]
```

with a sentence saying that the infinite `repeat(2)` stops when `range(5)`
does, because `map()` stops at the shortest input.

Reported rather than applied because it doubles a deliberately one-line entry,
and because the same "shortest input wins" rule is now stated three entries
later under `zip_longest`, so you may prefer to keep them together.

---

[] Reject

**MANIFEST — not a proposal. Changes applied to
`Chapters/41_Functional_Toolkits.md` in this pass.**

All gates re-run and passing after the last edit:
`extract_examples.py --write -o build/private/41`,
`validate_output.py --tree build/private/41`,
`ruff check`, `ty check`, `heading_links.py`, `banned_phrases.py`,
`reflow_prose.py` (clean, no paragraph would reflow),
and each changed listing executed directly.
Six listings changed code, so `Examples/` needs a `make sync`:
`functools_cache.py`, `functools_cached_property.py`, `functools_lru_cache.py`,
`functools_partialmethod.py`, `itertools_groupby.py` and `student_pairs.py`.

1.  Section intro: **corrected a false claim.** "These tools are already
    written, already correct, and implemented in C for speed" — six of the
    eleven entries are pure Python. Verified by identity against `_functools`:
    `reduce`, `partial`, `cmp_to_key` and `Placeholder` are C, and the caches
    run through the C `_lru_cache_wrapper`, but `partialmethod`,
    `cached_property`, `wraps`, `update_wrapper`, `total_ordering`,
    `singledispatch` and `singledispatchmethod` are all Python. Rewritten to
    name the C ones.
2.  Section intro: "from a single fold" → "from a single `reduce()` call".
    "Fold" is undefined at that point and only gets its working definition
    thirteen lines later; the chapter-40 pass removed the same word from the
    arc's opening paragraph for the same reason.
3.  `reduce`: added the empty-sequence `TypeError` (quoted verbatim) and the
    third `initial` argument that prevents it. The entry previously described
    a fold with no mention of its one failure mode.
4.  `cache`: added `print(fib.cache_info())` and the counts that explain it
    (31 misses, 28 hits, 59 calls against 2,692,537 undecorated — all measured
    on the pinned build). The listing previously proved only that `fib(30)` is
    `832040`, which a reader cannot distinguish from an uncached run.
5.  `cache`: linked to [Caching](18_Performance.md#caching), which runs the
    cached and uncached versions side by side, and forward to
    [Recursion](#recursion). Chapter 18 has held this exact demonstration
    (`cache_speedup.py`) all along with no link in either direction.
6.  `cache`: the lapsed-listener reference now points at chapter 30's
    subsection anchor instead of the whole chapter.
7.  `lru_cache`: **the listing asserted an eviction it did not demonstrate.**
    A comment said "Evicts 1" and the output was
    `hits=0, misses=3, currsize=2`, from which nothing about eviction follows.
    Added `square(2)` (a hit) and `square(1)` (a fourth miss on a value
    computed first), so the marker is now `hits=1, misses=4`, and added the
    paragraph that reads the four numbers.
8.  `partialmethod`: **the chapter's biggest untaught lookalike pair.** Read
    CPython 3.15's `functools.py`: `partial.__get__` returns
    `MethodType(self, obj)` (bound arguments first, instance after), while
    `partialmethod._make_unbound_method` calls
    `self.func(cls_or_self, *pto_args, ...)` (instance first). So a `partial`
    in a class body works for the keyword case the listing happens to show and
    breaks for a positional one. Verified: `partial(pad, 5)` in the class body
    raises `AttributeError: 'int' object has no attribute 'value'`. Added the
    paragraph, including that `partial` became a descriptor in 3.14 (CPython
    gh-121027: `FutureWarning` in 3.13, behavior change in 3.14).
9.  `partialmethod`: `Text` converted to `@dataclass`. Its `__init__` only
    assigned a parameter to a field, which the house style says must be a
    dataclass unless the manual form is the lesson and the prose says so.
    `Weight` under `total_ordering` is the chapter's one legitimate manual
    class and does explain itself, so the chapter is now consistent about it.
    Verified that `@dataclass` leaves the unannotated
    `zero_pad = partialmethod(pad, fill="0")` class attribute alone.
10. `cached_property`: `Lazy` converted to `@dataclass` for the same reason.
    Verified that the cached value, the `x.n = 10` staleness demo, and
    `del x.squared` all behave identically.
11. `wraps`: added the near-miss. Without `@wraps`, the same `print()` reports
    `wrapper - None` (verified), and every tool that reads those attributes
    reads the wrapper. Also added `__wrapped__`, which the entry's one-line
    description omits.
12. `singledispatchmethod`: added that dispatch is on the first argument after
    `self`, never on `self`. "The same dispatch, written as a method" leaves
    that ambiguous, and dispatching on the receiver is the natural wrong guess.
13. Transition into `itertools`: "applies the same idea to lazy iteration"
    ("the same idea" had no referent) → "ready-made pieces you compose,
    instead of loops you write and test again".
14. `itertools` intro: forward link to [Lazy Evaluation](#lazy-evaluation)
    (the section uses laziness two hundred lines before defining it) and back
    link to [Reusable Algorithms](23_Iterators.md#reusable-algorithms), which
    already introduces `chain`, `islice`, `groupby`, `takewhile` and `count`.
    The chapter previously had no reference to chapter 23 anywhere.
15. `islice`: added the two ways it differs from a list slice — negative
    indices raise `ValueError` (verified), and it consumes what it passes over
    so an iterator resumes where the slice stopped (verified).
16. `batched`: added `strict=True`, which raises
    `ValueError: batched(): incomplete batch` (verified verbatim), and framed
    it as the pagination-versus-fixed-record choice.
17. `takewhile`: the trailing `1` in the listing's input exists to separate it
    from `filter()` and the chapter never said so. Added the contrast
    (`filter` gives `[1, 2, 1]`), the reason it only matters on an infinite
    source, and a link to chapter 23, which works the same distinction
    through in depth.
18. `dropwhile`: the matching half — the same trailing `1` survives
    `dropwhile()` and would not survive `filterfalse()` (`[3, 4]`).
19. `zip_longest`: added the three-way choice. The entry taught the padding
    form without ever naming `zip(strict=True)`, whose error message is now
    quoted verbatim.
20. `groupby`: **added the demonstration for a rule the chapter asserted.**
    "The input must already be sorted by that key" had no listing behind it.
    Added `groupby(["b", "a", "b"])`, which returns `"b"` twice with no error,
    and the `sorted()` fix.
21. `groupby`: added the second trap, which was not mentioned at all. Each
    group is a view onto one underlying iterator, so `list(groupby(data))`
    returns the keys paired with three exhausted iterators (verified:
    `[('a', []), ('b', []), ('c', [])]`). This is the mistake a reader makes
    the first time they try to keep the groups around.
22. `tee`: linked to [Generators](23_Iterators.md#generators), which measures
    the buffering this entry describes, and added the third caution chapter 23
    carries and this one dropped: the branches share one unlocked buffer, so
    they cannot go to separate threads.
23. Recursion: tied the section to the `cache` entry. Branching recursion
    recomputes subproblems, which is the reason the chapter's own `fib()` is
    decorated rather than looped. The two sections previously shared a worked
    example and never mentioned each other.
24. Recursion: added that `sys.setrecursionlimit()` raises the ceiling, and
    that doing so is the wrong answer for a flat sequence. A reader told
    "deep recursion will raise `RecursionError`" asks how to raise the limit,
    and the chapter did not say. (I checked and deliberately did *not* claim
    that raising the limit risks a hard crash: on the pinned 3.15 build a pure
    Python recursion 200,000 frames deep completes cleanly with the limit
    raised.)
25. `nested_sum.py` prose: **corrected a false statement.** "which is why it
    stays three lines" — `deep_sum()`'s body is seven. Rewritten to state the
    real property, that the body says nothing about depth.
26. Lazy Evaluation: added the near-miss. `list(squares())[:5]` is what a
    reader writes instead, and it never returns. The section explained
    laziness thoroughly and never showed the mistake it prevents.
27. Lazy Evaluation: the bare `[Performance](18_Performance.md)` reference
    replaced with the named anchor
    [Lazy Evaluation with Generators](18_Performance.md#lazy-evaluation-with-generators).
28. Case Study intro: "see these chapters' ideas working together" (vague, and
    an overclaim — the listing uses two of the chapter's thirty-one tools)
    replaced with the four things it actually demonstrates.
29. `student_pairs.py`: removed `type Student = str`. The house style names
    exactly this construct as forbidden ("never a bare scalar rename like
    `type Symbol = str`"), and a grep confirms this was the only bare scalar
    `type` alias in `Chapters/` or `Solutions/`. `Group` and `Round` are
    compound and stay.
30. Every paragraph touched was run through `reflow_prose.py` so the chapter
    is Semantic-Line-Breaks clean.

Also checked and found clean, so no change was made: no use of the "promise"
metaphor and none introduced; no "reach for"; every `#:` marker matches a
direct run of the extracted script (including `student_pairs.py`, which I
confirmed is stable across `PYTHONHASHSEED` values 0, 1 and 12345 — it keys a
`Counter` on `frozenset[str]` but never iterates one, so string-hash
randomization cannot reach the output); `sys.getrecursionlimit()` is 1000 on
the pinned build; the `total_ordering` entry's plain `Weight` class is an
explained deviation from the dataclass rule and stays; the `sentinel()` call in
`itertools_zip_longest.py` is the PEP 661 builtin and needs no import on 3.15;
and the chapter's cross-references into 07, 14, 18, 23, 30, 33 and 40 all
resolve under `heading_links.py`.
