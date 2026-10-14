# State Machines: Solutions

Several exercises below reuse the book's generic table-driven engine,
so it appears once here, in its own file that those exercises import:

```python
# table_machine.py
from collections.abc import Callable, Sequence
from enum import Enum
from typing import Any
from record import record

@record
class Rule[I]:
    state: Enum
    input_type: type[I]
    next_state: Enum
    action: Callable[[I], None] | None = None
    condition: Callable[[I], bool] | None = None

type Table = dict[tuple[Enum, type], list[Rule[Any]]]

class NoTransition(RuntimeError):
    "No rule matched this state and input."

class StateMachine:
    def __init__(self, initial: Enum,
                 rules: Sequence[Rule[Any]]) -> None:
        self.state = initial
        self.table: Table = {}
        for rule in rules:
            key = (rule.state, rule.input_type)
            self.table.setdefault(key, []).append(rule)

    def handle(self, input_: object) -> None:
        for rule in self.table.get(
                (self.state, type(input_)), []):
            condition = rule.condition
            if condition is None or condition(input_):
                if rule.action is not None:
                    rule.action(input_)
                self.state = rule.next_state
                return
        raise NoTransition(
            f"no rule from {self.state} "
            f"on {type(input_).__name__}")
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
    def next(self, input_: object, /) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        ...
    def step(self, input_: object) -> None:
        ...

def run_all(machine: StateMachine,
            inputs: Iterable[object]) -> None:
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
    def __str__(self) -> str:
        ...
    def next(self, input_: object) -> State:
        ...

class Grumpy:
    def run(self) -> None:
        ...
    def __str__(self) -> str:
        ...
    def next(self, input_: object) -> State:
        ...

class Prozac:
    def run(self) -> None:
        ...
    def __str__(self) -> str:
        ...
    def next(self, input_: object) -> State:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the final `return self` in `Happy.next()`,
`ty` reports an `invalid-return-type`,
because the method can fall off its end and return `None`.
The demo still prints the same lines, since every input that reaches `Happy` has a branch there,
but if a second `Calm` in a row reaches `Happy`, its `next()` returns `None`,
and `step()`'s call to `run()` raises an `AttributeError`.
Each `next()` in the solution ends with `return self`,
so an input a state ignores keeps the machine where it is.

```python
# exercise_2.py
from collections.abc import Iterable
from typing import Protocol

# The chapter's state.py and state_machine.py, inlined:
class State(Protocol):
    def run(self) -> None: ...
    def next(self, input_: object, /) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def step(self, input_: object) -> None:
        state = self.current_state
        self.current_state = state.next(input_)
        print(state, input_, "->", self.current_state)
        self.current_state.run()

def run_all(machine: StateMachine,
            inputs: Iterable[object]) -> None:
    for input_ in inputs:
        machine.step(input_)

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
    def __str__(self) -> str:
        return type(self).__name__
    def next(self, input_: object) -> State:
        if isinstance(input_, Annoy):
            return Grumpy()
        if isinstance(input_, TakePill):
            return Prozac()
        return self

class Grumpy:
    def run(self) -> None:
        print("What do you want?")
    def __str__(self) -> str:
        return type(self).__name__
    def next(self, input_: object) -> State:
        if isinstance(input_, Calm):
            return Happy()
        if isinstance(input_, TakePill):
            return Prozac()
        return self

class Prozac:
    def run(self) -> None:
        print("Everything is wonderful.")
    def __str__(self) -> str:
        return type(self).__name__
    def next(self, input_: object) -> State:
        return self

run_all(StateMachine(Happy()),
        [Annoy(), Calm(), TakePill(), Annoy()])
#: Great to see you!
#: Happy Annoy -> Grumpy
#: What do you want?
#: Grumpy Calm -> Happy
#: Great to see you!
#: Happy TakePill -> Prozac
#: Everything is wonderful.
#: Prozac Annoy -> Prozac
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
        self._states: dict[str, WordState] = {}
        self.current = initial

    def register(self, name: str, state: WordState) -> None:
        self._states[name] = state

    def process(self, word: str) -> None:
        state = self._states[self.current]
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
`state_machine.py`'s `step()` does when it calls `next()`.

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
> Give one `(state, input)` pair two rules told apart by a condition,
> such as a load too heavy for the fast spin.
> Then press `Start` in the middle of a cycle,
> an input for which that state has no rule,
> and decide what the caller does with the `NoTransition`:
> ignore the press or stop the machine.
> Say which policy suits a washing machine, and why.

<details>
<summary>Where to look</summary>

