# Deep review: 05_Functions

> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

This chapter is in strong shape: every marker verified against the pinned
3.15.0b3 interpreter, all quoted error messages checked verbatim, every
outbound anchor resolves, and the lookalike pairs a functions chapter needs
(collect vs. unpack, mutate vs. rebind, `is None` vs. truthiness, `/` vs.
`*`) are all taught explicitly. The findings were small enough to decide,
so everything landed in the applied-directly list and nothing below needs
a verdict. The `sentinel()`-builds-a-new-object-per-call claim is a
standing exemption in `deep_review_db.md` and was left untouched.

## Applied directly

- Intro, after the `minmax` fragment: added "The commas build the tuple;
  the function still returns one object." Heads off the "functions can
  return multiple values" misconception the fragment otherwise invites.
- Default and Keyword Arguments, after `default_args.py`: new short
  paragraph stating that passing by name needs no default (`host` has
  none) and giving the call-site ordering rule with its `SyntaxError`
  message (`positional argument follows keyword argument`, verified on
  3.15.0b3). It mirrors the def-site rule paragraph that follows, so the
  two ordering rules now sit side by side.
- Names Inside a Function: added "Python decides which names are local
  when it compiles the function body, so where the assignment sits makes
  no difference." The section stated the whole-function rule but not the
  mechanism behind it.
- Positional-Only and Keyword-Only Parameters: moved the "A signature can
  use every form at once, in one fixed order..." sentence from the
  section's opening definition block down to directly above
  `all_markers.py`, which previously appeared with no introduction. The
  opening block was nine definition lines before any code; the sentence
  now sits beside the listing that demonstrates it.
- Lambdas: `sorted()` now "accepts a `key` function, calls it on each
  element, and orders by the results" (the reader previously met `key`
  cold); "pass it by name" became "pass the function itself" (the old
  phrasing collided with the by-name keyword-argument sense used earlier
  in the chapter).
- Lambdas, after the listing: added why `def` beats a named lambda
  (assigning a lambda gives up its anonymity; `def` gives a real name
  for tracebacks), cashing in the listing's `# Usually prefer def`
  comment, which the prose never explained. Also tightened "Compared to
  other languages" to "Unlike anonymous functions in many other
  languages, a lambda body is limited to a single expression."
- New exercise 8 plus its solution in `Solutions/05_Functions.md`: delete
  `global` from `writes_global()` and predict; then add a leading
  `print(count)` to `rebinds()` and explain why it raises
  `UnboundLocalError` despite the assignment coming later. "Names Inside
  a Function" was the only section with no exercise coverage, and the
  read-before-a-later-assignment case is the classic proof of the
  whole-function rule. Solution passes `check_solutions`, ty, ruff, and
  the output gate (the deliberately broken lines carry `# type: ignore`
  and `# noqa`, explained in the solution's prose).

## Considered and declined

- **Splitting "Default and Keyword Arguments".** The section carries three
  lessons (defaults/keywords, argument binding and mutation, sentinels),
  but the mutation material sits exactly where the reader asks "why did
  the default keep the 1?", and five other chapters link to the
  `#default-and-keyword-arguments` anchor for content spread across the
  whole section. Splitting buys a shorter section at the cost of the flow
  and the anchors. Left as is.
- **`unpacking.py`'s `trace()` teaches forwarding and first-class
  functions at once.** Technically two new things in one listing, but the
  prose flags the second explicitly and links it forward to
  Functional Foundations and Decorators; splitting would orphan a
  two-line demo. Left as is.
- **`sentinel_default.py` returns `MISSING` instead of raising.** Real
  code would re-raise, and a reader adapting the listing could leak the
  sentinel. The deviation is deliberate (it shows the sentinel's
  self-describing repr, which is the PEP 661 selling point), the inline
  comment says "Normally re-raises here", the prose repeats it, and
  the exercise-2 solution shows the raising form. Left as is.
- **No conclusion section.** Chapters 02-07 all end on Exercises; the
  absence is the book's convention for Part I, not a gap.
