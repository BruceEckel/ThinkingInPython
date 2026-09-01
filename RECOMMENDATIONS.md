# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-08-30, after applying the consistency review:
all 39 `CONSISTENCY.md` recommendations are applied and verified
(`make verify` green); that file now records the outcomes.

## Chapter Edit Steps

1. Do an adversarial review of chapter 27. Fix everything you can, only present unresolved issues here on the console.
2. `make rewrite` on that chapter
3. Hand-edit the chapter
4. Run `/bruce-edit-capture` on the chapter

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

3. **Adversarial review, results to `ADVERSARIAL.md`.**
   Structural findings should land before hand-polish, not after. The
   consistency pass covered coherence between chapters; this one asks what
   doesn't work, what isn't correct, and what could be better.

4. **Fresh-reader exercise pass.**
   A session attempts each exercise cold, using only the chapter, and diffs
   its experience against Solutions. Catches Solutions drift, which no gate
   covers.

5. **Defer the whole-book readability sweep to last.**
   Every rewrite and review round adds new prose, and new prose is where AI
   tells appear. One sweep after chapter-level work settles mops it all up;
   running it earlier audits text that will change.

## Suggested sequence

1. Item 3 (adversarial review, structural, before polish).
2. The item 1/2 loop through the remaining chapters.
3. Item 4 (exercise pass).
4. Item 5 (readability sweep).
5. One green `make sweep`.
6. The hand-editing pass.

Items 3 and 4 are each a single Claude session, runnable on request.
`CONSISTENCY.md` has served its purpose; delete it whenever you're done
with the record.
