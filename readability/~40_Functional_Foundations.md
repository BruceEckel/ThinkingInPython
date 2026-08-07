[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/40_Functional_Foundations.md`

This chapter reads as human throughout.
A full sweep of the Tier 1A/1B/2/3 vocabulary tables (§7) returned exactly one hit, and that one was the literal noun "key" in "dictionary key."
No bold spans, no curly quotes, no spaced ` -- `, no banned strings, no non-ASCII characters, no signposting, no rhetorical-question transitions, no rule-of-three padding.
The only pattern that shows up at all is mild restatement (§70 / treadmill effect): three places where a sentence re-delivers a claim the chapter already made a paragraph or a section earlier.
All three findings are P2 polish, and the first one is explicitly borderline.

***

[] Reject

**Section:** Pure Functions (final one-line paragraph of the section, just before `## Immutability`)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> Every later feature in these chapters is, in part,
> a way to keep more of your code pure.

Proposed:
> Cut these two lines.

Why: The section already opened with the same claim from the other direction, "Purity is the foundation on which everything else in these chapters builds," so the closer restates rather than advances, and "is, in part," hedges it back down.
This one is borderline: it is a characteristic section-closing thesis that also forward-links the rest of the part, so if you read the two sentences as foundation-versus-goal rather than as a pair, keep it.

***

[] Reject

**Section:** Partial Application (paragraph beginning "Use partial application when an API expects...")
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> Rather than write a throwaway wrapper,
> you preset the fixed arguments and pass the result straight in.

Proposed:
> Cut these two lines.

Why: The section's opening sentence already said `functools.partial()` "does this without writing a wrapper by hand," so the wrapper point arrives a second time with no new information.
The paragraph then runs straight into "Unlike a lambda, `partial()` keeps the bound arguments as data you can inspect," which is the sentence carrying new content.
If you want to go further, the preceding line ("Use partial application when an API expects a function of one argument and you have a function of several.") also overlaps "which is handy when a higher-order function needs a single-argument callable" two lines above it; cutting only the wrapper sentence is the minimum effective edit.

***

[] Reject

**Section:** Composing Functions (paragraph beginning "Composition scales by addition.")
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> Stacking `compose()` calls forms a pipeline that reads as the list of steps it performs.

Proposed:
> Cut this sentence.

Why: The section's own opening already set up the pipeline image, "You can assemble behavior from small pieces, / the way a pipeline reads as a sequence of steps," so this repeats it in fresh words instead of adding to it.
The surrounding sentences ("Each stage is also testable on its own..." and "When a requirement changes, you insert or swap a single stage...") each carry a distinct claim and read cleanly with this line removed.
