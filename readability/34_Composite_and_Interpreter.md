> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/34_Composite_and_Interpreter.md` (r2)

The chapter still reads as human throughout, and a sweep of the full Tier
1A/1B/2/3 vocabulary tables returns zero hits, same as the first review.
The two findings that review raised (the "clever part" label, the `x + 1`
inaccuracy) are both fixed in the current text.

All the findings sat in prose that had never been through a readability
pass: the paragraphs the deep review added while it was being written, plus the
sentences today's apply added. Nothing in the chapter's older prose came up.

The clear-cut fixes were applied to the chapter directly (listed below);
one block remains for your judgment.

## Applied directly

- `A Template Is a Tree` lead-in: "a closed union like `Node` with only two
  members" → "with two members" (dropping "only" changes nothing), and the
  clause "so an `isinstance` test narrows it as well as a `match` would and
  the `else` branch is the `str` case" gained the missing comma before "and,"
  which also restores the semantic line break.
- Paragraph after `evaluate.py`: "shows the composite claim directly" →
  "shows the nesting" ("the composite claim" named the chapter's argument
  rather than a thing in the output, and "directly" fails the deletion test).
- Paragraph after `simplify.py`: "The same syntax runs in both directions
  here" → "The same syntax does two opposite jobs" (syntax does not run, and
  the colon then fills in the two jobs; "here" was filler).
- "Matching the pair of simplified children ... is what lets the rules
  compose" → "... lets the rules compose" (the cleft the global rule names;
  the deletion test passes).

***

**Section:** `## A Template Is a Tree`, lead-in paragraph
**Pattern:** Paragraph-length uniformity / read-aloud test (P2)

The lead-in has grown to fifteen lines and carries five separate facts
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

This is the one finding here I cannot settle for you. The split is cosmetic and
the paragraph is not wrong, so declining costs nothing; I raise it because the
paragraph is the chapter's longest and it now reads as a list rather than an
argument. (The comma and the "only" fixes the earlier version of this block
bundled are already applied, so only the paragraph break is in question.)

[] Reject
