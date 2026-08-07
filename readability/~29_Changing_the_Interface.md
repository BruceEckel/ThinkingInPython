[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/29_Changing_the_Interface.md`

This chapter reads as human throughout.
No Tier-1A vocabulary, no promotional language, no rule-of-three padding, no signposting hooks, no curly quotes, no boldface stacking, no spaced ` -- `, and no invented specifics: every claim is tied to a listing or a named mechanism.
The only thing worth touching is a syntactic loop in the final section, where the same trailing appositive frame (`, which is the X`) fires five times in about twenty lines, plus one wordy tail on the closing sentence.

***

[] Reject

**Section:** Retiring the Old Interface (paragraph after `deprecating.py`)
**Pattern:** Structure and rhythm test, sentence-construction uniformity / §11 adjacent (P2)

Current:
> The `# type: ignore` is there because `ty` reports the deprecated call as a diagnostic,
> which is the half that reaches a caller before they run anything.

Proposed:
> The `# type: ignore` is there because `ty` reports the deprecated call as a diagnostic,
> the half that reaches a caller before they run anything.

Why: In this section the frame `, which is the ...` appears five times in quick succession ("which is the point:", "which is the half", "which is the trap:", "which is the finer instrument:", "which is why they are safe moves"), and the metronomic repeat is audible read aloud.
Dropping "which is" here costs nothing and leaves the two load-bearing uses ("the point," "the trap") intact.

***

[] Reject

**Section:** Retiring the Old Interface (`@overload` paragraph)
**Pattern:** Structure and rhythm test, sentence-construction uniformity (P2)

Current:
> `@overload` accepts it too, which is the finer instrument:

Proposed:
> `@overload` accepts it too, the finer instrument:

Why: Fourth instance of the same appositive frame in the section, and the shortest one to unwind.
Same fix as the block above; the colon and the sentence that follows are unchanged.

***

[] Reject

**Section:** Retiring the Old Interface (last sentence of the chapter body)
**Pattern:** §23 Filler Phrases (P2)

Current:
> and marking the old interface is how you make the risk visible on a schedule instead of discovering it at the moment you delete something.

Proposed:
> and marking the old interface is how you make the risk visible on a schedule instead of discovering it when you delete something.

Why: "at the moment you" is the "at this point in time" pattern; "when" says the same thing in three fewer words.
Borderline: if the precise-instant emphasis is deliberate here, reject this one.
