> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 31_Patterns--State_Machines (third review, 2026-10-15)

This third review reads the chapter and its Solutions file after the October rework:
the states as `Enum` rows (`TrapState`), the per-state `action`, the split `trap_states.py`,
and the Moore/Mealy framing of the two designs.
It ran during the open editing pass (`edit-start-31`), on the chapter as committed in 9a21c461.
I checked the three `ty` claims with scratch probes against `build/examples` on `ty` 0.0.87:
a member tuple holding the message alone, or the two in the wrong order, passes `ty`
(the first fails at import with `TypeError: _value_ not set in __new__`, the second at the first `next()` call),
Pyright reports both,
pairing `Column` with `choose_row()` draws `invalid-argument-type`,
and the same rule written inline as the constructor argument passes.
Every `#:` marker matches a direct run.
A verify-claims agent (Opus) checked about sixty Solutions claims and all nine solutions' runs;
its four errors are applied below.
`tip verify-ch CH=31` passes 27 of 27.
One block needs your decision.

## Applied directly

Chapter:

- Opening of "Each State Decides": "a record holding the function that produces the next `State` and an action that produces the `State`'s behavior" named two of three fields and used "produces" twice. Now names the message, the `next` function, and the action.
- "`step()` prints `mouse appears`" used `step()` four listings before its definition. Now "`print()` shows a member as its value".
- "runs when it is called" and "when a mouse is caught": active voice.
- "`run()` fires on entry" is "`run()` is an entry action", the literal term.
- "the one input for which `waiting()` has no `case`" was false: five of the six moves have no `case` there. Now "an input that `waiting()`'s `case _` alone matches".
- "no state's `run()` reads anything off the machine": positive form, "reads the state's own fields alone".
- "two facts the trace shows": the trace shows the first fact alone (the second is every state against every move). Now "checks two facts: the nine moves bring the trap back to `Waiting`, as the trace shows, and ...".
- "joins the test with no edit to the test": "is tested as soon as it exists".
- "Every state therefore needs a transition function of its own" overstated the alias consequence; two states that share a function stay distinct when their messages differ. Now "Two states that share a transition function must differ in their message or their action".
- "`State` is now an `Enum` of names ... The states in this design are bare names. The table holds all the behavior." said the same thing twice. Merged into one sentence.
- The Engine section explained `Rule[I]` with the `Column` example that the Vending Machine section explains again. The Engine keeps the general statement; the concrete example stays where the rule is built.
- "the input class was checked where the rule was built": active, "the checker matched each input class to its methods where the rule was built".
- "It only needs a plain `Enum` with `auto()` initialization": "only" before a code span, and "need no value" as the reason. Now "carry no data, and the demo prints a state by its `name`, so a plain `Enum` with `auto()` values is enough".
- "That exactness lets the table keep separate entries for `Row` and `Column`" credited exact-type keying with something `isinstance()` dispatch would also do (the two classes are unrelated). Cut; the subclass exclusion keeps the paragraph's point.
- "The list is bound to `rules`": "The listing binds the list to `rules`".
- "The message alone leaves you inferring the condition from the quantity": "would leave you to infer it from the `left` count".
- "A member is one frozen record shared by every machine" held for the first design only; the table design's members are bare `Enum` members. Now "one object shared by every machine that uses it, and in the first design a frozen record besides".
- "supply guards" after "what a library supplies": "offer guards".
- `tools/data/positional_refs_baseline.txt`: "by the first call" accepted (a runtime call, not a listing position); the stale `Happy.next()` entry from the class-based Solutions removed.

Solutions:

- Exercise 2: "`trap_states.py`'s two-element tuples" was stale since `HOLDING` gained its third element. Now "the tuples in `trap_states.py`".
- Exercise 4 hint: "moves every rule out of the state classes" named the old design. Now "out of the states' transition functions".
- Exercise 4 hint: "The controller then holds no rules, only a lookup" was false (`TableController` holds the table). Now "holds the table and does one lookup per word".
- Exercise 5: "leads only to `APPEARS`" is "whose one successor is `APPEARS`".
- Exercise 8: "from `15 IDLE` through `30 IDLE`" misnamed the last line; the readings end at 20. Now "to `20 IDLE`".
- Exercise 9 heading: "A `Nickel` the table has never heard of" stranded its preposition. Now "A `Nickel` with No Rule"; nothing linked the old anchor.
- Exercise 9: "when the new subclass really does behave differently, as `Row` and `Column` do" called two unrelated classes subclasses and carried "really". Now "when the new input behaves differently".

## Findings

### `Row` is an `Enum` but `Column` is a record, and the prose says why for one of them

In "A Vending Machine", after the input classes:
"`Row` is an `Enum` whose four members name the rows, so a row outside the grid is a type error at the call rather than an index error inside `_slot()`."
`Column` is a `@record` holding an `int`, so `Column(7)` is accepted by the checker and fails inside `_slot()` with the index error the sentence says `Row` avoids.
A reader who takes the sentence as advice asks why the column did not get the same treatment, and the chapter does not say.

Two fixes, and I recommend the first:

1. Make `Column` an `Enum` like `Row`, with members `C0`..`C3` valued 0..3 and the same `__str__()` ("col 1").
   `_slot()` reads `col.value`, so it is unchanged, and `Column(1)` in `vending_demo.py` and `test_vending.py` still works, since calling an `Enum` with a value looks the member up.
   The only prose change is "The inputs `Money` and `Column` are records" becoming "`Money` is a record", and the `Row` sentence becomes "`Row` and `Column` are `Enum`s whose members name the rows and columns, so a selection outside the grid is a type error at the call rather than an index error inside `_slot()`."
   The 4x4 grid is then stated twice, in the comprehension and in the two enums, which is the one thing I would hold against it.
2. Keep `Column` a record and add one sentence saying so: "`Column` stays a record holding an `int`, so a column outside the grid is still an index error inside `_slot()`; exercise 9's `Nickel` shows the same gap from the other side."
   This keeps the listing but leaves the asymmetry as a thing the chapter explains rather than removes.

I did not make the change because it edits a listing during your editing pass and the demo's `Column(1)` reads differently once `Column` is an `Enum` (a lookup rather than a construction), which is a call about the listing's voice.

`[] Reject`

## Considered and declined

- Exercise 6 presses `Start` during `FILLING`, the first state after the starting `Start`; the exercise says "in the middle of a cycle". A press during `WASHING` would match the wording more closely (one more `Full()` before the second `Start`, and the marker becomes `no rule from WashState.WASHING on Start`), but `FILLING` is inside the cycle and the solution's point, what the caller does with `NoTransition`, holds as written.
- "Nothing here needs a `switch`, reflection, or a `Condition`/`Transition` class hierarchy" stays, as the second review ruled.
- The chapter writes `Waiting` and `Holding` (the printed names) in some sentences and `WAITING` and `HOLDING` (the members) in others. Each use matches what it points at, the trace or the enum, so I left both.
- "the name resolves because annotations are evaluated lazily" could link PEP 649 in chapter 17, but the sentence is a reminder, not the chapter's subject, and chapter 8's forward-reference row already covers the reader who needs it.
