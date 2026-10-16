> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/35_Patterns--Flyweight/README.md`,
2026-10-16.
The file carried no AI-vocabulary clusters, no chatbot artifacts, no
promotional language, and no watch-list words outside the recurring
keeps; its faults were "and"s joining clauses with different subjects,
one effect stated before its cause, one restatement, one tailing
negation, and one sentence whose "so" skipped a step the listing takes.
Seven fixes went in directly, and no finding needed Bruce's judgment, so
this file holds no live block and serves as the applied-directly record.
The capture claim in solution 4 was checked against `move()`
(`board[dst] = board.pop(src)`) before its rewrite.
`tip verify-ch CH=35 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 208, effect before cause and an "and" joining clauses with
  different subjects: "tracing runs straight through both builds, and
  the ratio comes out larger at every size. The unshared peak then
  counts the shared field ..." became "tracing runs straight through
  both builds. The unshared peak then counts the shared field, which is
  still alive, on top of its own, so the ratio comes out larger at every
  size."
- Line 284, restatement with a doubled connective: "The flyweight's
  saving is therefore per cell, so the bytes saved grow with the map"
  became "That difference repeats in every cell, so the bytes saved grow
  with the map."
- Line 571, "so" that skipped a step: "`board[dst] = ...` replaces the
  captured piece's reference at `dst` with the moving piece's reference,
  so a capture removes one entry from the board" became "`move()` pops
  the moving piece's reference from `src` and writes it over the
  captured piece's reference at `dst`, so a capture leaves the board one
  entry shorter." Replacing the reference at `dst` alone leaves the
  count unchanged; the `pop()` removes the entry.
- Line 682, "and" joining clauses with different subjects: "Python frees
  those `Color` objects, and the `WeakValueDictionary` drops their
  entries on its own" became two sentences, the second with "then".
- Line 1016, "and" standing for "but": "The lock orders the builds, and
  all four still run" became "The lock puts the builds in order, but all
  four still run."
- Line 1095, "and" joining clauses with different subjects after a
  serial "and": "calls the function, and stores the result, and no lock
  spans those steps" became two sentences.
- Line 1112, §9 tailing negation and a chained "and": "so every lookup
  hits, and each lookup is one `dict` index, with no lock to take"
  became "so every lookup hits. Each lookup is one `dict` index and
  takes no lock."

## Considered and declined

- Lines 339-345, solution 3's opening states that asserting on the
  assigned cell passes "whether or not the cells share a tile", shows
  it, then says the test "passes on code that shares nothing". A
  claim-evidence-restatement by shape, but the last clause is the
  conclusion the demonstration earns, and every merge tried needed
  "even" or a contrast word the logic does not support.
- Lines 676-678, "Like `weak_pool.py`'s `Name`, this `Color` writes the
  `dataclass` call in full, because ... `record()` forwards `slots=False`
  alone." It repeats the hint, but the hint sits in a separate fold, and
  within the Solution fold this is the only statement of why `record()`
  cannot supply `weakref_slot=True`.
- Lines 818-821, solution 6's "Validate before the pool lookup" step
  repeats the opening paragraph's "checks the components at the top of
  `__new__()`, before the lookup". The file's intro, listing, then steps
  structure restates the move in every solution; trimming one would
  break the pattern the other seven follow.
- Line 825, italic *parse, don't validate*. It names the principle
  chapter 12 introduces rather than emphasizing, the same contrastive
  italics the book uses for a named idea.
- Line 914, "The type checker still catches each `Literal`-version
  mistake that the enum leaves possible." Dense, but the exercise asks
  this question in these terms, and the sentence's restriction (only
  the mistakes still possible) is the claim.
- Line 1104, "Serializing every miss" repeating the previous sentence's
  "serializes every miss". The repetition names the noun the global
  antecedent rule asks for, in place of a "This".
- The bold step labels ("**Name each new kind in both tables.**") are
  §15 boldface by shape, but they are the file's step convention across
  all eight solutions, not emphasis.
