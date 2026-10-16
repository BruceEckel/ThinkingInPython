> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Error Handling, Solutions

The Solutions file for chapter 42 carries no Tier 1 or Tier 2 vocabulary,
no signposting, no significance inflation, no curly quotes, and one
watch-list word, a `never` that states the claim.
The six changes below split or rewrite "and" joins between clauses with
different subjects where "but", "so", or "while" fit, drop one stray
"then", and remove a doubled "same".
Each touched sentence was checked against its listing: `exercise_1.py`
prints `func_c(0) runs` and `func_c(3) runs` and no line for `4`, and
`exercise_5.py` calls `add_note()` only inside its `except` clause.
`tip verify-ch CH=42 ISOLATED=1` passed after the edits (27 passed).
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Lines 99-101, "and" standing for "so": "`func_c()` prints a line when it runs, and that line confirms the skip. The line appears for `0` and `3` and is missing for `4`." -> "`func_c()` prints a line when it runs. The line appears for `0` and `3` and is missing for `4`, which confirms the skip." The absent line confirms the skip, so the confirmation moves beside the absence.
- Line 266, stray connective: "To prefix every error in a chain, you then call `result.map_error(prefix)` once" -> "you call". Nothing precedes the "then" in that paragraph.
- Lines 499-502, wording and a doubled "same": "A caller that calls `parse("oops")`" -> "A caller of `parse("oops")`"; "returns that same `TypeError` as `Err(TypeError(...))`, the same shape" -> "returns the `TypeError` as ..., the same shape". The chapter's `@safe` would hold a different exception object, so "that same" also overstated.
- Lines 575-580, "and" hiding the consequence, plus "and" hiding a contrast: "returns its `Ok` from inside the `try` block, and `add_note()` sits in the `except` clause" -> "returns its `Ok` from inside the `try` block and never reaches `add_note()`, which sits in the `except` clause"; "An `Ok` holds an answer, and notes attach to exceptions" -> ", while notes attach to exceptions". The paragraph's 85-column lines were rewrapped at 70.
- Lines 592-596, "and" joining different subjects ("while" fit): "Here it sequences the two calls, and the lambda discards the answer" -> "while the lambda discards the answer"; the closing "reads better here" lost its second "here" (the sentence before opens with "Here").
- Lines 681-683, "and" hiding a contrast ("yet" fit): "fail in three different functions for three different reasons, and `composed()` returns the same `None` for all three" -> two sentences.

## Considered and declined

- Lines 589-591, "`bind()` reads worst in that case": a superlative by shape, but the comparison is among `bind()`'s own uses, and the case named (an answer the next step discards) is the one where it fits least.
- Lines 95-97, "Because `func_d()` sits before `func_c()` in the chain, an `Err` from `func_d()` has a later step to skip": repeats the opening paragraph's placement point, but it closes the "Insert the new step" label, which the reader reaches after the listing.
- Lines 361-365, "`Ok` and `Err` take whatever type parameters each call needs": restates "One generic `Ok`/`Err` pair carries both shapes", but it closes the explanation by naming the mechanism after the two concrete instantiations.
- Lines 688-692, "so the caller receives the same `None` from every failing step": echoes the paragraph above ("`composed()` returns the same `None` for all three"), but here it follows from the mechanism ("`None` is one value and holds no reason") that the "Stop at the first failure" step explains.
- Line 587, "so it never propagates to the top-level handler": the `never` is the claim, a guarantee about every successful-catch path (readability_db's watch-list-absolute keep).
- Lines 582-583, "The `Err` holds the exception, and the exception holds the note as ordinary data": different subjects, but the two clauses are links of one chain that the "so" clause concludes, so the "and" is additive.
