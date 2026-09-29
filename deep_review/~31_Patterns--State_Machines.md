> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 31_Patterns--State_Machines (2026-09-25)

This run follows the five prose passes (literal, positive, straighten, cohesion, antecedents), each committed on its own.
Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the chapters it links (6, 12, 13, 25, 26, 28), the committed `#:` markers, a `ty` probe, and the installed `transitions` 0.9.3 and `python-statemachine` 3.2.1 wheels (both supply hierarchical states).
`make verify-ch CH=31` passes 24 of 24.

## Applied directly

Chapter, corrections (several introduced by the prose passes, caught in their diffs):

- "An Unexpected Input": the positive pass called `ESCAPES` in `Waiting` "a case outside the nine moves in the file", but `ESCAPES` is one of the nine. Now "an input the current state does not name", which the nine moves never produce in `Waiting`.
- The same section's "Staying in the same state is itself a transition" contradicted "nine moves that between them exercise every transition", which counts only the six explicit ones. Now "Staying in the same state still does something."
- Empty base `class State: pass`: the prose said only that the error waits for the call. A `ty` probe shows the checker rejects the engine itself (`unresolved-attribute` on `self.current_state.next(event)`), since the empty base declares no `next()`. That now comes first, and the `NotImplementedError` base is described as the one that satisfies the checker.
- Row-order paragraph: "as though a dollar more would sell it" is wrong for a 25-cent slot with 10 cents in. Now "as though more money would sell it."
- Opening: the straighten pass made the pattern the actor ("A *Template Method* often moves the system..."). Restored "The code that moves the system ... is often a *Template Method*."
- "Each state is one shared object: a state class stores nothing" gave the effect before its cause. Reordered.

Chapter, teaching:

- After the `match` description: added the near-miss. Each `case` spells `MouseAction.APPEARS`, and a bare `APPEARS` would be a capture pattern that matches every event, with a link to chapter 13's "A Bare Name Captures, a Dotted Name Compares".

Solutions:

- Exercise 6: `log_msg()` had no return annotation. Now `-> Callable[[object], None]`.
- Exercise 3: `from __future__ import annotations` is unnecessary on 3.15 (lazy annotations), and `WordState.TRANSITIONS` was a mutable class attribute without `ClassVar`, against house style. The import is now `ClassVar`, and the attribute is `ClassVar[dict[str, str]]`.
- Exercise 5: "one iteration of the consuming `for` loop" described a loop the listing lacks (`list()` drives the generator). Also, "`mouse_trap_states.py`'s `next()` methods enforce the same guarantee" was false: those methods accept any move and let `case _` absorb it. Both corrected.
- Exercise 6: "the noisy source the chapter describes" pointed at a word the literal pass removed from the chapter. Now "a source of stray presses."

Prose passes: two edits reverted during the positive pass (the reason a state's table cannot sit in its class body had been dropped, and the exact-class sentence had become garbled). One literal-pass sentence about misspelled strings was reworded.

## Considered and declined

- "Adding a state or an input is ... an entry in the table and a method or two" appears both at the end of "A Vending Machine" and in "Which Design Should You Use?". The second is the comparison's recap, so the repeat is doing work.
- `MouseAction` members are called "bare names" although each carries a string value. The contrast is with the vending events' per-event data, which the next sentence states.
- Exercise 2 says "using `state_machine.py`" and the solution inlines it. The Solutions files inline chapter listings as a practice.
- The hand-written `StateMachine.__init__()` in both engines stays, per the standing exemption in `deep_review_db.md`.
