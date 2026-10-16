> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/04_Foundations--Control_Flow/README.md`, 2026-10-16.
The file had few AI-writing tells, so this review holds no live block
and serves as the record of the edits applied directly.
Most were an "and" joining two clauses with different subjects, plus one past-tense slip in a hint.
Each sentence about a listing was checked against the listing (and the `read_text()` claim against `pathlib`'s source) before it was touched.
`tip verify-ch CH=04 ISOLATED=1` passes.

## Applied directly

- 14 (exercise 1 hint), present tense for standing behavior: "how the loop ended, not on what the body did" -> "ends ... does".
- 77 (exercise 2), "and" standing for "so": "includes the `1` ..., and `collatz_sequence(10)` returns `(6, 2)`" -> "..., so ...".
- 79-80 (exercise 2), "and" joining a consequence: "has a branch of its own, and the increment runs under the same test" -> "a branch of its own, where the increment runs ...".
- 147-148 (exercise 3), "and" joining a consequence with a new subject: "at most one of them is true on any iteration, and each block's outcome stays the same" -> two sentences, the second with "therefore".
- 326 (exercise 6), two claims on one "and": "four lines instead of one, and until it finishes the name `evens` holds a partial result" -> two sentences.
- 328 (exercise 6), "and" standing for "so": "The loop says how to build it, and the reader traces the loop" -> "so the reader traces".
- 332-335 (exercise 6), rewrapped the paragraph to about 70 columns; wording unchanged.
- 416-417 (exercise 7), "and" joining two claims with different subjects: "`from` accepts any expression that produces an exception, and a name bound by `except` is one such expression" -> two sentences.
- 530-531 (exercise 9), "and" standing for a contrast: "the survivor sits mid-list, and here it sits first" -> two sentences.
- 579 (exercise 10), "and" standing for "while": "`int()` accepts both strings and `look_first()` rejects both" -> two sentences.

## Considered and declined

- 107-108, "The sequence takes six steps, and one of them (`5 -> 16`) starts from an odd `n`": additive, two counts from the same run.
- 426-429, the parallel pair "`__context__` answers ..., and Python fills that attribute in automatically" / "`__cause__` answers ..., and `from` alone fills that one in": the matched structure carries the contrast, so both sentences stay.
- 476, "Two things follow from that control.": a count that names what follows, not §28 signposting.
- 520-521, "At position 0 the loop sees `2` and `remove()` deletes the first equal item": two steps of one walkthrough.
- The bold step labels ("**Let an unmatched exception through.**", "**Chain from a constructed cause.**") are a Solutions convention, not §15/§16 boldface overuse.
- 484, "a stream that has no end": the positive alternatives ("endless") are no plainer.
- The many `only` hits (110, 149, 215, 244, 288, 292, 588) are all ruled-fine shapes ("only when", "only a", "only between", "only where").
