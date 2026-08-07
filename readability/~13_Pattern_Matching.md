[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/13_Pattern_Matching.md`

This chapter reads as human-written technical prose throughout.
No AI vocabulary clusters, no significance inflation, no signposting, no rule-of-three padding,
no curly quotes, no boldface overuse, no spaced ` -- `, and no banned strings ("reach for", `from __future__ import annotations`).
Sentence lengths vary, the examples carry specific detail (`N806`, `__match_args__`, the `SyntaxError` texts, the named languages in the `switch` comparison),
and each section advances the argument rather than restating it.
Only two small clarity edits are worth proposing, both P2.

[] Reject

**Section:** Sequence Patterns (paragraph beginning "A sequence pattern deliberately excludes `str` and `bytes`.")
**Pattern:** §23 Filler Phrases / clarity (P2)

Current:
> Matching `"abc"` against `case [a, b, c]` does not match,

Proposed:
> `case [a, b, c]` does not match `"abc"`,

Why: The sentence says "Matching ... does not match," which loops the verb back on its own gerund; putting the pattern in subject position states the same fact once. The following line ("even though a string is a sequence in every other context.") reads unchanged.

***

[] Reject

**Section:** Exhaustive Matching (opening paragraph)
**Pattern:** §23 Filler Phrases, "make verbs do the work" (P2)

Current:
> Now you can perform a match on that union.

Proposed:
> Now you can `match` on that union.

Why: "perform a match on" is a weak verb phrase for the direct verb; the chapter already uses the direct form later in "make it an `Enum` and `match` on its members."
