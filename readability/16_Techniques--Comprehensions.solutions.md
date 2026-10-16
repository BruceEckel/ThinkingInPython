> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Comprehensions, Solutions

The Solutions file for chapter 16 carries no Tier 1 or Tier 2 vocabulary,
no signposting, no significance inflation, and no curly quotes.
The three changes below split two "and" joins between clauses with
different subjects and cut one sentence in exercise 4 that restated the
sentence above it.
Each touched sentence was checked against its listing: `int(e)` runs only
when both tests pass, `capitalize()` leaves `"J"` as `"J"`, and `show()`
prints and returns its line.
`tip verify-ch CH=16 ISOLATED=1` passed after the edits.
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Lines 38-39, "and" joining different subjects: "The predicate has two parts, `isinstance(e, str)` and `e.isdigit()`, and `int(e)` runs when both are true" -> two sentences; each clause is a claim of its own.
- Lines 180-181, treadmill (repeated claim): cut "It treats `"J"` and `"John"` as two distinct strings," which restates line 176's "`"J"` and `"John"` are distinct strings, so the set keeps both"; the surviving sentence now reads "The set collapses exact duplicates of the normalized form, so a `"J"` that abbreviates `"John"` stays a separate entry."
- Lines 258-259, "and" hiding a contrast: "`show()` does two jobs, and a reader must open it to learn that one of them is printing" -> two sentences. (Close alternative: ", but a reader must open it".)

## Considered and declined

- Lines 239-252, "the printing is the purpose", "makes the list the point", "`lines` is the point", "where printing is the purpose": the point/purpose pair repeats across exercise 5's two labeled steps, but each use sets one side of the comprehension-or-loop decision against the other, and the repetition carries that contrast.
- Line 248 and lines 254-255, "whether you want the list", "when you want the collection it produces": "want" addresses the reader's intent (recurring keep).
- Line 124, "That ordering matters when the output expression changes the length": §70 by shape, but the sentence names the condition under which the ordering matters rather than rating it.
- Line 178, "The filter exists to drop the initial `"J"` as noise": the chapter never states the filter's intent, but this sentence states no contradicting fact, and the claim is the solution's own reading of the listing.
- Line 407, "the filter runs for every element and the output expression runs again for each element that passes": different subjects, but the clauses are the two counts the hint's next sentence adds together, so the "and" is additive.
- Lines 17, 27, 42, and 147, "runs only on the elements", "calls `isdigit()` only on strings", "the only element", "collide only if": the restriction is the claim in each, and two are ruled-fine shapes ("the only X", "only if").
- The bold step labels in exercises 3, 4, 5, 8, and 9 (§15 by shape): the Solutions files' convention for a labeled step, not emphasis.
