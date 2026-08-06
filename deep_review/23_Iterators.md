# Deep review: 23_Iterators.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Say that `Iterable[T]` cannot warn a reader about the second pass

**Kind:** teaching
**Where:** section "Generators", after "When data must be walked twice, collect it into a list once, or hand out an iterable like `Countdown` above..." (line ~158)
**Problem:** The chapter teaches that a spent generator silently yields nothing, then gives the caller-side advice ("collect into a list"). It never says the thing that makes this dangerous in a typed codebase: `Iterable[T]` covers a list and a one-shot iterator equally, so a function that walks its argument twice type-checks cleanly and then returns a wrong answer. The chapter's own `total()` is annotated `Iterable[int]`, which is correct because it sums once, but a reader has no way to know that the annotation is carrying that guarantee. Later in the chapter the reader learns that `ty` and `ruff` cannot detect an endless iterator; this is the companion gap, and it *is* expressible in the type system, which makes it the more useful lesson.

Verified: `sum(xs), sum(xs)` over a generator argument annotated `Iterable[int]` returns `(3, 0)` and `ty` reports nothing. Changing the annotation to `Collection[int]` makes `ty` reject the generator at the call site (`protocol member __contains__ is not defined on type Iterator[int]`) while still accepting a list, a tuple, and a `range`.

**Proposal:** Add a paragraph plus a short listing. Prose:

> The annotation cannot warn you.
> `Iterable[T]` describes a list and a half-spent generator equally well,
> so a function that walks its argument twice type-checks and then returns a wrong answer on the second pass.
> When a function iterates more than once, say so in the signature.
> `Collection[T]` and `Sequence[T]` ask for more than iteration,
> and no iterator supplies it,
> so the checker rejects the generator at the call instead of letting it run wrong.
> `total()` above stays `Iterable[int]` because it sums once.

Listing:

```python
# walked_twice.py
from collections.abc import Collection, Iterable, Iterator

def gen(n: int) -> Iterator[int]:
    yield from range(n)

def twice_iterable(xs: Iterable[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)

def twice_collection(xs: Collection[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)

print(twice_iterable(gen(3)))  # ty sees nothing wrong
#: (3, 0)
print(twice_collection([1, 2, 3]))
#: (3, 3)
```

with a following sentence noting that `twice_collection(gen(3))` is the call `ty` refuses, and that the listing cannot show it because a chapter listing must type-check.

Alternatives, if a new listing is too much: (a) prose only, no listing; (b) fold it into exercise 4, which already asks the reader to fix a second-pass bug two ways, by adding "and say which annotation on the consuming function would have caught this before it ran."

**Cost:** A new listing needs the full verify loop (sync, `ty`, `ruff`, `validate_output`). It introduces `Collection`, which the chapter does not otherwise use; chapter 8's typing table already lists `Sequence`/`Iterable`/`Iterator` and links here, so the vocabulary is available. Nothing else in the book asserts that `Iterable` is the default annotation for a consumed argument.

---

## 2. Exercise 7's endless `OverStream` never returns under `traverse()`

**Kind:** exercise
**Where:** "Exercises", item 7 (line ~681)
**Problem:** The exercise says "build an `OverStream` over `itertools.count(1)`, traverse 50,000 items, and report `len(stream.seen)`." `traverse()` as written loops `while not it.is_done()`, and `is_done()` over `count(1)` is never `True`, so `traverse(OverStream(count(1)))` runs until the machine runs out of memory. A reader following the instruction literally gets the hang the previous section warned about, with no hint that they were supposed to bound it themselves. If that is the intended trap it needs to say so, and if it is not it needs a bound.

**Proposal:** Make the bound explicit and keep the lesson:

> Then build an `OverStream` over `itertools.count(1)` and drive it with your own loop
> that stops after 50,000 items, since `traverse()` would never return,
> and report `len(stream.seen)`.
> What has `first()` cost you on an endless source?

Alternative: keep `traverse()` and wrap the source instead (`OverStream(islice(count(1), 50_000))`), which is a smaller change but loses the "the GoF driver has no stopping condition" observation.

