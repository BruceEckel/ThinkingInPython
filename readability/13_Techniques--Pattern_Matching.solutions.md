> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/13_Techniques--Pattern_Matching/README.md`,
2026-10-16.
The prose had few AI tells; most findings were clause joins that hid a
consequence or a contrast behind "and". Nine fixes went in directly,
and no finding needed Bruce's judgment, so this file holds no live block
and serves as the applied-directly record.
The claims touched were checked against the listings: six cases covering
nine sign pairs in `exercise_5_signs.py`, and `act()`'s printed
`fallback, FALLBACK is now Signal.STOP`.
`tip verify-ch CH=13 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 37, "and" hiding a consequence (global rule): "matches any value,
  and Python rejects the `case _`" became "..., so Python rejects".
- Lines 82-84, "and" joining different subjects: "So `[_, *_]` also fits
  a singleton, and `[_]` must come before it. Otherwise ... first and
  the 'singleton' case is unreachable." became two sentences: "So
  `[_, *_]` also fits a singleton. `[_]` must come before it, or
  `[_, *_]` matches the one-element list first, leaving the 'singleton'
  case unreachable."
- Lines 87-90, misplaced reason: "checks its type alone, since
  `classify()` returns the same string" read as if the return value
  caused the mechanism. Now "checks its type alone. That suits
  `classify()`, which returns the same string whatever `x` and `y` hold."
- Lines 150-152, treadmill: "the type checker proves that ... reaches
  `case _`. The checker therefore infers that `shape` can be a
  `Rectangle`" said the same step twice. Now one sentence: "finds that
  ... reaches `case _`, so `shape` can be a `Rectangle` at the
  `assert_never()` call."
- Lines 153-155, "and" joining different subjects: "meaning 'this code
  is unreachable,' and `Rectangle` differs from `Never`, so ..." split
  into two sentences.
- Line 223, hidden contrast: "return the same string, and each one
  matches a different shape" became "..., but each one matches".
- Lines 439-440, hand-wrap: rejoined the stray break in "The solution
  keeps / an unreachable `case _`". Wording unchanged.
- Lines 513-514, "and" hiding a consequence: "the cases are literals in a
  two-column table, and a missing combination is visible at a glance"
  became two sentences.
- Line 623, precision: "`act()` returns 'fallback' for `Signal.STOP`"
  became "`act()` takes the fallback case for `Signal.STOP`", since the
  listing's `act()` returns `fallback, FALLBACK is now Signal.STOP`, not
  the bare string "fallback" that `dotted()` and `guarded()` return.
- Lines 631-632, repeated subject: "Python accepts `case FALLBACK:`
  because it is the last case. Python rejects another case after it with
  a `SyntaxError`." became one sentence with one subject, "..., and
  rejects any case after it with a `SyntaxError`."

## Considered and declined

- Lines 373-375, treadmill: "One new channel produces two diagnostics
  because ... every function that matches on the union" repeats the
  "one per function that matches on the union" at lines 347-348. Kept:
  it gives the reason and ties the result back to the chapter's point
  about the match version's cost of adding a type, which is the lesson
  of the exercise.
- Line 157, §70 metadiscourse: "The `type-assertion-failure` is the check
  the chapter describes." It links the diagnostic to the chapter's claim
  rather than telling the reader how to read the output, so it stays.
- Line 361, "The output above shows the first diagnostic": locates the
  quoted output for the next sentence, which names the second one.
- Lines 76, 367, watch word `only`: "`[]` matches only an empty
  sequence" and "type-checks only when the cases above it have
  eliminated every member" state real restrictions (ruled-fine shapes).
- Lines 626-627, negative "compares nothing": the negation is the claim
  of the exercise (a capture pattern performs no comparison).
- Lines 647-648, §10 rule of three: "an `is` test like this one, a membership
  test, or a call" is a real inventory of what a guard can hold, which
  the next sentence uses.
- The bold step labels ("**Tell lists apart by length.**" and the rest),
  §15: a Solutions convention used across the README files.
- Mixed wrapping (some paragraphs one sentence per line, some wrapped
  near 70 columns): rewrapping paragraphs whose wording did not change
  would add churn, so only edited lines were rewrapped.
