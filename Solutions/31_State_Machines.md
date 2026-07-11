# State Machines: Solutions

Several exercises below reuse the book's generic table-driven engine,
so it is defined once, here, as its own file that the others import:

```python
# state_machine.py
from collections.abc import Callable
from enum import Enum
from typing import Any

type Transition = tuple[
    Callable[..., bool] | None, Callable[..., None] | None, Enum
]
type Table = dict[tuple[Enum, type], list[Transition]]

class StateMachine:
    def __init__(self, initial: Enum, table: Table) -> None:
        self.state = initial
        self.table = table

    def handle(self, event: Any) -> None:
        for condition, action, next_state in self.table.get(
                (self.state, type(event)), []):
            if condition is None or condition(event):
                if action is not None:
                    action(event)
                self.state = next_state
                return
        raise RuntimeError(
            f"no transition from {self.state!r} "
            f"on {type(event).__name__}")
```

## 1. A connection limiter, with a proxy that releases on check-in

```python
# exercise_1.py
from __future__ import annotations

class RealConnection:
    def __init__(self, number: int) -> None:
        self.number = number

    def query(self, sql: str) -> str:
        return f"connection {self.number}: {sql}"

class ConnectionManager:
    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._in_use = 0
        self._next_number = 1

    def checkout(self) -> ConnectionProxy:
        if self._in_use >= self._limit:
            raise RuntimeError("no connections available")
        self._in_use += 1
        conn = RealConnection(self._next_number)
        self._next_number += 1
        return ConnectionProxy(conn, self)

    def _check_in(self) -> None:
        self._in_use -= 1

class ConnectionProxy:
    def __init__(self, real: RealConnection,
                 manager: ConnectionManager) -> None:
        self._real = real
        self._manager = manager
        self._checked_in = False

    def query(self, sql: str) -> str:
        if self._checked_in:
            raise RuntimeError("connection already checked in")
        return self._real.query(sql)

    def check_in(self) -> None:
        if not self._checked_in:
            self._checked_in = True
            self._manager._check_in()

manager = ConnectionManager(limit=2)
c1 = manager.checkout()
c2 = manager.checkout()
try:
    manager.checkout()
except RuntimeError as e:
    print("caught:", e)
#: caught: no connections available
c1.check_in()
c3 = manager.checkout()  # Succeeds: c1's slot was released
print(c3.query("SELECT 2"))
#: connection 3: SELECT 2
```

`ConnectionManager` never hands out a bare `RealConnection`. Every
caller gets a `ConnectionProxy` instead, so the manager, not the
caller, controls when a connection counts as "in use." `check_in()`
is the only path back to `_in_use -= 1`, and it can only run once per
proxy, guarded by `_checked_in`; querying a checked-in proxy raises
instead of silently succeeding against a connection the manager
already considers returned.

## 2. `UnpredictablePerson` with a `Prozac` mood

```python
# exercise_2.py
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
[Surrogate](26_Surrogate.md#state), applied to a new domain.

## 3. A washing machine, table-driven

```python
# exercise_3.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

class Start:
    pass
class Full:
    pass
class WashDone:
    pass
class RinseDone:
    pass
class SpinDone:
    pass
class Reset:
    pass

class WashingMachine(StateMachine):
    def __init__(self) -> None:
        self.log: list[str] = []
        table: Table = {
            (WashState.IDLE, Start):
                [(None, self.log_msg("filling"), WashState.FILLING)],
            (WashState.FILLING, Full):
                [(None, self.log_msg("washing"), WashState.WASHING)],
            (WashState.WASHING, WashDone):
                [(None, self.log_msg("rinsing"), WashState.RINSING)],
            (WashState.RINSING, RinseDone): [(
                None, self.log_msg("spinning"), WashState.SPINNING)],
            (WashState.SPINNING, SpinDone):
                [(None, self.log_msg("done"), WashState.DONE)],
            (WashState.DONE, Reset):
                [(None, self.log_msg("idle"), WashState.IDLE)],
        }
        super().__init__(WashState.IDLE, table)

    def log_msg(self, msg: str):
        def action(event: object) -> None:
            self.log.append(msg)
        return action

wm = WashingMachine()
events = [
    Start(), Full(), WashDone(), RinseDone(), SpinDone(), Reset()]
for event in events:
    wm.handle(event)
print(wm.log)
#: ['filling', 'washing', 'rinsing', 'spinning', 'done', 'idle']
```

Each wash cycle stage is a straight line, one event type per state
with no branching, unlike the vending machine's conditional
transitions. The washing machine still uses the exact same
`state_machine.py` engine; only the table and the small marker event
classes are specific to washing laundry.

## 4. A word-driven state machine with per-state transition tables

```python
# exercise_4.py
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
        return self.TRANSITIONS.get(word, self.TRANSITIONS["*"])

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
`Controller` itself never branches on which state or word it is
processing; it only asks the current state object what comes next,
the same delegation `state.py`'s `next()` method uses. Reading a
sequence of words from a file one per line is a one-line change:
`words = Path("moves.txt").read_text().split()`.

## 5. Configuring the machine from one transition table

The per-state design in exercise 4 spreads the turnstile's rules
across two classes, one dictionary each. Collecting both into a single
table, keyed by `(state, word)`, makes the whole machine's behavior
editable in one place:

