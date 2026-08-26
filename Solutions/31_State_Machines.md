# State Machines: Solutions

Several exercises below reuse the book's generic table-driven engine,
so it is defined once, here, as its own file that the others import:

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

```python
# exercise_1.py
class Mood:
    def hello(self) -> str:
        raise NotImplementedError

class Happy(Mood):
    def hello(self) -> str:
        return "Great to see you!"

class Grumpy(Mood):
    def hello(self) -> str:
        return "What do you want?"

class Prozac(Mood):
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
`hello()` method. `UnpredictablePerson` never mentions any specific
mood by name, so adding a third one changes nothing about the
surrogate itself, only which `Mood` object gets swapped in through
`change_to()`. This is the *State* surrogate from
[Surrogate](../Chapters/26_Surrogate.md#state), applied to a new domain.

## 2. A washing machine, table-driven

```python
# exercise_2.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

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

    def log_msg(self, msg: str):
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
```

The `(RINSING, RinseDone)` key holds the two rows the exercise asks
for, told apart by `too_heavy()`: a load over six kilograms takes the
slow spin, and anything lighter falls through to the unconditional
fast-spin row below it. The condition reads `load_kg` off the machine,
where `begin()` recorded it when the cycle started, since a `RinseDone`
event carries no data of its own. The rest of the cycle is a straight
line, one event type per state, and the machine is still the chapter's
`table_machine.py` engine unchanged.

## 3. A word-driven state machine with per-state transition tables

```python
# exercise_3.py
from __future__ import annotations

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
    TRANSITIONS: dict[str, str] = {}

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

This is the classic turnstile: `push` while locked does nothing (the
`"*"` fallback), `coin` unlocks it, and `push` while unlocked locks it
again. Each state subclass carries its own transition table as a class
attribute and looks itself up with `.get(word, ...["*"])`, so
`Controller` does not branch on which state or word it is
processing; it asks the current state object what comes next,
the same delegation `state.py`'s `next()` method uses. Reading a
sequence of words from a file one per line is a one-line change:
`words = Path("moves.txt").read_text().split()`.

## 4. Configuring the machine from one transition table

The per-state design in exercise 3 spreads the turnstile's rules
across two classes, one dictionary each. Collecting both into a single
table, keyed by `(state, word)`, makes the whole machine's behavior
editable in one place:

```python
# exercise_4.py
TRANSITIONS: dict[tuple[str, str], str] = {
    ("locked", "coin"): "unlocked",
    ("locked", "push"): "locked",
    ("unlocked", "push"): "locked",
    ("unlocked", "coin"): "unlocked",
}

class TableController:
    def __init__(self, initial: str,
                 table: dict[tuple[str, str], str]) -> None:
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

Both versions produce the same history. The per-state design (exercise
3) puts each state's rules with that state, which reads well when a
state's behavior involves more than a lookup. The single-table design
puts every rule for the whole machine in one dictionary, which is
easier to audit and edit as a unit, the same trade-off the chapter's
own [table-driven state machine](../Chapters/31_State_Machines.md#table-driven-state-machine) makes
over the per-state `mouse_trap.py`.

## 5. The mood machine, rebuilt on `table_machine.py`

```python
# exercise_5.py
from enum import Enum, auto
from table_machine import StateMachine, Table

class MoodState(Enum):
    HAPPY = auto()
    GRUMPY = auto()
    PROZAC = auto()

class TakePill:
    pass
class Annoy:
    pass
class Calm:
    pass

class MoodMachine(StateMachine):
    def __init__(self) -> None:
        self.message = ""
        happy_takes_pill = (
            None, self.say("Everything is wonderful."),
            MoodState.PROZAC)
        table: Table = {
            (MoodState.HAPPY, Annoy): [(
                None, self.say("What do you want?"),
                MoodState.GRUMPY)],
            (MoodState.GRUMPY, Calm): [(
                None, self.say("Great to see you!"),
                MoodState.HAPPY)],
            (MoodState.HAPPY, TakePill): [happy_takes_pill],
            (MoodState.GRUMPY, TakePill):
                [happy_takes_pill],
        }
        super().__init__(MoodState.HAPPY, table)

    def say(self, msg: str):
        def action(event: object) -> None:
            self.message = msg
        return action

