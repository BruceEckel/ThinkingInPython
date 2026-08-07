[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/09_Class_Attributes.md

This chapter is clean. A full scan turned up no Tier-1A/1B/Tier-2 AI vocabulary, no boldface runs, no bullet padding, no signposting or hedging, no rule-of-three inflation, no curly quotes, no spaced ` -- `, and no banned strings. Sentence length varies and every paragraph advances the argument. The three findings below are small clarity nits, not AI tells, and all three are borderline.

***

[] Reject

**Section:** Declaring Shared State with ClassVar (paragraph beginning "The annotation on `label` is not required here.")
**Pattern:** Pronoun-antecedent ambiguity (clarity; outside §1-§70) (P2)

Current:
> It earns its place for symmetry with `total`,

Proposed:
> The annotation earns its place for symmetry with `total`,
[[Do this but see if you can rewrite to get rid of "earns its place"]]

Why: The preceding line ends "...the attribute it initializes," so the reader meets three `it`s in two lines with two different referents; naming the subject once removes the stumble. Borderline: the sense is recoverable, this only saves the reader a re-read.

***

[] Reject

**Section:** Real Per-Object Defaults (opening paragraph)
**Pattern:** Treadmill effect, restated noun (Structure and Rhythm Tests) (P2)

Current:
> Each object then gets its own storage for instance variables:

Proposed:
> Each object then gets its own storage:

Why: The previous line already says the `@dataclass` "turns the class-attribute syntax into instance variable defaults," so the trailing "for instance variables" repeats the term without adding anything. Borderline: it is a two-word trim.

***

[] Reject

**Section:** Real Per-Object Defaults (paragraph beginning "A `@dataclass` reads the class-attribute declarations as a template")
**Pattern:** Name collision across listings (clarity; outside §1-§70) (P2)

Current:
> That is why `b.x = -1` cannot leak into a later `B()`,
> while `a.rating = 1` on `Stars` left `b` reading a value someone else could change.

Proposed:
> That is why assigning `x` on one `B` cannot leak into a later `B()`,
> while `a.rating = 1` on `Stars` left `b` reading a value someone else could change.

Why: `real_defaults.py` never defines `b` (that assignment is what Exercise 3 asks the reader to write), and the same sentence pair then uses `b` for the `Stars` instance, so one letter names two different objects a line apart. The proposal drops the phantom variable and leaves the second clause untouched.
