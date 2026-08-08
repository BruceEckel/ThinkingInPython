[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/20_Rethinking_Objects.md`

Run after the deep-review edits landed, so the new and moved prose gets the same
scan the rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written during the deep review.

***

[] Reject

**Section:** The Liskov Substitution Principle (new closing paragraph)
**Pattern:** §23 clarity, a metaphor that miscounts (P2)

Current:
> Substitutability is only the first crack.
> OOP made four promises: encapsulation, ...

Proposed:
> Substitutability is the first thing OOP promised that no tool can check.
> OOP made four promises: encapsulation, ...

Why: "the first crack" implies substitutability is one of the four promises the
next sentence lists, and it is not.
Saying what the section actually showed keeps the handoff to the list clean.

***

[] Reject

**Section:** Prefer Composition to Inheritance (lead-in to `composition.py`)
**Pattern:** §7 metaphor standing in for the literal statement (P2)

Current:
> Composition scales past this repair job.

Proposed:
> Composition does more than repair a broken subclass.

Why: "scales past this repair job" asks the reader to hold two figures at once,
and `CountingBox` is not a repair of anything: it is a different design.
The replacement makes the same transition literally.

***

[] Reject

**Section:** Polymorphism Without Inheritance, opening of the moved What Is Polymorphism?
**Pattern:** §23 clarity, an opener that qualifies before it states (P2)

Current:
> Inheritance is only one expression of polymorphism.
> More broadly, polymorphism means that a function parameter accepts more than one type.

Proposed:
> Polymorphism means that a function parameter accepts more than one type.
> Inheritance is only one way to get there.

Why: since the move, this is the first thing the section says, and it opens by
qualifying a definition the reader has not been given.
Stating the definition first also lets the sentence after it, about which types
and what the function may do with them, follow directly.

***

[] Reject

**Section:** Prefer Composition to Inheritance (around `counting_box.py`)
**Pattern:** §11 repetition (P2)

Current:
> Hold a list instead of being one, and expose only what you meant to expose:
>
> [listing]
>
> `CountingBox` holds a list instead of being one.
> Nothing arrives from a base class, ...

Proposed: drop the repeated clause from the paragraph after the listing:
> Nothing arrives from a base class, so nothing can slip past the counter:
> the only way into `items` is a method this class wrote.

Why: the lead-in and the follow-up say the same six words on either side of the
listing. The lead-in earns them, because it is the instruction; the follow-up
should start on what that buys.

***

[] Reject

**Section:** The Immutability Solution (after `frozen_leaky.py`)
**Pattern:** accuracy, a count that does not match the listing (P1)

Current:
> The listing shows both failures side by side:
> the rebinding that `frozen=True` catches,
> and the two that it does not.

Proposed:
> The listing shows all three side by side:
> the rebinding `frozen=True` catches,
> and the mutation and the failed hash it does not.

Why: "both failures" and "the two that it does not" disagree with each other and
with the listing, which prints three outcomes.
Naming the three removes the arithmetic.
