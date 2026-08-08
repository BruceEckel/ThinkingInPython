[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Six fixes were applied directly and are already in `Chapters/31_State_Machines.md`
(read the diff): "`if-else` clause" corrected to "`match` statement" (the listing
uses `match`); `run_all()`'s one-sentence description untangled; "`State` pattern"
italicized to match the rest of the chapter; a note in *An Unexpected Input* that a
self-transition re-runs the state's action; a note in *The Engine* that a `None`
condition always matches and so must come last; a note that the `...` in
`Callable[..., bool]` leaves the row's methods unchecked against the row's key; and
a note that the vending table is built in `__init__()` because its entries are bound
methods. Everything below is reported rather than applied.

---

[] Reject

**Style audit: the table-driven `StateMachine.__init__()` only assigns its two
parameters.**

```python
class StateMachine:
    def __init__(self, initial: Enum, table: Table) -> None:
        self.state = initial
        self.table = table
```

`thinking-in-python-skill.md`: "A class whose `__init__()` only assigns parameters
or defaults to fields is a `@dataclass` (frozen unless mutation is the point).
Write the manual form only when the code is teaching it... and then say why." Nothing
here says why, so this is the unexplained deviation the style pass looks for.

The honest counter-argument, which is why this is reported rather than applied: this
class is a base a reader subclasses with a hand-written `__init__()`, and a
`@dataclass` base under a manual-`__init__()` subclass is a slightly odd pairing;
the generated `__eq__`/`__repr__` would also try to compare and print a dict of
bound methods, which means nothing. Two ways out, pick one:

1. Convert it: `@dataclass class StateMachine: state: Enum; table: Table`. The field
   has to be named `state` (not `initial`), so `VendingMachine.__init__()`'s
   `super().__init__(State.QUIESCENT, table)` still works positionally.
2. Keep it and add one clause to the prose saying the engine is written out by hand
   because a reader is meant to subclass it and see the two attributes it owns.

Recommendation: (2). It is the smaller change and the class genuinely reads better
as a framework than as a record.

The same rule brushes `mouse_trap2.py`'s `TableState.__init__()`, which only sets
`self.transitions = {}`. That one has a real reason not to become a bare annotation
(`transitions: dict[object, State]`): the empty dict is what turns a state whose
table you forgot to fill into `TableState has no transition for ...` instead of an
`AttributeError`. Worth half a sentence in the prose if you touch that paragraph
anyway.

---

[] Reject

**Both engines raise a bare `RuntimeError`, and the GUI catches it bare.**

`TableState.next()` (line 283), the table-driven `handle()` (line 453),
`test_no_transition_raises` (line 705) and `vending_view.py`'s `send()` (line 764)
all traffic in plain `RuntimeError`. `send()`'s

```python
except RuntimeError:
    vm.message = "not allowed yet"
```

swallows any `RuntimeError` from anywhere inside `handle()`, including one raised by
a buggy action method, and reports it to the user as "not allowed yet." The book's
own style rule is to catch the specific exception type you can handle, and its
naming rule ("Exception names need no `Error` suffix") points at the fix.

Proposed: define `class NoTransition(RuntimeError)` in the table-driven engine, raise
it from `handle()`, catch it in `vending_view.py` and assert it in the test. Whether
`mouse_trap2.py`'s `TableState` should share the name is a judgment call — the two
engines are otherwise independent, and sharing would force `mouse_trap2.py` to import
from `tabledriven/`, which the chapter deliberately keeps separate. Recommendation:
add `NoTransition` to the table-driven engine only, and leave `TableState`'s
`RuntimeError` alone, since that listing's point is the table, not the exception.

Cost: touches three listings, one test, and the paragraph at line 378 ("its `next()`
raises an exception on anything else"), plus the `#:`-free test file.

---

[] Reject

**The chapter has no closing section, and its neighbors do.**

26 ends with *One Surrogate, Two Intents*, 27 with *Which Factory Should You Use?*,
29 with *Telling the Wrappers Apart*, 30 with *What Stayed Constant*, 32 with *One
Type or Many*, 33 with *One Dispatch Is Enough*. 31 ends on a `tkinter` listing and
goes straight to Exercises, which leaves the chapter's central question — you have
now been shown two designs, when do you use which — answered only in fragments
scattered across four places: the intro (line 15), *An Unexpected Input* (line 367),
the "Adding a state or an input is now a local change" paragraph (line 641), and the
message-versus-print paragraph (line 709).

Proposed: a short `## Which Design Should You Use?` between `vending_view.py` and
`## Exercises`, pulling those threads together. Roughly: each-state-decides suits a
machine whose states have real behavior and few transitions, and reads well when the
transitions are obvious from the state's own name; one-table suits a machine you
build from a diagram, whose inputs carry data, or whose transitions need conditions;
the tell is whether you would rather read the transitions per state or all at once.

Cost: adds a heading between the GUI listing and the exercises. Nothing links to
that position. If you would rather not add a section, the paragraph at line 641 is
where this would go instead.

---

[] Reject

**Exercises 6 and 7 are one-line restatements of exercise 2.**

- 2. "Apply the table-driven `StateMachine`... to a washing-machine problem. Give one
  `(state, input)` pair two rows told apart by a condition..."
- 6. "Create an elevator state machine system using `tabledriven/state_machine.py`,
  whose transitions can carry conditions."
- 7. "Create a heating/air-conditioning system using `tabledriven/state_machine.py`."

All three are "build a table-driven machine for domain X," and only 2 says what
would make the answer right. `ADVERSARIAL.md` already flags 6 and 7 by name as
legacy exercises that never got the treatment the earlier chapters' did.

Meanwhile nothing in the set exercises the two things this review found readers most
likely to get wrong: that the engine keys on `type(event)` exactly, and that an
unconditional row must come last.

Proposed: keep 6 and 7 (both have worked solutions) but give each a specific
requirement, and add one that bites on exact-type dispatch. For example:

> 6.  Create an elevator state machine using the table-driven engine. Give the
>     "doors closing" state two rows for the same input, one guarded by a
>     door-obstruction condition.
> 7.  Create a heating/air-conditioning system using the table-driven engine.
>     A single `TemperatureReading` input must be able to lead to heating, cooling,
>     or idle, decided entirely by conditions on one `(state, input)` key.
> 9.  Add a `Nickel` class deriving from `Money` to `vending_machine.py` and feed
>     one to the machine without touching the table. Explain the exception, then
>     make it work two ways: by adding a row, and by making `Nickel` an instance of
>     `Money` rather than a subclass. Say which you would ship.

Cost: renumbering. Exercise 5 refers to "exercise 1" and the prose at line 83 refers
to "exercise 3"; adding at the end avoids both, which is why the new one is 9.
`Solutions/31_State_Machines.md` would need the new answer, and its numbering is
already broken (see the first finding).

---

[] Reject

**`mouse_trap2.py` sits under `## Each State Decides` with no heading of its own,
which makes it hard to refer to and hard to find.**

The section runs 350 lines and holds two complete mousetraps plus the `state.py` /
`state_machine.py` framework. The chapter then refers to them as "version 1" and
"version 2" (line 369 onward) with no headings carrying those names. Proposed:
`### A Table Inside Each State` immediately before "While the use of `match` inside
the `next()` methods is perfectly reasonable" (line 251), and optionally
`### One State Class per Behavior` before "Here's the first version of the mousetrap
program" (line 132). Cost: `heading_links.py` will want new anchors only if
something links to them; nothing does today.

---

[] Reject

**Lines 78-83: the stated reason the constructor-starts-the-engine trap is safe
here does not name the mechanism that makes it safe.**

Current text:

> The constructor also runs the initial state,
> the construction-starts-the-engine choice that drew a warning in that chapter.
> It is safe here because the state objects are stateless singletons,
> fully formed before any machine exists.

The trap in [Don't Start the Engine in the
Constructor](25_Template_Method.md#dont-start-the-engine-in-the-constructor) is
about the *machine's* half-built state: `super().__init__()` runs the engine before
the subclass finishes its own `__init__()`. What actually protects this chapter is
that (a) `MouseTrap.__init__()` has nothing to assign after its `super().__init__()`
call, and (b) `Waiting.run()` touches nothing on the machine. Whether the state
objects are "stateless" is a separate question, and the answer changes twenty
listings later: `mouse_trap2.py`'s `TableState` objects each carry a `transitions`
dict, so they are not stateless singletons at all (they happen to be filled in
before any `MouseTrap()` is built, which is the property that matters and is not the
one the sentence claims).

Proposed replacement for those two lines:

> It is safe here for two reasons that are easy to lose:
> `MouseTrap.__init__()` assigns nothing after its `super().__init__()` call,
> and no state's `run()` reads anything off the machine.

The following sentence ("A `State` whose `run()` reads attributes off the machine
revives the trap, which is worth remembering during exercise 3") then lands as the
natural consequence rather than as a new idea.

This is one end of the 25 → 31 cross-chapter thread; the 25 end needs no change.

---

[] Reject

**Line 412: "An enum member has no room for the twenty-five cents" is not true, and
it is the load-bearing sentence of the paragraph that motivates the whole
table-driven design.**

An `Enum` member has exactly that room: `class Coin(Enum): QUARTER = 25` carries the
value, and `add_money()` could read `coin.value`. Two separate enums, `FirstDigit`
and `SecondDigit`, would even keep the two digit positions apart under the engine's
`type(event)` key, since each enum is its own type. A reader who knows enums will
stop here.

The real reason inputs become classes is narrower and more interesting: an enum
fixes its members when the enum is written, so it can only carry values from a
closed set decided in advance, and every member of one enum shares one dispatch key.
Classes let an event carry a value that was not known when the code was written (a
bill validator's amount) while still being its own dispatch key.

Recommended replacement for that one line:

> An enum fixes its members in advance, so it can carry only the values you knew
> about when you wrote it, and every member of one enum arrives under the same
> dispatch key.

Alternative if you want to keep the sentence short and concrete: drop the line
entirely. The two sentences before it ("each input becomes an object of its own
class, and the table keys on that class rather than on a value") already make the
point without the shaky justification.

---

[] Reject

**`tabledriven/state_machine.py` and `state_machine.py` are two different modules
with the same name in one chapter, and they shadow each other in a shared process.**

The chapter names the collision ("The names restart here. `tabledriven/state_machine.py`
holds a different `StateMachine` from the one above") but treats it as a naming
coincidence rather than a hazard. It is the hazard `thinking-in-python-skill.md`
warns about under "A module already in `sys.modules` is never re-resolved from
`sys.path`... Give a widely-imported shared module a distinctive name instead of a
common one."

Reproduced in this workspace. Dropping a test for the *first* design beside the
mousetrap, then running the chapter's suite the way `make gate` does:

```
# build/examples/31_State_Machines/test_aa_mouse.py
import inspect
from state_machine import StateMachine
def test_which_module() -> None:
    print(inspect.getsourcefile(StateMachine))
    assert hasattr(StateMachine, "run_all")
```

```
$ uv run pytest build/examples/31_State_Machines -q -s
.../31_State_Machines/tabledriven/state_machine.py
AssertionError: wrong state_machine module!
```

`tabledriven/test_vending.py` is collected first, its import caches
`state_machine` in `sys.modules`, and the chapter-root test silently receives the
table-driven engine. `validate_output.py` is safe only because it clears
`sys.modules` after every block; nothing else in the loop does.

Proposed change: rename the second engine to `tabledriven/table_machine.py`. Touches
the `# tabledriven/state_machine.py` marker line, the `from state_machine import
StateMachine, Table` in `vending_machine.py`, and four prose mentions (the "The names
restart here" paragraph and exercises 2, 6 and 7). It does **not** touch the
`#the-engine` anchor that `Chapters/32_Multiple_Dispatching.md` links to.

Cost, and the reason this is reported rather than applied: `Solutions/31_State_Machines.md`
defines its own shared copy under the name `state_machine.py` and every solution
imports it, so the rename has to land in both trees at once, and `Solutions/` is
outside this review's scope. If you would rather keep the name, the fallback is one
sentence in the "The names restart here" paragraph saying the two must never be
imported into the same process, which at least tells the reader why their own test
file broke.

---

[] Reject

**`Solutions/31_State_Machines.md` has a stray exercise 1, so all nine solution
numbers are off by one against the chapter's eight exercises.**

`Solutions/31_State_Machines.md`'s `## 1. A connection limiter, with a proxy that
releases on check-in` is a *Surrogate* exercise, not a state-machine one. It is the
same assignment as `Chapters/26_Surrogate.md` exercise 5 ("a fixed number of
connections ... hand out a proxy ... release the connection back to the system"),
which already has its own worked answer at `Solutions/26_Surrogate.md`
`## 5. A connection pool that hands out proxies`. `ADVERSARIAL.md` line 203 still
says "Chapter 31: nine exercises," which dates the leftover: the chapter used to
carry that exercise and it was moved to 26 without deleting the solution.

The consequence is that every solution in the file answers the wrong-numbered
exercise:

| Chapter exercise | Solution heading |
| --- | --- |
| 1 `UnpredictablePerson`/`Prozac` | 2 |
| 2 washing machine | 3 |
| 3 word-driven, per-state tables | 4 |
| 4 single transition table | 5 |
| 5 mood machine on `state_machine.py` | 6 |
| 6 elevator | 7 |
| 7 heating/air-conditioning | 8 |
| 8 `mouse_move_generator()` | 9 |

Proposed change (in `Solutions/`, which this review is not allowed to edit): delete
the `## 1. A connection limiter...` block and renumber the remaining eight headings
down by one, so `## 2.` becomes `## 1.` and so on. Also rename the extracted files
in the renumbered blocks (`# exercise_2.py` → `# exercise_1.py`, etc.) and run
`make prune-examples` afterwards, since `SolutionsCode/31_State_Machines/exercise_9.py`
will become orphaned. Also worth correcting `ADVERSARIAL.md` line 203 to "eight
exercises."

The deleted solution is not lost work: `Solutions/26_Surrogate.md` #5 is the better
of the two (it uses `__getattr__()` forwarding and a context manager, where the ch31
copy hand-forwards `query()` and relies on the caller remembering `check_in()`). The
ch31 copy also opens with `from __future__ import annotations`, which the book drops
everywhere else under PEP 649.

---

[] Reject

**Line 469: "An event's dispatch class must appear in the table verbatim."**

"Verbatim" describes text, not a class. Proposed: "An event's dispatch class must
appear in the table by name; a subclass will not do." That also repeats the
consequence, which is the half a reader needs.

---

[] Reject

**`TableState.next()` uses `from None`, against the book's own chaining rule.**

```python
except KeyError:
    raise RuntimeError(
        f"{type(self).__name__} has no transition "
        f"for {event}") from None
```

`thinking-in-python-skill.md`: "When raising a different exception in response to one
you caught, use `raise NewException(...) from original` to preserve the chain." The
deviation is defensible here — the `KeyError` repeats the event the message already
names — but it is unexplained, and this is one of the few `from None`s in the book,
so a reader may take it as the default. Proposed: either switch to `from e`, or add
half a sentence after the listing: "`from None` drops the `KeyError`, which would
only repeat the event the message already names."

---

[] Reject

**Line 111: "For test code, a text file provides the sequence of mouse inputs."**

`mouse_moves.txt` is not test code; it is the demo's input, read at the bottom of
both mousetrap listings. There is no test for either mousetrap. Proposed: "A text
file supplies the sequence of mouse inputs."

---

[] Reject

**Line 47: "created once at module level" is not where the states are created.**

`mouse_trap.py` creates the four state objects in `MouseTrap`'s *class body*
(`waiting: ClassVar[State] = Waiting()`), not at module level. The distinction
matters two paragraphs later, where the chapter argues about what exists when.
Proposed: "...where every state is created once, as a class attribute."

---

[] Reject

**Line 255: "In Python that is no obstacle" contrasts with a language never named.**

The paragraph says you cannot write a state's table inside its own class, then
answers "In Python that is no obstacle," which reads as a comparison against some
other language the sentence forgot to mention — and the obstacle is real in Python
too, which is why the tables move to the bottom of the file. Proposed: cut the
sentence and let the next one carry it, so the paragraph ends "...which do not all
exist until every class definition runs. Define the classes first, then fill in the
tables at module level, after all the state objects exist."

---

[] Reject

**Line 388: "A pure state machine" — "pure" is doing no work.**

Nothing earlier in the chapter has established impure state machines, and "pure"
collides with the functional-programming sense. The sentence means a machine whose
behavior lives entirely in one table. Proposed: "A fully table-driven design can go
further and represent the entire machine as a single transition table."

---

[] Reject

**Small wording, no argument attached:**

- Line 67: `for i in inputs` in `run_all()`. `i` reads as an index everywhere else in
  the book, and the method it feeds spells the same thing `event`
  (`State.next(self, event: object)`). Proposed: rename to `event` in the listing
  and in the sentence at line 106 that quotes `print(i)`. Left unapplied because the
  `i` is a deliberate carry-over from the Java edition's `for (Input i : inputs)`.
- Lines 433-434 and 488-489 make the same claim twice, once as a code comment
  ("A state is an `Enum` member, so a misspelled state is a type error rather than a
  silent dead end") and once as prose ("The states are an `Enum`, so the type checker
  catches a misspelled state name instead of letting it fail silently at runtime").
  The prose version is also imprecise: with an `Enum`, a misspelling is a checker
  error *and* an `AttributeError` at runtime — the silent dead end is what you get
  from bare strings, which is what the comment says and the prose loses. Proposed:
  keep the comment, and change the prose to "The states are an `Enum` rather than
  strings, so a misspelled state name is a type error instead of a transition that
  never fires."
- Line 53: "Thus you can see it's an expansion of the idea of the *State* pattern"
  opens with three words of throat-clearing. Proposed: "It expands the *State*
  pattern: `run()` does something different depending on the state the system is
  in." Left unapplied because the sentence is original *Thinking in Java* prose and
  the voice call is yours.

---

## Cross-chapter

**`Chapters/32_Multiple_Dispatching.md`, lines 221-224.** No change needed, but
recorded so the thread's two ends stay together. 32 says:

> Two properties of the lookup carry over from the [table-driven state
> machine](31_State_Machines.md#the-engine). The match is on classes exactly, so a
> subclass of `Paper` finds none of `Paper`'s rows. And a missing pair raises
> `KeyError` at the first duel that needs it, the fail-fast policy that suits a table
> under construction...

Both halves still hold against 31 after this review: the `#the-engine` anchor is
unchanged, the exact-type paragraph at 31's line 464 is unchanged, and 31's
fail-fast policy statement at lines 381-383 is unchanged. The one thing that would break
it is the `NoTransition` proposal above — 32 says "raises `KeyError`" about its own
table and 31 currently says "raises an exception," so introducing a named exception
in 31 makes 32's parallel slightly less exact. If you take the `NoTransition`
finding, reread 32's line 223 and decide whether it wants "raises at the first duel"
instead of naming `KeyError`.

`Chapters/37_Pattern_Refactoring.md`'s `bins[type(t)]` (line 282) is the third end of
this thread and needs nothing from 31.

**`Chapters/25_Template_Method.md`.** The
`premature_engine.py` → `StateMachine.__init__` thread is intact from the 25 side.
The 31 side is the "Lines 78-83" finding above, which changes only 31.

**`ADVERSARIAL.md` line 203** says "Chapter 31: nine exercises." The chapter has
eight. See the first finding.
