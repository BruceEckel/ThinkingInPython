When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability review of
`Chapters/40_Functional_Foundations.md` in the clean-slate sweep.
The chapter reads as first-edition voice throughout:
varied sentence lengths, concrete claims tied to listings,
and no Tier 1A vocabulary, curly quotes, spaced ` -- `, boldface stacking,
or structural tells anywhere.
The entries in `readability_db.md` for this chapter
(the `match`-versus-table closing sentence and the two definition colons
in the dispatch section) were checked and left alone, as that file directs,
and the phrasings the deep review considered and declined
(the "Mutability alone is not what removes hashing" cleft,
the `itertools` sliding-window phrase,
"This way, a function can carry state without a class")
were not re-raised.
Everything found had one sensible answer,
so this file has no live blocks:
five small fixes were applied directly
and the judgment calls are recorded below as considered and declined.

## Applied directly

- Immutability, "so the value can serve as a dictionary key or a set
  member": "can serve as" is now "can be" (§8 copula avoidance; also
  matches "a value that must *be* a dictionary key" later in the same
  section).
- Higher-Order Functions, "produces nothing at all, with no error to
  point at": now "silently produces nothing" ("at all" fails the deletion
  test, and "to point at" strands a preposition whose object was fronted;
  "silently" keeps the no-error information). The cross-reference link
  moves to its own line unchanged.
- Same section, "without building the list at all": dropped "at all"
  (deletion test; second use in one section).
- Same section, "it has to see every element": now "it must see every
  element" (watch-list "has to").
- Closures, "When state has to exist": now "When state must exist"
  (watch-list "has to").

## Considered and declined

- Intro and close, the "payoff" motif: "The ideas pay off before the
  vocabulary arrives", "The payoff is trust", and "The second `print()`
  is the payoff". The last is §39 self-labeling by shape, but the
  sentence after it delivers the substance (the input list unchanged,
  so recompute, cache, or parallelize), and the three uses are the
  chapter's deliberate through-line: each section shows what purity buys.
  Left as written.
- First-Class Objects, "This is what *first-class* means." The "is what"
  rule's own carve-out: deleting the cleft breaks the sentence rather
  than tightening it. Same for "This is what a decorator does" in
  Higher-Order Functions. Both kept.
- Partial Application, "The keyword is doing real work here." §34
  real-inflation by shape, but the named contrast follows immediately:
  `partial(power, 2)` would bind `base` and compute `2 ** 5`. The
  adjective is earned. Kept.
- Closures, "give exactly one function the right to change it."
  "Exactly" is a precise numeric match (one function, not two or zero),
  which the global rule allows. Kept.
- Immutability, "Each is immutable in itself, and no deeper." "Itself"
  is load-bearing: the clause draws the shallow-versus-deep contrast the
  next line demonstrates with `([1], 2)`. Kept.
- Pure Functions, "It reads nothing else and changes nothing else." The
  global rule cites this construction as ordinary usage ("nothing else"
  as object). Kept.
- Close, "None of this is a different language. It is ordinary Python
  in which each piece depends on its arguments alone." Negative-parallel
  by shape, but it is a real contrast and a deliberate echo of the
  intro's "None of this asks you to abandon loops, classes, or
  mutation." Kept.
- The four uses of "already" (intro's "already correct on the edge
  case", Lambdas' "where the reader already is", Placeholder's
  "`partial()` already appends", the Part V pointer's "the mechanism
  Python already has"): each draws a real contrast (correct before you
  touch it, present before the lookup, existing behavior, no new
  mechanism). All kept.
