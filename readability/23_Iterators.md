> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/23_Iterators.md`

Run after the deep-review edits landed, so the new prose, the two new headings,
and the moved test block get the same scan the rest of the chapter got in
review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human prose.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface stacking,
and the new exercises match the voice of the eight before them.
Every finding below is a seam left by this pass: three of the four exist only
because a heading arrived or a block moved.

***

**Section:** The Protocol Answers Nothing for Free (the new closing section)
**Pattern:** §29 Fragmented Header, a heading and its first clause saying the same thing (P1)

Current:
> ## The Protocol Answers Nothing for Free
>
> Both surprises in [The Costs of Laziness](#the-costs-of-laziness)
> come from the same rule: the protocol answers no question for free.

Proposed: keep the heading and let the sentence carry the consequence instead
of the restatement.
> ## The Protocol Answers Nothing for Free
>
> Both surprises in [The Costs of Laziness](#the-costs-of-laziness)
> come from the same rule.

Why: the heading was promoted from this paragraph's own opening clause, so the
two now sit four words apart saying the same thing, and the reader is told the
rule before the colon that was going to state it.
Cutting the clause leaves the two "the only way to find out" sentences to
define the rule, which they already do, and the heading to name it.

This needs your call rather than mine because the alternative is the other
direction: keep the clause and retitle the section to name the consequence
instead, something like `## What the Protocol Will Not Tell You`.
The heading is new in this pass and nothing links to it yet, so retitling is
still free; once a later chapter points at `#the-protocol-answers-nothing-for-free`,
it is not.
I lean toward the cut, because the heading is the better of the two phrasings.

[] Reject

***

**Section:** Generators (the moved `test_iterators.py` lead-in)
**Pattern:** §11 repetition, the same claim three times in four lines (P2)

Current:
> so it can be iterated repeatedly, as the tests below confirm.
>
> These tests collect each iterator into a list and compare them,
> covering the sequences and their empty edge cases.
> This confirms that a custom iterable can be re-iterated,
> and that `total()` works on every source:

Proposed:
> so it can be iterated repeatedly, as the tests below confirm.
>
> These tests collect each iterator into a list and compare them,
> covering the sequences and their empty edge cases,
> and check that `total()` works on every source:

Why: the two passages were 160 lines apart before the move and now sit
adjacent, so "as the tests below confirm" and "This confirms that a custom
iterable can be re-iterated" repeat both the verb and the claim, and the claim
itself ("can be iterated repeatedly") was made in the line above that.
The re-iteration point survives in the sentence that introduces it and in the
test named `test_countdown_is_reiterable`.

Your call on which of the two sentences keeps the claim: I cut it from the
lead-in because the forward reference reads better attached to `Countdown`,
but the opposite trim works if you would rather the lead-in stand alone.

[] Reject

***

**Section:** The Costs of Laziness (the new heading)
**Pattern:** §29 Fragmented Header, heading echoed by the line beneath it (P2)

Current:
> ## The Costs of Laziness
>
> There are two surprising consequences of laziness.
> Both are silent:

Proposed:
> ## The Costs of Laziness
>
> Two of those consequences are surprising, and both are silent:

Why: "laziness" repeats immediately under a heading that just said it, and
"There are two surprising consequences" is the weaker of the two openings now
that the heading announces the subject.
The replacement also links the new section to the paragraph above it, which
ends on what laziness buys, so the heading reads as the turn from benefit to
cost rather than as a fresh start.

[] Reject

***

**Section:** Generators, the `tee` lead-in
**Pattern:** a forward-pointing "this" before the thing it points at (P2)

Current:
> This `squares()` is the plain-function form from `eager_validation.py`,
> with the generator expression standing in for `produce()`:

Proposed:
> The `squares()` below is the plain-function form from `eager_validation.py`,
> with the generator expression standing in for `produce()`:

Why: "This `squares()`" names something the reader has not reached yet, and the
nearest `squares()` on the page is the generator function from
`generator_lifecycle.py`, which is the one the sentence exists to distinguish
it from.
Naming the direction removes the momentary wrong referent.

[] Reject
