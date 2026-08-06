# Humanizer candidates: Chapters/33_Visitor.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied and what was never flagged.
This is a changelog now, not a worklist.

## Applied

Every block survived review. Five prose edits plus four listing comments:

- A1, the opening paragraph at lines 6-11, where "hierarchy" appeared three
  times and "unchangeable" twice in five sentences. Bruce's wording on the
  last line: "but that's not an option," not the drafted "but that's off
  the table."
- A2, "load-bearing" at line 117, replaced with what the annotation is for.
- A3, the emphasis italic on *which* at line 113.
- B1, "honest" at line 120, replaced with the concrete statement of what
  fails the type checker.
- B2, the two consecutive sentences opening with "This" at lines 132-135.
- Housekeeping 1, the three near-identical `flower_visitors.py` comments at
  lines 62, 67, 72, rewritten per class ("Bee pollinates:", "Fly also
  pollinates:", "Worm eats instead:").
- Housekeeping 2, the first-person listing comment at line 82, now
  "Now perform Bug operations on the flowers:".

Both housekeeping items were re-synced; the surrounding code is unchanged
and the `#:` markers still match.

The review leaned toward B2 being a much weaker case than A1. It stayed in
the file and was applied.

## Considered and not flagged

- **Repeated italics on *Visitor*, *Multiple Dispatching*, and *GoF
  Design Patterns*.** These recur through the chapter (lines 3, 6, 13,
  134, 206, 211, 269). This is the book's standing convention for GoF
  pattern names, not the generic "first use only" rule the emphasis
  check looks for, so it's a different case from A3's stray "*which*".
- **"The `Any` is the quiet price of the empty base, the same bargain
  [Data Transfer Objects] paid for its attribute bag" (line 124-126).**
  Reads like an aphorism formula on the surface, but it's anchored to a
  specific, real cross-reference and states an actual shared tradeoff
  between two chapters rather than gesturing at vague profundity. Left
  alone.
- **"Adding a new operation is a new function. Adding a new flower is a
  class and, where needed, a one-line registration" (lines 201-202).**
  Looks like a broken parallel, but the asymmetry is real: an operation
  genuinely needs only a function, while a flower can need an extra
  registration step. Fixing the parallelism would misstate the code.
- **"Bee"/"Fly"/"Worm" and "Gladiolus"/"Ranunculus"/"Chrysanthemum"
  triples.** These look like a Rule-of-Three, but they're the actual
  domain classes in the listing, inherited from this pattern's running
  example, not a prose device.
- **"never" at line 185** ("`nectar()` calls it through the dispatcher,
  never by its own name") is a literal, factual claim about how
  `singledispatch` calls registered functions, not the rhetorical
  "never" the watch list targets. Left alone.
- **"hook" at lines 135 and 208** ("the `accept()` hook"). Standard
  software-engineering term for an extension point, not the marketing
  sense the watch list means. Left alone.
- **"hierarchy" recurring past the A1 paragraph.** It's the chapter's
  central technical noun and can't be avoided when explaining a pattern
  that's entirely about class hierarchies. Only the tight cluster in
  lines 6-11 read as an echo; the rest is unavoidable vocabulary.

## Scan coverage

Clean, no hits: §7 AI-vocabulary word list, curly quotes, em dashes
(none appear in this chapter at all, not even the author's own), spaced
` -- `, emoji, boldface-header lists, inline-header vertical lists,
"Challenges and Future Prospects" formula, vague weasel attribution,
collaborative-communication artifacts, sycophantic tone, hedging,
false ranges, hyphenated-pair overuse, signposting/announcements,
fragmented headers, and `[[ ]]` draft notes. First-person "we" appeared
exactly once, inside a listing comment (Housekeeping 2), not in prose.