[The Engine](../../Chapters/31_Patterns--State_Machines.md#the-engine) tries the rules under a `(state, input type)` key in order and takes the first whose condition passes.
Put a guarded rule for the heavy load ahead of an unconditional rule, and let the condition read the load from the machine.
For the stray `Start`, see how [An Unexpected Input](../../Chapters/31_Patterns--State_Machines.md#an-unexpected-input) weighs staying in the same state against raising an exception, then weigh a control panel's stray presses against a cycle that stops.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from collections.abc import Callable
from enum import Enum, auto
from exceptions import expect
from record import record
from table_machine import NoTransition, Rule, StateMachine

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

@record
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

    def too_heavy(self, input_: RinseDone) -> bool:
        ...

    def log_msg(
            self, msg: str) -> Callable[[object], None]:
        ...
```

<details>
<summary>Solution</summary>

If you put the unconditional fast-spin rule first,
it matches every `RinseDone`, and the eight-kilogram load logs `'fast spin'` like the light one.
A rule with no condition matches every time,
as [The Engine](../../Chapters/31_Patterns--State_Machines.md#the-engine) points out,
so the solution lists the guarded rule first and leaves the unconditional rule to catch the rest.

```python
# exercise_6.py
from collections.abc import Callable
from enum import Enum, auto
from exceptions import expect
from record import record
from table_machine import NoTransition, Rule, StateMachine

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

@record
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
        rules = [
            Rule(WashState.IDLE, Start, WashState.FILLING,
                 self.begin),
            Rule(WashState.FILLING, Full, WashState.WASHING,
                 self.log_msg("washing")),
            Rule(WashState.WASHING, WashDone,
                 WashState.RINSING,
                 self.log_msg("rinsing")),
            Rule(WashState.RINSING, RinseDone,
                 WashState.SPINNING,
                 self.log_msg("slow spin"), self.too_heavy),
            Rule(WashState.RINSING, RinseDone,
                 WashState.SPINNING,
                 self.log_msg("fast spin")),
            Rule(WashState.SPINNING, SpinDone,
                 WashState.DONE, self.log_msg("done")),
        ]
        super().__init__(WashState.IDLE, rules)

    def begin(self, start: Start) -> None:
        self.load_kg = start.load_kg
        self.log.append("filling")

    def too_heavy(self, input_: RinseDone) -> bool:
        return self.load_kg > 6

    def log_msg(
            self, msg: str) -> Callable[[object], None]:
        def action(input_: object) -> None:
            self.log.append(msg)
        return action

cycle = [Full(), WashDone(), RinseDone(), SpinDone()]
heavy = WashingMachine()
for input_ in [Start(8), *cycle]:
    heavy.handle(input_)
print(heavy.log)
#: ['filling', 'washing', 'rinsing', 'slow spin', 'done']
light = WashingMachine()
for input_ in [Start(3), *cycle]:
    light.handle(input_)
print(light.log)
#: ['filling', 'washing', 'rinsing', 'fast spin', 'done']

# Start pressed again, mid-cycle:
busy = WashingMachine()
busy.handle(Start(3))
expect(NoTransition, busy.handle, Start(5))
#: [NoTransition] no rule from WashState.FILLING on Start
print(busy.state.name, busy.load_kg)
#: FILLING 3
```

**Split one input on a condition.** The `(RINSING, RinseDone)` key
holds the two rules the exercise requires, told apart by
`too_heavy()`. A load over six kilograms takes the slow spin, and
anything lighter falls through to the unconditional fast-spin rule
below it. The rest of the cycle is a straight line, one input type
per state, and the machine is still the chapter's
`table_machine.py` engine unchanged.

**Record what later conditions need.** A `RinseDone` input carries no data of its
own, so the condition reads `load_kg` off the machine, where
`begin()` recorded it when the cycle started.

**Reject an input with no rule.** A second `Start` during `FILLING` finds no rule, so `handle()` raises
`NoTransition`. The press changes nothing. The state is still
`FILLING` and `load_kg` is still 3, because the engine finds a rule
before it runs any action.

For a washing machine the caller should
ignore the press, catching `NoTransition` and continuing.
A control panel is a source of
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
> Give the "doors closing" state two rules for the same input,
> one guarded by a door-obstruction condition.

<details>
<summary>Where to look</summary>

[The Engine](../../Chapters/31_Patterns--State_Machines.md#the-engine) lets several rules share one `(state, input type)` key, tried in order.
Under the doors-closing state and a sensor input, put the obstruction condition on the first rule and leave the second rule unconditional.
The condition is a method that reads the input, so the table stays data.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()
    DOORS_CLOSING = auto()

@record
class CallButton:
    floor: int

class ArrivedAtFloor:
    pass
class CloseDoors:
    pass

@record
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

    def arrive(self, input_: object) -> None:
        ...

    def obstructed(self, sensor: DoorSensor) -> bool:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the unconditional rule to `ElevatorState.DOORS_OPEN` under `(IDLE, CallButton)`,
a call for the floor the car is on fails both `above()` and `below()`,
and `handle()` raises `NoTransition`: `no rule from ElevatorState.IDLE on CallButton`.
The demo makes no such call, so its output does not change.
The solution keeps that rule last, as the group's `else`.

```python
# exercise_7.py
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()
    DOORS_CLOSING = auto()

@record
class CallButton:
    floor: int

class ArrivedAtFloor:
    pass
class CloseDoors:
    pass

@record
class DoorSensor:
    blocked: bool

class Elevator(StateMachine):
    def __init__(self, floor: int = 0) -> None:
        self.floor = floor
        self.target = floor
        rules = [
            Rule(ElevatorState.IDLE, CallButton,
                 ElevatorState.MOVING_UP, self.set_target,
                 self.above),
            Rule(ElevatorState.IDLE, CallButton,
                 ElevatorState.MOVING_DOWN, self.set_target,
                 self.below),
            Rule(ElevatorState.IDLE, CallButton,
                 ElevatorState.DOORS_OPEN),
            Rule(ElevatorState.MOVING_UP, ArrivedAtFloor,
                 ElevatorState.DOORS_OPEN, self.arrive),
            Rule(ElevatorState.MOVING_DOWN, ArrivedAtFloor,
                 ElevatorState.DOORS_OPEN, self.arrive),
            Rule(ElevatorState.DOORS_OPEN, CloseDoors,
                 ElevatorState.DOORS_CLOSING),
            Rule(ElevatorState.DOORS_CLOSING, DoorSensor,
                 ElevatorState.DOORS_OPEN,
                 condition=self.obstructed),
            Rule(ElevatorState.DOORS_CLOSING, DoorSensor,
                 ElevatorState.IDLE),
        ]
        super().__init__(ElevatorState.IDLE, rules)

    def above(self, call: CallButton) -> bool:
        return call.floor > self.floor

    def below(self, call: CallButton) -> bool:
        return call.floor < self.floor

    def set_target(self, call: CallButton) -> None:
        self.target = call.floor

    def arrive(self, input_: object) -> None:
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

**Choose a direction from the call.** The `(IDLE, CallButton)` key holds three candidate rules, in the vending machine's
`(State.SELECTING, Column)` shape: candidate transitions share
one key, `handle()` tries them in order, and the first whose condition
passes wins. `above()` and `below()` pick `MOVING_UP` or
`MOVING_DOWN`, and a call for the current floor falls through both
conditions to open the doors with no travel.

**Reopen the doors on an obstruction.** The "doors closing" state
carries the two rules the exercise requires, the same idiom two wide.
Under `(DOORS_CLOSING, DoorSensor)`, the first rule reopens the doors
when `obstructed()` passes, and the unconditional rule below it
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
Order the rules so the conditional ones come first and an unconditional rule, as the last resort, returns to idle.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class HVACState(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

@record
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

If you put the unconditional rule to `HVACState.IDLE` first
under `(IDLE, TemperatureReading)`, every reading prints `IDLE`, from
`15 IDLE` through `30 IDLE`. `handle()` takes the first rule whose
condition passes, and a rule with no condition always passes, so the
machine stops there and does not reach the `too_cold()` and `too_hot()`
rules below it. The solution lists the conditional rules first and keeps
the unconditional rule last, as the fallback.

```python
# exercise_8.py
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class HVACState(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

@record
class TemperatureReading:
    degrees: float

class HVAC(StateMachine):
    def __init__(self, target: float = 20,
                 band: float = 2) -> None:
        self.target = target
        self.band = band
        rules = [
            Rule(HVACState.IDLE, TemperatureReading,
                 HVACState.HEATING,
                 condition=self.too_cold),
            Rule(HVACState.IDLE, TemperatureReading,
                 HVACState.COOLING,
                 condition=self.too_hot),
            Rule(HVACState.IDLE, TemperatureReading,
                 HVACState.IDLE),
            Rule(HVACState.HEATING, TemperatureReading,
                 HVACState.HEATING,
                 condition=self.too_cold),
            Rule(HVACState.HEATING, TemperatureReading,
                 HVACState.IDLE),
            Rule(HVACState.COOLING, TemperatureReading,
                 HVACState.COOLING,
                 condition=self.too_hot),
            Rule(HVACState.COOLING, TemperatureReading,
                 HVACState.IDLE),
        ]
        super().__init__(HVACState.IDLE, rules)

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
holds three rules, so a single reading leads to heating, cooling, or
staying idle, and the two conditions decide which, as the exercise
requires.

**Run until back inside the band.** The running states carry their own
two-rule groups. A reading still outside the band keeps the system
running, and one inside the band falls through to the unconditional
rule back to `IDLE`.

Every
decision in the machine is a condition on the one input type. Every
rule here keeps the default `None` action, and the fall-through rules
keep the default `None` condition too, so both fields are optional per rule.

</details>
</details>
</details>

## 9. A `Nickel` the table has never heard of

> Build a two-state machine that collects `Money`,
> modeled on `vending_machine.py`'s.
> Add a `Nickel` class deriving from `Money` and feed one in without touching the table.
> Explain the exception, then make it work two ways: by adding a rule,
> and by making `Nickel` an instance of `Money` rather than a subclass.
> Say which you would keep.

<details>
<summary>Where to look</summary>

[A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine) explains that the engine looks up `type(input_)` as the key, so a subclass of an input type has no rule of its own.
Read the `NoTransition` message to see which class it reports, then fix it once by adding keys and once by choosing what the input is.
Compare how many rules each fix needs as denominations and states multiply.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from enum import Enum, auto
from exceptions import expect
from record import record
from table_machine import NoTransition, Rule, StateMachine

class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()

@record
class Money:
    name: str
    value: int

@record
class Nickel(Money):  # A subclass, not a new instance
    pass

class Machine(StateMachine):
    def __init__(self, *,
                 accept_nickels: bool = False) -> None:
        ...

    def add(self, input_: Money) -> None:
        ...

NICKEL = Money("nickel", 5)
```

<details>
<summary>Solution</summary>

```python
# exercise_9.py
from enum import Enum, auto
from exceptions import expect
from record import record
from table_machine import NoTransition, Rule, StateMachine

class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()

@record
class Money:
    name: str
    value: int

@record
class Nickel(Money):  # A subclass, not a new instance
    pass

class Machine(StateMachine):
    def __init__(self, *,
                 accept_nickels: bool = False) -> None:
        self.amount = 0
        rules = [
            Rule(s, Money, State.COLLECTING, self.add)
            for s in State
        ]
        if accept_nickels:  # Fix 1: rules keyed on Nickel
            rules += [
                Rule(s, Nickel, State.COLLECTING, self.add)
                for s in State
            ]
        super().__init__(State.QUIESCENT, rules)

    def add(self, input_: Money) -> None:
        self.amount += input_.value

m = Machine()
m.handle(Money("quarter", 25))
print(m.state, m.amount)
#: State.COLLECTING 25
expect(NoTransition, m.handle, Nickel("nickel", 5))
#: [NoTransition] no rule from State.COLLECTING on Nickel

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
and its message names the input class that found no rule: `Nickel`.
`handle()` looks up `(self.state, type(input_))`, and
`type(Nickel("nickel", 5))` is `Nickel`. A dictionary probe compares
keys by equality, so the `Nickel` key misses the `Money` rule although
`Nickel` subclasses `Money`. Nothing walks the
[MRO](../../Chapters/07_Foundations--Classes.md#method-resolution-order).
That lookup is the exact-type dispatch the chapter describes, and a
subclass of an input type is how most readers first meet it.

**Give the subclass its own rules.** Fix 1 adds `(state, Nickel)`
rules. Those rules work, and they scale badly. Every new denomination
needs a rule for every state that accepts
money, so a machine with five states and six coins carries thirty rules
that all do the same thing.

Fix 1 is the right fix when the new subclass really does behave
differently, as `Row` and `Column` do in
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
so create one when you want a separate rule and not when you want a
separate value.

</details>
</details>
</details>

## 10. The mood machine, as `Enum` members

> Rewrite exercise 2's mood machine in the shape of `enum_states.py`:
> a `Mood` enum of rows,
> each carrying its greeting and its transition function,
> with the inputs as a `StrEnum` and `state_machine.py`'s engine running it.
> Say what a mood gains and loses as an enum member rather than a class.

<details>
<summary>Where to look</summary>

[States as `Enum` Members](../../Chapters/31_Patterns--State_Machines.md#states-as-enum-members) shows the shape: a record with a `run()` and a stored `next`, mixed into an `Enum` and driven by the first design's engine.
Make the inputs a `StrEnum`, so each transition function can `match` on them and the trace prints them as words.
Inline `state.py` and `state_machine.py` the way exercise 2 does.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from collections.abc import Callable, Iterable
from enum import Enum, StrEnum
from typing import Protocol
from record import record

class State(Protocol):
    def run(self) -> None: ...
    def next(self, input_: object, /) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        ...
    def step(self, input_: object) -> None:
        ...

def run_all(machine: StateMachine,
            inputs: Iterable[object]) -> None:
    ...

class Input(StrEnum):
    ANNOY = "annoy"
    CALM = "calm"
    TAKE_PILL = "take pill"

@record
class StateRow:
    message: str
    next: Callable[[object], State]
    def run(self) -> None:
        ...

def happy(input_: object) -> Mood:
    ...

def grumpy(input_: object) -> Mood:
    ...

class Mood(StateRow, Enum):
    HAPPY = ("Great to see you!", happy)
    GRUMPY = ("What do you want?", grumpy)
    PROZAC = ("Everything is wonderful.",
              lambda _: Mood.PROZAC)
    def __str__(self) -> str:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_10.py
from collections.abc import Callable, Iterable
from enum import Enum, StrEnum
from typing import Protocol
from record import record

# The chapter's state.py, state_machine.py, and
# enum_states.py's StateRow, inlined:
class State(Protocol):
    def run(self) -> None: ...
    def next(self, input_: object, /) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def step(self, input_: object) -> None:
        state = self.current_state
        self.current_state = state.next(input_)
        print(state, input_, "->", self.current_state)
        self.current_state.run()

def run_all(machine: StateMachine,
            inputs: Iterable[object]) -> None:
    for input_ in inputs:
        machine.step(input_)

class Input(StrEnum):
    ANNOY = "annoy"
    CALM = "calm"
    TAKE_PILL = "take pill"

@record
class StateRow:
    message: str
    next: Callable[[object], State]
    def run(self) -> None:
        print(self.message)

def happy(input_: object) -> Mood:
    match input_:
        case Input.ANNOY:
            return Mood.GRUMPY
        case Input.TAKE_PILL:
            return Mood.PROZAC
        case _:
            return Mood.HAPPY

def grumpy(input_: object) -> Mood:
    match input_:
        case Input.CALM:
            return Mood.HAPPY
        case Input.TAKE_PILL:
            return Mood.PROZAC
        case _:
            return Mood.GRUMPY

class Mood(StateRow, Enum):
    HAPPY = ("Great to see you!", happy)
    GRUMPY = ("What do you want?", grumpy)
    PROZAC = ("Everything is wonderful.",
              lambda _: Mood.PROZAC)
    def __str__(self) -> str:
        return self.name.capitalize()

run_all(StateMachine(Mood.HAPPY), [
    Input.ANNOY, Input.CALM, Input.TAKE_PILL, Input.ANNOY])
#: Great to see you!
#: Happy annoy -> Grumpy
#: What do you want?
#: Grumpy calm -> Happy
#: Great to see you!
#: Happy take pill -> Prozac
#: Everything is wonderful.
#: Prozac annoy -> Prozac
#: Everything is wonderful.
print([mood.name for mood in Mood])
#: ['HAPPY', 'GRUMPY', 'PROZAC']
```

**Each mood is one row.** `Mood.HAPPY` holds its greeting and `happy()`, the function that names its successors, so reading the member tells you what the mood says and where it can go.
`PROZAC` needs no function of its own: its transition is a lambda that answers every input with `Mood.PROZAC`, the same "stays put" that exercise 2's `Prozac.next()` wrote as `return self`.
The engine is exercise 2's, unchanged, and the trace is exercise 2's with the inputs printed as the `StrEnum`'s words.

**What a mood gains as a member.** The moods are a closed set the program and the type checker both know.
`list(Mood)` enumerates them, a reader can search for the name `Mood.PROZAC`, and a parameter typed `Mood` accepts a member and rejects a stray `Happy()` instance of the kind exercise 2 constructs.
Exercise 2's engine accepts any object with `run()` and `next()`, so the set of moods there is open and nothing lists it.

**What a mood loses.** A member is one frozen record shared by every machine in the program, so a mood that keeps data of its own, such as a count of the `ANNOY` inputs it has received, has nowhere to put it.
Exercise 2's classes can carry that state per instance, and a mood whose behavior needs more than a message and a successor is a class in either design.

</details>
</details>
</details>
