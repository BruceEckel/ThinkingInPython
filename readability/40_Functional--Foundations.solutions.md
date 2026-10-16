> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/40_Functional--Foundations/README.md`,
2026-10-16.
The prose had few AI tells. The findings were "and" joins that hid a
consequence or a contrast, one self-labeling lead-in, one redundant
instruction, one trailing clause that repeated its paragraph's opening,
and lines that had drifted past the README's 70-column hand-wrap.
Fourteen fixes went in directly, and no finding needed Bruce's judgment,
so this file holds no live block and serves as the applied-directly
record.
The claims touched were checked against the listings and the chapter:
`exercise_7_map.py` binds the `map` object to `raw`, the chapter's rule
of thumb picks the comprehension for an inline expression, the
Fahrenheit values 64.4, 77.0, and 86.9 follow from 18.0, 25.0, and 30.5,
and `exercise_9.py` prints `data`'s Celsius values after calling both
functions.
`tip verify-ch CH=40 ISOLATED=1` passed, 27 of 27. Line numbers below
are the pre-edit ones.

## Applied directly

- Lines 123-125, "and" hiding a consequence: "the other four entries,
  and the calling code stays as it was" became two sentences.
- Lines 228-229, hand-wrap: the type-checker sentence ran to 78
  columns; rewrapped, wording unchanged.
- Lines 296-302, hand-wrap: the section-5 trap paragraph had lines near
  90 columns; rewrapped, wording unchanged.
- Lines 320-328, hand-wrap: the "Preset the leading argument" and "Show
  where the keyword fails" steps had lines past 100 columns; rewrapped,
  wording unchanged.
- Lines 336-341, treadmill: the closing clause ", while the runtime
  raises its `TypeError` only at the call" repeated the step's opening
  ("finds the mistake earlier than the runtime does") and line 327 ("The
  partial fails at the call"); it went, and the step was rewrapped.
- Lines 378-387 and 399, hand-wrap: the two section-6 steps and the
  sentence before the tuple listing ran past 75 columns; rewrapped,
  wording unchanged.
- Lines 457-460, hand-wrap: the "Write the expressions inline" step;
  rewrapped, wording unchanged.
- Line 465, redundant instruction: "Run the sort to confirm that order."
  went, since the listing's marker above shows the order.
- Line 468, §39 self-labeling: "Dropping the `list()` is the part that
  surprises:" became "Without the `list()`, `raw` is a `map` object:",
  which states what the listing shows and leaves the surprise to the
  two steps below it.
- Lines 482-486, hand-wrap: the "Inspect the lazy object" step;
  rewrapped, wording unchanged.
- Lines 544-545, hidden contrast: "captures two names, `step` and
  `count`, and `count` alone needs" became "..., but `count` alone
  needs".
- Lines 548-551, "and" joining two claims and hiding a consequence:
  "`increment()` assigns `count`, and assignment is how Python decides
  a name is local" became "`count` differs because `increment()`
  assigns it. Assignment is how ..."; "makes `count` a local of
  `increment()`, and `count += step` reads the local" became "..., so
  `count += step` reads the local".
- Lines 659-674, hand-wrap: the "Add the upper bound" and "Reorder the
  stages" steps had lines past 90 columns; rewrapped, wording
  unchanged.
- Lines 678 and 683, "and" hiding a contrast, and an imprecise count:
  "The field name `celsius` alone records the unit, and
  `to_fahrenheit()` keeps that name" became two sentences; "stay the
  same after three traversals" became "after both calls", since the
  listing's last line prints the values after `report()` and
  `converted_first()` have each run once. Both paragraphs were
  rewrapped.

## Considered and declined

- The "Where to look" hint paragraphs (lines 12-14, 63-65, 142-144,
  194-196, 277-279, 359-361, 436-438, 509-511, 576-578) carry one
  sentence per line, several past 100 columns. Kept: the hints in the
  other Solutions files use the same layout (chapters 20-29 each carry
  7 to 25 hint lines past 90 columns), so rewrapping these alone would
  make this file the odd one.
- Lines 416-419, colon: "That split is the chapter's point: `Final`
  makes the checker reject a rebinding of the name, and the value's own
  type makes it reject a change to the contents." The words after the
  colon restate the split in its two halves, the restatement the colon
  rule keeps, and the two-clause weight is the split's own shape.
- Lines 320-321 and 325-327, "and" between premises: "`low` is the first
  parameter, and `partial()` fills positional arguments from the left,
  so ..." and "`partial()` stores its arguments, and the signature check
  waits for the call, so ...". Kept: each "and" joins two premises that
  the "so" clause then draws on together, which is additive.
- Line 659, "`colder_than()` mirrors `warmer_than()`, and `partial()`
  turns each into the one-argument callable `filter()` requires." The
  subjects differ, but the second clause neither contrasts with nor
  follows from the first; it adds the step's other half.
- Line 49, "The chapter names that tracking as the problem with
  `withdraw()`." The chapter says "To understand one `withdraw()` call
  you must trace every call before it", which the sentence paraphrases
  accurately.
- Lines 488-489, "is the more dangerous half." A judgment by shape, but
  the next sentence supplies the reason (an empty list with no
  exception), so it is not an unearned label.
