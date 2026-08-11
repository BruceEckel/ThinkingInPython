When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/25_Template_Method.md`.
`readability_db.md` carries nothing binding for this chapter.
The deep review (`deep_review/~25_Template_Method.md`) settled several
watch-list hits, all honored here without re-flagging:
the term *hook* (standard name, GoF and `unittest`'s own docstrings),
the "Actually" in the conclusion heading (contrastive),
"never call that sequence yourself" (carries the inversion-of-control point),
"shown four of them," and "the steps it cares about."
The chapter is clean of curly quotes, spaced ` -- `, Tier 1A vocabulary,
and structural tells; sentence lengths vary well.
One direct fix; no live blocks.

## Applied directly

- Line 133, watch-list "happen": "shows what happens when a framework
  does not" is now "shows what goes wrong when a framework does not."
  The listing demonstrates a failure (`AttributeError`), so the more
  specific verb is available and accurate.

## Considered and declined

- Intro, "At the heart of a framework is the *Template Method*."
  Phrase-shaped like §4's "in the heart of," but this is a literal
  structural claim, the chapter's definition sentence, and the fronting
  puts the new term at the end where the colon expands it. Left alone.
- "`Greeter("Bruce")` never gets to greet." "Never" is on the
  avoid-if-possible list, but the sentence's charm is the Greeter/greet
  wordplay and the finality "never" gives it; "does not get to greet"
  flattens the beat that opens the post-listing explanation. Voice, kept.
- "a faithful substitute" (Substitutability section and conclusion).
  §35-shaped (a moral adjective on code), but "faithful" here is the
  conventional idiom of faithful translation or reproduction, meaning
  behavior-preserving, and the conclusion's use deliberately echoes the
  section that defines it. Both kept.
- Conclusion, the four-way anaphora "Structure fixes it... A checker
  fixes it... The interpreter fixes it... Discipline fixes the rest."
  Uniform sentence shape by the structure test, but the parallelism is
  the section's organizing scheme (four mechanisms answered by one
  question), matching the precedent `readability_db.md` records for
  35_Flyweight's decision-table prose. Kept.
- "The guarantee is real, but it is the checker's guarantee." §34
  real/actual inflation by shape, but the named-contrast carve-out
  applies: the sentence contrasts a real guarantee with where it comes
  from, and the restriction lands in the second half. Kept.
- Exercise uses of "never" ("who has never read this chapter," "an
  exception the base never raises"): the first is natural direct
  address, the second is a precise behavioral claim that "does not
  raise" would weaken. Both kept.
