# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-09-02, after the whole-book adversarial review ran
(results in `adversarial_review.md`, not yet applied). Before that,
the whole-book exercise pass was applied:
45 chapters, ~320 exercises performed cold, 75 findings in 30 chapters,
73 applied and 2 declined. Its record is `archive/~exercise_review.md`.
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

1. **Apply `adversarial_review.md`.**
   The adversarial review ran 2026-09-02: one fresh agent per chapter,
   all 47 chapters, report-only, Sonnet for the mechanical chapters and
   Opus for the 13 dense ones, 18 and 19 last under the timing brief.
   252 findings (40 does-not-work, 143 missing, 69 could-be-better),
   no chapter clean. The file's header names the five systemic
   patterns and the eight behavior holes to start with. Findings are
   verified by their agents (command and output in the finding text)
   but not yet reproduced by a second reader: verify before applying,
   the gate's way, as both prior passes did. Structural findings
   should land before hand-polish.

2. **Tighten the capture loop before bulk-rewriting.**
   After each hand-edited chapter, run `/bruce-edit-capture` before
   rewriting the next range. Every rule promoted early applies to every
   chapter still ahead of the cursor.

3. **Run `make rewrite` a few ranges ahead of the hand-editing cursor**,
   not the whole book at once. A whole-book run now would apply today's
   rule set to chapter 47; the staged version applies a richer rule set
   the further out it goes. Chapters 1-24 get a bulk run last, with the
   mature DB.

4. **Defer the whole-book readability sweep to last.**
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

1. Item 1 (apply the adversarial review, structural, before polish).
2. The item 2/3 loop through the remaining chapters.
3. Item 4 (readability sweep).
4. One green `make sweep`.
5. The hand-editing pass.
