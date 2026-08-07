[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/24_Singleton.md

This chapter reads as human throughout.
A scan of the full Tier 1A/1B/2/3 vocabulary tables returns zero hits, there is no boldface in the prose, no rhetorical-question or "let's" signposting, no generic conclusion, and the sentence rhythm varies (short fragments like "Two `import` statements, one printed line." sit next to long technical sentences).
The only findings are small wordiness cuts and one pronoun that crosses a heading.

***

[] Reject

**Section:** A Module Is Already a Singleton (last line before "When You Want a Class")
**Pattern:** §23 Filler Phrases (P2)

Current:
> For the majority of singleton needs, the module approach solves the problem.

Proposed:
> For most singleton needs, a module solves the problem.

Why: "the majority of" is a long way to say "most," and "the module approach solves the problem" restates a noun the sentence already has.

***

[] Reject

**Section:** Nothing Keeps the Class Private (final sentence)
**Pattern:** §23 Filler Phrases (P2)

Current:
> It also turns out that the reachable class is useful when a test needs a fresh,
> uncached `Settings`.

Proposed:
> The reachable class is also useful when a test needs a fresh,
> uncached `Settings`.

Why: "It also turns out that" is an empty frame; deleting it loses nothing and puts the real subject at the front of the sentence.

***

[] Reject

**Section:** The Classic Implementations (paragraph before "Lazy Creation")
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> but notice that each does more work than the module or the cached factory above.

Proposed:
> but each does more work than the module or the cached factory above.

Why: "notice that" tells the reader how to read the clause instead of stating it; the deletion test passes cleanly.
Borderline: directing a reader's attention is legitimate in a teaching text, so this is a tightening, not a defect.

***

[] Reject

**Section:** Lazy Creation (first sentence of the section)
**Pattern:** §29 Fragmented Headers (P2)

Current:
> It is *lazy*: it builds the inner object on the first call,

Proposed:
> The classic approach is *lazy*: it builds the inner object on the first call,

Why: the antecedent of "It" is "The classic approach," which sits on the other side of the `### Lazy Creation` heading, so a reader arriving at the section (or following a cross-reference to it) has no referent.
