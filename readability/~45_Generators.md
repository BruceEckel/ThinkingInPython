[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/45_Generators.md`

This chapter does not read as AI-written.
No Tier-1A vocabulary, no promotional language, no rule-of-three padding, no generic closer; sentence and paragraph lengths vary, and the technical claims are specific throughout.
The only recurring soft spot is interpretive metadiscourse (§70/§39): a handful of sentences that tell the reader what to notice or which item is interesting, where the content that follows already does that work.
Four findings, all P2.

[] Reject

**Section:** Annotating a Generator (final paragraph, the `NewType` transposition discussion)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> Each channel has its own type, so the checker catches every transposition.

Proposed:
> Cut this sentence.

Why: It restates the paragraph's own opening sentence ("The `NewType` definitions prevent accidental transposition.") after the three "All three ..." sentences have already demonstrated it, so the paragraph ends stronger on the contrast that follows it (`Generator[str, str, str]` accepts the reversal without complaint).
Borderline: it also works as a bridge into that last line, so if the abruptness bothers you, reject.

***

[] Reject

**Section:** A Generator Is a Description (paragraph after `two_way_generator.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> Notice that `interview()` does not know where the answers originate.

Proposed:
> `interview()` does not know where the answers originate.

Why: "Notice that" directs attention instead of stating the fact, and the sentence loses nothing when the frame is deleted.
The chapter has three of these attention-directing openers ("Notice that" here, "Note that" before `yield_from_return.py`, "Notice that" in exercise 7); the exercise one is doing real instructional work and should stay.

***

[] Reject

**Section:** The Return Channel (lead-in to `yield_from_return.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> Note that `report()` returns nothing and only yields:

Proposed:
> `report()` returns nothing and only yields:

Why: Same deletion test as the previous finding: the frame carries no information, and the sentence reads more directly without it.

***

[] Reject

**Section:** The Send Channel (paragraph after the "The numbers travel down..." paragraph)
**Pattern:** §39 Self-Labeling Significance (P2)

Current:
> `g.send(2)` is the interesting one.
> It supplies alpha's second value, which lets `collect("alpha")` finish,
> which completes the first `yield from`, which starts the second one.

Proposed:
> `g.send(2)` supplies alpha's second value, which lets `collect("alpha")` finish,
> which completes the first `yield from`, which starts the second one.

Why: The label announces that a call is interesting, and the very next sentence proves it; deleting the label lets the chain of consequences make the point, and the following sentence ("A single `send()` therefore ends one inner generator...") still supplies the emphasis.
Worth noting the density behind this one: "interesting" also appears in "The `# type: ignore` is interesting." and "A generator is more interesting than a coroutine here...". Those two both earn it (the second names a reason outright), so only this one is proposed for change.
