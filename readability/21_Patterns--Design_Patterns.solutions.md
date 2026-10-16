> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Solutions/21_Patterns--Design_Patterns/README.md

Readability sweep of the Design Patterns solutions, 2026-10-16. The file
reads as human-written technical prose: no Tier 1A vocabulary, no curly
quotes, no spaced ` -- `, no signposting or generic closers. Most of its
faults were "and" joins between clauses with different subjects, plus
one sentence that restated its neighbor and several paragraphs whose
hand wrap had gone ragged after earlier passes. Every one had a single
sensible fix, so this file holds no live block and is the
applied-directly record. The exercise 4 claim about the chapter's
figure was checked against "The Reach of a Change": on the left,
`Report` gains a branch and `main` gains a case.

## Applied directly

- Line 95-99, treadmill (two sentences making one point): "...because the
  `match` reads well. The shape works, but every new format is an edit
  you make by hand." -> "...because the `match` reads well, but every new
  format is an edit you make by hand." The cut sentence repeated the one
  before it.
- Line 134-135, "and" joining different subjects: "takes one assignment,
  and `render()` stays as it was" -> two sentences.
- Line 140-141, "and" hiding a contrast: "`STYLES` absorbs the format,
  and a field is a different vector of change" -> two sentences.
- Line 146-147, "and" hiding a contrast: "a new format is one assignment
  and a new field is an edit to every format" -> two sentences.
- Line 234-235, "and" hiding a contrast: "Five constructs become one
  parameter, and the type checker still knows..." -> two sentences, the
  second ending in a colon that delivers the `Callable` comparison.
- Line 241-243, "and" joining different subjects: "passing a behavior
  means passing an object, and the crossed-out parts build that object"
  -> two sentences.
- Line 327, adverb compound: "a wrongly-shaped argument" -> "a wrongly
  shaped argument" (an -ly adverb takes no hyphen).
- Line 442-443, a count with no referent in reach: "The first version
  below makes all three edits." -> "The first version below edits all
  three: the alias, `main()`, and `render()`."
- Line 504-506, colon pointing past a parenthetical: "The change
  therefore reaches two parts, as the left half of the chapter's figure
  shows: `Report` and `main`." -> "...reaches two parts, `Report` and
  `main`, as the left half of the chapter's figure shows."
- Line 557-558, "and" joining different subjects: "`Report` and `Writer`
  keep their source, and no writer names `Writer`" -> two sentences.
- Lines 3-8, 62-65, 102-104, 239-245, 323-353, 438-445, 503-506,
  565-572: rewrapped hand-wrapped prose to about 70 columns where earlier
  edits had left one-sentence lines and short fragments. Wording
  unchanged beyond the items above.

## Considered and declined

- Lines 95 and 134, the bold labels "**Branch on the format.**" and
  "**Hold each format as data.**" (§15, §16). They name the two listings'
  approaches and follow the bold step-label form the Solutions files use.
- Line 326, "What stops working? Nothing." (§43). The exercise asks the
  reader to "say what stopped working", so the question is the content.
- Line 343-348, the closing paragraph of exercise 3 restates the hint's
  test ("If nothing broke, the piece was supporting code..."). The hint
  sits in a collapsed step a reader may have skipped, and the solution
  closes on the test it has just run twice; "worth keeping and worth
  naming" weighs the piece against removing it, the §53 carve-out.
- Line 205-206, "states that signature without declaring a type": the
  negative is the claim (the contrast with a Java interface).
- Line 62, "plain text": the contrast with CSV and JSON, the case the
  "plain" rule keeps.
- Line 337-338, "What stops working is the requirement": a pseudo-cleft
  whose complement echoes the exercise's question, not an "is what"
  delaying a verb.
