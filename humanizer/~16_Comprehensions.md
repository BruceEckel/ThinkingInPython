[[Reviewed]]
# Humanizer candidates: Chapters/16_Comprehensions.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

## How to use this

Each edit is a `###` block with a CURRENT and a PROPOSED fence.
Delete any block you don't want, save the file, and hand it back to me.
I apply what survives, verbatim, and run `make verify`.

The CURRENT fences are exact copies from the chapter,
so don't hand-edit inside them or the match will fail.
If you want a different wording, edit the PROPOSED fence instead
and I will use yours.

Tier A is what I'd apply. Tier B is genuinely arguable, delete freely.
Housekeeping is not humanizer output; separate list at the end.

## Verdict

The chapter is close to clean: no curly quotes, no emoji, no boldface-header
lists, no promotional language, no rule-of-three padding, no aphorism
formulas, no knowledge-cutoff disclaimers, and italics are used correctly
(only to introduce `Comprehensions` and `generator expression` on first use).
The real findings were structural and small: two person slips ("Let's",
"we"), a doubled "already" next to a stray "themselves," and a three-sentence
staccato run that also read as a tailing-negation fragment. Tier B added
two heading-echo openers and two minor word echoes. Largest single finding:
the person-consistency slips, since this book is otherwise consistently
second person.

All Tier A and Tier B edits have been applied (the B3 "Set
Comprehensions" opener's PROPOSED fence had a missing article, fixed to
"use the same principles" when applied).

## Housekeeping

None found. Checked and clean: no double blank line before any heading
(every heading in this chapter uses exactly one), no `[[ ]]` draft notes,
no spaced ` -- `, no stray em dashes of any kind, and Semantic Line Breaks
look intact throughout (every long sentence already breaks at its clause
boundaries; the one very long bullet at line 25 has no internal comma to
break at, so it isn't drift).

## Considered and not flagged

- Italics are used only to introduce `Comprehensions` (line 3) and
  `generator expression` (line 403) on first use; no emphasis-italics
  anywhere in the chapter.
- "itself nested inside the outer comprehension" (line 254) is load-bearing:
  it disambiguates which noun ("sorted()") the participial phrase modifies.
  Dropping it makes the sentence ambiguous, so it stays.
- "reads honestly" (line 325) draws a real contrast with "a loop wearing a
  disguise" (line 311) a few sentences earlier; it earns its place under
  the watch-list test and is kept in the A3 rewrite above.
- "a loop wearing a disguise" (line 311) is a specific, fresh metaphor, not
  a generic aphorism formula ("X is the Y of Z"); left alone.
- The three short parallel sentences at lines 284-286
  (`in_stock` answers.../`sort()` answers.../`report` answers...) and the
  "three parts mirror the list comprehension" passage at lines 379-381 both
  map onto a real, distinct three-part structure in the code, not a padded
  rule-of-three list; left alone.
- The semicolon at lines 146-147 (`zip()` stops...; pass `strict=True`...)
  ties two tightly linked clauses, matching the sparing-use rule in
  CLAUDE.md; left alone.
- No em dashes appear anywhere in the chapter, so there's nothing to
  protect or flag on that front.

## Scan coverage

Clean, no hits: curly quotes, emoji, boldface-header vertical lists,
promotional/advertisement language, vague attributions and weasel words,
knowledge-cutoff disclaimers and speculative gap-filling, sycophantic tone,
filler phrases, excessive hedging, false ranges, hyphenated-word-pair
overuse, persuasive-authority tropes, the "nothing else"/"nothing
but"/"nothing more" family, "Challenges and Future Prospects"-style
sections, collaborative-communication artifacts, and diff-anchored writing.
Word-level AI vocabulary (§7: delve, crucial, intricate, underscore,
showcase, testament, vibrant, tapestry, pivotal, landscape, garner, align
with, fostering, enhance) had zero hits, consistent with the same result in
chapters 46 and 47.
