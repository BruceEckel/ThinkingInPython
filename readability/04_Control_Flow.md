When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability pass over `Chapters/04_Control_Flow.md` in the
clean-slate sweep, run after the deep review was applied.
The chapter is clean of AI vocabulary: no Tier 1A words, no curly quotes,
no spaced ` -- `, no signposting, no rule-of-three padding,
and the sentence rhythm varies naturally.
What the pass found was watch-list residue
(two `anyway`s, two flourish `itself`s, an `at all`, a `has to`, a `happen`,
"the way out" from the don't-use tier),
two `is what` clefts that failed the deletion test,
two stranded prepositions, and one dangling modifier.
Every finding had one sensible fix, so all were applied directly
and this file has no decision blocks.
Line numbers below refer to the chapter before these edits.

## Applied directly

- L163, don't-use list ("the way out"): "This `else` is also the way out of
  two nested loops" now "is also how you leave two nested loops at once",
  echoing the "leaving two loops at once" phrasing earlier in the section.
- L247, watch list ("has to"): "so nothing in the body has to pop again or
  keep a separate copy" now "so the body needs no second pop and no
  separate copy".
- L254, stranded preposition: "the two containers you are most likely to do
  it to" now "the two containers you are most likely to mutate this way".
- L281, stranding-adjacent: "Neither behavior is something to work around"
  now "Neither behavior calls for a workaround".
- L324, watch list ("anyway"): "Avoid the name anyway, since a reader must
  work out which meaning applies" now "Avoid the name, though: a reader
  must work out which meaning applies".
- L374, "is what" cleft (deletion test passes): "which is what you do when
  the caller should hear about the bad argument" now "which you do when".
- L381, stranded preposition: "Catch the exceptions you can do something
  about" now "Catch an exception only when you can do something about it",
  which keeps the idiom and puts the object back in place.
- L461, "is what" cleft plus stranded "on": "the class name is what the
  handler matches on" now "the handler matches on the class name".
- L465, flourish "itself": "the text Python itself would print" now "the
  text Python would print"; the "not a summary of it" contrast carries the
  emphasis.
- L467, watch list ("anyway"): "Python records the earlier exception in
  `__context__` anyway" now "Python still records the earlier exception
  in `__context__`".
- L469, watch list ("at all"): "nothing appears above the new exception at
  all" now ends at "exception"; "nothing" needs no intensifier.
- L515, watch list ("happen"): "setup and cleanup happen as a pair" now
  "run as a pair", since both are code.
- L556, dangling modifier: "When reading or writing a file, `pathlib`
  provides utility methods" now opens "For reading or writing a file",
  so the modifier no longer claims `pathlib` does the reading.
- L606, exercise 7, flourish "itself": "an exception object it constructs
  itself" now "an exception object it constructs"; the italicized
  *different* plus "it constructs" carries the not-the-caught-one point.

## Considered and declined

- Three uses of "never" (L112 "`6` through `9` never print", L213 "the
  extra score never appears", L331 "one that never does stops the
  program"). L331's is essential: it defines the no-handler case. The
  other two are the clearest wording; "do not print" and "does not appear"
  say the same thing less directly.
- L385 "`except Exception:` is the broad catch you want instead": "want"
  is addressed to the reader, which the global rule's carve-out covers
  (same call as the 31_State_Machines entry in `readability_db.md`).
- L471 "when it would only distract from your own message": "only" draws
  the real contrast with "explains" in the same sentence.
- L277 "the slot the loop already passed": "already" is temporal and earns
  its place; the mechanism depends on the pass having occurred first.
- L516 "even if the body raises an exception": the concessive "even if" is
  the claim; nothing else says it.
- L508 "asks the only question that matters: does this conversion work?"
  Not a §43 rhetorical-question transition: the question is the content
  (what the `try` block asks), and "only" carries the contrast with the
  proxy question `isdigit()` asks.
- L279 "with no exception to tell you": §9 tailing negation by shape, but
  it is a full infinitive clause and the silent-failure point is the
  sentence's payload. Kept.
- L312 "Unlike C, there is no fall-through": an expletive there-is, which
  is `/activate`'s territory, not an AI tell; the sentence is clear and
  short. Left alone.
