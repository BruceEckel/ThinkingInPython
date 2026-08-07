[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/36_Memento.md`

This chapter reads as human throughout.
A full vocabulary scan turns up no Tier 1A or Tier 2 AI words, no boldface or bullet padding,
no signposting, no generic conclusion, no curly quotes, and no spaced ` -- `.
Sentence length varies well and every paragraph carries new information.
The five findings below are small clarity and precision edits, all P2;
there is nothing here at P0 or P1.

***

[] Reject

**Section:** The Classic Memento (paragraph beginning "The caretaker's side of the contract is restraint.")
**Pattern:** Clarity, number agreement (no §) (P2)

Current:
> In Python it is a convention,
> though freezing the memento means the honest mistakes (mutating the snapshot)
> fail loudly.

Proposed:
> In Python it is a convention,
> though freezing the memento means an honest mistake (mutating the snapshot)
> fails loudly.

Why: The plural "the honest mistakes" is glossed by a singular parenthetical, and the definite article points back at nothing.
The singular fixes both without changing the claim.

***

[] Reject

**Section:** The Classic Memento (paragraph beginning "A `type Memento = tuple[str, ...]` alias")
**Pattern:** Clarity, mood (no §) (P2)

Current:
> A `type Memento = tuple[str, ...]` alias type-checks at every call site instead of the class.

Proposed:
> A `type Memento = tuple[str, ...]` alias would type-check at every call site instead of the class.

Why: The present tense states this as a fact about the code just shown, which uses a class, not an alias.
The rest of the paragraph argues against the alias, so the sentence is describing a road not taken.

***

[] Reject

**Section:** Immutability (paragraph beginning "`draw()` returns a new `Sketch`")
**Pattern:** Clarity, subordination (no §) (P2)

Current:
> This is the argument made by [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution),
> as [Flyweight](35_Flyweight.md) shares immutable values across space,
> and Memento shares them across time.

Proposed:
> This is the argument made by [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution).
> [Flyweight](35_Flyweight.md) shares immutable values across space,
> and Memento shares them across time.

Why: The "as" makes the Flyweight/Memento contrast read as a reason for the Rethinking Objects attribution, which it is not.
Splitting into two sentences keeps the space/time parallel intact and leaves both links untouched.

***

[] Reject

**Section:** The Caretaker: a Generic History (paragraph beginning "`do()` pushes the present into the past")
**Pattern:** §35 Moral-Adjective Category Errors, related note on gratuitous universal quantifiers (P2)

Current:
> The states you undid are no longer reachable by redo,
> which is how every editor behaves.

Proposed:
> The states you undid are no longer reachable by redo,
> which is how editors behave.

Why: "every editor" is a universal the chapter cannot support, and editors with branching undo are a real counterexample.
Dropping the quantifier also softens the echo with "which is how an editor knows to gray out the menu item" five lines later, which is the other reason to touch this line.

***

[] Reject

**Section:** Mementos That Outlive the Process (paragraph beginning "Drift in the other direction is quieter still.")
**Pattern:** §23 Filler Phrases, often-empty adverbs (P2)

Current:
> while the renamed field is simply missing.

Proposed:
> while the renamed field is missing.

Why: "missing" already carries everything "simply" was adding, and this is the second "simply" in thirteen lines
(the first is "`title` is simply absent, since the old bytes never had one."), so the pair reads as a verbal tic rather than emphasis.
Cutting the second one is the smaller edit; cut both if you would rather.
