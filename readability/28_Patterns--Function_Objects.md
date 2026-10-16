> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: 28_Patterns--Function_Objects

The chapter reads as finished technical prose: no Tier 1A or Tier 2 vocabulary, no signposting, no stacked transitions, no staccato runs, and sentence lengths that vary.
Every watch-list hit falls under a recurring keep in `readability_db.md` or a carve-out in the global rules.
Two "and" splices joining clauses with different subjects were split directly.
This file holds no live block, so it is the applied-directly record.

## Applied directly

- Line 19, global rule (split an "and" between different subjects; "while" fits): "The job stays the same, and the caller picks the algorithm that performs it." -> two sentences.
- Line 975, same rule: "one bus holds every list and the event type selects the handlers" -> "one bus holds every list. The event type selects the handlers." The split also keeps the "Instead of every subject holding its own list" frame on the clause it governs.

## Considered and declined

- Line 3-4, epigraph, "does it later or does it a different way each time": "does it" is on the watch list, but the repetition is the epigraph's rhythm. Kept.
- Line 106, "to say what one list of functions says": settled at Bruce's 2026-10-04 ruling (`readability_db.md`).
- Line 110, "A `Command` base class is worthwhile when the commands share implementation": weighs an effort against a stated condition ("worth" keep).
- Line 120 and 992, "plain functions" / "A plain function": contrasts the function with the bound method, closure, and class forms around it ("plain" keep).
- Line 214, "Python's best-known closure mistake": a standing keep in `readability_db.md`.
- Line 268, colon in "are *open*: they need somewhere to start, not a bracket": the colon delivers the definition of the italicized term (passes the "that is" test).
- Line 338, 506, 596, 614, "X, not Y" contrasts: each names a real alternative the reader might assume (a `None` to check, the failure value, a class structure, an interface), and they sit far apart. Not a §9 cluster.
- Line 472, "need only a place to start": "only a X" is a ruled-fine shape, and the restriction is the contrast with bisection's bracket.
- Line 515, "decides for itself": reflexive and load-bearing.
- Line 521, 708, 926, "The test file confirms that:": a book-wide lead-in for test bullets (chapters 11, 23, 29, 30, 34, 35, 36, and B use it). Not a §61 template tell.
- Line 711, "A handler receives only its own event type.": the bullet mirrors the test name `test_handler_receives_only_its_event_type`, and "only its own" is a ruled-fine shape.
- Line 882, "never runs it": the claim (the type checker reads the source statically).
- Line 884-885, "so a handler names its event once": repeats the motivation from line 754. Kept as the paragraph's tie back to why the tagged bus reads the annotation.
- Line 979, "exactly one": a precise count against "many handlers" in the sentence before.
- Line 1024, exercise "or do you now want an object?": "want" addressed to the reader (carve-out), and exercise imperatives are exempt.
