[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/31_State_Machines.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/31_State_Machines` (5 tests), all seven runnable
scripts run, and `tabledriven/vending_view.py` is correctly skipped
via `tools/data/norun.txt`. Claims probed on the pinned toolchain:
`StrEnum` members print as and compare equal to their values (the
markers show `mouse appears`, not `MouseAction.APPEARS`); the first
nine moves of `mouse_moves.txt` do exercise all six transitions in the
trap; the vending arithmetic in every marker line checks out
(`(c + 1) * 25` pricing, 150 in, 50 spent twice, 75 > 50 too
expensive, the seeded sold-out slot); and the "forgot to fill the
table" probe surfaced the one factual error (below). Outgoing anchors
into 25, 26, 12, 28, and 23 all resolve, and the inbound anchors other
chapters rely on (`#the-engine` from 32 and 37,
`#table-driven-state-machine` from 35, `#a-vending-machine` from 45)
are untouched. `Solutions/31_State_Machines.md` covers all nine
exercises, but three solutions did not do what their exercises
explicitly require; those are rewritten (see the applied list). No
live blocks remain: every finding had one defensible answer.

## Applied directly

- Table-inside-each-state section: the unfilled-table error was quoted
  as `TableState has no transition for ...`; the message names the
  concrete state class (`type(self).__name__`), probe-verified as
  `Waiting has no transition for mouse appears`. Now quotes `Waiting`.
- Cut "as exercise 3 will show" from the constructor-trap paragraph.
  Exercise 3 (and its solution) is the word-driven turnstile; nothing
  in it revives the read-attributes-off-the-machine trap, so the
  promise dangled.
- Exercise 3 reworded to match its solution and its own remainder: the
  sentence "Each state stores a reference back to the controller
  object so that it can request the state change" contradicted the
  exercise's own `next_state()`-returns-the-next-state design and the
  solution, which returns a state name and lets the controller move.
  Also "override a `next_state()` method that holds its own transition
  table" is now "give each state subclass its own transition table,
  which its `next_state()` method consults" (the solution holds the
  table in a class attribute, consulted by the base method).
- `Solutions/31_State_Machines.md` exercise 2 rewritten: the exercise
  requires "one `(state, input)` pair two rows told apart by a
  condition, such as a load too heavy for the fast spin", and the
  solution had no conditions (its prose even said "no branching").
  `(RINSING, RinseDone)` now carries a `too_heavy()` slow-spin row
  over an unconditional fast-spin row, with `Start` carrying
  `load_kg`. The alternative, deleting the requirement from the
  exercise, would have removed the one thing the exercise drills.
- Solutions exercise 7 rewritten for the same reason: the exercise
  requires "a single `TemperatureReading` input ... decided entirely
  by conditions on one `(state, input)` key", and the solution used
  four distinct event types and zero conditions. Now one
  `TemperatureReading` type, a three-row `(IDLE, TemperatureReading)`
  group (heat, cool, or stay), and two-row groups on the running
  states; the closing prose keeps the old solution's
  both-slots-optional observation.
- Solutions exercise 6 extended: the exercise names "the 'doors
  closing' state two rows for the same input, one guarded by a
  door-obstruction condition", which the solution lacked (it had the
  three-way call-button pick but no doors-closing state). Added
  `DOORS_CLOSING`, `CloseDoors`, and a `DoorSensor(blocked)` pair
  (obstructed reopens, clear finishes in `IDLE`), keeping the
  call-button trio.
- Solutions `table_machine.py` brought back in line with the chapter's
  engine: `handle(self, event: Any)` is now `event: object` with the
  `Any` import dropped (the file claims to be "the book's generic
  table-driven engine", and the chapter version uses `object`;
  typing-precision-over-Any is house policy). Verified clean under
  `ty` and ruff.
- `NoTransition` docstring in both the chapter and the solutions copy:
  "The table has no row for this state and event" is now "No table row
  matched this state and event", since the exception also fires when a
  key exists but every condition in its group returns `False`.
- Engine section, teaching addition for that same case: after the
  catch-all-row sentence, "A group with no such catch-all row can
  still match nothing: if every condition returns `False`, `handle()`
  falls through to the same `NoTransition` a missing key raises."
- Vending section, teaching addition (lookalike pair): why the states
  are `Enum` with `auto()` while `MouseAction` was a `StrEnum`;
  nothing parses these states from text, so they need no string
  values.
- The by-hand-not-dataclass justification for the engine's
  `StateMachine` now gives a reason that survives scrutiny: the
  constructor renames what it stores (`initial` in, `state` kept),
  which a generated `__init__()` cannot express. The old reason,
  "because a reader should subclass it", was untrue (dataclasses
  subclass fine).
- Module-cache paragraph: "under its basename" is now "under its
  import name" (the `sys.modules` key is the import name, not a
  filename), and "never looks it up again once it is there" is now "a
  later `import` takes the cached module without looking at any file"
  (watch-list "never", and the new phrasing states the mechanism).
- Exercise 9 "Say which you would ship" is now "Say which you would
  keep", and the solution's "Ship fix 2" is now "Keep fix 2"
  (watch-list "ships").
- Base-class paragraph: "worth its two lines" is now "worth its few
  lines"; the class body is four lines.
- Small prose repairs: "easier to quickly read and understand the
  state transitions from looking at the table" tightened to "easier to
  read the state transitions from a table"; dropped "only" from "would
  only repeat the event"; "plain methods" is now "ordinary methods";
  solutions prose dropped "itself never branches"/"only asks"
  ("does not branch"/"asks"), "only ever leads" ("leads only"),
  "exists precisely so" ("exists so"), and fixed the exercise-4
  solution calling the per-state design "exercise 4" (it is
  exercise 3).
- Ran `make reflow CH=31` (no further changes needed).

## Considered and declined

- The intro's "the key distinction between this design and the next"
  stays although "A Table Inside Each State" sits between the two
  designs it contrasts: `mouse_trap2.py` still has each state deciding
  from its own table, and the Table-Driven section opens by drawing
  the line correctly ("A fully table-driven design can go further").
- The engine listing's header comment ("A state is an Enum member, so
  a misspelled state is a type error...") overlaps the prose before
  the vending listing, but `table_machine.py` is a reusable file a
  reader may open alone, so the comment stays.
- `state.py`'s `next(self, event: object)` keeps `object` rather than
  a narrower event type: the base class is the framework half, and the
  chapter's second design feeds it non-enum events.
- The `mouse_moves.txt` parsing triple (read, strip, filter comments)
  is duplicated at the bottom of both mousetrap files; a shared helper
  would break each listing's self-containment for a three-line saving.
- Chapter 26's `state.py` and this chapter's `state.py` share a
  basename, which the module-cache paragraph might seem to warn about,
  but they live in different chapter directories and no program
  imports both.
