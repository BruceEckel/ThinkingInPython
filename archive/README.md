# archive

Finished working documents, kept for the record and out of the way.

Nothing here is read by the build. `make verify`, `gate`, and every tool
under `tools/` scan `Chapters/`, `Solutions/`, and their generated trees,
so a file moved here stops being a distraction in the root listing
without any risk of breaking a target.

A review file arrives with a leading `~`, the same completion marker the
`deep-review` skill uses, so the name says the work landed.

What lives here is a record, not a queue. When a document still has open
items in it, it belongs in the root where it will be seen. The
distillates that later rounds must still read (`deep_review_db.md`,
`readability_db.md`, `bruce_edit_db.md`) therefore stay at the root, and
so does `WhatsNew_Candidates.md`, which is a worklist nobody has worked
through yet.

## Contents

- `~correctness_review.md` — the decision queue from the 2026-09-02
  whole-book correctness sweep. All ten blocks applied in `e4a4e6cd`.
  Its "Applied directly" section is the record of the 56 errors that
  sweep fixed, grouped by error shape, and a later review should read it
  before re-proposing anything in that list. The sweep's own commits are
  `7583395d` through `e2e5ba75`.
- `~adversarial_undecided.md` — the author-level queue from the
  2026-09-03 adversarial review. 37 of 38 calls were performed that day;
  the last (a chapter 01 AI anecdote) was declined on 2026-09-29 and is a
  standing rejection in `deep_review_db.md`.
- `~RECOMMENDATIONS.md` — the "what to work on next" list as of
  2026-09-03. Archived 2026-09-29, when every item in it was settled; its
  two GoF attributions were checked against the GoF text and hold.
