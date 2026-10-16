> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Pattern Matching

This chapter had several passes earlier today (straighten, metadiscourse, continuity),
and the scan turned up few AI-writing tells.
Six findings had one sensible answer, so they went into the chapter directly
and are listed below.
This file has no live blocks.
It records the applied changes and the findings judged not worth acting on.
`tip reflow CH=13` and `tip verify-ch CH=13 ISOLATED=1` pass (27 of 27).

## Applied directly

- Line 36 (§70 restatement, treadmill): "runs the body of the first one that fits. After that one `case` body runs, the statement ends." -> "ends after the first matching `case` body runs." Line 8 already says the first fitting `case` runs, so one sentence covers it.
- Line 219 (personification, the global "wants" rule): "A pattern rarely means to take a string apart" -> "You rarely want a pattern to take a string apart" (a reader's "want" is the carve-out in `readability_db.md`).
- Line 370 (pointer with two candidates): "makes that case unreachable" -> "makes the `bool` case unreachable"; "that case" could point at `case int(n)`, the nearer noun.
- Lines 683-684 (R2, commerce standing for a consequence): "its cost grows ... A dictionary lookup costs the same at any size" -> "its running time grows ... A dictionary lookup takes about the same time at any size." "About" hedges the average-case claim for a hash lookup. The close alternative kept "cost" as computational time, which R2 allows for a measured quantity, but no measurement appears here.
- Lines 870-871 (and-split, subject change): "with its own `render()` and `cost()`, and nothing else changes" -> two sentences.
- Lines 880-881 (and-split, subject change): "with its own `match`, and the existing classes and functions stay untouched" -> two sentences, parallel with the fix above.

## Considered and declined

- Line 19, "`match` becomes valuable once the patterns do more than test equality." "Valuable" is a §7 word, but it is the only Tier hit in the chapter, and `readability_db.md` says a single hit is not a cluster. A rewrite that names what `match` gains would add a claim the sentence does not make.
- Lines 37-38, "Cases do not fall through as they do in C's `switch`, and `match` has no `break` to forget." The subject changes at the "and", but the two clauses are parallel absences (no fall-through, no `break`), so the "and" is additive. Splitting them left a run of three short sentences.
- Line 465, "so it dispatches cleanly on JSON-shaped data." "Cleanly" passes the deletion test as a word with content: it means the extra keys do not interfere.
- Lines 147-148, "`case Signal.GO` compares. `case DEFAULT` binds." Two short sentences in a row, but this is the deliberate beat the section heading sets up (the recurring keep for short emphatic fragments).
- Lines 546-551, the short run after `nested_patterns.py` `[2]` ("`survey([Point(0, 5)])` matches. ... Either alternative binds `n`. The compiler enforces the same-names rule."). The sentences are short but each makes its own claim. Merging any pair would join clauses with different subjects on an "and".
- Line 706, "Every channel also has a rough cost to send a message," and line 845, "render and price each channel alike." Money in the program's domain, which R2 keeps.
- Line 888, "It also has a name: the *expression problem*." By shape this is a §69 colon reveal, but the colon delivers the term being introduced (the lead-in names "a name"), so it passes the colon rule.
- Line 629, "lists every member: a sealed hierarchy or an enum." The colon delivers the examples of such declarations, so "namely" fits.
