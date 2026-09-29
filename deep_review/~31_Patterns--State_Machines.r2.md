> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 31_Patterns--State_Machines (second review, 2026-09-29)

This second review reads the chapter and its Solutions file after the 2026-09-25 review, the 2026-09-26 openers, the 2026-09-28 move of `TableState` into `table_state.py`, and the *State Machine* decision.
Chapter 31 had no 2026-09-27 fix-triage commit, and none of the later edits cut a lead-in that carried a fact.
I checked the `ty` claims against `ty` 0.0.84 with scratch probes: the empty base draws `unresolved-attribute` on both `run()` and `next()`, the `ABC` subclass missing `next()` draws `call-non-callable` ("Cannot instantiate abstract class"), and the Protocol draws `invalid-argument-type`.
Nothing here needs your decision, so the file has no live blocks.
`tip verify-ch CH=31` passes 24 of 24.

## Applied directly

Chapter:

- Empty `State` base: "`State` declares no `next()` for `run_all()` to call" named one of two errors. `ty` also rejects `__init__()`'s `run()` call. Now "declares neither the `run()` nor the `next()` the engine calls". "rejects the engine itself" lost "itself".
- The `NotImplementedError` base "raises from the base's method instead" had no object. Now "The call to the missing method then raises that `NotImplementedError` from the base".
- `TableState.__init__()`: "rather than an `AttributeError`" left the reader to work out where the `AttributeError` would come from. Now names the missing `transitions` attribute, and "forget to fill one" says "a state's table".
- "The output matches the first version's, move for move" was not true of the whole listing, whose last call differs (the next section's subject). Now "The nine moves produce the first version's output, line for line."
- "have to match" and "has to live" became "must".

Solutions:

- Exercise 2: "exactly what distinguishes this design from the table-driven one exercise 7 uses" singled out one of three table-driven exercises and carried "exactly". Now "the chapter's table-driven one".
- Exercise 3: "the same delegation `state.py`'s `next()` method uses" credited delegation to a Protocol that declares a signature. The delegation is `state_machine.py`'s `run_all()` calling `next()`. Corrected.
- Exercise 8: "both slots really are optional" lost "really".

## Considered and declined

- "Nothing here needs a `switch`, reflection, or a `Condition`/`Transition` class hierarchy" names mechanisms of the Java original that the chapter mentions only in part. The sentence reads as a list of things the Python version avoids, and it is yours.
- The note that the harness skips `vending_view.py` (`tools/data/norun.txt`) points the reader at a repo file. It has stood through two reviews, so I left it.
- Every solution was checked against its exercise; each does what the exercise asks. Exercise 3 feeds a list rather than a file and gives the one-line file read in its prose, which answers the exercise's "such as".
