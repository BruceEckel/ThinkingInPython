When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/44_Effect_Management.md`, run after the
deep review (`deep_review/~44_Effect_Management.md`) was applied.
The chapter has no Tier 1 or Tier 2 vocabulary hits, no curly quotes,
no inline-header list abuse, and no boilerplate phrasing;
the spaced `--` in the Zen of Python quotation is quoted text under a
vale guard and was left alone, as were the ten verified AI-language
one-liners and every non-Python listing.
The findings below are watch-list placements and one watch-word verb.
No live blocks remain: every finding had one defensible answer.

## Applied directly

- Line 16, "only" placement: "Caching only works because the cached
  function is pure" is now "Caching works only because"; the "only"
  governs the reason, matching the deep review's "You get these benefits
  only if" fix.
- Line 58, empty adverb: "broader than just side effects" is now
  "broader than side effects"; the deletion test passes, and the "also"
  in the next sentence carries the extension.
- Line 191, "only" placement: "it only guards the exception `slope()`'s
  author expected" is now "it guards only the exception"; the "only"
  governs which exception, not the verb.
- Line 854, watch-word "happen": "Collisions often happened quietly,
  producing hidden bugs" is now "Collisions were often silent";
  same claim, without the generic verb.

## Considered and declined

- **"So why track them at all?" (Two Phases lead-in).** A §43
  rhetorical transition and an "at all" watch-list hit by shape.
  Kept: the question is earned by the paragraph before it, which argues
  Effects cannot be eliminated, so "why bother tracking" is the reader's
  own objection; the deep review edited this paragraph and named it by
  this phrase, so the line was seen and kept there too.
- **"It just hard-codes the machinery to a single Effect" (async
  paragraph).** "Just" survives the deletion test poorly on paper but
  carries the concession: the previous sentence grants that the
  machinery works, and "just" marks the one shortfall. Cutting it
  flattens the contrast.
- **"Could Python itself gain Effect tracking" (PEP paragraph).**
  "Itself" draws the real contrast between the language and the
  third-party libraries the preceding paragraphs covered.
- **"You could replace the function call with the crash itself"
  (bottom-value discussion).** "Itself" separates the call from the
  value it denotes, which is the referential-transparency point.
- **"It might change something in the world. It might read from an
  unreliable source. It might fail and take the system down." (Effects
  Are the Next Barrier).** Three parallel sentences, §10/§31 by shape.
  Kept: they map in order onto the chapter's three Effect kinds
  (side effect, side cause, exception), so the parallelism is the
  structure, not padding.
- **"The history of programming is a history of scaling barriers."**
  §32 aphorism by shape, but it is the section's thesis and the section
  spends its length supporting it with named cases (namespaces, version
  control, testing, garbage collection).
- **"The logic looks correct. The math checks out." (Effect Management
  Systems opening).** Two short near-parallel sentences; kept as the
  debugging-narrative rhythm, and they check different things
  (structure versus arithmetic).
- **The "even" escalations** ("or even the exit code the operating
  system checks"; "It can even invoke the continuation several times").
  Both mark a real step past what the reader expects; the second closes
  the once/discard/several-times ladder.