**Cost:** none.

---

## 3. "Both surprises ... come from the same cause" explains only the second one

**Kind:** teaching
**Where:** section "The Pattern That Disappeared", closing paragraph (line ~653)
**Problem:** The two surprises are (a) a generator's body does not run until the first `next()`, so validation fires late, and (b) an exhausted generator yields nothing without an error. The closing paragraph claims both come from the same cause and then supports it with "`for` and `list()` catch the answer and report nothing, so an exhausted source and an empty one produce identical output," which is an explanation of (b) alone. Deferred start has nothing to do with an absorbed `StopIteration`. A reader who goes back to check will not find the connection.

There is a reading that makes "both" true: the protocol gives no free query, so you cannot learn whether the arguments were valid without pulling, and you cannot learn whether the source is spent without pulling. That is a good point, but the paragraph does not make it.

**Proposal:** Rewrite the paragraph to state the shared cause and then split it across the two surprises:

> Both surprises earlier in this chapter come from the same rule:
> the protocol answers no question for free.
> The only way to find out whether the body accepts its arguments is to pull a value and let it run,
> and the only way to find out whether the source is spent is to pull and be told nothing came back.
> `for` and `list()` catch that second answer and report nothing,
> so an exhausted source and an empty one produce identical output.
> The protocol is free, and quiet.

Alternative: narrow the claim instead, replacing "Both surprises earlier in this chapter" with "The second surprise earlier in this chapter" and leaving the rest as it is. Smaller, but it drops a real connection.

**Cost:** none. Note that "fusion" in this sentence was already changed to "cause" (watch-list word); this proposal supersedes that wording.

---

## 4. The `eq=False` justification describes a state that cannot arise

**Kind:** prose
**Where:** section "A Type-Checking Iterator", the `eq=False` paragraph (line ~447)
**Problem:** "Two wrappers over one source compare equal, no matter how far each has advanced." Verified: two `TypedIterator`s only compare equal when they hold the *same* `imp` object, and in that case they share one cursor, so neither can be at a different position from the other. Two wrappers over separate iterators of the same list compare unequal already, since iterators use identity equality. So the clause a reader is most likely to seize on describes something that does not happen, and the genuinely damaging consequence of a generated `__eq__()`, that `__hash__` becomes `None` and the iterator can no longer go in a set or serve as a dict key, is stated first and then buried under the weaker argument.

**Proposal:** Lead with the hashability and put the equality point in terms that hold:

> Note the `eq=False` in the `dataclass` decoration.
> A data class that generates `__eq__()` sets `__hash__` to `None`,
> so the wrapper can no longer go in a set or serve as a dict key,
> which every other iterator in Python can do.
> Field-by-field comparison is also the wrong question to ask about a cursor:
> two wrappers sharing one source compare equal even though they have consumed different numbers of items,
> and two wrappers over separate iterators of the same list compare unequal.
> Turning equality off restores the identity comparison an iterator should have.

**Cost:** none.

---

## 5. Link the `yield from` forward reference to chapter 45

**Kind:** structure
**Where:** section "Delegating with `yield from`", the paragraph beginning "The two forms agree for a generator that only produces values" (line ~288)
**Problem:** This paragraph raises three things it does not cover: the value of a `yield from` expression, `send()`, and `throw()`. All three are the subject of chapter 45, which the reader has no way to know from here. The chapter already links forward once, for the three-part annotation, so the pattern is established. Chapter 34 links *into* this section, so it is a well-trafficked anchor and a dangling forward reference here is worth closing.

**Proposal:** Append one sentence to the paragraph:

