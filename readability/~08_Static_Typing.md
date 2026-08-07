[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/08_Static_Typing.md`

This chapter reads as human throughout.
A full pass over the Tier 1A/1B/2 vocabulary, the promotional, significance, and hedging patterns, the structural tells, and the repo-banned strings turned up almost nothing: no `reach for`, no `from __future__ import annotations`, no spaced ` -- `, no curly quotes, no boldface or bullet inflation, no rhetorical padding, and sentence and paragraph lengths vary naturally.
The only recurring soft spot is §70-style restatement, where a definition is given, then given again in different words a sentence later.
All four findings below are that same pattern, and all are P2.

***

[] Reject

**Section:** Variance
**Pattern:** Referent clarity (P2), borderline

Current:
> A read-only shape has no such problem,

Proposed:
> A read-only container has no such problem,

Why: The listing directly above defines a class named `Shape`, so "a read-only shape" reads as though it names that class rather than a read-only container such as `Sequence`.
This is a clarity fix rather than a classic AI tell, so it is borderline for this skill.

***

[X] Reject

**Section:** Structural Typing with Protocols
**Pattern:** §70 Interpretive Metadiscourse / restatement (P2)

Current:
> Dynamic typing and structural typing are the same idea checked at different moments.
> Dynamic typing trusts the object once the code is running,
> while structural typing proves the shape beforehand.

Proposed:
> Dynamic typing and structural typing are the same idea checked at different moments.

Why: The paragraph states the same timing contrast three times running: "Instead of waiting until the program is running, a type checker verifies ahead of time," then "the same idea checked at different moments," then "trusts the object once the code is running ... proves the shape beforehand."
The middle sentence is the compact version, so the third adds wording rather than information.

***

[] Reject

**Section:** Classes as Values: `type[C]`
**Pattern:** §70 Interpretive Metadiscourse / restatement (P2)

Current:
> The form `type[SomeType]` means the class object, or any subclass of it.
> `type[C]` annotates the class, not an instance:

Proposed:
> The form `type[SomeType]` means the class object, or any subclass of it:

Why: "annotates the class, not an instance" restates the sentence immediately before it, which the section heading has already said as well.
Moving the colon onto the surviving sentence keeps the lead-in to the listing intact.

***

[] Reject

**Section:** Generic Functions and Classes
**Pattern:** §70 Interpretive Metadiscourse / restatement (P2), borderline

Current:
> A *type parameter* correctly specifies the returned type.
> The type held by the list is the type the function returns.

Proposed:
> A *type parameter* correctly specifies the returned type.

Why: The relation between element type and return type was already stated two paragraphs earlier ("A useful annotation returns a type that matches the list's element type, whatever that type is"), so the second line repeats it a third time.
Borderline, since restating an abstract claim concretely is a legitimate teaching move.
