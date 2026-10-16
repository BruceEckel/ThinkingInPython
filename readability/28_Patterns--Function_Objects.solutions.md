> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/28_Patterns--Function_Objects/README.md`,
2026-10-16.
The prose had few AI tells. Most findings were "and" joins that hid a
contrast or a consequence, two paragraphs that restated their section's
opening paragraph, and lines that had drifted past the README's
70-column hand-wrap. Fourteen fixes went in directly, and no finding
needed Bruce's judgment, so this file holds no live block and serves as
the applied-directly record.
The claims touched were checked against the listings and the chapter:
Newton's first step from `1.0` to `1.5` under a `0.6` tolerance, the
three `@event` classes in `bank_events.py`, `tagged_bus.py`'s
`publish()` raising a `TypeError` for a type outside `EVENTS`, and
`Repeat` being a `@record` in `callable_command.py`.
`tip verify-ch CH=28 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Lines 57-58, "and" hiding a reason: "commands print a line, and a
  printed line has nothing to undo" became two sentences.
- Line 116, "and" joining two claims: "no longer enough, and the reason
  is undo, not state" became two sentences.
- Line 120, hidden contrast: "and a callable answers one" became
  "while a callable answers one".
- Lines 122-126, treadmill: the step's opening clause "Because
  `Command`, the chapter's `Callable[[], None]`, describes one call"
  repeated lines 66 and 119-120, so it went; the step now opens "A list
  of undoable commands needs a type with two members". The following
  "`Macro` annotates ..., and `Deposit` matches ..." (different
  subjects, each its own claim) became two sentences.
- Line 132, hidden contrast: "share implementation, and these commands
  share none" became two sentences.
- Lines 138-141, hand-wrap: the `Deposit`-is-a-record paragraph had
  lines near 90 columns; rewrapped, wording unchanged.
- Lines 212-218 and 309-311, hand-wrap: the section-2 trap paragraph
  and the "Give failure a reason" step had lines past 80 columns;
  rewrapped, wording unchanged.
- Lines 331-342, treadmill: the paragraph after "Name each attempt"
  restated the opening paragraph's "`Callable` ... declares no
  `__name__`" in a sentence of its own, then said `ty` rejects the
  read. The restatement went, and the `ty` sentence now points back to
  the opening paragraph; the Pyright contrast and the `Finder` sentence
  stay.
- Lines 380-387, hidden contrast: "`sorted()` provides the algorithm
  ..., and the caller supplies the interchangeable policy" became two
  sentences; the stray break in "Passing a different / `key`" was
  rewrapped.
- Lines 441-449 and 505-507, hand-wrap: the section-4 trap paragraph and
  the "Keep existing calls working" step had lines past 100 columns;
  rewrapped, wording unchanged.
- Lines 516-517, "and" joining two claims: "print the same wrong-looking
  answer, `1.500000`, and that answer shows the tolerance took effect"
  became two sentences.
- Line 527, hidden contrast: "`partial()` binds arguments, and a
  closure's body can use the setting in any expression" became two
  sentences.
- Line 686, hidden concession: "is the intended feature, and it still
  changes" became "..., but it still changes".
- Lines 812-821, "and" joining two claims: "None of the three preserves
  late lookup of `n`, and that is the point of the exercise's closing
  question" became "... of `n`. The exercise's closing question turns on
  that." The paragraph and the step-6 and step-7 openers (lines 787-789,
  918-920, 922-927, 930-936) were rewrapped; in step 7, "runs cleanly
  through the three `@event` classes ..., and that clean run hides the
  mistake" also became two sentences.

## Considered and declined

- Lines 62-67 and 116-120, treadmill: both say a `Command` describes one
  call while undo needs two requests. Kept: the first is the trap
  paragraph before the listing, which the other solutions in this file
  also open with, and the second answers the exercise's question ("is a
  function still enough?") in its own words.
- Line 327, colon: "The chapter's advice about the failure value still
  holds: `first_root()` checks the result's type, not its truthiness."
  The words after the colon state the advice as it applies here, a
  restatement, which the colon rule keeps.
- Lines 791-792 ("Nothing is wrong with the lambdas.") and line 928
  ("No name references that class, and no event is an instance of
  it."), negative statements. Kept: each negation is the claim.
- Lines 822-824, "The late-binding trap and late binding as a feature are
  the same mechanism." A closing generalization by shape (§25), but it
  states the exercise's lesson, not a send-off.