> [Generators](45_Generators.md#yield-from-composes-descriptions) works all three channels.

**Cost:** Adds a second inbound reference to a chapter 45 heading, so a rename of "`yield from` Composes Descriptions" now breaks two links instead of one. `heading_links.py` gates it, so the break would be loud.

---

## 6. "with a builtin termination" reads as a Python builtin

**Kind:** prose
**Where:** section "Reusable Algorithms", after `test_endless.py` (line ~395)
**Problem:** "The first test is `list(count(1))` but with a builtin termination." In a Python book, "builtin" names a specific thing, and there is no builtin here: `counter()` is a hand-written generator with a tripwire. A reader stops to work out which builtin is meant.

**Proposal:** "The first test is `list(count(1))` with a stopping point built into the source."

**Cost:** none.

---

## 7. The `__getitem__` iteration fallback is never mentioned

**Kind:** teaching
**Where:** section "Iteration Is Built In", after "Two methods make up the protocol." (line ~23)
**Problem:** The chapter states flatly that two methods make up the protocol. That is true for code written today and false for code a reader will meet: a class defining only `__getitem__()` over integer indices is iterable by `for`, by comprehensions, and by `iter()`, yet `isinstance(obj, Iterable)` reports `False` and a `Iterable[T]` annotation rejects it. Verified on the pinned build: `[c for c in Old()]` produces `['a', 'b', 'c']`, `isinstance(Old(), Iterable)` is `False`, and `iter(Old())` returns a real iterator object. A reader debugging why a working `for` loop fails an `isinstance` check or a type annotation has nothing in this chapter to explain it, and this is the chapter that owns the question.

**Proposal:** Two sentences, no listing:

> One legacy path bypasses `__iter__()`.
> A class that defines only `__getitem__()` taking integers from zero is still iterable:
> `iter()` builds an iterator that indexes it until `IndexError`.
> Such a class works with `for` while failing `isinstance(obj, Iterable)`
> and failing an `Iterable[T]` annotation,
> which is the one case where the loop and the checker disagree.
> Write `__iter__()` in new code.

Alternative: a three-line listing showing the disagreement, which makes it concrete but costs a listing in the chapter's shortest section.

**Cost:** none. It does slightly complicate "Two methods make up the protocol," which is the section's opening claim, so it belongs after that claim has been paid off by `basic_iteration.py`, not before.

---

## 8. "Only `next()` in a loop hands you that exception" is ambiguous

**Kind:** prose
**Where:** section "The Pattern That Disappeared", after `asking_costs.py` (line ~643)
**Problem:** "In a loop" reads as a qualifier on when `next()` raises an exception, but `next()` raises whenever it is called without a default, loop or not; the loop in `doubled()` is incidental. Two paragraphs earlier the chapter showed `next(numbers, DONE)` outside a loop, so a reader has both forms in mind and the sentence does not distinguish them. What the sentence means is that a bare `next()` is the only construct in the chapter that lets `StopIteration` reach you.

**Proposal:** "Only a bare `next()` hands you that exception. Given a default it returns the default, and every other construct here absorbs it."

**Cost:** none.

---

## 9. Two sections have no exercise

**Kind:** exercise
**Where:** "Exercises" (line ~658)
**Problem:** The eight exercises cover the protocol, generators, exhaustion, `tee`, `itertools`, and the GoF dissolution, but nothing asks the reader to do anything with `yield from` or with the type-checking wrapper, which are two of the chapter's six sections. `yield from` in particular is a construct the reader will write, and the chapter's own claim that it "forwards `send()` and `throw()`" is left as an assertion nobody tests.

**Proposal:** Add two exercises:

> 9.  `flatten()` and `flatten_loop()` agree on the values they produce.
>     Give the recursive call a `return` value and have the caller bind it
>     (`total = yield from flatten(item)`), then run both versions
>     and explain what `flatten_loop()` returns instead.
> 10. `typed()` accepts an `Iterable[object]` while `TypedIterator` requires an `Iterator[object]`.
>     Explain why from the bodies of the two, and say what the test file has to do differently for each.

Alternative: one exercise instead of two, choosing the `yield from` one, since the type-checking section is the shorter of the two gaps.

**Cost:** Exercise 9's return-value question overlaps chapter 45's "The Return Channel" section. That is arguably fine, since the chapter already states the fact here, but check that it does not deflate 45's listing.

---

## 10. The eager-validation idiom is described but never shown

**Kind:** teaching
**Where:** section "Generators", "To validate eagerly, check the arguments in a plain function and have it return an inner generator." (line ~148)
**Problem:** This is the standard fix for the deferred-body surprise and the paragraph before it makes a real case that the reader will need it. Then it arrives as one sentence with no code. The shape of the fix, an ordinary `def` that validates and returns a call to a nested generator function, is not obvious from the description, and a reader who guesses wrong writes a `def` with a `yield` in it and gets the same deferred behavior back.

**Proposal:** Six lines under that sentence:

```python
# eager_validation.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError(f"n must not be negative: {n}")
    def produce() -> Iterator[int]:
        for i in range(n):
            yield i * i
    return produce()

try:
    squares(-1)  # Raises now, not at first next()
except ValueError as e:
    print(e)
#: n must not be negative: -1
```

with a following sentence noting that `squares()` has no `yield`, so calling it runs the check immediately, and only `produce()` is deferred.

Alternative: leave it as prose and make it exercise 4's second half, which already asks the reader to restructure `generator_lifecycle.py`.

**Cost:** A new listing needs the full verify loop. It also puts a nested function in a chapter that otherwise has none, which is a second unfamiliar element in one listing; if that reads as too much, the alternative above avoids it.

---

## 11. Small prose nits

**Kind:** prose
**Where:** throughout
**Problem:** Individually minor, listed together so they can be accepted or rejected as a batch.

**Proposal:**

- line ~23: "so a function written against an iterable automatically stays decoupled from the container" -- drop "automatically", which adds nothing.
- line ~28: the comment `# Called by a for loop` sits on `it = iter(nums)` and reads as though `it` is what a `for` loop calls. If this comment is being touched anyway, "`# A for loop makes this call`" says it. (Left alone per the house rule on existing comments.)
- line ~112: "A generator can even be *infinite*." -- "even" is on the watch list and deleting it changes nothing.
- line ~356: "That call never returns, and no test survives." -- "no test survives" is a flourish; "and the test never finishes" says it.
- line ~588: "Python dropped both methods rather than pay for them everywhere" -- "rather than paying" agrees better.

**Cost:** none.

---

## Verified clean (no action)

- All 14 extracted files: `ruff` clean, `ty` clean, 16 tests pass, every `#:` marker matches real stdout.
- `tee.py`'s threshold boolean (`buffered > listed * 0.9`) ran `True` five times out of five; measured 4,096,544 buffered against 3,999,992 listed, which matches the figures quoted in the prose exactly and leaves a wide margin over the 3.6 MB threshold.
- Every cross-reference resolves (`heading_links.py` passes): 45 (annotation), 19 (`concurrent_tee`), 16, 14, 21, 20, 05. Chapter 19 does document `threading.concurrent_tee()` under the anchor named here.
- No relative "the previous chapter/section" phrases anywhere in the chapter; every backward reference is a named link.
- The 23/45 boundary is drawn where this chapter says it is: 23 owns the one-way `Iterator[T]` form and `yield from` as pure delegation, 45 opens by naming 23 and takes over the send and return channels. No overlap or contradiction found.
- `sentinel("DONE")` with no `Final` annotation matches the book-wide convention (ch 05, 15, 17, 41). `N = 100_000` with no `Final` matches ch 18 and ch 19 demo scripts. `tracemalloc` is introduced in ch 18, which precedes this chapter.
- The claim that `ruff`'s comprehension rule rewrites `[n for n in count(1)]` to `list(count(1))` is correct (C416).
- PEP 479's `StopIteration` to `RuntimeError` conversion is correctly described and reproduces on the pinned 3.15.0b4.

---

## Already fixed directly (no decision needed)

- line ~398: "the near-miss described previously" to "the lookalike described previously". "near-miss" is on the do-not-use tier of the watch list, and "lookalike" is the word the chapter already uses for this construct twelve lines earlier ("because its lookalike is the `if` clause of a generator expression").
- line ~593: "Python fuses that question into `__next__()`" to "Python makes that question part of `__next__()`". "fuse" is on the do-not-use tier.
- line ~653: "come from the same fusion" to "come from the same cause". Same word. See proposal 3, which rewrites this sentence further.
