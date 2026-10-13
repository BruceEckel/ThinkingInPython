---
name: listing-design
description: Propose design improvements to a chapter's listings. For every extractable listing, ask six questions (incidental code, runtime checks the type checker could make, demo code in a library file, a trace that shows the chapter's subject, parameter names that match the prose, repeated output lines), and report each proposal with its tradeoff. Edits nothing. Use when asked to review, improve, or find improvements in a chapter's listings or code (or the book's). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Listing design: propose the better listing

The review passes ask whether a chapter is right: whether the prose
is true of the code, whether the markers match, whether a sentence
is clear.
A listing can pass every one of those and still be the wrong
listing for its chapter, because it carries code that serves no
point the chapter makes, checks at runtime what the type checker
could check, or prints a trace that shows half of what the reader
needs.
Those faults are invisible to a consistency check: the prose
explains the code as written, so the pair looks deliberate.
They show up only against an alternative, and this pass exists to
generate the alternative for every listing and compare.

Bruce's observation (2026-10-12): several improvement passes went
over a chapter whose listings parsed a text file, carried their demo
beside their classes, and printed a trace that named the input but
never the transition, and none of the passes proposed a change,
because none of them asked.
Every one of those changes came out of a question he asked about
one listing.
This pass asks those questions of every listing.

It reports and edits nothing.
A listing change moves markers, prose, figures, and Solutions
copies, and whether it is worth that is the author's call.

## Scope

Every fenced ```python block whose first line is a `# path.py`
comment, in the named chapters, plus the `text` blocks a listing
reads.
Read the whole chapter first: a proposal has to know what the
chapter is about before it can say which lines are beside the point.
Read `Solutions/<stem>/README.md` far enough to know which listings
the exercises import, since a change to a library listing reaches
them.

## The six questions

Ask each question of each listing.
Most listings answer all six with "fine"; the report lists the rest.

### 1. Which lines are about the chapter's subject?

Sort the listing's lines into the ones that show the subject (the
pattern, the construct, the technique the section teaches) and the
ones that exist so the demo can run: reading a file, parsing input,
building fixtures, string formatting, argument handling.
Incidental code is fine when it is short and the subject needs it.
It is a proposal when it is longer than the subject code around it,
when it repeats in a second listing, or when the prose has to spend
sentences explaining it.

The usual repairs: move the incidental code to a helper module the
listing imports (`utils/` for a helper several chapters share, a
chapter-local module otherwise), replace parsed input with a literal
of typed objects, or delete it when a simpler fixture makes the same
point.

### 2. What does the listing check at runtime that the type checker could check?

Look for strings, dictionaries, and `object` parameters that stand
in for a type: a string that must match an enum member, a dict
whose keys are the names of things the module defines, a lookup that
raises a `KeyError` or `ValueError` for a misspelling, an
`isinstance()` chain over a known set of classes.
Ask whether an `Enum`, a `Literal`, a record, a `Protocol`, or a
generic would let `ty` report the mistake before the program runs,
and whether the chapter's subject is better served by the static
form.

Keep the runtime check when the chapter is about the boundary where
untrusted input arrives, or when the dynamic form is the subject
(a registry, a plugin table, a dispatch dict the chapter builds up).

### 3. Does a listing other code imports also run a demo?

A listing that defines classes or functions and then, at module
level, exercises them with `#:` markers prints whenever it is
imported.
The book's convention is a library listing with no top-level
effects plus a separate demo listing that imports it (chapter 31's
`observers.py` and `thermometer.py`).
Propose the split when another listing or a Solutions file imports
the module, when the demo is long enough to bury the classes, or
when the demo has two parts with prose between them.

A listing nothing imports, whose demo is a few lines, stays whole.

### 4. Does the trace show the subject?

Read the `#:` markers as the reader will, with the prose that walks
them.
Ask what the chapter wants the reader to see in the output, and
whether each printed line shows it: a state machine's trace shows
the transition (from, input, to), an observer demo shows who was
notified of what, a cache demo shows hits and misses, a timing demo
shows the two numbers side by side.
A trace that prints the input on one line and the resulting state's
action on the next, with no line that joins them, makes the reader
assemble the transition.

Propose the print that shows the subject in one line, and say which
markers move.

### 5. Do the names in the code match the words in the prose?

For each parameter, variable, and method name in the listing, find
the word the prose uses for the same thing.
A parameter named `event` under prose that says "input" throughout,
a method `handle()` the prose calls "dispatch", a variable `data`
the prose calls "the record": each makes the reader translate.
Propose the rename toward the prose word, and name the obstacle
when there is one (a builtin, a keyword, a stdlib module name) and
the convention that resolves it (`input_`, `class_`).

Leave a name the chapter explains as a term of its own, and a name
a library fixes.

### 6. Does any output line repeat what a neighboring line prints?

