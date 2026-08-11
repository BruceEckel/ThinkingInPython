When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the readability pass over `Chapters/34_Composite_and_Interpreter.md`.
The chapter is clean: it carries a recent deep review whose applied list
included a prose pass, sentence lengths vary,
and no Tier 1A vocabulary, curly quotes, spaced `--`,
or structural tells appear.
The decisions `deep_review/~34_Composite_and_Interpreter.md` recorded as
considered and declined (the "A Template Is a Tree" heading,
the bare "raises `KeyError`", the "Match over a closed set" close,
and the `simplify.py` inline comment) were checked and not re-raised,
and nothing in `readability_db.md` names this chapter.
No fix was applied directly and there are no live blocks;
the watch-list hits below were each examined and kept.

## Considered and declined

- **"Both alternatives bind `other`, and they have to:"**
  (Simplification section) has watch-family "have to".
  Kept: the clause it introduces already reads
  "every alternative in a `|` must bind the same set of names,"
  so swapping in "they must" would put "must ... must" in one sentence,
  and the current form is the spoken-rhythm beat before the rule.
- **"a pattern that never calls `Num`"** (same section).
  "Never" is on the avoid-if-possible list.
  Kept: the sentence exists to defuse what the syntax looks like,
  a constructor call, and the categorical "never" is the claim,
  that no call occurs on any match.
- **"these reflected methods trust their operand completely"**
  (Interpreter section) has an intensifier.
  Kept: "completely" draws the contrast with `Meters` in the same sentence,
  whose reflected methods check their operand and decline,
  and the following sentences depend on that totality
  ("at runtime nothing checks").
- **"The first one earns its place."** (A Template Is a Tree)
  is §39 self-labeling by shape.
  Kept: it is a five-word topic sentence marking that `to_query()`
  is not an arbitrary demo,
  and the injection evidence follows in the next sentence,
  so the content does the work the label announces.
- **"a paragraph below says why a `list` would not do"**
  (A Composite of Data Classes) is forward-pointing metadiscourse by shape.
  Kept: the deep review deliberately moved the immutability argument
  to the tuple-plus-`frozen` paragraph,
  and this half-line stops a reader from objecting at the field declaration
  before the argument arrives.
