When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/27_Factory.md`.
The chapter is post-deep-review and reads clean:
no Tier 1A vocabulary, no curly quotes, no spaced ` -- `,
no rule-of-three padding, no metadiscourse, no generic closers.
`readability_db.md`'s 27_Factory precedent was honored:
"Factory might be the most common design pattern" stays untouched.
The deep review's declined items
(the "... or so it seems" opener, the question-form heading,
the `NotImplementedError` teaching contrast) were not re-raised.
Two direct fixes, no live blocks.

## Applied directly

- Line 595, stranded preposition (global rule): "with no error to point
  at" is now "with no error to signal it". The object of "at" was
  fronted, the same shape as "the field they sit on". Close
  alternative: "with no error to mark it".
- Line 371, weak verb phrase (§23): "Thus you're able to isolate" is
  now "Thus you can isolate". Same family as "has the ability to"
  becoming "can"; the "Thus" and the "in one place" aside stay as
  first-edition cadence.

## Considered and declined

- "the GUI that you're working with" and "no base class to derive from
  while still type checking": each preposition closes a mid-sentence
  clause, not the sentence, which is what the stranding rule governs.
  Both read as natural phrasal usage; fronting ("the GUI with which
  you're working") would stiffen first-edition prose.
- "genuinely a process" (Builder section) and "a genuine process"
  (the closing bullet list): §34 by vocabulary, but both carry the
  named contrast the carve-out requires, construction-as-process
  against optional values that keyword arguments cover.
- "real work beyond calling a constructor" (twice): same carve-out;
  the contrast is named in the sentence both times.
- Three sentence-opening "Thus" (lines 11, 120, 371): not on §62's
  list, and the cadence is the first edition's. Left alone.
- "the pattern does not go away, it stops needing a class hierarchy to
  express it": a short comma splice, but the halves are one claim and
  the global rule targets genuinely long splices. Deliberate rhythm.
- "There is no factory method and no factory class; the `dict` is the
  factory": negative-parallelism-adjacent (§9), but the double
  negation rules out the two classic forms the chapter has just shown,
  so both halves carry weight.
- The bullet list under "Which Factory Should You Use?": a decision
  table written as parallel condition-then-choice items, genuine list
  content, matching the kept 35_Flyweight parallelism in
  `readability_db.md`.
- "The humblest builder in Python is easy to overlook": a superlative
  by shape, but it introduces the concrete `"".join(parts)` case in
  the next sentence, and the modesty is the point. Voice.
- "A separate factory class is worth writing when ...": §53's carve-out
  covers it; the "worth" weighs writing effort against a stated
  condition rather than endorsing a fact.
