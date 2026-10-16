> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Classes, Solutions

The Solutions file for chapter 07 carries no Tier 1 or Tier 2 vocabulary,
no signposting, and no significance inflation.
The six changes below split "and" joins between clauses with different
subjects, cut one hint sentence that restated the sentence above it, and
merge a choppy run at the end of exercise 6's hint.
The numbers the prose quotes (`36.85000000000002`, `27.0` against
`26.999999999999996`, the equal unrounded `100.0` pair, and `expect()`'s
`no exception raised`) were checked by running them under `uv run`.
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Lines 17-18, "and" joining different subjects: "The setter then runs on the computed value, and the test catches the setter's `ValueError`" -> two sentences.
- Lines 48-49, "and" hiding a consequence: "`shrink(-2)` then stores `-2.5`, and `expect()` fails with ..." -> two sentences. (Close alternative: ", so `expect()` fails".)
- Lines 363-364, "and" hiding a consequence: "computes and caches `total` at that moment, and `"summing"` still appears once" -> two sentences.
- Line 381, treadmill (repeated claim): cut "Notice which method `print()` uses for the object and which one the list uses for its elements.", which restates the hint's first sentence.
- Line 466, staccato run: "The decorator is for the type checker. Run the type checker with and without `@override` and compare." -> "The decorator is for the type checker, so run the checker with and without `@override` and compare."
- Lines 527-528, "and" joining different subjects: "Every override of it becomes an unrelated new method, and Python reports nothing" -> two sentences, matching the same fix in the chapter's review.

## Considered and declined

- Lines 279-280, "The lookup starts at the class of the object, and `self` is a `MoreDerived`, so each call resolves to `MoreDerived.show()` first": the two clauses are joint premises of the "so", and splitting them would hang the conclusion on the second alone.
- Lines 277-278, "`MoreDerived` inherits `show_twice()` from `Simple`, and `show_twice()` calls `self.show()` twice": additive sequence; no "but", "so", or "while" fits.
- Lines 431-433, "`print()` calls the `__str__()` that `Temperature` inherits from `object`, and that method calls `__repr__()`": two steps of one call chain, which the "and" rule keeps.
- Lines 437-438, "because a container formats its elements with `repr()`, not `str()`": repeats line 404's claim, but each sits in a different rung of the reveal ladder, and a reader may open only one.
- Lines 520-522, "`@override` states an intention, the type checker verifies it, and the running program ignores it": a triple by shape (§10), but three real parts the paragraph has just walked through.
- Lines 530-531, "A decorator that changes no behavior at run time is worth writing when a tool reads it": §53 by shape, but "worth" weighs the effort of writing it against a stated condition (recurring keep).
- Lines 441-443, "the form you want in a traceback": "want" addresses the reader (recurring keep).
- Lines 228 and 272, "only when an override calls it" and "shows only the `show()` chain": ruled-fine `only` shapes.
