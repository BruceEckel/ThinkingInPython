[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/21_The_Pattern_Concept.md`

This chapter reads overwhelmingly human. A vocabulary sweep for the §7 tiers turns up exactly one Tier 1A word in the whole file, and the long original passages (vector of change, Pattern Taxonomy, Design Principles) are clean. What tells there are cluster in the short connective paragraphs that link the older material to this book's subtraction theme: a few sentences that restate their own paragraph one more time before moving on. Four findings, one P1 and three P2.

***

[] Reject

**Section:** What Is a Pattern? (the "That completeness has a failure mode" paragraph)
**Pattern:** §32 Aphorism Formulas / treadmill restatement (P2)

Current:
> A pattern without its problem is just overhead.

Proposed:
> Cut this sentence.

Why: The two sentences immediately before it already make this point twice ("A pattern earns its place only when the problem it solves is present" and "If nothing varies, you do not need machinery for isolating variation"), so the third pass adds a coinage rather than a claim, and lands as a paragraph-closing aphorism.

***

[] Reject

**Section:** What Is a Pattern? ("Although they're called 'design patterns'")
**Pattern:** §7 Overused AI Vocabulary, Tier 1A "realm" (P1)

Current:
> they aren't tied to the realm of design.

Proposed:
> they aren't tied to design.

Why: "realm" is on the replace-on-sight list, and the phrase "the realm of" is doing no work here; the sentences that follow already establish that "design" means the design phase.

***

[] Reject

**Section:** What Is a Pattern? ("A vector of change is discovered, not predicted")
**Pattern:** §31 Manufactured Punchlines / treadmill restatement (P2)

Current:
> Let real changes reveal it.

Proposed:
> Cut this sentence.

Why: A five-word imperative wedged between the sentence that says guessing up front doesn't work and the sentence that says the second real change is your evidence; it restates both without adding anything, and its "real" is a bare intensifier (§34).

***

[] Reject

**Section:** What Is a Pattern? ("The goal of design patterns is to isolate changes in your code")
**Pattern:** §39 Self-Labeling Significance (P2)

Current:
> (albeit one built into the language, which is a case worth returning to).

Proposed:
> (albeit one built into the language).

Why: Borderline. The clause labels the point as important instead of pointing anywhere, and When a Pattern Dissolves takes it up two sections later without needing the flag. The sharper alternative would be a same-file link to that heading, but I am not proposing one, since adding a link target is out of scope for this pass.
