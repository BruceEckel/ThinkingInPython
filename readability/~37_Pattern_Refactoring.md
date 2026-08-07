[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapter 37, Pattern Refactoring

This chapter reads as human-written technical prose.
There is no AI-vocabulary cluster, no boldface, no curly quotes, no rule-of-three padding, and no promotional framing.
The only clear tell is the closing aphorism in "Choosing the Lightest Construct";
the rest of the findings are small clarity edits on compressed sentences, and most are marked borderline.

***

[] Reject

**Section:** Simulating a Trash Recycler (line 174, the sentence introducing `test_parse_trash.py`)
**Pattern:** §13 Passive Voice and Subjectless Fragments (advisory here) (P2)

Current:
> Testing parses a small in-memory file, so it does not depend on `trash.dat`:

Proposed:
> The test parses a small in-memory file, so it does not depend on `trash.dat`:

Why: The gerund "Testing" hides the actor, and the following "it" then has no clear referent; the parallel sentence for the earlier test file says "The tests confirm that...".
The block that follows contains exactly one test function, so the singular is accurate.

***

[] Reject

**Section:** Adding Operations: Visitor, and Why Python Skips It (line 388)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> so it falls through to the base function and performs the default behavior.

Proposed:
> so it falls through to the base function.

Why: "performs the default behavior" restates "falls through to the base function" in different words.
Borderline: the repetition may be deliberate reinforcement for a reader meeting `singledispatch` fallback for the first time.

***

[] Reject

**Section:** Adding Operations: Visitor, and Why Python Skips It (line 398)
**Pattern:** clarity edit, no §NN (P2)

Current:
> `sum_value()` earlier was a function.

Proposed:
> The earlier `sum_value()` is an ordinary function.

Why: As written the sentence asserts almost nothing ("was a function"), and the past tense clashes with the present tense used for code everywhere else in the chapter.
The proposed wording echoes the chapter's earlier line, "`sum_value()` is an ordinary function," which is the point being called back to.
Borderline: this is a word-order clunk rather than an AI pattern.

***

[] Reject

**Section:** Adding Operations: Visitor, and Why Python Skips It (line 399)
**Pattern:** §34 Real/Actual Adjective Inflation, §23 often-empty adverbs (P2)

Current:
> Use `singledispatch` only when the behavior genuinely differs by type.

Proposed:
> Use `singledispatch` only when the behavior differs by type.

Why: "genuinely" is an intensifier with no contrast named; the sentence means the same without it.
Borderline: it is a single instance, and it could be read as contrasting with behavior that only appears to differ.

***

[] Reject

**Section:** Choosing the Lightest Construct (line 414, final prose line of the chapter body)
**Pattern:** §32 Aphorism Formulas, fake-profound kicker ending (P1)

Current:
> The true measure of a pattern is whether it is still useful once the language does part of the work.

Proposed:
> A pattern is worth keeping only when it is still useful once the language does part of the work.

Why: "The true measure of X is Y" is the aphorism template, placed as the chapter's closing line, and "true" adds nothing the sentence does not already say.
The proposed version keeps the claim intact and states it directly instead of as a maxim.
