When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/46_Stateless.md`.
The chapter reads as first-edition voice throughout:
varied sentence lengths, concrete claims tied to listings,
and the deep review had cleared most watch-list hits before this pass ran.
Four mechanical fixes were applied directly; no finding needs a decision.
The "Retrofitting an Effect" paragraph was treated as settled content
(modernized to ty 0.0.70 this session per your instruction) and left alone.

## Applied directly

- Line 91, watch word "happen": "Nothing the Effect describes happens until
  you call `run()`" is now "Nothing the Effect describes runs until you call
  `run()`"; the run/`run()` echo matches the "Nothing Runs Yet" heading.
- Line 131, sentence-final stranded preposition: "without saying where that
  instance comes from:" is now "without saying what supplies that instance:",
  which also foreshadows `supply()`.
- Line 771, clause-final stranded preposition (same rule the deep review
  applied to "classes of its own to depend on"): "explains where that cost
  comes from and how an interface avoids it" is now "explains the source of
  that cost and how an interface avoids it".
- Line 1292, §53 "worth knowing" frame: "That has a consequence worth knowing
  before you incorporate Stateless into an existing application" is now "That
  has a consequence when you incorporate Stateless into an existing
  application"; the next sentence states the consequence.

## Considered and declined

- **"It simply returns a `Generator`" keeps its "simply".** An empty adverb by
  the deletion test, but it is the deflating beat after "Calling `greet()`
  performs no work", the same move `readability_db.md` records keeping in
  30_Observer's "It is simply a callable".
- **"Failures never vanish; they only relocate."** Two watch words in one
  sentence, but it is a single earned capstone closing a section that just
  demonstrated the claim twice, and the skill allows one short emphatic
  closer.
- **"There is no `capsys`, no monkeypatching of `print`, and no mock."** A
  triple by shape (§10), but each item names a real testing technique the
  Effect version replaces, so the list is content rather than padding.
- **"`isinstance()` accepts an instance of the class or a subclass and nothing
  else"** (line 765) is the global rule's own keeper example: dropping the tag
  stops ruling out the structural match the sentence exists to rule out.
- **"a driver encountering one can do nothing but stop"** stays: the modal
  "can do nothing but X" carve-out, already recorded by the deep review.
- **"`A` is what the computation needs" / "`R` is what it produces"** stay:
  the words after "is what" are a clause that cannot attach without it, the
  global rule's keeper case ("`R` is what it produces" is its example).
- **The seven "already"s** (lines 774, 1074, 1120, 1127, 1186, 1319, 1327)
  each carry a temporal contrast the sentence needs (a function that already
  returns an Effect versus one being wrapped, a loop already running, a
  handler already applied versus one at the edge), so none is filler.
- **The two "However"s** (lines 159, 821) are far apart and each marks a real
  turn; transition words count only when piled up.
