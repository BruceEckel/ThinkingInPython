> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Iterators, Solutions

The Solutions file for chapter 23 carries no Tier 1 or Tier 2 vocabulary,
no signposting, no significance inflation, and no curly quotes.
The ten changes below split "and" joins between clauses with different
subjects where "but", "so", or "whereas" fit, cut one restated clause,
correct one ratio computed from the file's own figures, and make one
sentence about `__next__()` literal.
Each touched sentence was checked against its listing or the chapter it
cites: chapter 18's "Lazy Evaluation with Generators" says a data set that
outgrows memory forces the operating system to swap pages to disk and
then fails with a `MemoryError`, and chapter 23's `flatten_loop()` holds
the `for x in flatten_loop(item)` branch.
`tip verify-ch CH=23 ISOLATED=1` passed after the edits.
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Lines 284-285, "and" hiding a contrast: "`Squares` holds one integer, `n`, and each pass recomputes from scratch" -> two sentences, "Each pass recomputes the values from scratch" (the noun named); "but" fit where the "and" sat.
- Lines 290-292, "and" hiding a contrast, plus a literal subject: "A data set that fits runs at full speed, and one that outgrows memory swaps pages to disk or fails with a `MemoryError`" -> "A data set that fits runs at full speed. A data set that outgrows memory forces the operating system to swap pages to disk, or the process fails with a `MemoryError`." A data set swaps nothing; chapter 18 names the operating system and the process. The paragraph's broken hand wrap (one 110-column line) was rewrapped at 70.
- Lines 374-375, "and" joining the two limits ("whereas" fit): "stretches the gap to the whole stream, and lockstep consumption shrinks it" -> two sentences.
- Line 383, ratio: "roughly forty times the memory" -> "roughly forty-five times". The file's own figures, about 416,000 over about 9,300, give 44.7.
- Lines 536-537, "and" hiding a contrast: "`traverse()` stops only when `is_done()` reports the end, and `count(1)` has none" -> "... reports the end. `count(1)` counts forever." (Close alternative: "`count(1)` has no end.", which keeps a negative.)
- Lines 628-629, "and" standing for "so": "The GoF interface assumes every collection allows that kind of access, and `OverStream` builds `seen`" -> ", so `OverStream` builds `seen`". The conjunction states the cause instead of a period dropping it.
- Lines 637-638, "and" hiding the trade-off: "Iterating over `count()` takes constant memory, and rewinding it is impossible" -> two sentences.
- Line 847, treadmill: cut "and take the same repair" from the paragraph's last sentence; its first two sentences say `flatten_loop()` takes the same fix in the same place.
- Lines 849-851, "and" joining different subjects, then a sentence elaborating the second: "`Nested` reads as though a leaf must be an `int`, and `ty` enforces that much. `ty` rejects a `float` in the same list." -> "`Nested` reads as though a leaf must be an `int`. `ty` enforces that much and rejects a `float` in the same list."
- Line 990, literal: "A class resumes at the top of `__next__()` on every call" -> "A class's `__next__()` starts over at the top on every call". A class does not pause, so it cannot resume; the method starts over, against the generator's "resumes there" two sentences above.

## Considered and declined

- Lines 141-143, "`Countdown` can count because it is a container that produces a generator on demand": restates part of the two labeled steps above it, but the paragraph closes the generator explanation by contrast ("reading that value consumes nothing" against "you must consume them"), and the exercise asks for that explanation.
- Lines 279-281, "one by storing and one by recomputing. The list's second pass reads the stored values back.": the second sentence repeats "by storing", but it opens the list half of a parallel pair that the `Squares` sentence closes.
- Line 727, "You cannot write a bare `peek(it)` function": the solution's opening paragraph writes a `peek()` that consumes, so the sentence means a correct one; "bare" against the `Peekable` wrapper carries that, and the exercise statement uses the same "You cannot".
- Line 450, "A reader might reasonably guess": a hedge by shape, but it frames the wrong guess the test refutes.
- Lines 976-977, "and somehow starting past the line that failed": "somehow" is voice, naming the awkwardness of the restart.
- Lines 377, 627, and 832-833, "`islice(ahead, k)` opens the gap, and the `zip()` loop holds it there", "A caller can index that sequence repeatedly, in any order, and every value stays in place", "Iterating over a string yields strings, and a one-character string is a `Sequence` of one-character strings": different subjects, but each "and" joins two steps of one action or two premises of one conclusion, so it is additive.
- The `only` uses ("stops only when its source stops", "only when a pass is slow", "works only if every value stays reachable", "differ only in how they re-yield"): ruled-fine shapes ("only when/if", "only in") where the restriction is the claim.
- Five uses of `ty` in exercise 9's last paragraph: the paragraph contrasts `ty` with Pyright, which the repo rules name as a reason to write `ty`.
- The bold step labels in exercises 2, 5, 7, 8, 9, and 10 (§15/§16 by shape): the Solutions files' convention for a labeled step, not emphasis.
- Long hand-wrapped lines outside the edited sentences (lines 54, 127, 177, 381, 389, and others): wrapping drift from earlier passes; rewrapping untouched paragraphs is churn for this pass.
