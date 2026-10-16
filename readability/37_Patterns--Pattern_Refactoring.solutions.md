> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/37_Patterns--Pattern_Refactoring/README.md`,
2026-10-16.
The prose carried no AI vocabulary, no signposting, and no chatbot
artifacts. The findings were one restated sentence, one "and" hiding a
contrast, two sentences whose logic or pointer read awkwardly, and six
hand-wrapped lines that bold step labels had stretched to 88-105 columns.
Nine fixes went in directly, and no finding needed Bruce's judgment, so
this file holds no live block and serves as the applied-directly record.
The `bin` sentence was checked against `exercise_4.py`'s
`"bin" not in cls.__dict__` test before it was reworded.
`tip verify-ch CH=37 ISOLATED=1` passed, 27 of 27.
Line numbers refer to the README after the edits.

## Applied directly

- Lines 132-134, inverted conditional: "If the test still passed,
  `__init_subclass__()` would have stopped registering subclasses" ->
  "A passing test would mean that `__init_subclass__()` had stopped
  registering subclasses." (a passing test is the evidence, not the
  cause, which the "if ... would have" form implied)
- Line 240, treadmill restatement: "Like `sum_value()`, each one is a
  single function that handles every material." -> "Each is a single
  function, like `sum_value()`." (the sentence before already says the
  same code runs for every material)
- Lines 537-538, "and" joining different subjects in a contrast: "The
  sorter must know the exact class that arrived, and the note uses the
  nearest registration along the MRO" became two sentences.
- Lines 543-544, vague pointer and doubled "default": "`__init_subclass__()`
  defaults each class to itself, so by default every material keeps a
  bin of its own" -> "`__init_subclass__()` sets each class's `bin` to
  that class by default, so every material keeps a bin of its own."
- Lines 387-389, hand-wrap: rewrapped the 105-column "Move the operation
  onto an object." line. Wording unchanged.
- Lines 532-534, hand-wrap: rewrapped "Resolve the note through the MRO."
  Wording unchanged.
- Lines 540-545, hand-wrap: rewrapped "Give each class a default bin."
  Wording unchanged.
- Lines 546-549, hand-wrap: rewrapped "Let a subclass share its parent's
  bin." Wording unchanged.
- Lines 687-693, hand-wrap: rewrapped "Fall back to a default answer."
  and "Refuse an unregistered type." Wording unchanged.

## Considered and declined

- Line 387, "What changes is where you define the operation." A
  pseudo-cleft by shape, but it answers the exercise's "explain what
  changed" in the exercise's own words. Kept.
- Lines 390-395, the closing "Use `singledispatchmethod` once the
  operation needs to read or update an object's state" restates the
  paragraph's opening condition. Kept: it turns the condition into
  advice the reader can act on, which the global rules allow.
- Lines 383-385, "Route each piece by its type." restates the opening
  paragraph's "`singledispatchmethod` dispatches on the argument after
  `self`". Kept: the step ladder states each step on its own, and the
  opening paragraph explains a failure rather than the solution.
- Line 536, "Both behaviors are deliberate, and neither is a fallback."
  The negative half answers the reader's likely reading of the MRO walk
  as a fallback, so it is the claim (the global positive-statement
  rule's keep).
- Line 554, "`type(t)` is a convenient key, not an inevitable one." A
  closer by shape (§32), but the contrast is real and the next sentence
  delivers its consequence. Kept.
- Line 129, "exactly `{"Aluminum", "Paper", "Glass", "Cardboard"}`".
  "exactly" marks a precise set match, the use the watch list allows.
- Lines 689-690, "produces no exception and no report from the type
  checker." The negation is the claim: the forgotten registration is
  silent.
- The bold step labels (`**Register the new material.**` and the rest)
  are §15 by shape, but they are the Solutions files' step convention,
  not emphasis.
