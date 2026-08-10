# Additional improvements

All five items below are done.
This file is now a record rather than a proposal, in the way `ADVERSARIAL.md`
became one.
The original numbering is kept so anything that cites an item still resolves.

## 1. Close the exercise/solution gaps, then gate them. Done.

Fifteen chapters had a gap when this was written, five of them with no
`Solutions/` file at all (21, 44, 45, 46, 47).
All five now have one, `Solutions/` holds 45 files, and no chapter with an
`## Exercises` section is missing its answers.

`tools/check_solutions.py` compares each chapter's exercise numbering against
its solution headings and runs first inside `solutions-gate`, which is a
prerequisite of `gate`.
It reports "Exercises and solutions line up" today, and drift cannot return
silently.
It understands a single heading answering several exercises
(`## 1 & 2.`, `## 1, 2.`, `## 1-3.`), and treats a chapter whose Exercises
section is prose rather than a list as needing no Solutions file.

## 3. Audit cross-chapter claims, not just anchors. Done, and yes, partly.

`[[Is this something a tool could do?]]`
Not the judgment, which is about meaning.
The narrowing, yes, and that was the expensive half.

`tools/check_claims.py` (`make claims`) sorts every cross-chapter link into
four shapes and reports only the one that can go stale:

- The text names the chapter (`[Iterators](23_Iterators.md)`), asserting
  nothing beyond the chapter's existence.
- The text quotes the target heading, so the two agree by construction and
  `heading_links.py` catches a later rename.
- The text is one word of the running sentence hyperlinked to where that term
  is taught (`[sentinel]`, `[narrows]`, `[mangled]`), which also claims
  nothing.
- The text is a phrase the author wrote describing what is over there.
  Nothing checks that, and it was wrong in every instance found by hand.

That takes 575 links down to 11 to read.
All 11 currently check out: five are `39_Pattern_Catalog` table rows, where a
pattern's name links to the section covering it by design, and the other six
describe their targets accurately.
The defects that motivated this item were fixed by the reviews that found
them; what was missing was the check that keeps them fixed.

Building it turned up one real bug, in the tool rather than the book: pandoc
drops leading characters up to the first letter when it builds an id, so
`### 1. Nothing stops an undeclared Effect` becomes
`#nothing-stops-an-undeclared-effect`.
The first slugify did not, and reported chapter 46's link to it as unresolved.
`tools/exercise_coverage.py` had inherited the same rule and was corrected
with it.

## 4. Put reflow-check in the gate. Done.

`reflow_prose.py` now runs in check mode inside `gate`, between the anchor
check and the example extraction, so prose that drifts out of Semantic Line
Breaks fails the build instead of waiting for someone to remember
`make reflow`.

This needed a fix first.
Check mode returned 0 whether or not any file would reflow: it exited nonzero
only on a round-trip failure, so gating it as written would have been
decorative.
It now returns 1 when any file would change and prints
"Run `make reflow` to apply", while `--write` still returns 0 after applying.
Verified in both directions by injecting drift into a chapter, watching the
gate fail, and watching it pass again after `make reflow`.

## 5. Hunt nondeterministic `#:` markers. Done. None found.

`validate_output.py --update` was run over all of `Chapters/` three times in
a row, snapshotting after each pass.
All three snapshots are byte-identical, and identical to the state before the
hunt.
No marker in the book is unstable today.

The three tightest threshold booleans were then run standalone eight times
each, since those are the ones that can flip under load rather than between
consecutive passes:

- `23_Iterators` `tee.py`, "tee held as much as the list" (a 0.9 margin): 8/8.
- `18_Performance` `hoist_attribute_lookup.py`, "did not halve" (2x): 8/8.
- `19_Concurrency` `gil_threads.py`, "threads no faster" (0.9): 8/8, matching
  the earlier standalone measurement recorded in `CLAUDE.md`.

`CLAUDE.md` already warns not to widen the `gil_threads.py` band, since at
0.7 a genuinely faster threaded run would still report "no faster."
That warning stands.
The one open threshold question is unrelated to stability and is recorded in
`deep_review_db.md`: chapter 3's `deque_time * 20 < list_time` was proposed
for tightening to 50, measured only on a shared Linux box, never confirmed on
this machine.

## 6. An exercise-coverage pass. Done.

`tools/exercise_coverage.py` (`make exercise-coverage`) maps every exercise
back to the sections it touches, by the listings it names, the functions and
classes those listings define, the anchors it links to, and the heading text
it quotes.
A section no exercise reaches is reported.

130 unpracticed `##` sections across 47 chapters, worst first: 18 (11), 46
(10), 11 (10), 12 (7), 08 (7), 21 (6).

Two cautions come with that number, both in the tool's docstring.
It counts `##` by default, because counting `###` would report 35
"unpracticed sections" for chapter 41's `itertools` catalog alone; `--deep`
includes them.
And the matching is literal, so it under-reports coverage: chapter 36's
exercise 7 ("Save a `Drawing` with `pickle`") genuinely practices "Mementos
That Outlive the Process" while naming nothing that section defines, and
reads as a gap.
Confirm a reported section by eye before writing an exercise for it.
It is a worklist, not a gate: a conclusion, a table, or a two-paragraph aside
wants no exercise, and forcing one onto each would be worse than the gap.
