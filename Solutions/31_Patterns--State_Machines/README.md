# State Machines: Solutions

Several exercises below reuse the book's generic table-driven engine,
so it appears once here, in its own file that those exercises import:

```python
# table_machine.py
from collections.abc import Callable
from enum import Enum

type Transition = tuple[
    Callable[..., bool] | None,
    Callable[..., None] | None, Enum
]
type Table = dict[tuple[Enum, type], list[Transition]]

class NoTransition(RuntimeError):
    "No table row matched this state and event."

class StateMachine:
    def __init__(self, initial: Enum, table: Table) -> None:
        self.state = initial
        self.table = table

    def handle(self, event: object) -> None:
        for condition, action, next_state in self.table.get(
                (self.state, type(event)), []):
            if condition is None or condition(event):
                if action is not None:
                    action(event)
                self.state = next_state
                return
        raise NoTransition(
            f"no transition from {self.state!r} "
            f"on {type(event).__name__}")
```

## 1. `UnpredictablePerson` with a `Prozac` mood

> Using [*State*](../../Chapters/26_Patterns--Surrogate.md#state),
> make a class called `UnpredictablePerson` that changes the kind of response to its `hello()` method depending on its current `Mood`.
> Add another kind of `Mood` called `Prozac`.

<details>
<summary>Where to look</summary>

[*State*](../../Chapters/26_Patterns--Surrogate.md#state) shows a surrogate that forwards a call to whichever state object it currently holds.
Define a `Mood` protocol with one `hello()` method, and give `UnpredictablePerson` a `change_to()` that swaps the held object.
A new mood is another class with the same method, so the person needs no change.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Protocol

class Mood(Protocol):
    def hello(self) -> str: ...

class Happy:
    def hello(self) -> str:
        ...

class Grumpy:
    def hello(self) -> str:
        ...

class Prozac:
    def hello(self) -> str:
        ...

class UnpredictablePerson:
    def __init__(self, mood: Mood) -> None:
        ...

    def change_to(self, mood: Mood) -> None:
        ...

    def hello(self) -> str:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from typing import Protocol

class Mood(Protocol):
    def hello(self) -> str: ...

class Happy:
    def hello(self) -> str:
        return "Great to see you!"

class Grumpy:
    def hello(self) -> str:
        return "What do you want?"

class Prozac:
    def hello(self) -> str:
        return "Everything is wonderful. Just wonderful."

class UnpredictablePerson:
    def __init__(self, mood: Mood) -> None:
        self._mood = mood

    def change_to(self, mood: Mood) -> None:
        self._mood = mood

    def hello(self) -> str:
        return self._mood.hello()

person = UnpredictablePerson(Happy())
print(person.hello())
#: Great to see you!
person.change_to(Grumpy())
print(person.hello())
#: What do you want?
person.change_to(Prozac())
print(person.hello())
#: Everything is wonderful. Just wonderful.
```

`Prozac` needs nothing beyond `Happy` and `Grumpy`'s own shape: one
`hello()` method. `UnpredictablePerson` names no specific mood, so a
third mood changes the `Mood` object that `change_to()` installs, and
no code in `UnpredictablePerson`.
`UnpredictablePerson` is the
[*State* surrogate](../../Chapters/26_Patterns--Surrogate.md#state),
applied to a new domain.

</details>
</details>
</details>

## 2. The mood machine, on the first design

> Turn exercise 1's `UnpredictablePerson` into a state machine using `state_machine.py`,
> the first design, where each state decides the next one.

<details>
<summary>Where to look</summary>

[Each State Decides](../../Chapters/31_Patterns--State_Machines.md#each-state-decides) gives states a `run()` and a `next()` that takes an input and returns the successor state.
Make each mood a state, make the inputs small classes, and test them with `isinstance()` inside each `next()`.
A state that stays the same returns itself.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Iterable
from typing import Protocol

class State(Protocol):
    def run(self) -> None: ...
    def next(self, event: object) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        ...
    def run_all(self, inputs: Iterable[object]) -> None:
        ...

class TakePill:
    def __repr__(self) -> str:
        ...

class Annoy:
    def __repr__(self) -> str:
        ...

class Calm:
    def __repr__(self) -> str:
        ...

class Happy:
    def run(self) -> None:
        ...
    def next(self, event: object) -> State:
        ...

class Grumpy:
    def run(self) -> None:
        ...
    def next(self, event: object) -> State:
        ...

class Prozac:
    def run(self) -> None:
        ...
    def next(self, event: object) -> State:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the final `return self` in `Happy.next()`,
`ty` reports an `invalid-return-type`,
because the method can fall off its end and return `None`.
The demo still prints the same lines, since every input that reaches `Happy` has a branch there,
but if a second `Calm` in a row reaches `Happy`, its `next()` returns `None`,
and `run_all()`'s call to `run()` raises an `AttributeError`.
Each `next()` in the solution ends with `return self`,
so an input a state ignores keeps the machine where it is.

```python
# exercise_2.py
from collections.abc import Iterable
from typing import Protocol

# The chapter's state.py and state_machine.py, inlined:
class State(Protocol):
    def run(self) -> None: ...
    def next(self, event: object) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def run_all(self, inputs: Iterable[object]) -> None:
        for event in inputs:
            print(event)
            self.current_state = (
                self.current_state.next(event))
            self.current_state.run()

class TakePill:
    def __repr__(self) -> str:
        return "TakePill"

class Annoy:
    def __repr__(self) -> str:
        return "Annoy"

class Calm:
    def __repr__(self) -> str:
        return "Calm"

class Happy:
    def run(self) -> None:
        print("Great to see you!")
    def next(self, event: object) -> State:
        if isinstance(event, Annoy):
            return Grumpy()
        if isinstance(event, TakePill):
            return Prozac()
        return self

class Grumpy:
    def run(self) -> None:
        print("What do you want?")
    def next(self, event: object) -> State:
        if isinstance(event, Calm):
            return Happy()
        if isinstance(event, TakePill):
            return Prozac()
        return self

class Prozac:
    def run(self) -> None:
        print("Everything is wonderful.")
    def next(self, event: object) -> State:
        return self

StateMachine(Happy()).run_all(
    [Annoy(), Calm(), TakePill(), Annoy()])
#: Great to see you!
#: Annoy
#: What do you want?
#: Calm
#: Great to see you!
#: TakePill
#: Everything is wonderful.
#: Annoy
#: Everything is wonderful.
```

**Let each state pick its successor.** Each state decides its own
successor. `Happy.next()` answers `Annoy` with a `Grumpy`,
`Grumpy.next()` answers `Calm` with a `Happy`, and both answer
`TakePill` with a `Prozac` that returns itself for everything after.

The states alone hold the transition rules, which
distinguishes this design from the chapter's table-driven one, where
the rules live in a dictionary a reader can audit in one place. Here
they live in the `next()` method of whichever state is current.

Where exercise 1's `UnpredictablePerson` swaps in a whole `Mood`
object through `change_to()`, this version reaches the same moods by
returning a new `State` from `next()`. Both model "a thing that
changes behavior over time." The *State* surrogate suits that job when
each mood needs real per-mood logic. The table-driven machine wins
when the transitions themselves, not the mood behaviors, are the part
worth making explicit and easy to audit.

</details>
</details>
</details>

## 3. A word-driven state machine with per-state transition tables

> Create a *State Machine* system in which the current state and the input together determine the next state.
> Use a `dict` to map a `str` naming a state to its state object.
> Give each state subclass its own transition table,
> which its `next_state()` method consults.
> Feed the machine a sequence of single words,
> such as a text file with one word per line.

<details>
<summary>Where to look</summary>

[A Table Inside Each State](../../Chapters/31_Patterns--State_Machines.md#a-table-inside-each-state) puts a dictionary in each state object and has `next()` consult it.
Here the table maps a word to the name of the next state, with a wildcard entry for words the state ignores.
A controller holding a `dict` of name to state object looks up the current state and asks it for the next name.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import ClassVar

class Controller:
    def __init__(self, initial: str) -> None:
        ...

    def register(self, name: str, state: WordState) -> None:
        ...

    def process(self, word: str) -> None:
        ...

class WordState:
    TRANSITIONS: ClassVar[dict[str, str]] = {}

    def next_state(self, word: str) -> str:
        ...

class Locked(WordState):
    TRANSITIONS = {"coin": "unlocked", "*": "locked"}

class Unlocked(WordState):
    TRANSITIONS = {"push": "locked", "*": "unlocked"}
```

<details>
<summary>Solution</summary>

If `next_state()` indexes the table with `self.TRANSITIONS[word]`,
the first word, `push` while locked, raises `KeyError: 'push'`.
A turnstile ignores a word that changes nothing,
so each table carries a `"*"` entry, and `next_state()` falls back on it through `.get()`.

```python
# exercise_3.py
from typing import ClassVar

class Controller:
    def __init__(self, initial: str) -> None:
        self.states: dict[str, WordState] = {}
        self.current = initial

    def register(self, name: str, state: WordState) -> None:
        self.states[name] = state

    def process(self, word: str) -> None:
        state = self.states[self.current]
        self.current = state.next_state(word)

class WordState:
    TRANSITIONS: ClassVar[dict[str, str]] = {}

    def next_state(self, word: str) -> str:
        return self.TRANSITIONS.get(
            word, self.TRANSITIONS["*"])

class Locked(WordState):
    TRANSITIONS = {"coin": "unlocked", "*": "locked"}

class Unlocked(WordState):
    TRANSITIONS = {"push": "locked", "*": "unlocked"}

controller = Controller("locked")
controller.register("locked", Locked())
controller.register("unlocked", Unlocked())

words = ["push", "coin", "push", "coin", "coin", "push"]
history = [controller.current]
for word in words:
    controller.process(word)
    history.append(controller.current)
print(" ".join(history))
#: locked locked unlocked locked unlocked unlocked locked
```

**Delegate to the current state.** `Controller` asks the current state object what comes next, as
`state_machine.py`'s `run_all()` does when it calls `next()`.

**Look up the next state.** `next_state()` looks the word up in its class's table with
`.get(word, ...["*"])`, so `Controller` has no branch on the current
state or word.

**Give each state its own table.** The machine is the classic turnstile: `push` while locked does nothing (the
`"*"` fallback), `coin` unlocks it, and `push` while unlocked locks it
again. Each state subclass carries its own transition table as a class
attribute.

Reading the words
from a file, one per line, takes one line of code:
`words = Path("moves.txt").read_text().split()`.

</details>
</details>
</details>

## 4. Configuring the machine from one transition table

> Modify the previous exercise so that you can configure the state machine by editing a single transition table.

<details>
<summary>Where to look</summary>

[Table-Driven *State Machine*](../../Chapters/31_Patterns--State_Machines.md#table-driven-state-machine) moves every rule out of the state classes and into data.
Key one `dict` on a `(state, word)` tuple and let its value be the next state.
The controller then holds no rules, only a lookup.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
type Transitions = dict[tuple[str, str], str]

TRANSITIONS: Transitions = {
    ("locked", "coin"): "unlocked",
    ("locked", "push"): "locked",
    ("unlocked", "push"): "locked",
    ("unlocked", "coin"): "unlocked",
}

class TableController:
    def __init__(self, initial: str,
                 table: Transitions) -> None:
        ...

    def process(self, word: str) -> None:
        ...
```

<details>
<summary>Solution</summary>

If the table holds the two rows that change the state and no others,
nothing in the table stands in for exercise 3's `"*"` entries,
and the first word, `push` while locked, raises `KeyError: ('locked', 'push')`.
A dictionary keyed on `(state, word)` has no wildcard,
so the solution writes out the two rows that leave the state unchanged.

The per-state design in exercise 3 spreads the turnstile's rules
across two classes, one dictionary each. A single table keyed by
`(state, word)` collects both dictionaries and makes the whole
machine's behavior editable in one place:

```python
# exercise_4.py
type Transitions = dict[tuple[str, str], str]

TRANSITIONS: Transitions = {
    ("locked", "coin"): "unlocked",
    ("locked", "push"): "locked",
    ("unlocked", "push"): "locked",
    ("unlocked", "coin"): "unlocked",
}

class TableController:
    def __init__(self, initial: str,
                 table: Transitions) -> None:
        self.current = initial
        self.table = table

    def process(self, word: str) -> None:
        self.current = self.table[self.current, word]

words = ["push", "coin", "push", "coin", "coin", "push"]
tc = TableController("locked", TRANSITIONS)
history = [tc.current]
for word in words:
    tc.process(word)
    history.append(tc.current)
print(" ".join(history))
#: locked locked unlocked locked unlocked unlocked locked
```

The per-state design (exercise 3) puts each state's rules with that
state, and reads well when a
state does more than look a word up. The single-table design puts
every rule for the whole machine in one dictionary, and is easier to
audit and edit as a unit. The chapter's own
[table-driven state machine](../../Chapters/31_Patterns--State_Machines.md#table-driven-state-machine)
makes the same trade-off over the per-state `mouse_trap_states.py`.

</details>
</details>
</details>

## 5. `mouse_move_generator()`

> Write a `mouse_move_generator()`,
> a [generator](../../Chapters/23_Patterns--Iterators.md#generators)
> that yields valid `MouseAction` moves in sequence,
> where each possible move depends on the previous one
> (it is another state machine).
> Have it accept an `int` for the number of moves to produce, then stop.

<details>
<summary>Where to look</summary>

In [One State Class per Behavior](../../Chapters/31_Patterns--State_Machines.md#one-state-class-per-behavior), each state's `match` names the `MouseAction` moves that make sense after it.
Write those legal successors as a `dict` from the previous action to a list of allowed next actions, with a starting key for "nothing yet."
Loop `count` times, pick from the list with `random.choice()`, and `yield` the pick, which becomes the previous action.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import random
from collections.abc import Iterator
from enum import StrEnum

class MouseAction(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

NEXT_ACTIONS: dict[MouseAction | None,
                   list[MouseAction]] = {
    None: [MouseAction.APPEARS],
    MouseAction.APPEARS: [MouseAction.RUNS_AWAY,
                          MouseAction.ENTERS],
    MouseAction.RUNS_AWAY: [MouseAction.APPEARS],
    MouseAction.ENTERS: [MouseAction.ESCAPES,
                         MouseAction.TRAPPED],
    MouseAction.ESCAPES: [MouseAction.APPEARS],
    MouseAction.TRAPPED: [MouseAction.REMOVED],
    MouseAction.REMOVED: [MouseAction.APPEARS],
}

def mouse_move_generator(
    count: int, seed: int = 0
) -> Iterator[MouseAction]:
    ...
```

<details>
<summary>Solution</summary>

If you pick from every `MouseAction` and ignore `previous`, the seeded
run prints `RUNS_AWAY TRAPPED APPEARS ENTERS` and
`APPEARS ESCAPES ESCAPES ESCAPES`. The mouse runs away before it
appears and escapes three times in a row, and the type checker passes
the variant, since each move is a valid `MouseAction`. The solution
looks up the legal successors of `previous` in `NEXT_ACTIONS`, so each
pick depends on the move before it.

```python
# exercise_5.py
import random
from collections.abc import Iterator
from enum import StrEnum

class MouseAction(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

NEXT_ACTIONS: dict[MouseAction | None,
                   list[MouseAction]] = {
    None: [MouseAction.APPEARS],
    MouseAction.APPEARS: [MouseAction.RUNS_AWAY,
                          MouseAction.ENTERS],
    MouseAction.RUNS_AWAY: [MouseAction.APPEARS],
    MouseAction.ENTERS: [MouseAction.ESCAPES,
                         MouseAction.TRAPPED],
    MouseAction.ESCAPES: [MouseAction.APPEARS],
    MouseAction.TRAPPED: [MouseAction.REMOVED],
    MouseAction.REMOVED: [MouseAction.APPEARS],
}

def mouse_move_generator(
    count: int, seed: int = 0
) -> Iterator[MouseAction]:
    rng = random.Random(seed)
    previous: MouseAction | None = None
    for _ in range(count):
        previous = rng.choice(NEXT_ACTIONS[previous])
        yield previous

moves = list(mouse_move_generator(8, seed=1))
print(" ".join(m.name for m in moves[:4]))
#: APPEARS RUNS_AWAY APPEARS RUNS_AWAY
print(" ".join(m.name for m in moves[4:]))
#: APPEARS ENTERS TRAPPED REMOVED
```

**Encode the legal successors.** `NEXT_ACTIONS` is a small state machine of its own: a dictionary from
"the action just produced" to "the legal actions that can follow it,"
including the special `None` key for "no action yet," which
leads only to `APPEARS`.

**Remember the last move.** The generator's own state is just `previous`,
the last action it yielded. Each time `list()` calls `next()` on the
generator, the generator picks a legal successor and remembers it
for the following call. `NEXT_ACTIONS` constrains every choice, so every
sequence this generator produces is legal by construction.

`mouse_trap_states.py` accepts any move in any state and lets each
`case _` absorb the moves that make no sense there, so the generator's
table is the stricter of the two.

</details>
</details>
</details>

## 6. A washing machine, table-driven

> Apply the table-driven `StateMachine` from `tabledriven/table_machine.py` to a washing-machine problem.
> Give one `(state, input)` pair two rows told apart by a condition,
> such as a load too heavy for the fast spin.
> Then press `Start` in the middle of a cycle,
> an input for which that state has no row,
> and decide what the caller does with the `NoTransition`:
> ignore the press or stop the machine.
> Say which policy suits a washing machine, and why.

<details>
<summary>Where to look</summary>

[The Engine](../../Chapters/31_Patterns--State_Machines.md#the-engine) tries the rows under a `(state, event type)` key in order and takes the first whose condition passes.
Put a guarded row for the heavy load ahead of an unconditional row, and let the condition read the load from the machine.
For the stray `Start`, see how [A View for the Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-view-for-the-vending-machine) treats a rejected click, then weigh a control panel's stray presses against a cycle that stops.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from exceptions import expect
from table_machine import NoTransition, StateMachine, Table

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

@dataclass
class Start:
    load_kg: float

class Full:
    pass
class WashDone:
    pass
class RinseDone:
    pass
class SpinDone:
    pass

class WashingMachine(StateMachine):
    def __init__(self) -> None:
        ...

    def begin(self, start: Start) -> None:
        ...

    def too_heavy(self, event: RinseDone) -> bool:
        ...

    def log_msg(
            self, msg: str) -> Callable[[object], None]:
        ...
```

<details>
<summary>Solution</summary>

If you put the unconditional fast-spin row first,
it matches every `RinseDone`, and the eight-kilogram load logs `'fast spin'` like the light one.
A row with no condition matches every time,
as [The Engine](../../Chapters/31_Patterns--State_Machines.md#the-engine) points out,
so the solution lists the guarded row first and leaves the unconditional row to catch the rest.

```python
# exercise_6.py
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from exceptions import expect
from table_machine import NoTransition, StateMachine, Table

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

@dataclass
class Start:
    load_kg: float

class Full:
    pass
class WashDone:
    pass
class RinseDone:
    pass
class SpinDone:
    pass

class WashingMachine(StateMachine):
    def __init__(self) -> None:
        self.load_kg = 0.0
        self.log: list[str] = []
        table: Table = {
            (WashState.IDLE, Start):
                [(None, self.begin, WashState.FILLING)],
            (WashState.FILLING, Full):
                [(None, self.log_msg("washing"),
                  WashState.WASHING)],
            (WashState.WASHING, WashDone):
                [(None, self.log_msg("rinsing"),
                  WashState.RINSING)],
            (WashState.RINSING, RinseDone): [
                (self.too_heavy, self.log_msg("slow spin"),
                 WashState.SPINNING),
                (None, self.log_msg("fast spin"),
                 WashState.SPINNING),
            ],
            (WashState.SPINNING, SpinDone):
                [(None, self.log_msg("done"),
                  WashState.DONE)],
        }
        super().__init__(WashState.IDLE, table)

    def begin(self, start: Start) -> None:
        self.load_kg = start.load_kg
        self.log.append("filling")

    def too_heavy(self, event: RinseDone) -> bool:
        return self.load_kg > 6

    def log_msg(
            self, msg: str) -> Callable[[object], None]:
        def action(event: object) -> None:
            self.log.append(msg)
        return action

cycle = [Full(), WashDone(), RinseDone(), SpinDone()]
heavy = WashingMachine()
for event in [Start(8), *cycle]:
    heavy.handle(event)
print(heavy.log)
#: ['filling', 'washing', 'rinsing', 'slow spin', 'done']
light = WashingMachine()
for event in [Start(3), *cycle]:
    light.handle(event)
print(light.log)
#: ['filling', 'washing', 'rinsing', 'fast spin', 'done']

# Start pressed again, mid-cycle:
busy = WashingMachine()
busy.handle(Start(3))
expect(NoTransition, busy.handle, Start(5))
#: [NoTransition] no transition from <WashState.FILLING: 2>
#: on Start
print(busy.state.name, busy.load_kg)
#: FILLING 3
```

**Split one input on a condition.** The `(RINSING, RinseDone)` key
holds the two rows the exercise requires, told apart by
`too_heavy()`. A load over six kilograms takes the slow spin, and
anything lighter falls through to the unconditional fast-spin row
below it. The rest of the cycle is a straight line, one event type
per state, and the machine is still the chapter's
`table_machine.py` engine unchanged.

**Record what later conditions need.** A `RinseDone` event carries no data of its
own, so the condition reads `load_kg` off the machine, where
`begin()` recorded it when the cycle started.

**Reject an input with no row.** A second `Start` during `FILLING` finds no row, so `handle()` raises
`NoTransition`. The press changes nothing. The state is still
`FILLING` and `load_kg` is still 3, because the engine finds a row
before it runs any action.

For a washing machine the caller should
ignore the press, catching `NoTransition` and continuing, as
`vending_view.py`'s `send()` does. A control panel is a source of
stray presses, and a cycle that stops because
someone leans on a button is the worse failure. Raising the
exception is still the right default for the engine. A caller can
turn an exception into a no-op, and cannot turn a silent no-op into
a report.

</details>
</details>
</details>

## 7. An elevator, table-driven

> Create an elevator state machine using `tabledriven/table_machine.py`.
> Give the "doors closing" state two rows for the same input,
> one guarded by a door-obstruction condition.

<details>
<summary>Where to look</summary>

[The Engine](../../Chapters/31_Patterns--State_Machines.md#the-engine) lets several rows share one `(state, event type)` key, tried in order.
Under the doors-closing state and a sensor event, put the obstruction condition on the first row and leave the second row unconditional.
The condition is a method that reads the event, so the table stays data.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()
    DOORS_CLOSING = auto()

@dataclass
class CallButton:
    floor: int

class ArrivedAtFloor:
    pass
class CloseDoors:
    pass

@dataclass
class DoorSensor:
    blocked: bool

class Elevator(StateMachine):
    def __init__(self, floor: int = 0) -> None:
        ...

    def above(self, call: CallButton) -> bool:
        ...

    def below(self, call: CallButton) -> bool:
        ...

    def set_target(self, call: CallButton) -> None:
        ...

    def arrive(self, event: object) -> None:
        ...

    def obstructed(self, sensor: DoorSensor) -> bool:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the unconditional `(None, None, ElevatorState.DOORS_OPEN)` row under `(IDLE, CallButton)`,
a call for the floor the car is on fails both `above()` and `below()`,
and `handle()` raises `NoTransition`: `no transition from <ElevatorState.IDLE: 1> on CallButton`.
The demo makes no such call, so its output does not change.
The solution keeps that row last, as the group's `else`.

```python
# exercise_7.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()
    DOORS_CLOSING = auto()

@dataclass
class CallButton:
    floor: int

class ArrivedAtFloor:
    pass
class CloseDoors:
    pass

@dataclass
class DoorSensor:
    blocked: bool

class Elevator(StateMachine):
    def __init__(self, floor: int = 0) -> None:
        self.floor = floor
        self.target = floor
        table: Table = {
            (ElevatorState.IDLE, CallButton): [
                (self.above, self.set_target,
                 ElevatorState.MOVING_UP),
                (self.below, self.set_target,
                 ElevatorState.MOVING_DOWN),
                (None, None, ElevatorState.DOORS_OPEN),
            ],
            (ElevatorState.MOVING_UP, ArrivedAtFloor):
                [(None, self.arrive,
                  ElevatorState.DOORS_OPEN)],
            (ElevatorState.MOVING_DOWN, ArrivedAtFloor):
                [(None, self.arrive,
                  ElevatorState.DOORS_OPEN)],
            (ElevatorState.DOORS_OPEN, CloseDoors):
                [(None, None, ElevatorState.DOORS_CLOSING)],
            (ElevatorState.DOORS_CLOSING, DoorSensor): [
                (self.obstructed, None,
                 ElevatorState.DOORS_OPEN),
                (None, None, ElevatorState.IDLE),
            ],
        }
        super().__init__(ElevatorState.IDLE, table)

    def above(self, call: CallButton) -> bool:
        return call.floor > self.floor

    def below(self, call: CallButton) -> bool:
        return call.floor < self.floor

    def set_target(self, call: CallButton) -> None:
        self.target = call.floor

    def arrive(self, event: object) -> None:
        self.floor = self.target

    def obstructed(self, sensor: DoorSensor) -> bool:
        return sensor.blocked

elevator = Elevator(floor=0)
elevator.handle(CallButton(3))
print(elevator.state, elevator.floor)
#: ElevatorState.MOVING_UP 0
elevator.handle(ArrivedAtFloor())
print(elevator.state, elevator.floor)
#: ElevatorState.DOORS_OPEN 3
elevator.handle(CloseDoors())
elevator.handle(DoorSensor(blocked=True))
print(elevator.state)
#: ElevatorState.DOORS_OPEN
elevator.handle(CloseDoors())
elevator.handle(DoorSensor(blocked=False))
print(elevator.state)
#: ElevatorState.IDLE
```

**Choose a direction from the call.** The `(IDLE, CallButton)` key holds three candidate rows, in the vending machine's
`(State.SELECTING, SecondDigit)` shape: candidate transitions share
one key, `handle()` tries them in order, and the first whose condition
passes wins. `above()` and `below()` pick `MOVING_UP` or
`MOVING_DOWN`, and a call for the current floor falls through both
conditions to open the doors with no travel.

**Reopen the doors on an obstruction.** The "doors closing" state
carries the two rows the exercise requires, the same idiom two wide.
Under `(DOORS_CLOSING, DoorSensor)`, the first row reopens the doors
when `obstructed()` passes, and the unconditional row below it
finishes the close in `IDLE`.

</details>
</details>
</details>

## 8. A heating/air-conditioning system, table-driven

> Create a heating/air-conditioning system using `tabledriven/table_machine.py`.
> A single `TemperatureReading` input must be able to lead to heating,
> cooling, or idle, decided entirely by conditions on one `(state, input)` key.

<details>
<summary>Where to look</summary>

[A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine) shows one input type leading to different next states through conditions on a shared key.
Give `TemperatureReading` a `degrees` field and write two condition methods that compare it with a target and a band.
Order the rows so the conditional ones come first and an unconditional row, as the last resort, returns to idle.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class HVACState(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

@dataclass
class TemperatureReading:
    degrees: float

class HVAC(StateMachine):
    def __init__(self, target: float = 20,
                 band: float = 2) -> None:
        ...

    def too_cold(self, r: TemperatureReading) -> bool:
        ...

    def too_hot(self, r: TemperatureReading) -> bool:
        ...
```

<details>
<summary>Solution</summary>

If you put the unconditional `(None, None, HVACState.IDLE)` row first
under `(IDLE, TemperatureReading)`, every reading prints `IDLE`, from
`15 IDLE` through `30 IDLE`. `handle()` takes the first row whose
condition passes, and a row with no condition always passes, so the
machine stops there and does not reach the `too_cold()` and `too_hot()`
rows below it. The solution lists the conditional rows first and keeps
the unconditional row last, as the fallback.

```python
# exercise_8.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class HVACState(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

@dataclass
class TemperatureReading:
    degrees: float

class HVAC(StateMachine):
    def __init__(self, target: float = 20,
                 band: float = 2) -> None:
        self.target = target
        self.band = band
        table: Table = {
            (HVACState.IDLE, TemperatureReading): [
                (self.too_cold, None, HVACState.HEATING),
                (self.too_hot, None, HVACState.COOLING),
                (None, None, HVACState.IDLE),
            ],
            (HVACState.HEATING, TemperatureReading): [
                (self.too_cold, None, HVACState.HEATING),
                (None, None, HVACState.IDLE),
            ],
            (HVACState.COOLING, TemperatureReading): [
                (self.too_hot, None, HVACState.COOLING),
                (None, None, HVACState.IDLE),
            ],
        }
        super().__init__(HVACState.IDLE, table)

    def too_cold(self, r: TemperatureReading) -> bool:
        return r.degrees < self.target - self.band

    def too_hot(self, r: TemperatureReading) -> bool:
        return r.degrees > self.target + self.band

hvac = HVAC()
for degrees in [15, 17, 21, 30, 20]:
    hvac.handle(TemperatureReading(degrees))
    print(degrees, hvac.state.name)
#: 15 HEATING
#: 17 HEATING
#: 21 IDLE
#: 30 COOLING
#: 20 IDLE
```

**Decide among three outcomes.** The machine has one input type. The `(IDLE, TemperatureReading)` key
holds three rows, so a single reading leads to heating, cooling, or
staying idle, and the two conditions decide which, as the exercise
requires.

**Run until back inside the band.** The running states carry their own
two-row groups. A reading still outside the band keeps the system
running, and one inside the band falls through to the unconditional
row back to `IDLE`.

Every
decision in the machine is a condition on the one event type. Every
action slot here holds `None`, and the fall-through rows leave the
condition slot `None` too, so both slots are optional per row.

</details>
</details>
</details>

## 9. A `Nickel` the table has never heard of

> Build a two-state machine that collects `Money`,
> modeled on `vending_machine.py`'s.
> Add a `Nickel` class deriving from `Money` and feed one in without touching the table.
> Explain the exception, then make it work two ways: by adding a row,
> and by making `Nickel` an instance of `Money` rather than a subclass.
> Say which you would keep.

<details>
<summary>Where to look</summary>

[A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine) explains that the engine looks up `type(event)` as the key, so a subclass of an event type has no row of its own.
Read the `NoTransition` message to see which class it reports, then fix it once by adding keys and once by choosing what the event is.
Compare how many rows each fix needs as denominations and states multiply.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from dataclasses import dataclass
from enum import Enum, auto
from exceptions import expect
from table_machine import NoTransition, StateMachine, Table

class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()

@dataclass
class Money:
    name: str
    value: int

@dataclass
class Nickel(Money):  # A subclass, not a new instance
    pass

class Machine(StateMachine):
    def __init__(self, *,
                 accept_nickels: bool = False) -> None:
        ...

    def add(self, event: Money) -> None:
        ...

NICKEL = Money("nickel", 5)
```

<details>
<summary>Solution</summary>

```python
# exercise_9.py
from dataclasses import dataclass
from enum import Enum, auto
from exceptions import expect
from table_machine import NoTransition, StateMachine, Table

class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()

@dataclass
class Money:
    name: str
    value: int

@dataclass
class Nickel(Money):  # A subclass, not a new instance
    pass

class Machine(StateMachine):
    def __init__(self, *,
                 accept_nickels: bool = False) -> None:
        self.amount = 0
        rows = [(None, self.add, State.COLLECTING)]
        table: Table = {
            (State.QUIESCENT, Money): rows,
            (State.COLLECTING, Money): rows,
        }
        if accept_nickels:  # Fix 1: a row keyed on Nickel
            table[(State.QUIESCENT, Nickel)] = rows
            table[(State.COLLECTING, Nickel)] = rows
        super().__init__(State.QUIESCENT, table)

    def add(self, event: Money) -> None:
        self.amount += event.value

m = Machine()
m.handle(Money("quarter", 25))
print(m.state, m.amount)
#: State.COLLECTING 25
expect(NoTransition, m.handle, Nickel("nickel", 5))
#: [NoTransition] no transition from <State.COLLECTING: 2>
#: on Nickel

# Fix 1: the table names Nickel too
m1 = Machine(accept_nickels=True)
m1.handle(Nickel("nickel", 5))
print(m1.amount)
#: 5

# Fix 2: a Nickel that is a Money, not a subclass of one
NICKEL = Money("nickel", 5)
m2 = Machine()
m2.handle(NICKEL)
print(m2.amount)
#: 5
```

**Reproduce the failure.** The exception is `NoTransition`, not a `TypeError` or a silent no-op,
and its message names the event class that found no row: `Nickel`.
`handle()` looks up `(self.state, type(event))`, and
`type(Nickel("nickel", 5))` is `Nickel`. A dictionary probe compares
keys by equality, so the `Nickel` key misses the `Money` row although
`Nickel` subclasses `Money`. Nothing walks the
[MRO](../../Chapters/07_Foundations--Classes.md#method-resolution-order).
That lookup is the exact-type dispatch the chapter describes, and a
subclass of an event type is how most readers first meet it.

**Give the subclass its own rows.** Fix 1 adds `(state, Nickel)`
rows. Those rows work, and they scale badly. Every new denomination
needs a row for every state that accepts
money, so a machine with five states and six coins carries thirty rows
that all do the same thing.

Fix 1 is the right fix when the new subclass really does behave
differently, as `FirstDigit` and `SecondDigit` do in
`vending_machine.py`. They exist as separate classes so they arrive
under different keys.

**Make the nickel a value.** Fix 2 stops making a class for something
that is a value. A nickel is not a new kind of money. It is a
`Money` whose `value` is 5.
`Money("nickel", 5)` arrives under a key the table has, so the table
and the classes stay as they are.

Keep fix 2. A subclass is worth creating when the machine must treat
the input differently. A nickel differs from a quarter only in a
number the existing action reads. The two fixes illustrate a
general rule: under exact-type dispatch, a class is a dispatch key,
so create one when you want a separate row and not when you want a
separate value.

</details>
</details>
</details>
