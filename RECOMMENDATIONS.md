# Recommendations

What to work on next, in priority order.
Claude maintains this file and rewrites it when something new occurs to it.
Last updated 2026-09-03, after the whole-book adversarial review was
applied: 252 findings, 213 applied (one agent per chapter, each
finding reproduced before its fix), 1 declined, 38 author-level calls
queued in `adversarial_undecided.md`. Its record is
`archive/~adversarial_review.md`; `make verify` green. Before that,
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

1. `make rewrite` on the chapter
2. Hand-edit the chapter
3. Run `/bruce-edit-capture` on the chapter

The correctness review that used to be step 4 is done book-wide and is
now a gate for the part of it a machine can decide
(`make self-reference`). What the gate cannot decide still needs a
reader, so keep a correctness pass in any chapter that gets substantial
new prose.

## The recommendations

1. **Write the chapter 01 AI anecdote.**
   The last entry in `adversarial_undecided.md`: one concrete case
   where book-level Python judgment steered an AI to a better
   solution, closing the AI section's now-final sentence with
   evidence. Only you can write it. Archive the file when it lands.
   The other 37 queue entries were approved and performed 2026-09-03;
   `make verify` green.

2. **Defer the whole-book readability sweep to last.**
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

1. Item 1 (the chapter 01 anecdote, the queue's last entry).
2. readability sweep
3. One green `make sweep`.
4. 'Chapter Edit Steps' through the remaining chapters.
