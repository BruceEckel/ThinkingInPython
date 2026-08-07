[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/31_State_Machines.md`

This chapter reads as human throughout. The vocabulary scan turned up nothing
from the Tier 1A/1B/2 tables (the only hits, "key" and "harness," are literal
technical uses: dictionary keys and the test harness). There are no bold-label
lists, no rule-of-three padding that isn't matched by real three-element
content, no curly quotes, no spaced ` -- `, and no banned strings. The three
findings below are all low-severity: two restatement glosses (§70) and one
overstated universal quantifier in an image alt text that contradicts the
chapter's own table.

Few findings. Consider this chapter effectively clean.

***

[] Reject

**Section:** Opening, before "Each State Decides" (lines 18-20)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> Another way to put it is that here,
> each `State` object has its own little `State` table,
> and in the subsequent design there is a single master state transition table for the whole system.

Proposed:
> Cut this sentence.

Why: The sentence immediately above already draws the same distinction in the same
vocabulary ("a single table holds all of the state transitions"), so the announced
rephrase adds no new information. If the "its own little table" image is worth
keeping, the cleaner fix is to fold it into the first sentence rather than
restate the whole contrast twice.

***

[] Reject

**Section:** After the `state_machine.py` listing (line 81)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The flow is fixed either way, and only where the steps live changes.

Proposed:
> Cut this sentence.

Why: The two preceding sentences already state that the flow is fixed and that only
the location of the varying steps differs, so this is a summary gloss of what was
just said. Borderline, since it does state the invariant explicitly as a teaching
move; if you keep it, the phrase "only where the steps live changes" is a garden
path (it reads for a beat as "the steps live changes") and is worth rewording.

***

[] Reject

**Section:** A Vending Machine, image alt text (line 484)
**Pattern:** §35 related note, gratuitous universal quantifiers (P2)

Current:
> while Quit refunds from any state back to QUIESCENT

Proposed:
> while Quit refunds from any of the other states back to QUIESCENT

Why: The table in `vending_machine.py` has no `(State.QUIESCENT, Quit)` row, and
`test_no_transition_raises` says so explicitly ("QUIESCENT has no transition for
Quit"), so "any state" overstates by one and contradicts the listing a reader is
about to see. This is an accuracy point rather than a slop pattern; the
replacement uses only facts already in the chapter.
