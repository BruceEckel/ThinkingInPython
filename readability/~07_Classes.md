[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/07_Classes.md`

This chapter reads as human-written throughout.
A vocabulary scan for the §7 Tier 1A/2/3 tables returned zero hits (the only matches for "underscore" are the literal characters), there are no curly quotes, no spaced ` -- `, no banned phrases, and no promotional or significance inflation anywhere.
What remains are five small redundancy-and-metadiscourse items, all P2: two "you can see that" framings pointing at a demo, one sentence that states the static-checking fact for the fourth time, one weak-verb phrase, and one closing sentence that repeats advice already given twice.

***

[] Reject

**Section:** Opening (untitled, before "## Inheritance"), the paragraph beginning "Python calls the constructor automatically"

**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> In the demo you can see that the creation of an object looks like a function call,
> but using the class name.

Proposed:
> In the demo, creating an object looks like a function call,
> but using the class name.

Why: "you can see that" is the §70 frame that tells the reader what to notice instead of stating it, and cutting it also removes the echo of "object creation" from the sentence immediately above ("the creation of an object").

***

[] Reject

**Section:** Inheritance, the paragraph after `demo_simple2.py`

**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> You can also see that the inherited `show_twice()` method is available in the derived class.

Proposed:
> The inherited `show_twice()` method is also available in the derived class.

Why: this sits directly under "The demo shows that the base-class constructor runs," so two adjacent sentences both frame the fact as something the reader is being pointed at; the second one states the fact directly instead.

***

[] Reject

**Section:** Marking Overrides with `@override`, the paragraph beginning "At run time `@override` adds no wrapper."

**Pattern:** Treadmill effect / low information density (Structure and Rhythm Tests) (P2)

Current:
> The type checker performs all verification before the program runs.

Proposed:
> Cut this sentence.

Why: the section has already said "A type checker now verifies the claim," "Python runs the program either way," and "Verification comes from a separate tool," so this is the fourth statement of the same fact and adds nothing the reader does not already have.
Borderline: if the closing contrast against "At run time" is wanted here, keep it and drop nothing.

***

[] Reject

**Section:** Properties, the paragraph beginning "The getter and setter are independent"

**Pattern:** §23 Filler Phrases, make verbs do the work (P2)

Current:
> A plain method is a better expression of the intent.

Proposed:
> A plain method expresses the intent.

Why: a noun phrase built on a weak copula ("is a better expression of") where a direct verb does the same job in fewer words.
Minor, and the sentence is not wrong as written.

***

[] Reject

**Section:** Composing Methods with `import`, the final paragraph

**Pattern:** §25 Generic Positive Conclusions / treadmill effect (P2)

Current:
> You will rarely need this in your own code.

Proposed:
> Cut this sentence.

Why: the same advice already appears twice in the same four-sentence paragraph, as "This is a curiosity more than a technique" and "composition or a module-level function is almost always a clearer choice," so the closer restates rather than ends on the last concrete point.
