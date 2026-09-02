# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-09-02, after the whole-book correctness sweep:
all 47 chapters checked, 56 false claims fixed
(commits `7583395d` through `e2e5ba75`, plus `e4a4e6cd` applying the
review file), `make verify` green.
The sweep's record and its reasoning live in
`archive/~correctness_review.md`.

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

1. **The exercise pass is now the highest-value item, and the evidence is
   in.** It used to sit at number 4 on a hunch. The correctness sweep
   turned that hunch into a count: eight of its findings were exercise
   premises that do not hold when performed, and in five of those the
   chapter was wrong while `Solutions/` was already right. Chapter 10's
   exercise 5 named one edit where the solution makes three. Chapter 38's
   exercise 3 could not produce its stated result on the chapter's own
   maze. Chapter 37's exercise 1 said to edit the file it then said needs
   no edits. Nothing gates the relationship between an exercise, its
   listing, and its solution, and it is visibly drifting.

   Run it as the sweep was run: one fresh agent per chapter, performing
   each exercise cold from the chapter alone, then diffing against
   `Solutions/`. Report-only, verify before applying. Budget roughly what
   the correctness sweep cost.

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

1. Item 1 (the exercise pass). The evidence is fresh and the drift is real.
2. Item 4 (adversarial review, structural, before polish).
3. The item 2/3 loop through the remaining chapters.
4. Item 5 (readability sweep).
5. One green `make sweep`.
6. The hand-editing pass.

Items 1 and 4 are each a single Claude session, runnable on request.
