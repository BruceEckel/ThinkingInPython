> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over Appendix B, run 2026-10-16 against `readability_db.md`
(no earlier review of this appendix exists).
The appendix had already been through the straighten, terminology, and
metadiscourse passes, so the AI-writing tells were few: no Tier 1A vocabulary,
no curly quotes, no spaced ` -- `, and the watch-list hits that remain are
keeps under the database's recurring judgments.
Five edits were applied directly; this file holds no live block and serves as
the record of those edits and of what was considered and left alone.

## Applied directly

- L9, and-join with a new subject: "It is about 450 lines, and most of its
  pieces come from earlier chapters:" -> "It is about 450 lines." / "Most of
  its pieces come from earlier chapters:" (the colon now delivers its list
  from a lead-in with one claim).
- L39, Semantic Line Breaks: two sentences sat on one source line, and
  `tip reflow` rejoined them because it reads "Appendix A." as an initial.
  "as `Ask` and `Tell` are in Appendix A. These eight..." -> "as Appendix A's
  `Ask` and `Tell` are." / "These eight..." so the sentence ends on a word
  reflow treats as a sentence end.
- L409, and-join hiding a contrast: "Both descriptions are accurate, and [The
  Check] shows the checker reporting each." -> two sentences ("but" fit where
  the "and" sat: accurate, yet both get reported).
- L1049, §70 restatement: cut "The demo prints each nonempty row, then each
  finding.", which repeated the description of `lines()` six lines above the
  listing.
- L1050, two-candidate pointer: "The checker infers `['Tell']` from the call
  to `tell()`." followed a sentence naming both `shout()` and `quiet()`, and
  the marker shows a row for `shout()` alone -> "infers `['Tell']` for
  `shout()` from its call to `tell()`."

## Considered and declined

- L21, "With that rule the tool stays small, and every unresolved call shows
  in a row." Two subjects, but "With that rule" governs both clauses as
  parallel consequences, so the "and" is additive.
- L148, "The checker reads source, and in source the name is `os.remove`."
  No "but", "so", or "whereas" fits the join; the repeated "source" is
  rhythm.
- L485, "`Row | None` is an ordinary optional." "Ordinary" contrasts with the
  sentinel and assert-guarded forms the book steers away from.
- L632, "a plain assignment": the contrast is with the annotated assignment
  named in the same list (recurring keep for "plain").
- L813, "The standard answer is to start every row empty": names the
  standard fixed-point iteration, not an endorsement.
- L1235, "Here a tool verifies it." A short beat after a long sentence, not a
  staccato run.
- L1239, "appearing in a class from this book": the participle carries the
  fact that the callback problem turns up in the book's own `Result`, not
  §3 decoration.
- L1259, "Here, in one place, is what the checker resolves:" A mild
  signpost, but it tells the reader the list gathers rules spread across
  three earlier sections, and the cleft's complement is a clause ("is what"
  keep).
- L1326-1328, "The limits in this second list are silent. They produce no
  `Unknown`." Three short sentences in a row, but each does work: the label,
  the definition of "silent", and the obligation that introduces the list.
- L1369, the closing sentence: concrete (it points back at `check_files.py`
  verifying the pure core), so not a §32 kicker.
- The four "Here," openers that introduce a listing (L193, L1181, L1259,
  L1293): an established pointer to the listing that follows, spaced far
  apart.
