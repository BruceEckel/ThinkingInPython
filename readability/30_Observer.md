When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/30_Observer.md`.
`readability_db.md` binds three items here, all honored:
"It is simply a callable." stays,
"amounts to nothing more than a list of callbacks" stays
(the global rule's own carve-out example),
and "a lambda equals only itself" was not touched.
The deep review (`deep_review/~30_Observer.md`) ran earlier in this sweep
and its style audit removed the watch-word hits this pass hunts
("happen", "raised" without an exception, a doubly negated "never"),
so the prose comes to this pass close to clean.
The mechanical sweep found no curly quotes, no spaced ` -- `,
no Tier 1A vocabulary, and no structural tells:
the opening two-bullet list and "Four things from the classic version
disappear: ..." are genuine lists;
the colons are labels or definitions ("One limitation: ...",
"Two-way bindings are the usual source: ..."), not §69 reveals;
"The `list()` copy inside `notify()` looks redundant. It is not."
is a single emphatic beat, not §31 staccato;
sentence lengths vary well
("values in, values out." against the long mechanism sentences).
Two direct fixes; no live blocks.

## Applied directly

- Line 10, watch-list "never": the opening bullet
  "The observable never needs to know their types" is now
  "The observable need not know their types".
  "need not" says the same in fewer words and matches the Pythonic
  section's own "need not be" pair.
  Close alternative: "does not need to know", longer for no gain.
- Line 22, watch-list "has to" family:
  "without the data having to know which views exist" is now
  "without the data knowing which views exist".
  The deletion test passes; the obligation reading adds nothing
  the shorter form lacks.

## Considered and declined

- "detaching an observer that never subscribed raises `ValueError`":
  watch-list "never", but it earns its place.
  "that never subscribed" means at no point subscribed,
  and the blur alternatives ("that is not subscribed") would cover
  an observer that subscribed and detached,
  a different case the same sentence goes on to discuss. Kept.
- "or subscribes a bound method whose instance already holds the
  reference": "already" draws the real contrast with the payload
  route in the same sentence (the reference is in hand, nothing
  extra gets passed). Kept, matching the 33_Visitor precedent.
- "so the next observer is silently skipped, and nothing signals the
  loss": §13 passive, advisory here. The passive keeps the skipped
  observer as the subject, which is where the paragraph's attention
  sits; an active rewrite ("the loop silently skips ...") shifts
  focus to the loop for no gain. Kept.
- "The list of callbacks becomes a line of waits": §32 "X becomes Y"
  by shape, but the claim is the concrete mechanism (sequential
  blocking), stated compactly, and it is chapter voice. Kept.
- "the checker reject a plain function as an observer": "plain" draws
  the real contrast with an `async` function, the carve-out the
  global rule names. Kept.
- "For event-heavy programs there are mature libraries": expletive
  construction by shape, but the sentence is a natural existence
  claim and the rewrites read worse; the activate pass owns this
  category. Kept.
- "the observers are I/O-bound" (predicate position): §26 would drop
  the hyphen after the noun, but "I/O-bound" is a term of art the
  Concurrency chapter also hyphenates, and consistency wins. Kept.
- The deep review's own declined items (the lowercase "a" after the
  heading colon, the repeated `*Observer*` italics, the roadmap
  paragraph) were not re-examined; its decisions stand.
