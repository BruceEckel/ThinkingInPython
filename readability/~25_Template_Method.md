[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/25_Template_Method.md`

This chapter reads as human throughout.
A full scan of the Tier 1A/1B/2/3 vocabulary tables, the banned repo strings, spaced ` -- `, curly quotes, and boldface returned zero hits, and the prose carries the specificity (`unittest`, `TestCase.run()`, the Hollywood Principle, the `@final`-is-checker-only caveat) that the skill lists as evidence of a real writer.
Only two findings survived vetting, both P2 repetition, and both are borderline calls a teaching book can legitimately reject.

[] Reject

**Section:** The Fixed Algorithm (paragraph beginning "The step methods default to `...`")
**Pattern:** §11 Elegant Variation / read-aloud echo (P2)

Current:
> The step methods default to `...`, doing nothing,
> so a subclass overrides only the steps it cares about,
> and a forgotten step silently does nothing.

Proposed:
> The step methods default to `...`,
> so a subclass overrides only the steps it cares about,
> and a forgotten step silently does nothing.

Why: "doing nothing" and "does nothing" land twice in one sentence, and the closing clause already tells the reader what an `...` body amounts to, so the first gloss is redundant.
Borderline: keeping it makes the ellipsis idiom explicit for a reader who has not met it.

***

[] Reject

**Section:** Substitutability (last full paragraph before the test listing)
**Pattern:** Treadmill effect / low information density (P2)

Current:
> Where the algorithm cannot proceed without a step,
> `@abstractmethod` says so and Python enforces it.

Proposed:
> Cut this sentence.

Why: the same remedy, with more detail and a cross-reference, already appears two paragraphs earlier ("When every subclass must supply a step, inherit from `ABC` and declare the step with `@abstractmethod` ... then Python refuses to instantiate a subclass that forgot it"), so this restates rather than advances, and the paragraph still lands on "The Template Method works only when every subclass is a faithful substitute for its base."
Borderline: restating a remedy at the point where the problem resurfaces is a defensible teaching move.

***

## Considered and not raised

Listed so a later review does not re-litigate them.

- "At the heart of a framework is the *Template Method*" (opening). Close to §27's "at its core," but here the phrase introduces a definition rather than staging a fake depth reveal, and the sentence carries real information.
- "a separation this chapter returns to below" (opening). Metadiscourse under §70/§28, but a forward pointer earns its place in a book chapter.
- "Notice which direction the calls flow." Instructional imperative, and what follows is genuinely new material, not a gloss on what was just said.
- "the convention every Python programmer carries." A universal quantifier of the kind §35 flags, but it reads as deliberate voice and the sentence is stronger with it.
- "The guarantee is real, but it is the checker's guarantee." Exempt under §34's named-contrast carve-out: the contrast is spelled out in the same clause.
- "a faithful substitute for its base." Not §35: "faithful" here is the ordinary "true to the original" sense, as in a faithful reproduction, not a moral adjective on a non-agent.
- Rule of three in "share state, build on each other, or come as a coherent group." Three distinct conditions, not padding to a count.
