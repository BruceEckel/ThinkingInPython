When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/32_Multiple_Dispatching.md`.
The chapter is clean by this skill's standards:
no Tier 1A vocabulary, no curly quotes, no spaced ` -- `,
no signposting or filler frames,
and sentence length varies well
("Python dispatches on one type at a time." against the long typing sentences).
The deep review's kept "exactly" in the exact-match claim was honored and not re-flagged.
Every finding had one sensible answer, so this review has no live blocks.

## Applied directly

- Operators walkthrough: "The last case shows what the sentinel is for"
  is now "shows why the sentinel exists"
  (global rule: stranded preposition; "what it is for" is the rule's own example).
- Typing paragraph: "Spelling the union out" is now "Writing the union out"
  (global don't-use list: "spelling" for an annotation's written form).
- `NotImplemented` parenthetical: "not the `NotImplementedError` exception,
  a lookalike pair worth keeping apart" is now
  "not the lookalike `NotImplementedError` exception"
  (§53 "worth" endorsement frame; "lookalike" keeps the confusability warning).
  Close alternative: cut the tag entirely and leave
  "not the `NotImplementedError` exception".
- Operators walkthrough, three inline refs gained the conventional empty parens:
  `int.__add__`, `Meters.__radd__`, and `str`'s missing `__radd__`
  are now `int.__add__()`, `Meters.__radd__()`, `__radd__()`
  (project convention: function refs use empty parens;
  the surrounding paragraphs write `__add__()`/`__radd__()` with parens).
  `Meters.__add__` in the same paragraph got the same fix.

## Considered and declined

- "Python's own operators already perform a two-step dispatch": "already" is
  on the avoid-if-possible list but earns its place, drawing the contrast
  with the two hand-rolled dispatches the reader has been writing.
- "Importing both modules works cleanly": "cleanly" survives the deletion
  test poorly on paper but carries "without side effects", the exact point
  the rest of the sentence explains; bare "works" would understate it.
- "The match is on classes exactly": settled in the deep review
  (`deep_review/~32_Multiple_Dispatching.md`), a precise match claim that
  solution 6 quotes. Not re-flagged.
- "Exact matching is the property that surprises people": reads like a §37
  emotion claim by shape, but it is the topic sentence for the `exact_match.py`
  demo that then shows the surprise; the content backs the claim.
- "It can be more sensible to make the table explicit": hedged first-edition
  voice introducing the table version; the hedge is Bruce's register, not
  over-qualification.
- The opening question ("how can you get them to interact properly?") is a
  genuine framing question the whole chapter answers, not a §43 stalling
  transition; first-edition voice.
- "not just how many types it considers": "just" is load-bearing; deleting it
  would claim the swap changes nothing about the count, which is false.
- "`int` has never heard of `Meters`": "never" earns its place in a vivid,
  factual personification of the fallback.
