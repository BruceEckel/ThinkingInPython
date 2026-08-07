[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/41_Functional_Toolkits.md`

This chapter reads mostly human. The reference sections (`functools`, `itertools`) are
terse, specific, and clean; the Case Study prose is genuinely good writing with
hard-to-fabricate detail. The few findings are low-grade: a repeated boilerplate
sentence across the two toolkit intros, two "Note that" metadiscourse openers, and
three places where a sentence restates what the line before it already said.
No Tier 1A vocabulary, no rule-of-three padding, no bullet slop, no ` -- `,
no banned phrases.

***

[] Reject

**Section:** `cache`
**Pattern:** §70 Interpretive Metadiscourse / §23 Filler Phrases (P2)

Current:
> Note that this only works correctly for pure functions.

Proposed:
> This only works correctly for pure functions.

Why: "Note that" tells the reader to notice instead of stating the fact; the sentence loses nothing without it. This is the first of two "Note that" openers in the chapter (the other is in `cached_property`), which is what makes it worth flagging rather than a one-off.

***

[] Reject

**Section:** `cache`
**Pattern:** Treadmill effect / low information density (P2)

Current:
> This accelerates future calls to `fib()`.

Proposed:
> Cut this sentence.

Why: The section's own opening line already says it ("so repeated calls with the same arguments cost nothing"), and the sentence before this one carries the new fact (every value up to 30 got cached, not just 30). Deletion test: nothing is lost.

***

[] Reject

**Section:** `cached_property`
**Pattern:** §70 Interpretive Metadiscourse / §23 Filler Phrases (P2)

Current:
> Note that you must be careful with caching,
> because mutating a property doesn't cause the cached result to be recalculated.

Proposed:
> Be careful with caching:
> mutating a property doesn't cause the cached result to be recalculated.

Why: Same "Note that" frame as the `cache` section, plus "you must be careful" is a weak verb phrase for a direct instruction. The colon keeps your own wording and line break intact.

***

[] Reject

**Section:** The `itertools` Toolkit (intro paragraph)
**Pattern:** §61 Template and Slot-Fill Phrases (P1)

Current:
> What follows starts with the simplest tools and works up to the ones with the most moving parts.

Proposed:
> Cut this sentence.

Why: This exact sentence, character for character, already closes the `functools` intro paragraph five sections earlier; a verbatim repeat reads as a section template rather than a written transition. Cutting the second occurrence leaves the itertools intro ending on its own concrete line about composing the tools. (If you prefer the reminder here, the alternative is to cut the `functools` one instead, but only one should survive.)

***

[] Reject

**Section:** Recursion
**Pattern:** Treadmill effect / low information density (P2)

Current:
> Recursion is beneficial when the data is recursive.

Proposed:
> Cut this sentence.

Why: It restates its own subject ("recursion suits recursive data") and the next sentence says the same thing concretely, naming trees, nested data, and directories. It is also the third time in three consecutive paragraphs that the chapter makes this claim, after "Its payoff shows up once the problem branches" and "Recursion suits problems that are naturally self-similar, such as walking a tree." Cutting it also thins the "walking a tree" / "walks a tree" echo between those two paragraphs.

***

[] Reject

**Section:** Lazy Evaluation
**Pattern:** §31 Manufactured Punchlines and Staccato Drama (P2)

Current:
> Nothing here is a batch.

Proposed:
> Cut this sentence.

Why: The clipped fragment stages a point that the very next sentence then states plainly ("`squares()` never runs ahead to precompute several values before handing one back"), inside a paragraph that already makes the same observation four ways. Cutting it leaves the concrete sentence to do the work.

***

[] Reject

**Section:** Case Study: Pairing Rotations
**Pattern:** §34 Real/Actual Adjective Inflation (P1)

Current:
> This is a good place to see these chapters' ideas working together on one small,
> real program instead of one at a time.

Proposed:
> This is a good place to see these chapters' ideas working together on one small program instead of one at a time.

Why: The contrast the sentence actually names is "together instead of one at a time," not real-versus-fake, so "real" is a bare intensifier doing no work. Borderline: if the intent is to contrast this with the one-liner demos above, the honest version would name that contrast explicitly, and I have not proposed one since the chapter does not state it.
