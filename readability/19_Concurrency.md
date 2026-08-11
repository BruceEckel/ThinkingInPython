When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/19_Concurrency.md` in the clean-slate
sweep. The chapter is clean of the strong AI tells: no Tier 1A vocabulary,
no curly quotes, no spaced `--`, no boldface stacking, no rule-of-three
padding, and its rhythm varies the way reviewed human prose does.
The findings were watch-list mechanics (stranded prepositions, a cleft,
two `worth` frames, one `never`), all settled rules, so every one was
applied directly. No live blocks.

## Applied directly

- Line 227, cleft ("is what"): "which is what the `started` lines in the
  trace record" is now "which the trace's `started` lines record".
  The rewrite also removes a garden path: "the trace record" read as a
  noun phrase.
- Line 682, stranded preposition: "which trace to log under" is now
  "which trace to use for logging". Fronting ("under which trace to log")
  read stiffer.
- Line 732, stranded preposition: "That is the case a `ContextVar` is
  for" is now "That is the problem a `ContextVar` solves".
- Line 774, stranded preposition: "still knows which request it belongs
  to" is now "still knows which request it is serving", mirroring "which
  request the code is serving" at the section's opening.
- Line 952, watch-list "never": "process startup delays never leak into a
  timed result" is now "cannot leak". The warmup runs before any timing
  starts, so the impossibility is structural, and "cannot" states it.
- Line 1556, §53 worth-frame: "The pairing is worth keeping straight:" is
  now the instruction "Keep the pairing straight:", which the rule's
  carve-out allows.
- Lines 1796-1797, stranded prepositions (the global rule's own example
  shape, "what it is for"): "Free threading changes what a thread is for.
  It does not change what `asyncio` is for." is now "Free threading
  changes a thread's job. It does not change `asyncio`'s.", echoing
  "A thread's remaining job" earlier in the same section.
- Line 1978, §53 "worth knowing": "with one difference worth knowing" is
  now "with one difference"; the next sentence states the difference.

## Considered and declined

- **"which is what you want" (twice: `tg.cancel()` at line 422, and the
  cancellation guideline).** Both are the reader-addressed "want" the
  global rule carves out (the `31_State_Machines` precedent in
  `readability_db.md`), and deleting "is what" leaves "which you want
  when...", grammatical but stilted. Spoken rhythm; both stay.
- **"What happens if `gather()` encounters a failure?" opening the
  `TaskGroup` section.** §43 by shape, but it is a genuine framing
  question answered concretely in the next sentence, and the chapter's
  only one. Textbook register, not a stalling transition.
- **"Context switching between threads is as efficient as possible, but
  it still has overhead."** Already examined and kept by the deep review;
  not re-raised.
- **Predicate "thread-safe" ("the class is not thread-safe", "An iterator
  has never been thread-safe").** §26 would drop the hyphen in predicate
  position, but "thread-safe" is a term of art hyphenated everywhere in
  the Python docs, predicate included. Register note covers it.
- **"is not decoration" appearing twice** (the `except*` and the
  `__main__` guard). A deliberate echo across the chapter's two
  looks-optional-but-isn't moments, not synonym cycling or a tic.
- **"`while not tasks.empty()` is trustworthy here"** brushes §35
  (a moral adjective on code), but the idiom means "its answer can be
  trusted", standard in concurrency writing, and the sentence immediately
  says why. Left alone.
- **"genuinely" three times** (subinterpreters overlap, the two
  convergence points, free-threaded parallelism). Each draws a named
  contrast with an apparent-but-false version the chapter just showed,
  which is §34's carve-out. Density is low for a chapter this size.
- **"happen" family** (lines 4, 98, 185, 629, and others). All ordinary
  uses; line 4's "happen 'at the same time'" quotes the definition the
  chapter then interrogates. Swapping in "occur" would be change for its
  own sake.
- **"Libraries worth exploring:"** (footnote). §53 by shape, but it
  captions a list in which every entry says what the library is, and it
  instructs the reader. First-edition voice.
