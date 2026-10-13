> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 36_Patterns--Memento, third round (2026-10-13)

This run follows `~36_Patterns--Memento.r2.md` (2026-09-29) and the first review (2026-09-25).
I read both, and `deep_review_db.md`, and re-proposed nothing in them.
`uv run tip verify-ch CH=36 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.
Tools: `ty` 0.0.86, Python 3.15.0 (managed build), pyright 1.1.414, mypy (via `uv tool run`).
With their `# type: ignore` stripped, `pickle_drift.py` and `ghost_field.py` draw `invalid-assignment` from `ty`,
`memento_type_safety.py` draws `invalid-argument-type` and `invalid-assignment` ("Property `strokes` defined in `Memento` is read-only"),
mypy reports "Cannot assign to a type" on the reassignment, and pyright reports nothing, so the chapter's checker sentences hold.
The slotted-record field-shift paragraph was probed with a `title`, `strokes`, `color` record that loses `strokes`: it loads `color=('circle',)`, as the chapter says.
The chapter's identity demos (`sharing.py`, `round_trip.py`) compare strings, tuples, and records, never small ints, so the 3.15 small-int cache does not touch them.
No live blocks.

## Applied directly

Chapter:

- "A Snapshot Is Not a Reference", last paragraph: the two sentences after the `deepcopy()` cost repeated what the paragraph after `sketch.py` says, which links back here. Cut; "costs time and memory" became "takes".
- After `memento_type_safety.py`: "raises an `AttributeError` at `memento.strokes`, where the code reads `.strokes`" said the place twice. Now "when it reads `memento.strokes`", and "run time" matches the chapter's "runtime".
- After `sharing.py`: "that tuple is the one object it allocates" was false, since `draw()` also builds the new `Drawing`. Now says `draw()` builds a new `Drawing` around a fresh tuple and copies none of the strings.
- "The Caretaker" opening: the sentences on holding the classic `Memento` and on what immutability removes are repeated, with the listing in view, in the lead-in to `history_classic.py`. Replaced with the step the opener lacked: a caretaker that reads no field can hold any type of state, so `History` is generic.
- `apply()` paragraph: "If you build a new state and keep it in a variable of your own" did not say what went wrong. Now "If a call site builds the new state and forgets to pass it to `do()`". "in place of the caller ... unchanged" is now "for the caller".
- After `partial_restore.py`: "as the last line shows" was a positional pointer. Now "so `history.undo()` takes it back".
- "A Deleted Field Leaves a Ghost": "The class declares no such field, so `getattr()` finds it" gave the wrong cause for `getattr()`. Now `repr()` and `==` follow from the missing field, while `getattr()` finds the ghost in `__dict__`.

Solutions:

- Exercise 7: with a bare `@record`, the solution said only that the default disappears. A probe shows worse: the slotted `__setstate__()` zips the fields with the old `__dict__`, so `title` loads as `'title'` and `strokes` as `'strokes'`. The paragraph now says so, then gives the `layer` failure.
- Exercise 2: the bound used a list with a length check and `pop(0)`. Chapter 3 teaches `deque(maxlen=n)` for this, so `_past` is now a `deque`, `do()` keeps the chapter's three lines, the marker shows `deque([1, 2], maxlen=2)`, and a new step paragraph explains the choice. The hint points to Containers' `deque` section; "what the list holds" became "what the past holds" in two places.
- Exercise 1: `test_erase_returns_new_drawing_leaving_original(\n) -> None:` split its signature to fit 60 columns. Renamed `test_erase_leaves_original_drawing()`, one line. Hint: "pops from the list like `draw()` appends" is now "the way `draw()` appends".
- Exercise 4: the fragment's `save()` and `restore()` had no blank line between them. Added.
- Exercise 6: "the listing's last line proves it" is now "the `history.undo()` that ends the listing proves it".

## Considered and declined

- `test_frozen_sketch.py` sits at the end of "Immutability", after the "Two kinds of state" paragraph, rather than beside `frozen_demo.py`. Moving it up would split the aliasing-to-sharing argument; the end of the section is a reasonable home.
- The `memento_history` figure between the caretaker lead-in and `history.py`, and the repeated `FrozenInstanceError` sentences, were settled by the earlier reviews.
- Exercise 6's "Worth doing in a library; noise in a solution." is a fragment in the author's voice; left. Its `ty` claim holds: `copy.replace()` on an unbounded `S` draws `invalid-argument-type`.

## For the session

- `tip prose CH=36` reports two stale baseline entries this review made stale: the watch-words `costs` line (cut) and the positional "the last line" line (rewritten). Both baselines can drop them.
- `tip prose` also lists a stale internal-names entry, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`, from chapter 15, not from this chapter.
- `Solutions/36_Patterns--Memento/exercise_2.py` and `test_ch36_erase_frozen.py` were regenerated by `verify-ch`'s sync.
