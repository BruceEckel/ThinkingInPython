When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/16_Comprehensions.md`, run after the
deep review in `deep_review/~16_Comprehensions.md` was applied.
That review's declined list and `readability_db.md` were read first and bind
this pass; nothing they settled is re-raised here.
The chapter is clean of AI-vocabulary clusters, curly quotes, and spaced
`--`; sentence rhythm varies; the parallel fragments in Choosing a Form are
a decision table written as prose, the shape the 35_Flyweight precedent
keeps.
No finding needed a live block.

## Applied directly

- Feeding the Iterator Clause (brackets-vs-parentheses paragraph),
  watch word "happen": "that pull happens outside the `with`" is now
  "that pull comes outside the `with`".
- Breaking Up a Complex Comprehension, watch word "happen": "filtering,
  flattening, sorting, and formatting all happen in a single expression"
  is now "all run in a single expression", matching the chapter's
  established verb ("No computation runs until you pull a value").
- Choosing a Form, watch word "happen": "The delimiters also decide when
  the work happens" is now "when the work runs". Close alternative was
  "occurs", avoiding the echo with "runs to completion" on the next
  line; "runs" won for matching the chapter's vocabulary, and the two
  verbs take different subjects.
- Exercise 5, banned "want" metaphor plus watch word "actually": "a list
  the caller would actually want" is now "a list the caller can use".
  The caller is code, so "want" was the machine-desire metaphor the
  global list bans, and "actually" restated a contrast the previous
  sentence (the list of `None`s) had drawn.

## Considered and declined

- "decides *whether* the comprehension produces an element at all"
  (Nested Comprehensions): "at all" is on the avoid-if-possible list but
  sharpens the zero-or-one contrast against the conditional expression,
  which always produces one element. Deleting it flattens the pair.
- "`map()` and `filter()` pay off when the function already exists":
  "already" draws the real contrast with writing a `lambda` on the spot,
  the same call as the kept "already" in 33_Visitor.
- "so `int()` never sees it" (exercise 1): "never" states the guarantee
  the predicate provides for every element; "does not see it" weakens it.
- "A comprehension nested inside `sorted()`, itself nested inside the
  outer comprehension": "itself" is referential, marking that `sorted()`
  rather than the inner comprehension sits inside the outer one.
- "Here's a two-level list comprehension using `Path.walk()`:" matches
  the §20 "here is a..." shape, but as a listing introduction it is
  ordinary authorial framing, not chatbot correspondence.
- "you want the collection" / "you want the side effect" (Comprehensions
  Build, Loops Execute; Choosing a Form): "want" with the reader as
  subject is ordinary English, not the banned code-desire metaphor.
- "the question was never asked", the anatomy bullets' "input sequence",
  and the async-generator aside were all kept by the deep review's
  declined list; not re-examined.
- The emphasis italics in the *is*/*whether* pair and "Those clauses
  *do* read left to right" carry the minimal-pair contrasts those
  sentences exist to draw; left alone.
- "more direct(ly)" appears twice in Unpacking in Comprehensions (the
  section opener's "a more direct way to flatten" and "saying what it
  does more directly" after the listing). The echo restates the
  section's claim rather than cycling synonyms; varying one would be
  change for its own sake.
