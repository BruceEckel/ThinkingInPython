[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/28_Function_Objects.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/28_Function_Objects` (7 tests pass), and all nine
scripts run. The technical claims were probed directly. The
`subscribe(Deposit, on_withdraw)` type-error claim holds: `ty` reports
`invalid-argument-type` ("`Deposit | Withdraw` is not assignable to
`Withdraw`"), so "No such `E` exists ... and it is a type error" is
accurate. The coarse-bisection value 1.406250 was traced by hand
(six halvings of [0, 2] down to width 0.0625, midpoint 1.40625) and is
deterministic, as are all the root-finder markers. The GoF quote
"an object-oriented replacement for callbacks" is genuine (Command
chapter, Applicability discussion). The late-binding demo is correct on
the pinned 3.15: the comprehension's lambdas share one cell for `n`,
and `partial`'s argument is evaluated at build time. The chain demo's
fall-through is real: on [1.0, 1.3] both endpoints give a negative
`f`, bisection returns `None`, and secant converges from outside the
interval. Incoming cross-references were verified: chapter 17's link
for the late-binding trap and chapters 30/31/36/37/39/40's links all
name anchors that exist here and describe what the sections say, and
chapter 21's taxonomy names the same trio in the same grouping as this
chapter's opening. Solutions/28 covers all six exercises consistently;
its exercise-6 solution treats the "which one still works" question as
a deliberate trap and says so. No live blocks this run: every finding
had one defensible answer.

## Applied directly

- Chain section: "`secant()` and `newton()` stop when their step stops
  shrinking" is now "declare success when their latest step shrinks
  below the tolerance". The code succeeds when the step becomes small;
  "stops shrinking" described a plateau the code never tests, and the
  sentence's real point (a tiny step is not a root) survives intact.
- Ladder item 5: "the second operation `undo()` needs" did not parse
  (undo is the second operation, not something that needs one); now
  "a second operation such as `undo()`", matching the Command section's
  own phrasing.
- Event bus intro: "no registration ceremony" contradicted the very
  next listing, where `subscribe()` is registration; now "registering
  one is a single `subscribe()` call", which keeps the contrast (no
  interface to implement) without denying the call exists.
- Callable-object paragraph: "Give a class `__call__()` ... and its
  instances carry state" was an imperative-plus-consequence sentence;
  now "A class with `__call__()` ... produces instances that carry
  state".
- Intro: "*Command* appears twice below" is now "*Command* appears
  first as a function, then as ...". Command's section has four
  listings; "twice" was literally false, and the sentence only needed
  the function-then-class contrast.
- Event bus: "the element type erases the parameter to `Handler[Any]`"
  had the element type erasing something; now "their element type is
  `Handler[Any]`, the parameter erased".
- Event bus: "The safety check happens once" → "The check runs once"
  ("happen" watch word); "every published event type that happens to
  have no subscriber" → "every published event type with no
  subscriber".

## Considered and declined

- Exercise 6's closing question ("Which one still works if you must
  compute the value at call time...?") presupposes an answer among the
  three fixes, and the solution answers "none of them". Left as is:
  the solution explicitly names the trap as the point of the clause,
  so the pair is a deliberate gotcha, not a mismatch.
- Strategy section: "`Placeholder` fills the gap" is singular, and the
  chapter's own `RootFinder` shape would need three placeholders to
  bind a trailing positional tolerance. Left as is: the sentence
  states the general idiom and links to Foundations for the mechanics.
- Repeated italics on pattern names (*Command*, *Strategy*, ...) after
  first use. House convention throughout Part III (chapter 21 does the
  same), not a first-use-only violation to fix chapter-locally.
- The intro calls the event-bus section "a closing section" though the
  ladder ("Choosing the Lightest Callable") follows it. Read as
  "closes the pattern sequence", which is true; every rewording tried
  was worse.
