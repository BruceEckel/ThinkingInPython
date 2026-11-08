---
name: alternative
description: Find and frame an alternative described in a listing walkthrough's own register. A paragraph narrates a listing, and a sentence in it says what a different construct, call, or design does, in the plain present with nothing marking it as the road not taken ("A `for` loop treats `StopIteration` as the normal end of the loop" under a `try`-driven listing; "`C().show()` then runs `B`'s version" after "Writing the bases as `C(B, A)`"). Each post-listing paragraph is read against its listing, each sentence is tested for whether it is true of the listing on the page, and a sentence about the other version gets the lightest frame that carries over. Use when asked to frame or mark the alternatives in a chapter, to find unmarked hypotheticals, or to run the alternative pass (or the book's). The argument names chapters by number or name, optionally followed by `section "<heading>"`; no argument means all of Chapters/.
---

# Alternative: the road not taken says so

A walkthrough paragraph tells the reader what the listing does.
A sentence in it that describes what some *other* construct would do,
in the same plain present and the same register, reads as the next
step of the run, and the reader backs up when it fails to match the
listing.
The case that started this pass (chapter 45, 2026-11-08), under
`drive_by_hand.py`, whose driver catches `StopIteration` in a `try`
statement:
"The caller receives that `return` as a `StopIteration`, and the
`Result` arrives as the exception's `value`.
A `for` loop treats `StopIteration` as the normal end of the loop, so
it discards the exception and loses the return value."
Bruce: "this seems like it's continuing to describe what happens in the
code, but it's actually describing an alternative -- that's not clear.
I have regularly seen this pattern of describing an alternative in the
same place where the description of what's actually happening is
described, and I would like to fix this everywhere."
Now: "The listing catches `StopIteration` in a `try` statement because
a `for` loop would discard the exception.
A `for` loop treats `StopIteration` as the normal end of the loop and
drops the `Result` along with the exception."

