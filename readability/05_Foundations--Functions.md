> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/05_Foundations--Functions.md`, 2026-10-16.
The chapter carries almost no AI-writing tells:
no Tier 1A vocabulary, no signposting, no manufactured punchlines,
and its watch-list hits are contrastive or reflexive uses the carry-forward keeps.
Four small edits were applied directly,
and nothing needed Bruce's judgment,
so this file holds no live block and serves as the applied-directly record.

## Applied directly

- Line 57, repeated subject: "Python is dynamically typed, so Python reports" -> "so it reports".
- Lines 440-441, staccato run (§31) of four short sentences:
  "`trace()` has the standard shape of a wrapper. It accepts any call and forwards it." ->
  one sentence joined by a colon (a restatement of what the shape is);
  "`expect()` has the same shape." stays its own sentence.
- Line 473, "and" joining clauses with different subjects:
  "`opts` carries a `"label"` key, and `trace()` forwards it as `label=`" ->
  "`opts` carries a `"label"` key, which `trace()` forwards as `label=`".
- Lines 538-539, two colons in one sentence (the list colon, then the listing colon):
  the closing colon before `all_markers.py` became a period.

## Considered and declined

- Line 197, "The default looks like an expression each call evaluates, but Python evaluates it once, at the `def`."
  Restates the section's opening sentence (§70 treadmill by shape).
  Kept, because it names the misreading that makes this a trap, which the opening sentence does not.
- Lines 270, 304, 306, three uses of "real" (`target`, `get()`, default) within a screen (§34).
  Each names its contrast, the sentinel or the demo's `return MISSING`,
  so the carry-forward's named-contrast keep covers all three;
  varying one would be synonym cycling (§11).
- Line 477, "`trace()` never reads the signature of the function it calls."
  A watch-list absolute that states the guarantee the clash depends on; kept.
- Line 126, "A call that names its arguments documents itself." Reflexive "itself"; kept.
- Lines 272-273, "for this purpose" after the `sentinel` built-in.
  Deletion leaves the meaning, but the phrase ties the built-in to the need the previous sentence states; too small to churn.
- Lines 478-479, "first appears" then "prints first" in adjacent sentences.
  Different senses (not before that call; ahead of the error), and the second sentence follows from the first; kept.
- Lines 600-602, the lambda single-expression rule restates line 574's definition.
  Kept, because it adds the contrast with other languages and the advice to write a `def`.
