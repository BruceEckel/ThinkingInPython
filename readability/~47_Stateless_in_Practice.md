[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/47_Stateless_in_Practice.md`

This chapter does not read as AI-written. It has none of the usual markers: no Tier 1A vocabulary, no curly quotes, no boldface stacking, no filler adverbs (`simply`, `actually`, `essentially`, `just` appear zero times in the prose), no hedge stacking, no generic conclusions, and every abstract claim is anchored to a named listing. Sentence and paragraph lengths vary throughout, and the numeric summary fragments ("Four implementations, one Ability, one running program.") are a consistent authorial device rather than manufactured staccato.

The one recurring habit worth Bruce's attention is a mild interpretive-metadiscourse tic: eight prose uses of the "worth X-ing / deserves a moment / the ones to study / the part worth memorizing" frame, each telling the reader how much weight to give what follows instead of letting the content do it. Two of the eight are pure padding and are flagged below; the rest have a reason attached and are fine. There is also a small cluster of heading-restating openers in the `retry()` subsections. Findings are few and all P2 except one tangled sentence.

***

[] Reject

**Section:** Abilities Are Not Special (line 108)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> That annotation reads `Depend[Ask, str]`, not `Depend[Need[Ask], str]`,
> and the difference deserves a moment.

Proposed:
> That annotation reads `Depend[Ask, str]`, not `Depend[Need[Ask], str]`.

Why: The second clause tells the reader to pay attention instead of paying off; the next five lines already explain the difference in full. Cutting it loses no information.

***

[] Reject

**Section:** Composing a Program (line 917)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> `report()` is where the two channels come apart,
> and its annotation is worth reading twice.

Proposed:
> `report()` is where the two channels come apart.

Why: Same frame as the finding above, and the four lines that follow do the actual reading of the annotation. Telling the reader to read something twice is weaker than the explanation already sitting under it.

***

[] Reject

**Section:** Supplying a Whole Cast (line 1335)
**Pattern:** Tangled sentence / clarity (P1)

Current:
> Every pair of abilities with a wide cast raises the odds of a collision.

Proposed:
> A wide cast raises the odds of a collision,
> since every pair of abilities is a chance for one.

Why: As written, the modifier attaches to the wrong noun (a pair of abilities does not have a cast), so the sentence has to be reparsed to get the point. If the intended sense was different from "more abilities means more pairs means more collision risk," reject this one rather than let me guess.

***

[] Reject

**Section:** Supplying a Whole Cast (line 1442)
**Pattern:** §39 Self-Labeling Significance (P2)

Current:
> The last two are the ones to study.

Proposed:
> Cut this sentence.

Why: The next two paragraphs open with "The third mixes the casts" and "The fourth run swaps one cast member," so the label is announcing what the content immediately does anyway. Borderline: it does steer a learner past the first two runs, so this is a judgment call rather than a defect.

***

[] Reject

**Section:** Why `retry()` Decorates the Function (line 1571)
**Pattern:** §29 Fragmented Headers / §42 Confidence Calibration (P2)

Current:
> Notice that `retry()` decorates the function, not the Effect.

Proposed:
> `retry()` decorates the function, not the Effect.

Why: The sentence restates its own heading, and "Notice that" front-loads a cue the contrast already carries. Dropping the two words keeps the "not the Effect" half, which the heading does not say.

***

[] Reject

**Section:** What Retry Costs the Signature (line 1604)
**Pattern:** §28 Signposting and Announcements (P2)

Current:
> Now read what the decoration did to the type.

Proposed:
> Cut this sentence.

Why: It announces what the heading already announced, and the paragraph works starting from "`save_user()` was `(str) -> Effect[Need[Database], Crashed, str]`." Borderline, and it pairs with the previous finding: both `retry()` subsections open by restating their headings, which is the reason to flag either.

***

[] Reject

**Section:** The Toolkit (line 1779)
**Pattern:** §39 Self-Labeling Significance (P2)

Current:
> The type column is the part worth memorizing.

Proposed:
> Cut this sentence.

Why: The heading of the column is already "What it does to the type," and the two tables plus the caveat paragraph are entirely about types, so the label adds emphasis rather than direction. Borderline: this is the clearest study instruction of the eight "worth" uses, so it is the most defensible one to keep.