The book-wide sweep that day (49 Opus agents, brief in
`build/alt-2026-11-08/`) framed 84 passages in 39 chapters, and nearly
all of them had one shape the scan could not see: the *second*
sentence of an alternative.
The opener carried a frame ("Writing the fix as `type(self).total +=
1`", "If you leave out the reset", "An `__init__()` that assigns
`_value_`"), and the continuation dropped it ("`C().show()` then runs
`B`'s version", "The lookup table then stays keyed by the tuples, so
`Tile(".")` raises a `ValueError`", "`simplify()` receives `5 * x`"),
and the bare continuation contradicted the listing's own `#:` output.
A marker protects only the sentence it sits in.

This pass edits `Chapters/NN_*.md` prose only; code blocks, `#:`
output markers, headings, and quoted material stay.
Given a `Solutions/<chapter>/README.md`, it edits that file's prose the
same way, except the block quote under each `## N.` heading, which
`tip statements` copies from the chapter.
Rule R57 in `bruce_edit_db.md` is the rule.

## Mechanical candidates

Run `tip positional CH=NN ARGS=--survey` first and read the `survey
alternative` lines (`tools/positional_refs.py`, 2026-11-08): a
sentence in a walkthrough paragraph that opens on an indefinite
article and a code span absent from the listing above, or that holds a
statement keyword absent from it, with no marker word, first mention
only.
It sees the opener of an alternative and never the continuation, and
most of its hits are keeps (a general fact true of the listing too),
so it is a floor, never the list.
The pass is the read: every paragraph that follows a listing, up to
the next listing or heading, sentence by sentence, with the listing
and its markers open beside it.

## The test

For each sentence in a post-listing paragraph:

1. Is the sentence about the listing on the page, or about something
   the listing does not do?
   Open the listing.
   A construct it lacks (a `for` where it has a `try`, an `as` the
   `with` line lacks, an `__init__()` where it has `__new__()`), a
   call it never makes, a value it never passes, a design the chapter
   argues against, a mistake a reader might make.
   A claim that contradicts a `#:` marker is the surest sign.
2. If it is about the alternative, does the sentence say so?
   A frame ("If you ...", "With a `return` at the match", "In that
   version", "Written with ..."), a modal ("would"), a word naming the
   thing as other than the listing's ("a version that", "a direct
   `Tile(...)` call", "a bare `except:`", "a misspelled `p.ff()`", "by
   contrast", "rather than", "where `X` does Y"), or a pointer back to
   a framed sentence ("That `pop(0)`", "its", "that class").
3. A sentence about the alternative with no marker of its own gets
   one.
   A "then" after a framed opener is the shape to watch: "then" says
   "next", and the reader takes the next step as the listing's.
4. Probe the alternative's claim under `uv run python` or `uv run ty
   check` before framing it.
   The sweep's probes found one false claim (Solutions 30's
   `show(model)` call fails the type checker), and a framed
   misdescription is worse than an unframed one.

## Frame with

The lightest marker that carries over, keeping the claim's words:

- What it replaces: "With a `return` at the match in place of the
  `break` at `[1]`, the function leaves both loops in one step."
- A condition: "If `__init__()` assigns `_value_`, the assignment
  comes too late."
- A frame for the continuation: "In that version the lookup table
  behind `Tile(".")` keeps the tuples as its keys", "In that order,
  `C().show()` runs `B`'s version", "With that call in place, the
  counter loses updates again", "Without the reset, `total` is still
  5 from the first call".
- A gerund subject: "Adding an `as` clause to the `with` line is
  legal, and the name it binds is `None`."
- A tie to the listing's choice: "The listing catches `StopIteration`
  in a `try` statement because a `for` loop would discard the
  exception."
  "would" is right for a counterfactual whose condition is on the
  page; after the frame, a standing fact about the alternative stays
  in the present.
- A colon that attaches the consequence to the thing that produces
  it: "`asyncio.BoundedSemaphore` checks for that mistake: a
  `release()` beyond its starting count raises a `ValueError`."
- When an alternative runs for several sentences inside a walkthrough
  paragraph, its own paragraph, opening on its frame, so the
  walkthrough paragraph explains one thing (R29).

## Keep when

- A general fact that holds for the listing too, in a paragraph that
  explains rather than narrates: "A `for` loop makes one `iter()`
  call, then calls `next()`" in the section that introduces `for`;
  "`gather()` wraps each coroutine in a task".
- An earlier sentence of the paragraph introduces the alternative as
  one, and the sentence points back to it: "The real mistake is
  catching too much. A bare `except:` ... catches the cancellation";
  "If you leave out `return cls`, `announce` returns `None`. Python
  then binds `None` to `Point`" (the "then" sits right after the
  conditional).
- A comparison paragraph whose subject is the difference: "`partial`
  and `partialmethod` differ as soon as an argument is positional."
- Advice, a `Done when:` paragraph about the reader's own run, a
  quoted diagnostic, prose that names another listing by file name,
  a reference to another chapter.

When the test is close, keep it and say so in the report.

## Boundaries

- One frame per alternative sentence; a sentence that has one does
  not get a second.
- Never reword the claim to fit the frame; if the claim is wrong, the
  claim is the fault, and a probe decides.
- Bruce's "we" and his em-dashes stay.
- The style rules this repair trips most: no imperative-plus-
  consequence ("Remove X and Y happens" is "If you remove X, Y
  happens"); "can" hedges a fact; "could" only for a condition or a
  past; a colon is a pointer, never a period; "instead" only where
  the structure does not already show the substitution.
- A frame added in front of a flagged word re-keys that word's
  baseline keep (`has no`, `never`, `already`, `[BOUND]`, a positional
  phrase); after `tip prose CH=NN`, accept the pair with the scoped
  `tip <check>-accept CH=NN` once the flagged word is confirmed
  unchanged.

## Working a chapter

1. `tip positional CH=NN ARGS=--survey`; keep the `survey alternative`
   lines inside the scope.
2. Read every post-listing paragraph in the chapter and its Solutions
   file against its listing, applying the test to each sentence.
3. Frame, probe, and edit.
4. `uv run tip verify-ch CH=NN`, then `uv run tip prose CH=NN`; read
   each `NEW` and `stale` line.
5. Commit the chapter, its Solutions file, and any accepted baselines
   together.

## Report

For each sentence framed: the file and line, the old and new words,
and the listing fact or probe that confirms the alternative's claim.
Then the close calls kept, with the marker or the reason each one
stood, and the baseline pairs accepted.
A pass that frames more than a few sentences per chapter is reading
general facts as alternatives; the sweep's rate was 0 to 4 a chapter.
