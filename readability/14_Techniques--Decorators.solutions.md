> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 14_Techniques--Decorators (Solutions)

The solutions carry no AI-writing tells: no vocabulary clusters, no curly quotes or spaced `--`, no stacked hedges, and no metadiscourse.
The fixes were sentence-level: "and" between two claims with different subjects, a few claims made more accurate against their listings, a past tense for standing behavior, and hand-wrap defects left behind where the bold step labels were inserted (lines that broke after one or two words).
This file holds no live block, so it is the record of the applied changes and of what was examined and left alone.

## Applied directly

- Lines 37-38 (exercise 1), "and" standing for a consequence: "`announce` returns `None`, and Python binds `None` to ..." -> "`announce` returns `None`. Python then binds `None` to ...".
- Lines 79-82 (exercise 1), "and" joining a contrast between different subjects: "`@dataclass` returns the class it received after adding generated methods to it, and `@singleton` returns a different object" -> two sentences. The paragraph was rewrapped too ("Two other kinds of" stood alone on a line).
- Lines 65-77 (exercise 1), hand-wrap defects only ("not at / instantiation.", "can / observe and record."), rewrapped at about 70 columns. No wording change.
- Lines 186-189 (exercise 2), "and" between different subjects hiding a contrast: "because the `#:` marker is constant and the raw number changes every run" -> "because the raw number changes every run while the `#:` marker stays constant".
- Line 198 (exercise 2), accuracy against the listing: "`timing`'s wrapper measures and reports the elapsed time around the real `add()` call" -> "times the real `add()` call and prints its timing line". The listing prints `add timed, non-negative: True`, not the elapsed time, as the paragraph above it says. Lines 191-203 rewrapped with it.
- Line 327 (exercise 3), causation stated backward: "The type checker matches a `Protocol` structurally, so none of the three inherits from `Drink`" -> "so none of the three needs to inherit from `Drink`". Structural matching makes inheritance unnecessary; it does not cause its absence.
- Line 525 (exercise 5), figure for a mechanism: "The type checker passes that version, so the failure waits until the program runs" -> "accepts that version, so the failure shows up when the program runs".
- Line 527 (exercise 5), "which" with two candidates (the pairs or the tuple): "a tuple of name-value pairs, which hashes whenever every argument does" -> "..., so the key hashes whenever every argument does".
- Lines 598-603 (exercise 5), "and" joining two claims with different subjects: "The two decorations call `memo` two different ways, and the body tells them apart" -> two sentences.
- Lines 607-609 (exercise 5), label echo and two different-subject "and"s: "**Keep the forms distinct.** The signature keeps the two calls distinct. `func` is the one positional parameter, and `maxsize` is keyword-only. A positional argument always binds to `func`, and `maxsize` must arrive by name." -> "The signature has one positional parameter, `func`, so a positional argument always binds to it. `maxsize` is keyword-only and must arrive by name."
- Lines 721-726 (exercise 6), hand-wrap defect ("function. A" with the next sentence on the following line), rewrapped. No wording change.
- Lines 728-735 (exercise 6), "outside the `try`" stated three times in two short paragraphs, and an "and" hiding a contrast: "The loop runs `times - 1` attempts inside a `try`, and the final attempt sits outside it" -> two sentences; "The last call, outside the `try`, satisfies both requirements" -> "That attempt satisfies both requirements"; the closing "since that call sits outside the `try`" -> "since that attempt sits outside the `try`", so one noun runs through. ("That attempt" rather than "The final call" also keeps `tip positional` quiet; its baseline now holds a stale entry for the old sentence.)
- Line 737 (exercise 6), accuracy: "Catching bare `Exception`" -> "Catching every `Exception`". A bare `except:` is a different construct from `except Exception`, which the listing uses.
- Lines 869-870 (exercise 7), tense for standing behavior and a different-subject "and": "The name `bump` refers to `wrapper`, and the `repeat` instance finished its work at decoration time." -> "The name `bump` refers to `wrapper`. The `repeat` instance finishes its work at decoration time." Lines 864-874 rewrapped with it.
- Lines 329-330 and 589-593 (exercises 3 and 5), hand-wrap defects only (one line of 120 columns), rewrapped. No wording change.

## Considered and declined

- Bold step labels opening paragraphs throughout (§16 by shape): the Solutions convention for walking a solution's steps (`CLAUDE.md` names "a bold step label"), so kept.
- Lines 458-462 (exercise 4), "The two counters show the class-attribute-versus-instance-attribute distinction. `self.count` lives on each instance ... `total_calls` lives on the class ...": restates the "Count each function's calls" and "Share one total across functions" paragraphs (§70 treadmill by shape). Kept: the exercise asks the reader to "note where the shared state lives compared to the per-instance `count`", and this paragraph is the one place that answers that comparison side by side, with the link to chapter 09.
- §34 "real" at lines 75, 186, 198, 622, and 738 ("most real uses", "In real code", "the real `add()` call", "A real implementation", "A real `retry`"): each sentence names its contrast (the listing's deterministic check, the wrapper layers, this exercise's shortcut), the recorded keep.
- Line 76, "covers most real uses: a registry, a plugin table, a validation pass at import time": a rule-of-three inventory and an unsourced "most". Kept as the author's judgment; the three items are concrete and the chapter's `register` is one of them.
- Line 332, "a separate class for every decaf variant": the combinatorial argument is about every combination, not only decaf, but the decaf case is the one the listing builds, so the specific stays.
- Line 731, "satisfies both requirements at once": the two requirements are not named before the sentence, but the next two sentences deliver them in order, so the forward pointer resolves at once.
- Lines 199-202 (exercise 2), "The output order follows the wrapping order." followed by the sentence that spells it out: a general claim, then the instance; kept as the takeaway the exercise's "predict the order" asks for.
- "and" joining two clauses that describe one structure or one sequence ("`trace`'s wrapper is the outermost layer and `timing`'s wrapper is inside it", "`memo` returns `decorate`, and Python applies `decorate` to `add`", "The outermost decorator prints first and last, and each inner layer's output appears nested in between"): two steps or two halves of one picture, so kept.
- Mixed wrapping elsewhere: several prose paragraphs follow one sentence per line rather than a 70-column hand-wrap (the hints, the opening paragraph of each solution). Rewrapping paragraphs that no other finding touched would be diff churn with no rendered change, so only lines with a visible break defect were rewrapped.
