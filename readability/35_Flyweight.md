When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/35_Flyweight.md` in the clean-slate sweep.
The chapter is clean:
no Tier 1A vocabulary, no curly quotes, no spaced `--`,
no signposting, no colon reveals, no generic conclusion,
and sentence rhythm varies well throughout.
The deep review's declined items
(the `==`-collapses-to-a-pointer-check sentence,
the compressed `int("...")` sentence,
the "Which Pool Should You Use?" heading, the section order)
and `readability_db.md`'s kept four-way `If X, do Y` parallelism
in the decision section were honored and not re-raised.
One repetition fix was applied directly; no finding needs a decision,
so this file has no live blocks.

## Applied directly

- Line 77, watch-list "only" repeated in adjacent sentences
  ("but only a handful of tile kinds" / "holds only grass, water, and rock"):
  the second sentence is now "Here, the handful is grass, water, and rock,"
  which drops the duplicate and ties the sentence to the handful claim.
  Close alternative: keep "the map holds" and drop only the word,
  but the restriction the word carried then leaks away.

## Considered and declined

- "is only safe when nobody can change it" (opening) and
  "can only hold one of them" (Typing the Symbol Set):
  both "only"s restrict genuinely, and the mid-verb placement is idiomatic;
  moving either to "safe only when" / "hold only one" is fussier, not clearer.
- The three "never"s
  ("the `Tile` object never stores it," "A cell's position never needs storing,"
  "`Color._pool` never shrinks") each state an invariant in one word;
  "does not store" and "does not shrink" weaken the across-all-uses claim
  the sentences exist to make.
- "trusts its argument is already a `Symbol`":
  "already" draws the temporal contrast with `to_symbol()`,
  the boundary where conversion happens upstream.
- "run again on an object that was already finished":
  "already" pairs with "again" to stress the re-run; deletion reads odd.
- "the two are worth combining once memory is the point":
  §53 flags the "worth X" family,
  but this one weighs an action against a stated purpose,
  which the rule's own carve-out ("worth the extra allocation") covers.
- "The customization must happen in `__new__()`":
  "happen" is on the watch list,
  but the sentence states a correctness requirement about timing,
  and every substitute ("occur," "belongs in") is no clearer,
  or shifts the claim from a requirement to a style preference.
- "which warns callers that something unusual is happening":
  second "happen" hit; construction is literally in progress at that point,
  and no substitute says it better.
- "so it keeps that exact name rather than something like `_symbol_`":
  "exact" earns its place;
  the metaclass matches the attribute name verbatim,
  so the precision contrast is the point.
- "for a perfectly interned type, equal values are the same object":
  "perfectly" distinguishes `Color`'s no-gap pool from `tile()`'s
  partial interning discussed in the next section; it is not a filler qualifier.
