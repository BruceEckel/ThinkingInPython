---
name: annealing
description: Settling pass after a deep review: re-run the deep-review passes over the whole chapter, apply every fix you are confident to make without the author, and discard the rest unreported. No review file, no proposals. Use when asked to anneal a chapter, typically after a deep_review file has been applied.
---

# Annealing a chapter: apply the certain, discard the rest

Applying a deep review moves a chapter, and the moves leave seams:
a sentence that still describes the old version of a listing,
a cross-reference aimed at a section that was renamed,
an output marker one edit behind its code,
style drift in freshly written prose.
Annealing is the settling pass that follows.
It re-reads the whole chapter with the deep-review lenses
and applies the confident findings directly, with nothing filed for later.
The argument names the chapter, by number or by name.

Run the same passes deep-review defines
(`.claude/skills/deep-review/SKILL.md`):
the editing pass, the teaching pass at both altitudes,
the house-style audit, and the prose pass,
including the third-party-library rule and the accrued notes.
The passes are identical; the disposition of findings is not.

**The confidence bar is deep-review's; the reporting channel is gone.**
Deep-review splits findings into two piles:
it implements the confident ones and files the rest for Bruce's judgment.
Annealing keeps the first pile and discards the second.
A finding below the bar is dropped:
no review file, no list in chat, no "you might consider" asides.
If it matters, the next deep review will surface it through the
review-file workflow, which is built for judgment calls; annealing is not.

Confidence keeps its deep-review meaning:
you know the fix is right, not that the fix is small.
A confident teaching addition is in bounds:
a lookalike pair that needs contrasting,
a near-miss the reader would write,
a mechanism a listing shows by its outcome alone.
Structural change stays out of bounds, for a reason of annealing's own.
Deep-review implements a section cut or a reordering when it can decide one,
and records that decision in the review file's applied-directly list,
where the next review reads it.
Annealing writes no file,
so the same change would move the chapter's shape with no record of why.
It also runs when a deep review has just settled that shape,
and reopening it a pass later is churn rather than settling.
So leave these alone:
cutting a section, reordering,
anything that changes the chapter's voice or pacing,
and a new listing whose placement is a judgment call.
When a confident finding admits several reasonable fixes,
make the one you would have recommended.

**Respect the review-file record.**
If an unprefixed `deep_review/NN_name.md` exists for the chapter,
that review has not been applied yet;
stop and say so rather than annealing over it.
Otherwise, before applying anything, read the chapter's most recent
completed review, the highest-numbered `deep_review/~NN_name*.md`.
A block marked `[X] Reject` there is a change Bruce declined:
do not apply it, or anything equivalent to it, however confident.

**Verify.** Every change follows the verify loop in `CLAUDE.md`.
A new listing gets the full treatment
(fenced block with `# slug.py` first line, deterministic markers
or wide-margin threshold booleans, sync, gates);
touched prose gets `make reflow CH=NN`.
Finish with `make verify` and read `git diff Chapters/` afterward:
a timing marker that flipped is a finding to investigate,
not drift to accept.

**Report.** The final message lists each applied change in a sentence,
with its reason, plus the `make verify` outcome.
If nothing cleared the bar, say the chapter annealed clean.
Bruce reviews the diff and commits himself.
