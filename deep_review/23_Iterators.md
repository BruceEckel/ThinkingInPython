When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

[] Reject

**"Iteration Is Built In", after `basic_iteration.py` (around line 42).
Missing: the `for` loop desugaring the section describes but never shows.**

The prose says "A `for` loop makes one `iter()` call, then calls `next()` until
`StopIteration` occurs," and `basic_iteration.py` shows `iter()`, `next()`, and
the `except StopIteration` separately. The reader never sees the three assembled
into the loop they replace, which is the one thing that makes the protocol click.
This is the chapter's cheapest mechanism-vs-outcome win.

Proposed: add a non-extracted fence (no `# slug.py` first line, so no gate runs
on it) immediately after the paragraph at line 42-46, with one sentence of lead-in:

> Written out, `for x in nums:` is this loop:
>
> ```
> it = iter(nums)          # Once, before the loop
> while True:
>     try:
>         x = next(it)     # Once per step
>     except StopIteration:
>         break
>     ...                  # The loop body
> ```

An unfenced-language block is used elsewhere in the book for exactly this kind of
non-runnable sketch (chapter 19's "The tempting fix is a lock inside the loop"
block). Alternative if you would rather not add a block: fold the same three
steps into the existing prose sentence. I recommend the block; the indentation is
doing the teaching.

[] Reject

**"Generators" section, `test_iterators.py` (block starts at line 277).
The test sits 190 lines after the code it tests, and the prose forward-references
it across that gap.**

Line 112 says `Countdown` "can be iterated repeatedly, as the re-iteration test
below confirms." The test that confirms it does not appear until after the
laziness discussion, `eager_validation.py`, `walked_twice.py`, and all of `tee`.
Every other test listing in this chapter sits immediately after the code it
exercises (`test_yield_from.py`, `test_endless.py`, `test_typed.py`), so this one
is the outlier.

Proposed: move the `test_iterators.py` block and its two-sentence lead-in
("These tests collect each iterator into a list and compare them...") up to
directly after the paragraph ending "...as the re-iteration test below confirms"
at line 112, and change that clause to "as the tests below confirm."

Cost of the move: nothing downstream names `test_iterators.py`, and it imports
only from `iterators.py`, which is already defined above the new position. The
`tee` paragraph then ends the section, which is a slightly weaker landing than a
test block; if that matters, the alternative is to leave the block where it is and
change line 112's forward reference to name the section it lands in.

[] Reject

**"Generators" section (lines 55-303). The section carries three separable
topics and runs 249 lines, the longest in the chapter by a wide margin.**

It introduces generator functions and generator-as-`__iter__()`, then the costs of
laziness (deferred body, eager validation, silent exhaustion, `Iterable` vs
`Collection`), then `tee`. The escalation is right and nothing is out of order,
but the reader gets no heading to navigate by, and the chapter's own conclusion
later refers back to "Both surprises earlier in this chapter" as if they were a
named unit.

Proposed: split at line 125 with a new `## The Costs of Laziness` heading placed
just before "There are two surprising consequences of laziness." Everything from
there through the `tee` discussion moves under it.

Cost: `#generators` is linked from chapters 15 (twice), 16, 27, 31, and 45, and
all of those point at the generator-basics half, which keeps the anchor. Nothing
links to the second half. Adding the heading also gives the closing paragraph a
name to point at, so "Both surprises earlier in this chapter" could become
"Both surprises in [The Costs of Laziness](#the-costs-of-laziness)".

[] Reject

**End of the chapter (lines 730-736). The chapter's conclusion is buried under a
section title about the GoF pattern.**