Read consecutive marker lines for a value that appears in both: a
state name that one line prints as a prefix and the next prints as
the current state, a message echoed by a wrapper and again by the
callee, a count printed before and after a no-op.
Propose dropping the copy that carries the less information, and
check that the first and last lines of the trace still identify
themselves once it is gone.

## The report

One entry per proposal, grouped by listing, in this shape:

- **`listing.py`, question N.** One sentence naming what the listing
  does now. One sentence naming the change. One sentence on what it
  improves. One sentence on the tradeoff: what gets longer, what
  moves (markers, prose, a figure, a Solutions copy), what the old
  form showed that the new one does not.

A listing with no proposal is a line: "`listing.py`: fine on all
six."
End with the proposals ranked, the one you would make first at the
top, and the count of listings read.

For one chapter the report goes in the reply.
For a batch of chapters that Bruce will judge, it goes on a review
page (project memory `review-work-as-artifact-pages`), one card per
proposal with the tradeoff on the card.

## What stays

- **A listing that is the subject.** Code that parses input in a
  chapter about parsing, a dispatch dict in a chapter about dispatch,
  a demo that is the whole listing. Question 1 asks what the chapter
  is about before it sorts a line as incidental.
- **A deliberate contrast.** A long form kept beside a short one so
  the reader sees the difference; the chapter says so.
- **An exercise's own fixture.** Solutions listings answer the
  exercise as set; they are read for what they import, and their own
  design is the exercise's.
- **Chapters 02-10.** Part I teaches the constructs a proposal would
  use; a `Protocol` or a record proposed before the chapter that
  introduces it is a proposal against the book's order.
- **The exemption records.** `deep_review_db.md` carries standing
  exemptions; `bruce_edit_db.md` carries the editing rules.

## Boundary with the neighboring passes

- `deep-review` checks what a chapter claims against its listings.
  This pass asks whether the listings are the ones the chapter
  should have.
- `verify-claims-opus` reports where prose is false of code. This
  pass can find code that is true to its prose and still wrong for
  the chapter.
- `/literal`, `/positive`, and the other prose passes edit
  sentences. This pass edits nothing and proposes listings.

## Calibration

A pass that proposes design changes is judged by whether it finds
the changes the author made on his own.
Record each calibration run here with its date and result.

- **2026-10-12, chapter 31 at tag `edit-start-31`, Opus, blind.**
  The run saw a copy of this file with the paragraph above about
  Bruce's observation removed and question 4's state-machine example
  replaced by a generic one, and it was barred from the current
  `Chapters/`, `Examples/`, and `Solutions/` trees. Its ranked
  report put the two target changes first: a typed `MOVES` literal
  replacing the duplicated text-file parse (it placed the literal in
  `mouse_action.py` as a tuple; the session's version is its own
  `mouse_moves.py`), and splitting the demos out of the two trap
  listings (it proposed one shared demo under "An Unexpected Input";
  the session made one demo file per version). Third was the joined
  transition line, which the session had also made. It found the
  `event`/`input` mismatch but chose the other direction, `event` in
  prose, since `input` is a builtin; Bruce chose `input_`. Beyond
  the targets it found a message bug in `vending_view.py` (the row
  key is named `row 2`, so `choose_row()` sets "Row row 2", which the
  column keypress overwrites before Tk repaints), a `RuntimeError`
  message that wraps across two marker lines, a `Row`/`Column`
  vocabulary for the selection keys, and a generic `State[E]`.
  Eleven listings read, ten proposals, 115k tokens, under four
  minutes.
- **2026-10-12, the whole book, 49 Opus agents, then applied.**
  359 proposals over 47 chapters (Q1 108, Q2 23, Q3 28, Q4 117, Q5 54,
  Q6 29). Bruce's ruling: apply all, hold the questionable ones for
  him. The session held 202 and applied 157; Bruce had already marked
  18 cards in chapters 02-04 Apply on the page, eight of them ones the
  session held, so those applied too. 46 Opus apply agents (one per
  chapter, 80-140k tokens, 30 s to 4 min, twenty at a time) edited the
  chapter, its Solutions copies, and its figure spec, ran
  `verify-ch ISOLATED=1`, and wrote a report; the whole-book `tip
  verify` was green on the first run. Three cards were not applied:
  two needed a `noqa` (ruff F821 for a `NameError` demo outside a
  `try`, N804 for a `__prepare__` first parameter other than `cls`),
  and one was moot after Bruce removed the listing. Two cards on
  timing-registered listings (`timing.txt`) had to be applied by hand,
  since the validator refuses to fill a new marker there. Lessons for
  the brief: an agent that finishes before a card is added needs a
  second pass with only the new cards; `tip prune` by one agent
  deletes another chapter's orphan, which is harmless; a card's
  column count is often one or two off, so the agent wraps.
