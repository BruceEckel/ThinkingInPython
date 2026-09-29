> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 36_Patterns--Memento, second round (2026-09-29)

This run follows the completed review of 2026-09-25 (`~36_Patterns--Memento.md`).
I read that file and `deep_review_db.md` first and re-proposed nothing in either.
Nothing here needs your decision, so the file has no live blocks.

Nine commits touched the chapter after the first review closed.
The 2026-09-28 move of the `copy.copy()` paragraph below `sketch.py` left one pointer without its referent, repaired below.
The 2026-09-26 `@record` conversion left sentences in both files that call the converted classes a "frozen dataclass" or name `frozen=True`.
The 2026-09-27 triage commit cut nothing that carried a fact.

Probed on `ty` 0.0.84 in `build/examples/36_Patterns--Memento`:
with their `# type: ignore` stripped, `pickle_drift.py` and `ghost_field.py` each draw `invalid-assignment` on the class reassignment,
and `memento_type_safety.py` draws `invalid-argument-type` on the `expect()` call and `invalid-assignment` ("Property `strokes` defined in `Memento` is read-only") on the forged assignment.
The chapter's three `ty` sentences hold as written.

## Applied directly

Chapter:

- Opening: "*Memento* is the undo mechanism" read as the only one, and "Command-based undo" later in the chapter is a second. Now "an undo mechanism".
- After `sketch.py`: "One level is enough because a stroke is a string" followed a sentence about `copy.copy()`, which copies no level of `strokes`. The 2026-09-28 move put it there. It now names `save()`'s one-level copy.
- "Why `Memento` Is a Class": "A parameter typed `Memento` accepts the class alone" said the parameter accepts a class. Now "accepts only a `Memento`".
- After `memento_type_safety.py`: "A record freezes the attribute, not just the tuple inside it" implied the record freezes the tuple. The tuple is immutable on its own. It now says so, and that the record makes the attribute read-only too.
- `test_frozen_sketch.py` sat after the "Two kinds of state" paragraph with no lead-in. Added one sentence saying what its two tests check, in the form "Testing the Sketch" uses.
- "Restoring Part of a State": "The answer has to come from the state itself, and ... `copy.replace()` supplies it" had two suppliers. Now the state supplies it through `copy.replace()`.
- `pickle_drift.py` paragraph: "`frozen=True` installs a `__setattr__()`" named an option `sketch_v2.py` no longer writes (it is `@record(slots=False)`). Now "a record's generated `__setattr__()`".
- "A Deleted Field": "so `repr()` itself raises" is now "so the generated `repr()` raises".
- `round_trip.py` paragraph: "since a data class compares by value" is now "a record".
- "Schema Migrations": "other libraries handle the two separately" said the opposite of the paragraph, where each library addresses both drift and the security risk. Now "address both".

Solutions:

- Exercise 5 asks for `goto()` "keeping redo consistent". The solution looped `undo()`, so a jump past the oldest state moved some states to `_future` and then raised an `IndexError`, leaving the history half-moved. `goto()` now checks the distance before moving anything, the demo shows the `IndexError` and an unchanged `present`, and the prose says why, tied to the chapter's `undo()`.
- Exercise 3: "Drop the `tuple(...)` and `ty check` still passes" was an imperative-plus-consequence sentence; now a condition. "the dataclass declares it" and "a frozen dataclass otherwise supplies" now say "record".
- Exercise 4: "wrapping a mutable list in a frozen dataclass" now says "record"; italics for emphasis on *inside* and *copied* removed.
- Exercise 2: the demo comment "0 is discarded, keeping only 2" read as the value 2. Now "the bound discards 0". The paragraph's parenthetical "rather than after every `do()` the program ever made" did not parse; rewritten, and "honest answer" is now "correct answer".
- Exercise 6: "a bare type variable `S` promises no such method" is now "has no such method".
- Exercise 7: "the illusion collapses", "sails through", and "the contrast the chapter's partial restore relies on" were figures standing in for the claim. They now say that the default disappears, that the empty title loads, and that `copy.replace()`, which the partial restore uses, behaves differently. Italics on *class* removed.
- Exercise 1: "exactly like `draw()` does" is now "as `draw()` does".

## Considered and declined

- "[Rethinking Objects] ... explains why `strokes` is a tuple": chapter 20's section explains the principle (`frozen_leaky.py`), not `strokes`, but "that section also explains why" reads as applying the principle here. Left.
- "Why `Memento` Is a Class" says reassigning `checkpoint.strokes` raises `FrozenInstanceError`, which the caretaker paragraph and the listing's prose also say. The three are each tied to a different point (the convention, the record link, the demo), so they stay.
- The figure between the caretaker lead-in's colon and `history.py`: the colon introduces the listing with the figure in between. A standing layout across the pattern chapters. Left.