The final paragraph ("Both surprises earlier in this chapter come from the same
rule: the protocol answers no question for free...") is the whole chapter's
closing insight, not a conclusion about GoF Iterator. It sits under
"The Pattern That Disappeared", so a reader skimming headings will not find it,
and the table of contents shows the chapter ending on a pattern-history note
rather than on its actual claim.

Proposed: promote that last paragraph to its own short section,
`## The Protocol Answers Nothing for Free`, immediately before "Exercises".
Nothing else moves. The heading names the insight, which is what the skill asks a
conclusion to do, and it also gives the two "surprises" paragraphs a destination.

[] Reject

**Line 736: "The protocol is free, and quiet."**

The same paragraph opens with "the protocol answers no question for free," where
*free* means "without cost." Five lines later *free* means "costs you nothing to
use." The two senses are opposite in effect and the reader has to stop and decide
which one the closing line means.

Proposed: "The protocol costs you nothing, and tells you nothing." That keeps the
two-beat rhythm and drops the collision. Alternative: "The protocol is cheap, and
quiet."

[] Reject

**Line 481: "Nothing in the toolchain (except an AI) will discover problems like
this."**

An AI is not part of the toolchain, so the parenthetical contradicts the sentence
it sits in, and the claim is unverified in a paragraph where the two neighbouring
claims (`ty` accepts `list(count(1))`; ruff's only relevant rule is the
comprehension one) are both demonstrably checked. "AI" appears in only one other
place in the book (chapter 44, line 683), so the aside also reads as
out-of-character here.

Proposed: either cut the parenthetical, leaving "Nothing in the toolchain will
discover problems like this," or make the claim its own sentence and own it:
"No static tool will find this. A reader, or a model reading the code, has to
notice that `count(1)` never ends." I recommend the plain cut.

[] Reject

**Line 143, `generator_lifecycle.py`: the comment `# Remainder of list`.**

There is no list at that point; `sq` is a generator, and the line is what builds
the first list. The comment means "the values that are left." As written it
invites the reader to think `sq` is a list, which is exactly the confusion the
listing exists to remove.

Proposed: `# The values that are left`.

[] Reject

**Exercises (lines 738-767): two of the chapter's seven sections have no
exercise.**

The set covers `iterators.py` (1, 2), `generator_lifecycle.py` (4),
`reusable_algorithms.py`/`test_endless.py` (3, 6), `tee.py` (5), and
`gof_iterator.py`/`asking_costs.py` (7, 8). Nothing touches
"Delegating with `yield from`" or "A Type-Checking Iterator", and those are the
two sections whose material a reader is most likely to adapt into their own code.

Proposed: add two exercises. Placing them in reading order would renumber 5-8, so
appending them as 9 and 10 is the cheaper option; your call.

> 9.  `flatten()` recurses on anything that is not an `int`.
>     Call it on `[1, "ab", 2]` and explain the `RecursionError` you get,
>     using the fact that a one-character string is still a `Sequence`.
>     Then fix `flatten()` so a `str` yields as one item, and say what the same
>     fix would look like in `flatten_loop()`.
>
> 10. `typed()` raises on the first item of the wrong type, which ends the
>     stream. Write `typed_skipping()`, which drops mismatched items and keeps
>     going, then say which of the two you would want wrapping a parsed log
>     file, and why. Which one is easier to write as `TypedIterator`?

[] Reject

**Chapter-level, low priority: the chapter never mentions the two-argument
`iter(callable, sentinel)` form.**

The chapter builds `DONE = sentinel("DONE")` twice and explains at lines 711-713
why the answer must be distinguishable from every value the source could yield.
The standard library has a builtin that is exactly that idea,
`iter(callable, sentinel)`, which calls `callable` until it returns the sentinel.
It would land naturally in one sentence next to the `DONE` explanation in
`asking_costs.py`'s prose and would let a reader recognize the form in real code.

Proposed, after "…into the same reply." at line 713:
"The builtin `iter()` takes the same bargain in its two-argument form:
`iter(callable, DONE)` calls `callable` until it hands back `DONE`."

I am reporting rather than applying this because the chapter is already dense and
the addition is an extra topic rather than a repair.

[] Reject

**Chapter-level, low priority: three different functions named `squares()`, with
three different mechanisms, and the chapter never connects them.**

`generator_lifecycle.py`'s `squares()` is a generator function.
`eager_validation.py`'s is a plain function returning an inner generator.
`tee.py`'s is a plain function returning a generator expression. The second and
third have the same shape, and the difference between the first and the second is
the whole point of the eager-validation listing, so the reuse of the name is
either a missed callback or a source of confusion depending on how closely the
reader is reading.

Proposed: one clause in the `tee.py` lead-in noting that this `squares()` is the
plain-function form from `eager_validation.py`, with the genexp standing in for
`produce()`. Alternative, if the echo is unintentional: rename `tee.py`'s to
something neutral like `stream()`, which also stops the reader from expecting the
`print` tracing behavior of the first one.

## Cross-chapter

[] Reject

**`Chapters/21_The_Pattern_Concept.md`, line 87, in "When a Pattern Dissolves".**

The section names four dissolutions and links three of them to their chapters:
`[Function Objects](28_Function_Objects.md)`, `[Factory](27_Factory.md)`,
`[Singleton](24_Singleton.md)`. The fourth, "Iterator is the clear case," has no
link, even though chapter 23 links back to this exact anchor from
"The Pattern That Disappeared" and that section is where the claim is cashed in.

Change I would make in chapter 21 (not made here):

> `Iterator is the clear case.`
>
> becomes
>
> `[Iterator](23_Iterators.md#the-pattern-that-disappeared) is the clear case.`

The anchor `#the-pattern-that-disappeared` is the pandoc auto-slug and is live
(`heading_links.py` passes against it).

Second, smaller item in the same chapter: lines 87-89 restate almost verbatim what
lines 71-72 already said sixteen lines earlier ("implicitly available in `for`
loops from the beginning of the language, and became an explicit feature in
Python 2.2" versus "It was implicit in the `for` loop from the start, and Python
2.2 made it a protocol"). Worth collapsing when chapter 21 is next edited.

[] Reject

**`Chapters/19_Concurrency.md`, line 1371, "Sharing an Iterator Between Threads".**

Chapter 23 forward-references this section for `threading.concurrent_tee()` and
for what goes wrong when two threads call `next()` on one iterator. Chapter 19
does not reference chapter 23 in return, so a reader who meets the iterator
protocol first in chapter 19 (four chapters early) gets no pointer to where it is
taught.

Change I would make in chapter 19 (not made here): in the section's opening
paragraph, after "An iterator has never been thread-safe:", add a pointer such as
"([Iterators](23_Iterators.md) covers the protocol itself)." Low priority; the
forward direction already works.
