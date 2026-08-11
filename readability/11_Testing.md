When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/11_Testing.md`,
run after the deep review in `deep_review/~11_Testing.md` was applied.
That review had removed most of the mechanical watch-list hits
("is what", "ever", "at all", "land", the doubled "seem"),
so this pass found only residues, and all of them cleared the
direct-application bar.
No finding needed your judgment, so there are no live blocks.

## Applied directly

- Random Numbers intro: "a different value each run,
  which a test cannot assert against" ended on a stranded preposition;
  now "so a test cannot assert a fixed result".
- Sharing Fixtures section: "leave anything a test writes to at the default
  per-test scope" also stranded its preposition;
  now "anything a test mutates", echoing "one test that mutates it"
  three lines up.
  Close alternative: "modifies", which would mirror
  "values nothing modifies" in the same sentence.
- Clock section: "only it says in its signature where the time comes from"
  now ends "where it gets the time" (stranded preposition).
- Network section: "needs no patching library at all" dropped "at all";
  the sentence means the same without it.

## Considered and declined

- "One of the most valuable habits in modern programming is unit testing."
  "Valuable" sits on the AI-frequency list and the superlative is
  unsupported, but this is the chapter's opening stance sentence,
  first-edition voice, and no other tells cluster near it.
  It matches the kept "Factory might be the most common design pattern"
  precedent in `readability_db.md`.
- "Perhaps more importantly," (safety-net paragraph).
  "Importantly" is a calibration adverb and "perhaps" hedges it,
  but the phrase carries a real ranking claim over the two benefits
  named in the paragraph before it, and it appears once in the chapter.
- "That said, TDD requires that you know what you are creating."
  A watched transition opener, but it marks a genuine turn from
  TDD's benefits to its limits, and transition words count only
  when piled up.
- The two "actually"s in the name-mangling section
  ("disagrees with what actually runs", "shows what actually got stored").
  Both draw the static-report-versus-runtime contrast the section exists
  to teach, so each earns its place despite the proximity.
- "The `Account` tests are black-box" keeps its predicate-position hyphen.
  The hyphen-drop rule for predicates yields to a term of art the chapter
  defines as "*black-box* test" a few lines earlier.
- "The `4` here is simply what `Random(0)` produces first."
  "Simply" is an empty adverb by the deletion test, but it supplies the
  deflating beat (do not read meaning into the 4), the same call as the
  kept "It is simply a callable" in `readability_db.md`.
  The "is what" is the keep-case: "what `Random(0)` produces first"
  is a noun clause that cannot attach without it.
- "goes looking for the clock" / "going looking for it" /
  "goes looking for something it was never handed".
  Three uses across the chapter are a deliberate motif
  (receiving a dependency versus fetching it), not synonym cycling,
  and the conclusion's echo of the opening is the chapter's frame.
- "states what it needs and nothing about how to build it."
  Not the trailing "and nothing else" tag: the "nothing" names the
  exclusion that is the point (declarative over constructive),
  so it survives the deletion test's carve-out.
