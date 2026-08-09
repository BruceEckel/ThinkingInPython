> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/34_Composite_and_Interpreter.md` (r2)

The chapter still reads as human throughout, and a sweep of the full Tier
1A/1B/2/3 vocabulary tables returns zero hits, same as the first review.
The two findings that review raised (the "clever part" label, the `x + 1`
inaccuracy) are both fixed in the current text.

All four findings below sit in prose that has never been through a readability
pass: the paragraphs the deep review added while it was being written, plus the
sentences today's apply added. Nothing in the chapter's older prose came up.

***

**Section:** `## A Template Is a Tree`, lead-in paragraph
**Pattern:** Paragraph-length uniformity / read-aloud test (P2)

The lead-in has grown to fifteen lines and now carries five separate facts
before the reader reaches a listing: what a `Template` is, that iteration skips
empty literal pieces, that `template.strings` keeps them, that the grammar is
flat rather than nested, that iteration produces `str | Interpolation`, and that
the `else` branch is therefore the `str` case. Two of those arrived as separate
patches (the `strings` clause, then the `str | Interpolation` clause), and the
paragraph has been absorbing them rather than reorganizing around them.

Proposed split, after "but everything else about it is this chapter's shape":

> ... The grammar is flat rather than nested,
> so the walk is a loop instead of a recursion,
> but everything else about it is this chapter's shape.
>
> Iterating a `Template` produces `str | Interpolation`,
> a closed union like `Node` with two members,
> so an `isinstance` test narrows it as well as a `match` would,
> and the `else` branch is the `str` case.
> The structure is data, and what it means is whatever a function decides:

Two changes beyond the break: a comma before "and the `else` branch" (that
sentence currently joins two independent clauses with none), and "with two
members" for "with only two members," since dropping "only" changes nothing.

This is the one finding here I cannot settle for you. The split is cosmetic and
the paragraph is not wrong, so declining costs nothing; I raise it because the
paragraph is the chapter's longest and it now reads as a list rather than an
argument. If you would rather keep one paragraph, the comma and the "only" are
still worth taking.

[] Reject

***

**Section:** "Evaluation Is a Tree Walk," paragraph after `evaluate.py`
**Pattern:** §70 Interpretive Metadiscourse, plus an empty adverb (§23) (P2)

Current:
> Printing `expr.left` shows the composite claim directly:
> the `Add` at the root holds a `Mul`, which holds a `Num` and a `Var`.

Proposed:
> Printing `expr.left` shows the nesting:
> the `Add` at the root holds a `Mul`, which holds a `Num` and a `Var`.

Why: "the composite claim" names an argument the chapter is making rather than
a thing in the output, so the reader has to translate it back into the nesting
before the second half lands. The second half already says what the first half
was pointing at. "Directly" is the deletion-test kind of adverb: the sentence
means the same without it.

This sentence is new with today's apply, added to explain the changed output
marker.

[] Reject

***

**Section:** "Simplification Rewrites the Tree," paragraph after `simplify.py`
**Pattern:** §7 odd word, metaphor standing in for a literal statement (P2)

Current:
> The same syntax runs in both directions here:
> a `Num(0)` on the left of a `case` is a pattern that never calls `Num`,
> while the one on the right of a `return` is the constructor.

Proposed:
> The same syntax does two opposite jobs:
> a `Num(0)` on the left of a `case` is a pattern that never calls `Num`,
> while the one on the right of a `return` is the constructor.

Why: syntax does not run, and "in both directions" asks the reader to work out
which two directions are meant before the colon explains it. "Two opposite jobs"
states the point the rest of the sentence then fills in. "Here" is filler; the
sentence is already anchored by the two positions it names.

Also new with today's apply.

[] Reject

***

**Section:** "Simplification Rewrites the Tree," paragraph beginning "Matching
the pair of simplified children"
**Pattern:** Global watch list, "Consider rewriting" tier: `is what` (P2)

Current:
> Matching the pair of simplified children, rather than the original node,
> is what lets the rules compose.

Proposed:
> Matching the pair of simplified children, rather than the original node,
> lets the rules compose.

Why: `is what` followed by a verb is the cleft the global rule names, and the
deletion test passes: the sentence means the same with it gone. The subject is
already a gerund phrase, so nothing needs the cleft to hold it in place.

[] Reject
