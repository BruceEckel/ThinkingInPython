> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 41_Functional--Toolkits

This chapter carried few AI-writing tells.
The ones it had were two short treadmill passages, one endorsement frame, one intensifier, and one paragraph holding two cautions; each had one sensible fix, and all five are applied below.
The file holds no live block, so it is the record of the applied changes and of the findings judged and kept.
`readability_db.md` was read first, and no prior `readability/~41_*` review exists.

## Applied directly

- Line 19, §12 false range and treadmill: "under `functools`, from a single `reduce()` call to an alternate dispatch mechanism." -> "under `functools`."
  Line 27 states the same simple-to-complex range concretely ("starts with the simplest tools and works up to `singledispatch`"), so the first statement of it was cut.
- Line 95, §53 endorsement frame: "comes back to why the recursive form is worth keeping" -> "explains why `fib()` keeps its recursive form".
  The Recursion section's `fib()` paragraph gives the reason (the recursion states the definition, the cache removes the repetition), so the pointer now names what it points at.
- After line 440, treadmill: cut the orphan bridge paragraph "`itertools` does for iteration what `functools` does for functions. It supplies ready-made pieces you compose, in place of loops you write and test again."
  The itertools section's opening says both halves with more detail: "Each is also a loop you would otherwise write by hand" (with the edge cases named) and "Combine `itertools` functions the way you combine any small function." Close alternative: keep it as the section bridge and cut nothing.
- Line 728, §34 intensifier: "the extra elements are genuinely surplus" -> "are surplus".
  The contrast ("data in their own right") sits two sentences later, not in this sentence, and the sentence means the same without the word. Reflow rejoined the line.
- Lines 793-799, one concept per paragraph: the `tee` paragraph held both cautions, the second opening "And `tee()` buffers".
  Split at that seam, with the second paragraph opening "The second caution concerns memory." before "`tee()` buffers every value...". "Two cautions apply." stays as the first paragraph's lead.

## Considered and declined

- Line 27, "What follows starts with the simplest tools and works up to..." §28 signposting by shape, but it carries the section's order and the one-function-per-type summary of `singledispatch`; with line 19's range cut, it is the only statement of that order.
- Line 102, "One trap: decorating a method with `@cache`..." §69 colon reveal by shape, but "One trap" is a label, and the colon delivers the trap it names.
- Lines 727 and 978, "Plain `zip()`" and "a plain recursive function". "Plain" draws a named contrast in each: against `strict=True` and `zip_longest()`, and against the cached `fib()`.
- Lines 934-937, "Laziness matters most at scale." and the repeated "one item at a time" in the next two sentences. The opener is a topic sentence the paragraph supports, and "Stages chain together" sets up "upstream" in the sentence after it, so the repetition does work.
- Lines 1031, 1040, and 1042, "exactly once" three times. Each states a precise combinatorial count, the use the global rule keeps.
- Line 1043, "The best-known case is *Kirkman's schoolgirl problem*". A superlative by shape, but it orients the reader toward the famous instance, the `readability_db.md` precedent for chapter 28's "best-known closure trap".
- Lines 1050 and 1141, "a good schedule rather than a perfect one" and "good rather than perfect". The echo ties the claim made when the greedy search is introduced to its measured result after `pair_rounds.py`.
- Line 1210, "deterministic in the sense that matters for testing". §70 by shape, but the next sentence delivers the sense (same inputs and seed, same rounds), so the phrase is a pointer, not a gloss.
- Line 1228, "A real pipeline is five or six". §34 by shape, but the contrast is named in the sentence before: this chapter's two-stage `islice(count(10, 2), 5)`.
