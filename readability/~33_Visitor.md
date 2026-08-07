[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/33_Visitor.md`

This chapter reads as human technical prose.
A full sweep of the Tier 1A, Tier 1B, and Tier 2 vocabulary tables (§7) returned
zero hits, and the prose is dense with checkable specifics (the `Any` annotation
and why it stays, the `_` rebinding mechanism, the `NotImplementedError`
alternative, the `match`-over-a-closed-union tradeoff), which is the opposite of
the portability tell.
The only thing worth Bruce's attention is a pair of empty intensifiers (§23),
and one of the two is genuinely borderline.

***

[] Reject

**Section:** Opening, paragraph beginning "*Visitor*, the final pattern in *GoF Design Patterns*"
**Pattern:** §23 Filler Phrases, often-empty adverbs (P2)

Current:
> The objects of the primary hierarchy simply `accept()` the `Visitor`,

Proposed:
> The objects of the primary hierarchy `accept()` the `Visitor`,

Why: "simply" reads as "and do nothing else," which the same sentence then
contradicts with "then call the `Visitor`'s dynamically bound method."
Borderline: this is old, comfortable prose and the adverb is doing faint
rhetorical work, so it is a reasonable one to decline.

***

[] Reject

**Section:** Paragraph beginning "The `accept()`/`visit()` pair is the *double dispatch*."
**Pattern:** §23 Filler Phrases, often-empty adverbs (P2)

Current:
> the flower-side dispatch simply goes back to having nothing to say.

Proposed:
> the flower-side dispatch goes back to having nothing to say.

Why: "simply" survives the deletion test with no change in meaning; the sentence
already carries the "nothing much happens" sense in "nothing to say."
This is the second "simply" in the chapter, which is what raises it above noise.
