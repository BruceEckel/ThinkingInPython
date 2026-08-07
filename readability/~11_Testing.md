[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/11_Testing.md`

This chapter reads as human prose throughout.
The Tier 1A/1B/2 vocabulary tables are essentially empty here (one "valuable," one "That said," one "Perhaps more importantly," all defensible in context), there are no promotional adjectives, no rule-of-three padding, no signposting, no boldface or bullet slop, no curly quotes, and no spaced ` -- `.
The only pattern that recurs is the treadmill effect: a claim stated, then restated in fresh words on the next line without advancing.
All four findings below are that same pattern, and all are P2.

[] Reject

**Section:** Test-Driven Development (TDD), the "That said" paragraph
**Pattern:** Treadmill effect / low information density (Structure and Rhythm Tests) (P2)

Current:
> You need that certainty to write tests first.

Proposed:
> Cut this sentence.

Why: The two lines above it already say it ("TDD requires that you know what you are creating" and "It assumes you are confident the design is correct, so that only implementation remains"); this is the third pass over the same claim, and "Often, however, you are not sure..." follows on cleanly without it.

***

[] Reject

**Section:** Test-Driven Development (TDD), same paragraph
**Pattern:** Treadmill effect / low information density (Structure and Rhythm Tests) (P2)

Current:
> Writing tests for exploratory programming is not practical.

Proposed:
> Cut this sentence.

Why: "TDD is wasteful" on the line immediately before is the same claim, and the sharper of the two; this one restates it with a weaker verb, so the paragraph loses nothing and ends on "wasteful" before the AI sentence.

***

[] Reject

**Section:** Fixtures Replace Setup and Teardown
**Pattern:** Treadmill effect / interpretive restatement (§70) (P2)

Current:
> A test that names `funded` as an argument receives the value the fixture returns.

Proposed:
> Cut this sentence.

Why: Three lines earlier the general rule is already stated ("You declare fixtures as parameters to a test, which tells `pytest` to call the fixture and pass its result to the test"), so this only swaps the wording; borderline, since restating the general rule against the concrete `funded` case is a legitimate teaching move, and the block above it already names `funded` as the fixture.

***

[] Reject

**Section:** White-Box and Black-Box Tests, the name-mangling paragraph
**Pattern:** Treadmill effect / low information density (Structure and Rhythm Tests) (P2)

Current:
> Anyone who knows the class name can still reach the attribute,
> because the rewrite changes only the name.

Proposed:
> Cut these two lines.

Why: This is the third statement of one fact in five lines, after "The rewritten name is a real attribute like any other, so `v._Vault__pin` reads it successfully" and "not to hide the attribute," and the listing above has already shown a reader reaching the attribute by class name; cutting it puts "not to hide the attribute" directly against the discipline-not-enforcement sentence that closes the paragraph.
