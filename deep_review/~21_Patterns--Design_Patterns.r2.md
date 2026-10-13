> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 21_Patterns--Design_Patterns (2026-10-13)

This is the second deep review, after `~21_Patterns--Design_Patterns.md` (2026-09-29) and two outside reviews whose verdicts are in `outside_review/`.
I read both, plus `deep_review_db.md`, and re-proposed nothing they settled.
I checked the taxonomy paragraph against GoF's "Organizing the Catalog" in `C:\git\DesignPatternsCD\markdown\`, each cross-chapter link against the section it names (chapter 20's `#guidelines` and `#protocols`, chapter 27's dictionary, self-registration, *Prototype*, and *Builder* sections, chapter 46's `Need`), the "each pattern chapter from *Iterator* through *Memento* includes a figure" claim against chapters 23 to 36, and the four coupling figures' labels and edges against the prose that walks them.
I re-probed the Solutions claim that `ty` reports `invalid-return-type` when `Report.render()` misses a `case`: on `ty` 0.0.86 and Python 3.15.0 it does, at the `-> str`.
`tip verify-ch CH=21 ISOLATED=1` passed 27 of 27 before and after, and `tip prose CH=21` reports nothing new.
There are no live blocks.

## Applied directly

Chapter:

- Opening: "One listing makes the point" left the reader asking which point. Now "Its one listing shows a pattern shrinking to a function."
- "Pattern Taxonomy": "three purposes, each named for the aspect that can vary" credited GoF with a rationale it does not give; GoF says purpose "reflects what a pattern does". Now "each named for what its patterns do."
- "What One Part Knows About Another": "The question is not whether ..., since ..., but how much" held its subject open across a negated clause and a reason. Now two positive clauses: every working program has dependent parts, so the question is how far a dependence reaches.
- "*Factory Method* does not remove the heavy edge either" became "keeps a heavy edge too", the positive form.
- "The Reach of a Change": the figure draws `MdWriter` as a dashed box that the prose never explained, and "the red edges are the ones the change adds" was inexact, since the new dashed satisfies-edge on the right is not red. Now the dashed box is named as the new class, and each red edge is "a new place that names `MdWriter`", which matches both panels.
- "A design's coupling is its heavy edges" contradicted the section's own *abstract coupling*, where a thin edge is coupling too. Now "A change travels along a design's heavy edges", which matches "Read the heavy edges first, because they are where a change reaches."
- "The Edge Python Deletes": "a caller that needs an `area()` from whatever it receives" did not match the figure, where the caller is a function named `area()` and the `Callable` panel has no `area()` method. Now "a caller, a function `area()` that needs the area of whatever it receives."
- Orthogonality bullet: *Coupling* was italicized as a new term, but the Coupling section defines it from GoF's glossary first. Dropped the italics; *Cohesion*, new here, keeps them.

Solutions:

- Opening: "Each solution works a single example through instead" covered exercise 4, which the paragraph then says has a checkable answer. Now "Each of those solutions".
- Solution 4: "The alias and `render()` both belong to `Report`" was off, since `main()` annotates with `AnyWriter` too. Now `render()` belongs to `Report` and the alias lists the writers `Report` accepts.
- Solution 4: "Here `MdWriter` edits one existing thing" made the class the editor. Now "adding `MdWriter`".
- Solution 4: "The `match` in `main()` is the heavy edge that remains" called a statement an edge. Now the `match` names every writer class, so its heavy edges remain, and a registry moves them.

## Considered and declined

- "What an Abstraction Erases" says a good abstraction "does more than hide" details, and the next paragraph says "Every abstraction hides some work." The two senses differ (the information a caller cannot recover, the work a caller cannot see), and the earlier review chose "hides" over "discards" for the second. Left.
- "*Visitor* is the reverse of the others" is loose, but the next three sentences say what is reversed. Left.
- Solution 4 opens with the missed-`case` trap before the listing it describes. The contrast-paragraph-first shape is the Solutions convention from commit 85f6ce4d. Left.
- No `#:` marker, listing, or figure changed.

## For the session

- Figure, `resources/images/coupling_reach.svg` (hand-authored): a red outline means opposite things in neighboring figures.
  In `coupling_gallery.svg` the red box is the part that "does not change" (its legend), and in `coupling_reach.svg` the red-outlined, shaded boxes are the parts whose source does change.
  A reader who learned the gallery's legend two paragraphs earlier reads the reach figure backward.
  The fix is in the figure: shade the changed parts without the red outline, or use another tint.
  I did not edit it, per the sweep's figure rule.
- `tip prose CH=21` runs `internal_names` over the whole book and reports "1 stale" baseline entry. My edits changed no code, so the stale entry comes from another chapter.
