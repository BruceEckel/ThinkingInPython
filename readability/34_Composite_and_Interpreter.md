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

Every finding was resolved directly and applied (listed below).
No blocks remain.

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
- `A Template Is a Tree` lead-in: split after "but everything else about it
  is this chapter's shape." (the paragraph had grown to fifteen lines and
  five facts as patches accumulated; the break separates what a `Template`
  is from how iterating one narrows, with no wording changed).
