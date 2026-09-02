# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-09-02, after the whole-book exercise pass:
45 chapters, ~320 exercises performed cold, 75 findings in 30 chapters,
queued in `exercise_review.md` (not yet applied).
It followed the whole-book correctness sweep: all 47 chapters checked,
56 false claims fixed (commits `7583395d` through `e2e5ba75`, plus
`e4a4e6cd` applying the review file), `make verify` green.
The sweep's record and its reasoning live in
`archive/~correctness_review.md`.

[[Note: find the GoF CD and upload it so Claude can verify against it]]

## Chapter Edit Steps

1. Do an adversarial review of the chapter. Fix everything you can, only present unresolved issues here on the console.
2. `make rewrite` on that chapter
3. Hand-edit the chapter
4. Run `/bruce-edit-capture` on the chapter

The correctness review that used to be step 4 is done book-wide and is
now a gate for the part of it a machine can decide
(`make self-reference`). What the gate cannot decide still needs a
reader, so keep a correctness pass in any chapter that gets substantial
new prose.

## The recommendations

1. **Apply `exercise_review.md`.** The exercise pass is done (2026-09-02,
   45 chapters, ~320 exercises, one fresh agent each performing every
   exercise cold before reading its solution). It found **75 findings in
   30 chapters: 0 blocking, 27 wrong, 15 drift, 33 minor**; fifteen
   chapters came back clean. `make sweep` was green before and after,
   which was the premise.

   Two results worth acting on beyond the queue itself:

   - **Ten of the 27 `wrong` findings are stale `ty` output quoted in
     `Solutions/`, and not one is in `Chapters/`.** The last `ty`-upgrade
     sweeps went through `Chapters/` and stopped. CLAUDE.md's
     `ty`-upgrade entry needs one more line: re-capture the quoted
     diagnostics in `Solutions/` too. Only 31 `error[...]` codes exist
     book-wide, so the sweep is small.
   - **`Solutions/40` and `Solutions/41` extract nothing** (16 python
     blocks, zero with a `# slug.py` first line), so they are never
     type-checked, linted, run, or pytest'd. Nothing is broken there
     today; nothing would tell you if it broke.

   Chapter 38 and chapter 10's exercise 5, the two the correctness sweep
   flagged, are both fixed. Chapter 37's exercise 1 is **not**: it still
   tells the reader to edit the file it then says needs no edits.

   Apply in the order the review's last section gives, and reproduce any
   finding not marked `[reproduced]` first. Evidence per chapter is in
   `exercise_review_reports/`; delete it with the review file when done.

2. **Tighten the capture loop before bulk-rewriting.**
   After each hand-edited chapter, run `/bruce-edit-capture` before
   rewriting the next range. Every rule promoted early applies to every
   chapter still ahead of the cursor.

3. **Run `make rewrite` a few ranges ahead of the hand-editing cursor**,
   not the whole book at once. A whole-book run now would apply today's
   rule set to chapter 47; the staged version applies a richer rule set
   the further out it goes. Chapters 1-24 get a bulk run last, with the
   mature DB.

4. **Adversarial review, results to a review file.**
   Structural findings should land before hand-polish. The consistency
   pass covered coherence between chapters and the correctness sweep
   covered truth; this one asks what does not work, what is missing, and
   what could be better. It is the one remaining review dimension with no
   coverage.

5. **Defer the whole-book readability sweep to last.**
   Every rewrite and review round adds new prose, and new prose is where
   AI tells appear. One sweep after chapter-level work settles mops it
   all up; running it earlier audits text that will change.

## Open items the sweep left for you

Two attributions to *GoF Design Patterns* were rewritten in `e4a4e6cd`
from what looked like Java rather than GoF, on reasoning rather than on
the book itself. Chapter 30's Observer no longer carries a `changed`
flag, and chapter 29 now names the pluggable and two-way adapters. Both
are worth a check against your copy.

## Suggested sequence

1. Item 1 (apply `exercise_review.md`). The evidence is fresh.
2. Item 4 (adversarial review, structural, before polish).
3. The item 2/3 loop through the remaining chapters.
4. Item 5 (readability sweep).
5. One green `make sweep`.
6. The hand-editing pass.

Items 1 and 4 are each a single Claude session, runnable on request.
