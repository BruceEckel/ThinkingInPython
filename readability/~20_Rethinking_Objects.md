[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/20_Rethinking_Objects.md`

This chapter reads as human throughout.
A full scan turned up no Tier 1A vocabulary, no boldface padding, no signposting or "let's" openers, no rhetorical-question transitions, no curly quotes, no spaced ` -- `, and no banned strings.
The one recurring habit worth flagging is a closing sentence that restates the paragraph it ends instead of adding to it; all three findings below are that same pattern.

***

[] Reject

**Section:** Encapsulation Leaks (last line of the paragraph following `leaky.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> Mutating the returned list manipulates the internal state.

Proposed:
> Cut this sentence.

Why: The two preceding sentences already say this ("Python's `return` hands out references, never copies" and "it could not stop the caller from mutating the list it returned"), so the line adds no fact and only glosses what the listing already showed.

***

[] Reject

**Section:** Polymorphism Without Inheritance / Protocols (paragraph after `test_newtype_boundary.py`)
**Pattern:** §31 Manufactured Punchlines and Staccato Drama (P1)

Current:
> Nothing in that test can fail.
> The `NewType` protection lives in the checker alone.
> A caller who passes a raw `int` where `UserId` is expected raises no exception.
> The value doesn't change.
> There is nothing at runtime for a test to catch.
> Only the checker sees it, and only at edit time.

Proposed:
> Nothing in that test can fail.
> The `NewType` protection lives in the checker alone.
> A caller who passes a raw `int` where `UserId` is expected raises no exception.
> Only the checker sees it, and only at edit time.

Why: Six consecutive short sentences state one fact five times over; "The value doesn't change" repeats the already-stated "at runtime it is the identity function, so `UserId(42)` is `42`," and "There is nothing at runtime for a test to catch" repeats the first and third lines. This is the one passage in the chapter whose rhythm reads engineered rather than written.

***

[] Reject

**Section:** Polymorphism Without Inheritance / Protocols (last line of the paragraph beginning "A protocol also sharpens what the Liskov Substitution Principle")
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The machine checks the signatures; you still own the behavior.

Proposed:
> Cut this sentence.

Why: The same paragraph already says "the checker verifies that half of the contract" and "No checker sees that half," so this is the third statement of one claim in nine lines, and the paragraph ends cleanly on "whether membership came from inheriting a base class or matching a protocol." Borderline in that it is clearly a deliberate closing beat; reject if you want the beat.
