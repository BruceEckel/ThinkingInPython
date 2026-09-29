When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Second deep review of chapter 43, run 2026-09-29 as part of the sweep
decision to re-review the nine chapters the first sweep skipped.
It carries forward `~43_Functional--Confidence.md`, which had no
rejections, and `deep_review_db.md`.
The 2026-09-27 triage cut one clause from this chapter ("and what this
chapter explores"); the paragraph after it still bridges to the chapter's
question, so nothing needed restoring.
Every listing ran and matched its markers, `parallel_pure.py` included
(serial 2.55 s, parallel 1.27 s under `--numbers`), and the `ty` 0.0.84
claims in Solutions exercise 7 were re-probed against the rewritten
listing: `float` in the `Ok` branch with `@final`, `float | Unknown`
without it, `ValueError` in the first error branch either way.
The pickling claim was probed on 3.15: a `lambda` and a closure each
fail in `pool.map()` with `_pickle.PicklingError`.

No finding needed a decision only you can make, so this file has no live
blocks.

## Applied directly

- Solutions exercise 1 solved the listing as it stood before commit
  97803bca raised the limits from `[10_000, ...]` to
  `[200_000, ...]`. At the chapter's limits the counts are
  `[17984, 33860, 49098, 63951]` and three runs on a 32-core machine
  report 4 distinct IDs every time, not 2 or 3. The solution now uses
  the chapter's limits, explains the 4, and keeps the small-limit
  measurement (3, 3, 3, re-measured today) as the case where a worker
  takes a second task before the last worker starts.
- Solutions exercise 7 rewrote a `describe(text)` that no longer
  exists. Chapter 42's `describe()` takes `(text, result)`. The
  solution's `describe()` now has that signature, its helper is named
  `compute()` as in chapter 42, and the line-count paragraph says what
  the count shows (two lines fewer: no `match result:` line, and one
  `return` in place of `case Err(error):` and its body). The claim
  "the two listings come out the same length" is gone; the listings
  differ in everything but `describe()`. The local `@final` records
  stay, since the `tool-upgrade` probe strips them from this listing.
- Solutions exercise 5: the copy of `group_rounds()` predated the
  chapter's `met()` helper and its "Too few left" comment. It now
  matches `student_pairs.py`, and so does the "delete this loop"
  snippet.
- Solutions exercise 3: idempotence "catches a sort that shuffles
  equal elements on the second pass" was false for `list[int]`, where
  equal elements cannot be told apart. Replaced by a sort that drops
  its last element, which the invariant passes and idempotence fails
  on every list of two or more.
- Solutions exercise 4: six runs with the database off shrank to
  `'µ'` four times and `'ß'` twice. The solution now says so, and
  says that the example database makes later runs replay the stored
  character. Exercise 4 in the chapter now tells the reader to delete
  `.hypothesis/` between runs, since otherwise "run the test a few
  times to see which characters" replays one character.
- Solutions exercise 4: "even `casefold()` promises no
  reversibility" used "promise" as a metaphor, and "One rule survives"
  named no rule. Now "For case-insensitive comparison Python provides
  `str.casefold()` rather than `str.lower()`, and `casefold()` cannot
  be reversed either."
- Solutions exercise 5: "The chapter carries the fix now" narrated
  history; now "The chapter's `group_rounds()` includes the guard".
  Cut "and the distinction is worth drawing".
- Solutions exercise 1: cut "genuinely" and "exactly" from the
  paragraph they intensified.
- Automatic Parallelism: `report()` was used with no word on where it
  comes from or why the listing's sample run shows no times. One
  sentence now links chapter 18's Numbers on Your Machine and says it
  prints only under `--numbers`.
- Automatic Parallelism: "if you shrink the limits back down" read as
  if the limits had once been smaller in the listing. Now "far enough".
- Referential Transparency: "Substitute the list for either call and
  `cart` ends with..." is an imperative-plus-consequence sentence; now
  "If you substitute...".
- Spectrum, rung 3: "holds exactly as far as" became "holds only as
  far as".
- Spectrum, rung 5: "dependently-typed" lost its hyphen, which an
  "-ly" adverb does not take.
- Hypothesis section: "shrinks that input to the smallest example ...
  so Hypothesis reports the bug as the smallest case" said "smallest"
  twice; now "so the report shows the simplest failing case rather
  than whichever random one failed first."

## Considered and declined

- `parallel_pure.py` still records its output in `# Sample run:`
  comments; the first review's reasoning holds.
- "Style contributes before the first rung" stays, as the first review
  decided.
- Solutions exercise 1 prints the number of distinct IDs rather than
  the IDs the exercise says to print. The analysis is about the count,
  and the IDs themselves differ on every run, so the count is the
  useful thing to print.