```python
# exercise_5.py
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
4) puts each state's rules with that state, which reads well when a
state's behavior involves more than a lookup. The single-table design
puts every rule for the whole machine in one dictionary, which is
easier to audit and edit as a unit, the same trade-off the chapter's
own [table-driven state machine](#table-driven-state-machine) makes
over the per-state `mouse_trap.py`.

## 6. The mood machine, rebuilt on `state_machine.py`

```python
# exercise_6.py
from enum import Enum, auto
from state_machine import StateMachine, Table

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
            (MoodState.GRUMPY, TakePill): [happy_takes_pill],
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

Where exercise 2's `UnpredictablePerson` swaps in a whole `Mood`
object through `change_to()`, this version drives the same mood
transitions through events and a table. Both model "a thing that
changes behavior over time"; the *State* surrogate suits it when each
mood needs real per-mood logic, and the table-driven machine suits it
when the transitions themselves, not the mood behaviors, are the part
worth making explicit and easy to audit.

## 7. An elevator, table-driven

```python
# exercise_7.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()

class CallButton:
    def __init__(self, floor: int) -> None:
        self.floor = floor

class ArrivedAtFloor:
    pass
class DoorsClosed:
    pass

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
                (None, self.open_doors, ElevatorState.DOORS_OPEN),
            ],
            (ElevatorState.MOVING_UP, ArrivedAtFloor):
                [(None, self.open_doors, ElevatorState.DOORS_OPEN)],
            (ElevatorState.MOVING_DOWN, ArrivedAtFloor):
                [(None, self.open_doors, ElevatorState.DOORS_OPEN)],
            (ElevatorState.DOORS_OPEN, DoorsClosed):
                [(None, None, ElevatorState.IDLE)],
        }
        super().__init__(ElevatorState.IDLE, table)

    def above(self, call: CallButton) -> bool:
        return call.floor > self.floor

    def below(self, call: CallButton) -> bool:
        return call.floor < self.floor

    def set_target(self, call: CallButton) -> None:
        self.target = call.floor

    def open_doors(self, event: object) -> None:
        self.floor = self.target

elevator = Elevator(floor=0)
elevator.handle(CallButton(3))
print(elevator.state, elevator.floor)
#: ElevatorState.MOVING_UP 0
elevator.handle(ArrivedAtFloor())
print(elevator.state, elevator.floor)
#: ElevatorState.DOORS_OPEN 3
```

This reuses the vending machine's exact three-way conditional-list
idiom from `(State.SELECTING, SecondDigit)`: several candidate
transitions sharing one `(state, event type)` key, tried in order,
the first whose condition passes wins. `above()`/`below()` pick
`MOVING_UP` or `MOVING_DOWN`; a call for the current floor falls
through both conditions to the unconditional last entry, opening the
doors immediately with no travel at all.

## 8. A heating/air-conditioning system, table-driven

```python
# exercise_8.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class HVACState(Enum):
    OFF = auto()
    HEATING = auto()
    COOLING = auto()

class TooCold:
    pass
class TooHot:
    pass
class AtTarget:
    pass
class TurnOff:
    pass

class HVAC(StateMachine):
    def __init__(self) -> None:
        table: Table = {
            (HVACState.OFF, TooCold):
                [(None, None, HVACState.HEATING)],
            (HVACState.OFF, TooHot):
                [(None, None, HVACState.COOLING)],
            (HVACState.HEATING, AtTarget):
                [(None, None, HVACState.OFF)],
            (HVACState.COOLING, AtTarget):
                [(None, None, HVACState.OFF)],
            (HVACState.HEATING, TurnOff):
                [(None, None, HVACState.OFF)],
            (HVACState.COOLING, TurnOff):
                [(None, None, HVACState.OFF)],
        }
        super().__init__(HVACState.OFF, table)

hvac = HVAC()
hvac.handle(TooCold())
print(hvac.state)
#: HVACState.HEATING
hvac.handle(AtTarget())
print(hvac.state)
#: HVACState.OFF
```

Every transition here has `None` for both condition and action,
since the system's whole behavior is which state it is in; nothing
extra needs computing or checking on the way. This is the simplest
possible table-driven machine and confirms that `condition` and
`action` are genuinely optional per transition, not required
boilerplate.

## 9. `mouse_move_generator()`

```python
# exercise_9.py
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

NEXT_ACTIONS: dict[MouseAction | None, list[MouseAction]] = {
    None: [MouseAction.APPEARS],
    MouseAction.APPEARS: [MouseAction.RUNS_AWAY, MouseAction.ENTERS],
    MouseAction.RUNS_AWAY: [MouseAction.APPEARS],
    MouseAction.ENTERS: [MouseAction.ESCAPES, MouseAction.TRAPPED],
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
print(" ".join(m.name for m in moves))
#: APPEARS RUNS_AWAY APPEARS RUNS_AWAY APPEARS ENTERS TRAPPED REMOVED
```

`NEXT_ACTIONS` is itself a small state machine: a dictionary from "the
action just produced" to "the legal actions that can follow it,"
including the special `None` key for "nothing has happened yet," which
only ever leads to `APPEARS`. The generator's own state is just
`previous`, the last action it yielded; each call to `next()` (each
iteration of the `for` loop that consumes it) picks a legal successor
and remembers it for the following call. Because every choice is
constrained by `NEXT_ACTIONS`, any sequence this generator produces is
automatically a legal one, the same guarantee `mouse_trap.py`'s
`next()` methods enforce by hand, one state class at a time.
