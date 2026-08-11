When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/15_Context_Managers.md`, after the
deep-review sweep already cleared several watch-list hits ("happen",
"spelling", "the way out", the "without exception" pun). The remaining prose
is clean: varied sentence lengths, short punches where the chapter needs them
("Lending is the dangerous half."), no Tier 1A vocabulary, no curly quotes,
no spaced ` -- `, no boldface or list inflation. Three watch-list residues
were settled directly; nothing needed a decision from you, so there are no
live blocks.

## Applied directly

- Line 228, watch-list "happen": "The return value decides what happens to
  that exception" is now "decides that exception's fate". Close alternative
  considered: "decides what the `with` statement does with that exception",
  rejected for the double "with".
- Line 819, watch-list "buy" plus an "is what" cleft: "That is what the
  protocol buys:" is now "That is the protocol's payoff:", which also
  bookends the intro's "The payoff is a borrower's contract two lines long."
- Line 837, watch-list "happen": "every change you make later happens inside
  the manager" is now "goes inside the manager", matching "a change inside
  `lease()`" two sections up.

## Considered and declined

- "How does `with` know what to run?" opening The Protocol (§43 rhetorical
  question). Earned: the previous section makes `@contextmanager` look like
  magic, and the question names the gap the section fills.
- "The yielded value is what `as` binds" (line 54). The global "is what"
  rule's own keep-example; the clause cannot attach without it.
- "because `__enter__()` just runs again" (line 155). "Just" carries the
  point: reuse needs no extra machinery, only a re-run.
- "unless you really want a block that nothing escapes" (line 374). "Want"
  is reader-addressed, which the rule's carve-out covers (same call as the
  31_State_Machines entry in readability_db.md); "really" carries the
  warning's emphasis.
- "it comes back even when the block raises an exception" (line 782).
  "Even" marks the hard case the test exists for.
- "It only tracks custody." (line 763). "Only" draws the real contrast with
  creating and destroying, named in the previous sentence.
- "it unwinds whatever it already entered" (line 212) and "already inherits
  from `ContextDecorator`" (line 424). Both "already"s are temporal or
  draw the with-no-work-from-you contrast; neither is filler.
- "`Queue` is thread-safe" and "the manager object ... is single-use"
  (§26 predicate-position hyphens). Both are programming terms of art,
  hyphenated in standard usage regardless of position.
- "which is how real database connection pools behave" (line 769, §34
  "real"). The contrast with the chapter's demo pool is named by context.
