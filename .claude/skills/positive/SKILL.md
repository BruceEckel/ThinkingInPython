---
name: positive
description: Say what happens, not what does not. A paragraph that makes the reader build an image and then cancel it, several times over, gets restated in positive form, keeping only the negatives that carry the claim. Use when asked to remove negatives from a chapter, or to state it positively (or the book). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Positive: state what happens

To understand a negative, a reader builds the positive picture and then
cancels it.
One cancellation costs nothing.
Four in a paragraph, and the reader is assembling and discarding images
faster than the paragraph delivers information,
which is why a technically clear passage can still be exhausting.
Strunk's Rule 11 says to put statements in positive form,
but it is one rule among eighteen in the `elements-of-style` pass,
which is how a paragraph carrying eight negatives went through that pass
unchanged.
This one does nothing else, so it counts.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## The test

Read a paragraph and count its negations.
Count the whole family, not just the word "not":

- **Plain**: not, no, never, nothing, none, nobody, neither, nor
- **Prefixed**: un-, in-, im-, non-, dis-, -less
- **Verbs that mean "did not"**: omit, lack, fail, avoid, refuse, miss,
  skip, ignore, stop, prevent
- **Nouns that mean "did not"**: omission, absence, failure, lack
- **Comparative**: less than, fewer than, other than, rather than,
  short of
- **Restrictive**: only, merely, just, at least, nothing but
- **Concessive**: all the same, even so, still, nevertheless, anyway
- **"Without" plus a gerund**: without deriving, without naming

Two or fewer in a paragraph is normal.
Three or more, or two inside one sentence, is a rewrite.

Then ask of each one: is this negation the claim, or is it an accident
of how the sentence came out?
Only the accidents change.

## How to turn one around

**Name the positive term.**
English usually has a word for the negated thing.

- "does not remember" becomes "forgets"
- "does not have many" becomes "has few"
- "did not pay attention to" becomes "ignored"
- "is not able to" becomes "cannot", and better, name what it does
  instead

**Say what happens, not what fails to.**
The strongest version of this rule.
The sentence describing a failure usually knows what did occur:

- "a concrete factory that omits `make_obstacle()` constructs with no
  error and raises an exception only when something calls the missing
  method"
  becomes "Constructing a concrete factory that supplies only
  `make_character()` succeeds, and the error waits until something calls
  `make_obstacle()`."
- "An `@abstractmethod` fails at instantiation ... and at least reports
  the omission before any call happens"
  becomes "An `@abstractmethod` moves that error earlier, to the
  constructor."

**Delete a negation that only hedges.**
"at least", "all the same", "even so", "still" often soften a claim the
sentence should make outright:

- "The checker verifies conformance all the same" becomes "The checker
  verifies conformance", or the clause goes entirely when a later
  paragraph makes the same point.

**Cut a negative preview.**
A paragraph that says what something does not do, ahead of a listing
that shows what it does, is spending negation on material the reader is
about to see stated positively.
Let the later passage carry it.

## What stays

- **The negation that is the claim.**
  "Python does not need a `Factory` class nested in every shape" is the
  point of its paragraph.
  So is "no error to signal it", "nothing imported the module that
  defines the class", and "`make()` never reads it".
  These are the book's findings, not accidents of phrasing.
- **Traps and warnings.**
  Part of what this book teaches is what a construct fails to guarantee.
  Those paragraphs are legitimately dense in negation, and the count
  test flags them; check whether each negation carries a distinct fact
  before touching one.
- **Half of a real contrast.**
  "a convention rather than concealment" needs both halves.
  So does "the mistake, not the model".
- **Code, always.**
  `NotImplementedError`, `is not`, `not in`, `None`, a `no_cheese()`
  method: identifiers and listings are outside this pass.
- **A negation with no positive term.**
  "not a data class" has no single word. Leave it rather than invent
  one, or restate the sentence around what the thing *is*.
- **Check the exemption records first.**
  `deep_review_db.md` in the repo root carries standing exemptions,
  and `bruce_edit_db.md` carries the promoted editing rules.

## Boundary with the neighboring passes

- `elements-of-style` carries this as Rule 11 among eighteen. If it had
  caught the paragraph, there would be nothing here; in practice its
  attention goes to needless words and active voice.
- `activate` fixes voice and register. A passive sentence and a negative
  sentence are different failures, and a passage can have both.
- `straighten` fixes the architecture of a sentence. Turning a negation
  around often shortens a sentence enough that `straighten` has less to
  do, which is why this pass runs first.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Report per paragraph: the negation count before and after, and the
negations kept with the reason each carries its own claim.
Bruce reviews the diff and commits himself.

## Accrued patterns

Negation shapes Bruce has flagged that the families above do not name
yet. When he identifies a new one, add it here as a bullet with a
before/after pair, and it becomes part of every future pass.
