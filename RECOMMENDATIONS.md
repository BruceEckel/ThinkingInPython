# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-08-30, after the book-altitude consistency pass:
its nineteen confident fixes are committed (`2e502ecc`), and the
human-call findings are in `CONSISTENCY.md`.

## The recommendations

1. **Triage `CONSISTENCY.md`.**
   The consistency pass fixed what it could and left the judgment calls
   there: the Part I / chapter 40 "Foundations" name collision, the
   duplicate-teaching pairs (ABC-vs-Protocol in ch26 and ch27 is the
   biggest), the GoF citation gaps, and ch11's assumed-before-taught debts.
   Anything that restructures prose should be decided before hand-editing
   reaches those chapters.

2. **Tighten the capture loop before bulk-rewriting.**
   After each hand-edited chapter, run `/bruce-edit-capture` before rewriting
   the next range. Every rule promoted early applies to every chapter still
   ahead of the cursor. This is the highest-leverage move for "fewest
   hand-edits": chapter 25's capture yielded eight rules, and C1 needs only
   one more sighting to promote.

3. **Run `make rewrite` a few ranges ahead of the hand-editing cursor**,
   not the whole book at once. The pass is moving sequentially (25→28), so
   `CH=29-33` next, vet the diff, hand-edit, capture, then the next range.
   A whole-book run now would apply today's rule set to chapter 47; the
   staged version applies a richer rule set the further out it goes.
   Chapters 1-24 get a bulk run last, with the mature DB.

4. **Adversarial review, results to `ADVERSARIAL.md`.**
   Structural findings should land before hand-polish, not after. The
   consistency pass covered coherence between chapters; this one asks what
   doesn't work, what isn't correct, and what could be better.

5. **Fresh-reader exercise pass.**
   A session attempts each exercise cold, using only the chapter, and diffs
   its experience against Solutions. Catches Solutions drift, which no gate
   covers.

6. **Defer the whole-book readability sweep to last.**
   Every rewrite and review round adds new prose, and new prose is where AI
   tells appear. One sweep after chapter-level work settles mops it all up;
   running it earlier audits text that will change.

## Suggested sequence

1. Item 1 (triage, feeds the rewrite loop).
2. Item 4 (adversarial review, structural, before polish).
3. The item 2/3 loop through the remaining chapters.
4. Item 5 (exercise pass).
5. Item 6 (readability sweep).
6. One green `make sweep`.
7. The hand-editing pass.

Items 4 and 5 are each a single Claude session, runnable on request.
