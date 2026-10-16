> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 47_Effects--Stateless_in_Practice

The chapter has been through several passes today (straighten, metadiscourse, claims, continuity),
so the AI-writing tells left were few and small:
two signposting sentences, two "and" joins across a change of subject,
a staged "This pattern has a name." reveal, a repeated race warning inside one paragraph,
and one vague advisory kicker.
Every finding had one sensible answer, so this file holds no live block
and serves as the record of the direct edits.
`tip reflow CH=47` and `tip verify-ch CH=47 ISOLATED=1` pass (27 of 27).

## Applied directly

- 811: §52/§39 staged reveal. "This pattern has a name. Treatments of algebraic effects open with the *State effect*, ..." -> "Treatments of algebraic effects open with this pattern and name it the *State effect*, with `get` and `put` as its two operations."
- 814: §28 signposting. Cut "One warning comes with the pattern."; the paragraph now opens on "No lock protects the cell."
- 816-820: treadmill. The paragraph said the forked Effects race twice ("interleaves their reads and writes", then "under `fork()` two Effects race on the cell"). The thread analogy joins the first statement with "so", and "Stateless has no equivalent." ends the paragraph as its own sentence.
- 883: repeated subject. "`research()`'s signature is also the only place its failures appear." -> "The signature is also the only place those failures appear." (the two sentences before it already open on `research()`).
- 1307: and-split (subject changes from "You" to "the listing"). "You supply leaves and make products, and the listing keeps the two apart." -> two sentences.
- 1419: watch word "even". "`Hero` stays distinct even then, since ..." -> "`Hero` would stay distinct, since ..." (the conditional matches "You could rename" before it).
- 1519: §34 "real" with no named contrast. "That is a real loss against the *Abstract Factory*" -> "That is a loss compared with the *Abstract Factory*".
- 1527: §32 kicker. Cut "Know which of those you are getting."; the subsection now ends on the concrete "The guarantee moves from a class hierarchy into a two-line function." Close alternative: keep it as advice, but "which of those" has two candidates and adds nothing the sentence before it does not say.
- 2057: treadmill. "Watch for a failure going past `catch()`, because `catch(ZeroDivisionError)` type-checks and then does nothing. The protection appears to be there." -> "The `catch(ZeroDivisionError)` in `caller()` type-checks and then does nothing, so the protection appears to be there." (the sentence before already says the failure goes past `catch()` untouched; checked against `undeclared_failure.py`).
- 2360: and-split (contrast across a subject change). "Each is reasonable alone, and none composes with another." -> "Each is reasonable alone. None composes with another."

## Considered and declined

- 183: "Answering differently at each request makes an unpredictable source testable." repeats the end of the sentence before it. Kept: the repetition is old-information-first chaining into the claim the section exists to show.
- "real clock" (268, 272, 375, 376, 384, 424): §34 by shape, but each names its contrast, the handled clock.
- 1014: "Here a scenario is nothing more than arguments to `supply()`." The diminishing is the point (the global rule's carve-out).
- 1097: "At this size the by-hand version is respectable, and a reader may prefer it." Author voice, a deliberate concession.
- 1354: "Here is what ZIO does that Stateless cannot." The global rule's own example of a needed "is what".
- 1409: "It prints nothing itself." The "itself" contrasts `encounter()` with the supplied `Narrator` that does the printing.
- 1685: "the thesis of both chapters applied to a cross-cutting concern." §39 by shape, but it names the specific claim and the next sentences demonstrate it.
- 1876: repeats 614's resource-scope limit. Kept: 614 says this section revisits it.
- 2030 and 2059: "The guarantee is about consistency, not completeness." and "The channel carries only what you put into it." Aphorism shapes, but each states the limit precisely and is the sentence a reader returns for.
- 2269: "No type reports the race." repeats 818. Kept: the limits section restates each limit by design.
- 2403: "The missing piece is a language that does the encoding for you." A closing line, but a concrete claim rather than a future-narrative flourish.
- 18-29: the chapter-opening bullet list. Real list content: each item is a section the chapter delivers.
- "worth researching" (825) and "worth another attempt" or "worth retrying" (1654, 1659, 2263): domain vocabulary and a real weighing, not the §53 endorsement frame.