mm = MoodMachine()
mm.handle(Annoy())
print(mm.state, mm.message)
#: MoodState.GRUMPY What do you want?
mm.handle(TakePill())
print(mm.state, mm.message)
#: MoodState.PROZAC Everything is wonderful.
```

Where exercise 1's `UnpredictablePerson` swaps in a whole `Mood`
object through `change_to()`, this version drives the same mood
transitions through events and a table. Both model "a thing that
changes behavior over time"; the *State* surrogate suits it when each
mood needs real per-mood logic, and the table-driven machine suits it
when the transitions themselves, not the mood behaviors, are the part
worth making explicit and easy to audit.

## 6. An elevator, table-driven

```python
# exercise_6.py
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

The "doors closing" state carries the two rows the exercise asks for:
`(DOORS_CLOSING, DoorSensor)` reopens the doors when `obstructed()`
passes, and the unconditional row below it lets an unobstructed close
finish in `IDLE`. The `(IDLE, CallButton)` key shows the same idiom
three wide, the vending machine's `(State.SELECTING, SecondDigit)`
shape: candidate transitions sharing one key, tried in order, the
first whose condition passes wins. `above()`/`below()` pick
`MOVING_UP` or `MOVING_DOWN`, and a call for the current floor falls
through both conditions to open the doors with no travel.

## 7. A heating/air-conditioning system, table-driven

```python
# exercise_7.py
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

The machine has one input type, and the `(IDLE, TemperatureReading)`
key holds three rows, so a single reading leads to heating, cooling,
or staying idle, decided entirely by the two conditions, as the
exercise requires. The running states carry their own two-row groups:
a reading still outside the band keeps the system running, and one
inside the band falls through to the unconditional row back to
`IDLE`. Every decision in the machine is a condition on the one event
type; no transition needs an action, which confirms that both slots
are genuinely optional per row.

## 8. `mouse_move_generator()`

```python
# exercise_8.py
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

`NEXT_ACTIONS` is a small state machine of its own: a dictionary from
"the action just produced" to "the legal actions that can follow it,"
including the special `None` key for "nothing has happened yet," which
leads only to `APPEARS`. The generator's own state is just
`previous`, the last action it yielded; each call to `next()` (each
iteration of the `for` loop that consumes it) picks a legal successor
and remembers it for the following call. Because every choice is
constrained by `NEXT_ACTIONS`, any sequence this generator produces is
automatically a legal one, the same guarantee `mouse_trap.py`'s
`next()` methods enforce by hand, one state class at a time.

## 9. A `Nickel` the table has never heard of

```python
# exercise_9.py
from dataclasses import dataclass
from enum import Enum, auto
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
try:
    m.handle(Nickel("nickel", 5))
except NoTransition as e:
    print(e)
#: no transition from <State.COLLECTING: 2> on Nickel

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

The exception is `NoTransition`, not a `TypeError` or a silent
no-op, and it names the class that was not found. `handle()` looks up
`(self.state, type(event))`, and `type(Nickel("nickel", 5))` is
`Nickel`. A dictionary probe compares keys by equality, so `Nickel`
does not match the `Money` key however closely the two are related.
Nothing walks the MRO. That is the exact-type dispatch the chapter
describes, and a subclass of an event type is the way most readers
first meet it.

**Fix 1** adds `(state, Nickel)` rows. This works, and it scales
badly: every new denomination needs a row for every state that accepts
money, so a machine with five states and six coins carries thirty
rows that all do the same thing. It is the right fix when the new
subclass really does behave differently, which is what `FirstDigit`
and `SecondDigit` do in `vending_machine.py`. There the subclassing
exists so the two arrive under different keys.

**Fix 2** stops making a class for something that is a value. A
nickel is not a new kind of money; it is a `Money` whose `value` is 5.
`Money("nickel", 5)` needs no table change, no new row, and no new
class, because it arrives under the key the table already has.

Keep fix 2. A subclass is worth creating when the machine must treat
the input differently, and a nickel differs from a quarter only in a
number the existing action already reads. The general rule the two
fixes illustrate: under exact-type dispatch, a class is a dispatch
key, so create one when you want a separate row and not when you want
a separate value.
