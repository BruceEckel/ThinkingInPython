# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-08-30, from a survey of the repo state:
clean tree, tools upgraded 2026-08-29, `make rewrite` run on 26-28,
`bruce_edit_db.md` at 9 rules and 1 candidate, `deep_review/` fully applied.

## The recommendations

1. **Tighten the capture loop before bulk-rewriting.**
   After each hand-edited chapter, run `/bruce-edit-capture` before rewriting
   the next range. Every rule promoted early applies to every chapter still
   ahead of the cursor. This is the highest-leverage move for "fewest
   hand-edits": chapter 25's capture yielded eight rules, and C1 needs only
   one more sighting to promote.

2. **Run `make rewrite` a few ranges ahead of the hand-editing cursor**,
   not the whole book at once. The pass is moving sequentially (25→28), so
   `CH=29-33` next, vet the diff, hand-edit, capture, then the next range.
   A whole-book run now would apply today's rule set to chapter 47; the
   staged version applies a richer rule set the further out it goes.
   Chapters 1-24 get a bulk run last, with the mature DB.

4. **Do the book-altitude consistency pass.**
   Nothing currently reviews above chapter level, and the known failure
   modes live exactly there: cross-chapter terminology drift, "previous
   chapter" phrases broken by splits, concepts explained twice or assumed
   before taught. Best done *before* the hand-editing pass, since its fixes
   can restructure prose that would otherwise get hand-polished twice.

5. **Adversarial review, results to `ADVERSARIAL.md`.**
   Same timing argument as the consistency pass: structural findings should
   land before hand-polish, not after.

6. **Fresh-reader exercise pass.**
   A session attempts each exercise cold, using only the chapter, and diffs
   its experience against Solutions. Catches Solutions drift, which no gate
   covers.

7. **Defer the whole-book readability sweep to last.**
   Every rewrite and review round adds new prose, and new prose is where AI
   tells appear. One sweep after chapter-level work settles mops it all up;
   running it earlier audits text that will change.

## Suggested sequence

2. Items 4 and 5 (structural, before polish).
3. The item 1/2 loop through the remaining chapters.
4. Item 6 (exercise pass).
5. Item 7 (readability sweep).
6. One green `make sweep`.
7. The hand-editing pass.

Items 4, 5, and 6 are each a single Claude session, runnable on request.
