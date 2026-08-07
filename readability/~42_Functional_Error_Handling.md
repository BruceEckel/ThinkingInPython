[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/42_Functional_Error_Handling.md`

This chapter reads as human throughout.
A scan for Tier 1A/1B/2 AI vocabulary returned zero hits, there are no curly quotes, no spaced ` -- `, no banned phrases, and no signposting or promotional constructions.
The only tells worth raising are three small restatements (a fact stated twice in adjacent lines, or a clause that announces what the next sentence already does) and one awkward conjunction.
Four findings, all P2.

***

[] Reject

**Section:** Exceptions Discard Partial Calculations (first paragraph)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> If a function raises an exception partway through a comprehension,
> you lose all partial calculations.
> Any successful results computed before the failure vanish:

Proposed:
> If a function raises an exception partway through a comprehension,
> you lose all partial calculations:

Why: The heading, the first sentence, and the second sentence all state the same fact three times before the listing arrives.
The second sentence adds no information the first does not already carry.

***

[] Reject

**Section:** A Result Type (paragraph beginning "`Result[int, str]` says this function returns...")
**Pattern:** §28 Signposting and Announcements (P2)

Current:
> Python's humbler form of the same idea is `int | None`,
> and the comparison locates `Result`'s value.

Proposed:
> Python's humbler form of the same idea is `int | None`.

Why: The clause announces that a comparison is about to locate `Result`'s value, and the next two sentences then perform that comparison.
Cutting the announcement loses nothing, since "Both force the caller to unpack, but `None` says only..." carries it.

***

[] Reject

**Section:** Composing With bind (paragraph after `composing_with_bind.py`)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> An `Err` anywhere short-circuits the whole thing.

Proposed:
> Cut this sentence.

Why: The same point was already made in this section's lead-in ("An `Err` anywhere in a chain skips the rest of the steps and falls through to the end"), and it is made again a page later in Combining Multiple Results ("An `Err` anywhere short-circuits to the end"), where the nested-bind case re-earns it.
Three statements of one fact; the middle one is the cuttable one, and the paragraph ends well on "It moved into `bind()`, where it appears once."

***

[] Reject

**Section:** Attaching Context to an Exception (opening sentence)
**Pattern:** Clarity edit, no §-pattern (P2)

Current:
> An exception knows what went wrong and not where it came from.

Proposed:
> An exception knows what went wrong but not where it came from.

Why: The contrast is adversative, so "but" reads more naturally than "and" and makes the sentence land on the first try.
Borderline: "and not" is grammatical and may be a deliberate parallel, so this is a clarity preference rather than an AI tell.
