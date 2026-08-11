When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability review of
`Chapters/41_Functional_Toolkits.md` in the clean-slate sweep.
The chapter is a catalog plus a case study,
and both halves read as first-edition voice:
short entries with concrete claims tied to output,
varied sentence lengths,
and no Tier 1A vocabulary, curly quotes, spaced ` -- `, boldface stacking,
or structural tells anywhere.
The deep review's declined items
(the `reduce` addition example, the twin "already ... already" intros,
`groupby`'s "only merges neighbors", the 1-factorization gloss,
and the `permutations` `r` phrasing)
were honored and not re-raised,
and nothing in `readability_db.md` names this chapter.
Everything found had one sensible answer,
so this file has no live blocks:
six small fixes were applied directly
and the judgment calls are recorded below as considered and declined.

## Applied directly

- `lru_cache`, "that miss is the proof that the eviction happened":
  now "that miss is the proof that `1` was evicted"
  (watch-list "happen"; also names the specific victim
  the comment in the listing points at).
- `itertools` intro, "the property [Lazy Evaluation] returns to below":
  now "revisits below"
  (the fronted object left "returns to" dangling before a bare adverb;
  a transitive verb needs no preposition).
- `groupby`, "The input must arrive already sorted by that key":
  dropped "already" (watch list; "arrive sorted" says it).
- Recursion, "will raise `RecursionError`":
  now "will raise a `RecursionError`"
  (house rule's article form; matches "raises a `ValueError`"
  in the case study).
- Case study, "caching only works for pure functions":
  now "works only for pure functions"
  (modifier placement; matches the `cache` entry's own
  "works correctly only for pure functions").
- Case study, "means having already generated rounds `0` through `99`":
  dropped "already" (watch list; the perfect participle carries it).

## Considered and declined

- `zip_longest`, the three-way "which is right when ..." parallelism
  (plain `zip()`, `strict=True`, `zip_longest()`).
  Rule-of-three by shape, but it is a decision table written as prose,
  the same form `readability_db.md` records as kept
  for 35_Flyweight's pool chooser, and the parallelism is what makes
  the three meanings of a length mismatch scannable. Left as written.
- Intro, "`functools` operates on functions themselves."
  "Themselves" is on the watch list, but it draws the real contrast
  the sentence exists for: the functions are the operands,
  not the things doing the work,
  against `itertools` assembling iterators in the next line. Kept.
- Case study, "so there is no group to fold the leftovers into".
  The preposition's object is fronted, but the clause is mid-sentence
  (the global rule governs sentence endings),
  and "fold into" deliberately echoes
  "folds the leftover player into an existing pair"
  two paragraphs earlier. Kept.
- Pipeline, "`takewhile()` had to pull the batch `(169, 196, 225)`
  and discard it". Watch-list "has to", but the necessity is the claim:
  the next sentence generalizes it as
  "a pull-based pipeline reads one value further than it keeps". Kept.
- `total_ordering`, "the ordering is not simply the fields in
  declaration order". "Simply" here means "merely", not an empty adverb:
  deleting it loses the nuance that the ordering may still use the
  fields, differently arranged. Kept.
- Conclusion, "ask whether the loop already has a name."
  "Already" draws the real contrast: the name exists before you
  write the loop. Kept.
- Case study intro, "This is a good place to see several of these ideas
  working on one small program". Signposting by shape,
  but the colon that follows maps four named tools onto the problem,
  so the sentence delivers content rather than announcing it. Kept.
- Recursion, "Its payoff shows up once the problem branches,
  not just repeats, as the next example shows."
  "Shows" twice in one sentence; synonym-cycling the second
  ("demonstrates") would be the AI tell, not the fix. Kept.
