# State Machines

Recall [*State*](26_Patterns--Surrogate.md#state):
a surrogate object that forwards calls to a swappable implementation.
*State* lets the client programmer swap the implementation.
*StateMachine* adds a structure that swaps it automatically,
from one object to the next.
Each implementation represents one state the system can occupy,
so the system behaves differently as it moves from state to state.

![`StateMachine` names only `State`, each state satisfies it, and `MouseTrap` and its states name each other](_images/coupling_31)

A [*Template Method*](25_Patterns--Template_Method.md)
often moves the system from one state to the next,
as the following framework for a basic state machine shows.
You call `run()` on a state to perform its behavior,
and you pass an "input" object to the state's `next()`,
which returns the state to enter next.

The chapter shows two designs that differ in one way: in the first,
each `State` object decides its own next state; in the second,
a single table holds every transition.

## Each State Decides

A `State` runs its operation and, given an event, names the next `State`:

```python
# state.py
from typing import Protocol

class State(Protocol):
    def run(self) -> None: ...
    def next(self, event: object) -> State: ...
```

Python does not require this Protocol.
Its few lines do two things: annotations can name `State` as a type,
and a state class that leaves a method out fails the type check wherever the program uses it as a `State`,
before anything runs.

The `StateMachine` keeps track of the current state,
which the constructor initializes.
The `run_all()` method takes a sequence of input objects.
For each one it asks the current state for the next state, moves there,
and calls that state's `run()`.
That loop is the *State* pattern plus the transition.
What `run()` does depends on which state the machine occupies:

```python
# state_machine.py
from collections.abc import Iterable
from state import State

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    # Template method:
    def run_all(self, inputs: Iterable[object]) -> None:
        for event in inputs:
            print(event)
            self.current_state = (
                self.current_state.next(event))
            self.current_state.run()
```

`run_all()` is the template method: it fixes the flow
(report the input, transition, run the new state),
while the varying behavior lives in each `State`'s `run()` and `next()`.
[*Template Method*](25_Patterns--Template_Method.md)
puts the varying steps in a subclass.
Here they come from the `State` objects the machine holds.

In this style of *StateMachine*, each state decides the next state.
As an example, here's a fancy mousetrap that can move through several states while trapping a mouse.
The possible moves a mouse can make are the inputs to the state machine:

```python
# mouse_action.py
from enum import StrEnum

class MouseAction(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"
```

Each possible move by a mouse is a member of the `MouseAction` enumeration
([Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too) introduces `Enum`).
Because it is a `StrEnum`, each member *is* a `str`,
and compares equal to and prints as its value.
That is why `print(event)` in `run_all()` shows `mouse appears` rather than `MouseAction.APPEARS`.
The members still hash and look up correctly, so they work as dictionary keys.
`MouseAction("mouse appears")` returns the matching member,
which is how the code below parses the test input.

A text file supplies the sequence of mouse inputs,
nine moves that between them exercise every transition in the trap:

```text
# mouse_moves.txt
mouse appears
mouse runs away
mouse appears
mouse enters trap
mouse escapes
mouse appears
mouse enters trap
mouse trapped
mouse removed
```

### One State Class per Behavior

Here's the first version of the mousetrap program.
Each state class defines its `run()` behavior,
and establishes its next state with a `match` statement:

```python
# mouse_trap_states.py
from pathlib import Path
from typing import ClassVar
from mouse_action import MouseAction
from state import State
from state_machine import StateMachine

class Waiting:
    def run(self) -> None:
        print("Waiting: Broadcasting cheese smell")

    def next(self, event: object) -> State:
        match event:
            case MouseAction.APPEARS:
                return MouseTrap.luring
            case _:
                return MouseTrap.waiting

class Luring:
    def run(self) -> None:
        print("Luring: Presenting Cheese, door open")

    def next(self, event: object) -> State:
        match event:
            case MouseAction.RUNS_AWAY:
                return MouseTrap.waiting
            case MouseAction.ENTERS:
                return MouseTrap.trapping
            case _:
                return MouseTrap.luring

class Trapping:
    def run(self) -> None:
        print("Trapping: Closing door")

    def next(self, event: object) -> State:
        match event:
            case MouseAction.ESCAPES:
                return MouseTrap.waiting
            case MouseAction.TRAPPED:
                return MouseTrap.holding
            case _:
                return MouseTrap.trapping

class Holding:
    def run(self) -> None:
        print("Holding: Mouse caught")

    def next(self, event: object) -> State:
        match event:
            case MouseAction.REMOVED:
                return MouseTrap.waiting
            case _:
                return MouseTrap.holding

class MouseTrap(StateMachine):
    waiting: ClassVar[State] = Waiting()
    luring: ClassVar[State] = Luring()
    trapping: ClassVar[State] = Trapping()
    holding: ClassVar[State] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)

text = Path("mouse_moves.txt").read_text()
moves = [line.strip() for line in text.splitlines()
         if line.strip() and not line.startswith("#")]
MouseTrap().run_all([MouseAction(m) for m in moves])
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse runs away
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse escapes
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse trapped
#: Holding: Mouse caught
#: mouse removed
#: Waiting: Broadcasting cheese smell

# ESCAPES has no case in Waiting, so case _
# fires and the machine stays at Waiting:
trap = MouseTrap()
trap.run_all([MouseAction.ESCAPES])
#: Waiting: Broadcasting cheese smell
#: mouse escapes
#: Waiting: Broadcasting cheese smell
```

`MouseTrap` holds all the possible states as class attributes and sets up the initial state.
Each state is one shared object: a state class stores nothing,
so a single `Waiting` serves every `MouseTrap` and every visit to that state.
The code at the bottom of the file builds a `MouseTrap` and runs it through the whole sequence of moves read from the text file.

Each `next()` is a `match` on the event:
a `case` for every input the state recognizes,
and a `case _` that returns the state the machine is in.
`Waiting.next()` returns `MouseTrap.luring` although `MouseTrap` is defined further down the file.
Python looks up a name inside a function when the function runs,
not when its `def` executes.
By the time anything calls `next()`,
the whole module has run and `MouseTrap` exists.

`StateMachine`'s constructor runs the initial state,
the construction-starts-the-engine choice that [*Template Method* warns against](25_Patterns--Template_Method.md#dont-start-the-engine-in-the-constructor).
Two facts make it safe here:
`MouseTrap.__init__()` assigns nothing after its `super().__init__()` call,
and no state's `run()` reads anything off the machine.
A later edit can undo either one.
If you give a `State` a `run()` that reads a machine attribute,
that warning applies again.

None of the four state classes inherits from `State`.
Each satisfies the Protocol by defining `run()` and `next()`.
A base class could also give the annotations a type to name:

    class State: pass

With that base the error waits for the call.
Python constructs an instance of a derived class that defines `run()` alone,
and the machine runs it until something calls its `next()`;
that call raises an `AttributeError`.
A base whose methods `raise NotImplementedError` raises from the base's method instead,
with whatever message you write there.
[*Surrogate*](26_Patterns--Surrogate.md#proxy) shows the other option:
make `State` an `ABC` with `@abstractmethod` on both methods,
and the error moves to the constructor,
which raises a `TypeError` for a subclass that defines `run()` alone.
The type checker reports that construction too,
so the `ABC` and the Protocol both report the missing method before the program runs;
the two plain bases report it at the call.

### A Table Inside Each State

The `match` statements inside `next()` work,
but a machine with many states means many of them, spread across many classes.
Another approach puts a table inside each `State` object,
listing the next state for each input.
A state's table cannot sit in that state's class body,
because the entries name the other states,
and those states exist only after every class definition has run.
So the classes come first,
and module-level code fills in the tables once every state object exists.

`TableState` supplies `next()` from a `transitions` dict that maps each input to its next state,
and leaves `run()` abstract for its subclasses.
It is an `ABC`, the alternative the first version set aside,
because here the base has code to share: every subclass inherits `next()`.
Its `run()` and `next()` have the signatures the `State` Protocol names,
so the `StateMachine` class from the previous example drives it unchanged.
`TableState.__init__()` starts every state with an empty dict.
If you forget to fill one,
the machine reports `Waiting has no transition for ...` rather than an `AttributeError`.
The subclasses shrink to their `run()` behavior.
The transitions live in the tables filled in at the bottom of the file:

```python
# mouse_trap_tables.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, override
from exceptions import expect
from mouse_action import MouseAction
from state import State
from state_machine import StateMachine

class TableState(ABC):
    def __init__(self) -> None:
        self.transitions: dict[object, State] = {}

    @abstractmethod
    def run(self) -> None: ...

    def next(self, event: object) -> State:
        try:
            return self.transitions[event]
        except KeyError:
            raise RuntimeError(
                f"{type(self).__name__} has no transition "
                f"for {event}") from None

class Waiting(TableState):
    @override
    def run(self) -> None:
        print("Waiting: Broadcasting cheese smell")

class Luring(TableState):
    @override
    def run(self) -> None:
        print("Luring: Presenting Cheese, door open")

class Trapping(TableState):
    @override
    def run(self) -> None:
        print("Trapping: Closing door")

class Holding(TableState):
    @override
    def run(self) -> None:
        print("Holding: Mouse caught")

class MouseTrap(StateMachine):
    waiting: ClassVar[TableState] = Waiting()
    luring: ClassVar[TableState] = Luring()
    trapping: ClassVar[TableState] = Trapping()
    holding: ClassVar[TableState] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)

# Every state object now exists, so each table can name
# its next states directly:
MouseTrap.waiting.transitions = {
    MouseAction.APPEARS: MouseTrap.luring,
}
MouseTrap.luring.transitions = {
    MouseAction.RUNS_AWAY: MouseTrap.waiting,
    MouseAction.ENTERS: MouseTrap.trapping,
}
MouseTrap.trapping.transitions = {
    MouseAction.ESCAPES: MouseTrap.waiting,
    MouseAction.TRAPPED: MouseTrap.holding,
}
MouseTrap.holding.transitions = {
    MouseAction.REMOVED: MouseTrap.waiting,
}

text = Path("mouse_moves.txt").read_text()
moves = [line.strip() for line in text.splitlines()
         if line.strip() and not line.startswith("#")]
MouseTrap().run_all([MouseAction(m) for m in moves])
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse runs away
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse escapes
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse trapped
#: Holding: Mouse caught
#: mouse removed
#: Waiting: Broadcasting cheese smell

# ESCAPES is not a key in Waiting.transitions:
trap2 = MouseTrap()
expect(RuntimeError, trap2.run_all, [MouseAction.ESCAPES])
#: Waiting: Broadcasting cheese smell
#: mouse escapes
#: [RuntimeError] Waiting has no transition for mouse
#: escapes
```

The output matches the first version's, move for move.
The source is what changed: with many `State` classes to maintain,
the tables read more easily than the `match` statements.

`next()` raises its `RuntimeError` `from None`,
because the chained `KeyError` would only repeat the event the message already names.

### An Unexpected Input

The two versions also differ on an unexpected input,
a case outside the nine moves in the file.
Both listings end with one more call that sends one:
feeding `MouseAction.ESCAPES` to a fresh trap in `Waiting`,
where neither the `match` nor the table names it.
Version 1 prints `Waiting: Broadcasting cheese smell` a second time.
Version 2 raises `RuntimeError: Waiting has no transition for mouse escapes`.

Version 1's `case _` arms return the current state,
so an unrecognized input keeps the machine where it is.
Staying in the same state is itself a transition.
`run_all()` calls `run()` on whatever state `next()` returns,
so a transition back to the current state runs that state's action a second time.
Version 2's table holds the explicit transitions alone,
and its `next()` raises an exception on every other input.

Either answer can be right, so choose it on purpose.
Staying in the same state suits a machine fed from a source that includes events meant for something else.
Raising an exception suits a table you are still building,
where a missing entry is a bug the exception reports.
The table-driven engine below raises an exception for the same reason.

## Table-Driven State Machine

The previous design keeps each state's transitions inside the state class.
A fully table-driven design represents the entire machine as a single transition table.
All the behavior is then in one place,
so you can build and maintain it directly from a state-transition diagram.
The example is a vending machine, built in two steps:
an engine with no vending-specific code in it, then the machine's table.

For a given current state and input, a transition row records three things:
whether a condition must pass, what action runs during the transition,
and what state comes next.
As a table:

    {(current_state, InputType): [(condition, action, next_state), ...]}

The original Java version of this example needed two extra class hierarchies,
`Condition` and `Transition`,
because the Java of the time had no way to store a method as a value.
Python functions are first-class, so the Python version needs neither hierarchy.
A condition is any callable returning a `bool`, an action is any callable,
and the table is an ordinary `dict`.

The inputs change shape too.
The mousetrap's inputs are `MouseAction` members, bare names.
The vending machine's inputs carry values: what a coin is worth,
which digit the user pressed.
So each input becomes an object of its own class,
and the table keys on that class rather than on a value.
An enum is the wrong shape here for two reasons.
You set its members when you write it,
so its values are the ones you knew about then.
Every member of one enum also shares that enum's class,
so `type(event)` is the same key for all of them.

This design reuses two names with new meanings.
`tabledriven/table_machine.py` holds a different `StateMachine` from the one above,
and `State` is now an `Enum` of names rather than a `Protocol` the state classes satisfy.
The states in this design do nothing.
The table holds all the behavior.

The file's name differs from the first engine's `state_machine.py` on purpose.
Python [caches each module under its import name](06_Foundations--Modules_and_Packages.md),
so a program that imports two files named `state_machine.py` gets the first one both times,
with no error.

### The Engine

For the current state and the type of the incoming event,
the engine tries the candidate transitions in order,
takes the first whose condition passes (or has no condition),
runs that transition's action, and moves to the next state:

```python
# tabledriven/table_machine.py
from collections.abc import Callable
from enum import Enum

# (condition, action, next_state); condition and action
# may be None. A state is an Enum member, so a misspelled
# state is a type error rather than a silent dead end.
type Transition = tuple[
    Callable[..., bool] | None, Callable[..., None] | None,
    Enum
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

The listing writes `StateMachine` by hand rather than as a `@dataclass`,
because a generated `__init__()` names each parameter after its field.
This constructor renames what it stores: the caller passes `initial`,
but the attribute is `state`, which `handle()` updates.

Several candidate transitions can share one `(state, input)` key.
Their conditions tell them apart.
The engine tries them top to bottom,
which is how a single input can lead to different states depending on a test.
A row whose condition is `None` matches every time,
so it belongs last in its group, as the `else` for the rows above it.
When every condition in a group returns `False`,
`handle()` raises the same `NoTransition` a missing key raises.
`NoTransition` derives from `RuntimeError`,
so a caller can catch the specific failure instead of every `RuntimeError` an action method might raise.

### A Vending Machine

One table now defines the whole machine.
The machine collects money, takes a two-digit selection,
then either dispenses the item, reports it sold out,
or clears a selection that costs more than the money inserted.
The conditions and actions are ordinary methods, stored directly in the table.

![The vending machine's five states and the inputs that move it between them](_images/stateMachine)

`Money` moves the machine to `COLLECTING` and keeps it there,
a first digit moves it to `SELECTING`,
and a second digit moves it to one of three states, decided by price and stock.
`Quit` refunds from any of the other states back to `QUIESCENT`.

The states are an `Enum`,
so the type checker reports a misspelled state name before the program runs.
A misspelled string would pass every check and surface as a `NoTransition` at runtime.
`MouseAction` is a `StrEnum` because its values have to match lines of the input file.
These states stay inside the program, so a plain `Enum` with `auto()` serves:

```python
# tabledriven/vending_machine.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()
    SELECTING = auto()
    UNAVAILABLE = auto()
    WANT_MORE = auto()

@dataclass
class Money:
    name: str
    value: int

    def __str__(self) -> str:
        return self.name

class Quit:
    def __str__(self) -> str:
        return "Quit"

@dataclass
class Digit:
    name: str
    value: int

    def __str__(self) -> str:
        return self.name

class FirstDigit(Digit):
    pass
class SecondDigit(Digit):
    pass

@dataclass
class ItemSlot:
    price: int
    quantity: int

class VendingMachine(StateMachine):
    def __init__(self) -> None:
        self.amount = 0  # Money inserted, in cents
        self.row = 0  # The first selection digit
        # Last action, for a view to display
        self.message = ""
        # A 4x4 grid; column c costs (c + 1) * 25 cents:
        self.items = [[ItemSlot((c + 1) * 25, 5)
                       for c in range(4)]
                      for _ in range(4)]
        # One sold-out slot
        self.items[3][0] = ItemSlot(25, 0)
        table: Table = {
            (State.QUIESCENT, Money):
                [(None, self.add_money, State.COLLECTING)],
            (State.COLLECTING, Money):
                [(None, self.add_money, State.COLLECTING)],
            (State.COLLECTING, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.COLLECTING, FirstDigit):
                [(None, self.choose_row, State.SELECTING)],
            (State.SELECTING, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.SELECTING, SecondDigit): [
                (self.too_expensive, self.clear,
                 State.COLLECTING),
                (self.sold_out, self.clear,
                 State.UNAVAILABLE),
                (None, self.dispense, State.WANT_MORE),
            ],
            (State.UNAVAILABLE, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.UNAVAILABLE, FirstDigit):
                [(None, self.choose_row, State.SELECTING)],
            (State.WANT_MORE, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.WANT_MORE, FirstDigit):
                [(None, self.choose_row, State.SELECTING)],
        }
        super().__init__(State.QUIESCENT, table)

    def _slot(self, col: SecondDigit) -> ItemSlot:
        return self.items[self.row][col.value]

    # Conditions:
    def too_expensive(self, col: SecondDigit) -> bool:
        return self._slot(col).price > self.amount

    def sold_out(self, col: SecondDigit) -> bool:
        return self._slot(col).quantity == 0

    def add_money(self, money: Money) -> None:
        self.amount += money.value
        self.message = f"Total = {self.amount}"

    def choose_row(self, digit: FirstDigit) -> None:
        self.row = digit.value
        self.message = f"Row {digit}"

    def clear(self, col: SecondDigit) -> None:
        slot = self._slot(col)
        self.message = (f"Cleared: costs {slot.price}, "
                        f"quantity {slot.quantity}")

    def dispense(self, col: SecondDigit) -> None:
        slot = self._slot(col)
        slot.quantity -= 1
        self.amount -= slot.price
        self.message = (
            f"Dispensing; remaining {self.amount}")

    def refund(self, event: object) -> None:
        self.message = f"Returning {self.amount}"
        self.amount = 0

if __name__ == "__main__":
    events = [
        Money("quarter", 25), Money("quarter", 25),
        Money("dollar", 100),
        # Buy [0][1]
        FirstDigit("A", 0), SecondDigit("col 1", 1),
        # Buy it again
        FirstDigit("A", 0), SecondDigit("col 1", 1),
        # Too expensive
        FirstDigit("C", 2), SecondDigit("col 2", 2),
        # Sold out
        FirstDigit("D", 3), SecondDigit("col 0", 0),
        Quit(),  # Refund and reset
        # Row D, col 0 is both too expensive (a dime
        # isn't 25 cents) and sold out (quantity 0);
        # too_expensive is listed first, so it wins:
        Money("dime", 10),
        FirstDigit("D", 3), SecondDigit("col 0", 0),
    ]
    machine = VendingMachine()
    for event in events:
        machine.handle(event)
        print(f"{event}: {machine.message} "
              f"[{machine.state.name}]")
#: quarter: Total = 25 [COLLECTING]
#: quarter: Total = 50 [COLLECTING]
#: dollar: Total = 150 [COLLECTING]
#: A: Row A [SELECTING]
#: col 1: Dispensing; remaining 100 [WANT_MORE]
#: A: Row A [SELECTING]
#: col 1: Dispensing; remaining 50 [WANT_MORE]
#: C: Row C [SELECTING]
#: col 2: Cleared: costs 75, quantity 5 [COLLECTING]
#: D: Row D [SELECTING]
#: col 0: Cleared: costs 25, quantity 0 [UNAVAILABLE]
#: Quit: Returning 50 [QUIESCENT]
#: dime: Total = 10 [COLLECTING]
#: D: Row D [SELECTING]
#: col 0: Cleared: costs 25, quantity 0 [COLLECTING]
```

The sold-out and too-expensive clears both print `Cleared` and end in different states.
Too expensive returns to `COLLECTING` with the money still inserted,
while sold out goes to `UNAVAILABLE`.
The state names the condition;
the message alone leaves you inferring it from the quantity.

The last three events insert a dime and pick the same sold-out slot again,
this time with too little money for it as well.
Both conditions are now true,
and `too_expensive` comes first in that row's list, so the engine takes it.
The machine reports `COLLECTING`, as though a dollar more would sell it,
although the slot is empty and no amount of money would.
If you swap the row order, the same input reports `UNAVAILABLE` instead.
That follows from the ordering rule stated above:
the first row whose condition passes wins,
even when a lower row is the one that matters.

The engine's lookup keys on `type(event)` exactly,
one dictionary lookup rather than an `isinstance()` test against each row.
The table keys separate rows on `FirstDigit` and `SecondDigit`,
two subclasses of `Digit` that differ only in their class.
The same exactness excludes a further subclass:
an event whose class derives from `Money` matches none of `Money`'s rows,
because the key is the event's exact class.

The table goes in `__init__()` rather than in the class body,
because each entry is a bound method.
`self.add_money` holds a reference to this machine,
so each `VendingMachine`'s table calls methods that read and write its own `amount` and `items`.

The engine passes the event to both callables,
which is why `refund()` takes an argument it ignores.
The `Callable[..., bool]` and `Callable[..., None]` annotations leave the parameters as `...` because each method declares the specific event type it handles,
and those types differ from row to row.
That `...` costs a check: the type checker accepts any callable in any row,
whatever event class the key names.
If you pair a `SecondDigit` key with a method written for a `FirstDigit`,
the table type-checks clean and does the wrong thing at runtime.

Adding a state or an input is now a local change:
an entry in the table and a method or two.
Nothing here needs a `switch`, reflection,
or a `Condition`/`Transition` class hierarchy.
The language's first-class functions and its `dict` supply what those mechanisms exist to provide.

### Testing the Vending Machine

Because the machine is deterministic,
a test can drive it through a sequence of events and check which state it reaches.
The cases worth testing are a successful purchase, the two conditional branches
(too expensive and sold out), a refund,
and the error when no transition matches:

```python
# tabledriven/test_vending.py
import pytest
from table_machine import NoTransition
from vending_machine import (
    FirstDigit,
    Money,
    Quit,
    SecondDigit,
    State,
    VendingMachine,
)

def feed(vm: VendingMachine, *events: object) -> None:
    for event in events:
        vm.handle(event)

def test_buy_dispenses_and_charges() -> None:
    vm = VendingMachine()
    assert vm.state is State.QUIESCENT
    # Item [0][1], 50c
    feed(vm, Money("quarter", 25), Money("quarter", 25),
         FirstDigit("A", 0), SecondDigit("two", 1))
    assert vm.state is State.WANT_MORE
    assert vm.amount == 0  # 50 in, 50 spent
    # One dispensed from five
    assert vm.items[0][1].quantity == 4
    assert vm.message == "Dispensing; remaining 0"

def test_too_expensive_clears_back_to_collecting() -> None:
    vm = VendingMachine()
    # 50c item, 25c in
    feed(vm, Money("quarter", 25),
         FirstDigit("A", 0), SecondDigit("two", 1))
    assert vm.state is State.COLLECTING
    assert vm.amount == 25  # Money kept
    assert vm.items[0][1].quantity == 5  # Nothing dispensed

def test_sold_out_goes_to_unavailable() -> None:
    vm = VendingMachine()
    # [3][0] is sold out
    feed(vm, Money("quarter", 25),
         FirstDigit("D", 3), SecondDigit("one", 0))
    assert vm.state is State.UNAVAILABLE
    assert vm.items[3][0].quantity == 0

def test_quit_refunds_and_resets() -> None:
    vm = VendingMachine()
    feed(vm, Money("dollar", 100), Quit())
    assert vm.state is State.QUIESCENT
    assert vm.amount == 0

def test_no_transition_raises() -> None:
    # QUIESCENT has no transition for Quit
    vm = VendingMachine()
    with pytest.raises(NoTransition):
        vm.handle(Quit())
```

### A View for the Vending Machine

Because the actions set `vm.message`,
`VendingMachine` leaves all output to its caller.
The same machine can therefore drive more than one view.
The text demo in `vending_machine.py` reads `message` and prints it.
Contrast `run_all()` in the first design,
which prints its input from inside the framework.
Printing there is convenient for a book listing and wrong for a reusable machine,
because it puts the `print()` call in the engine,
where every user of `run_all()` gets it.

Using `tkinter`, you can build a GUI for the vending machine.
The panel reads `amount`, the stock, and `message` and shows them on screen.
Its coin, refund, and item buttons turn presses into events for `handle()`.
Because this listing requires user interaction, the harness skips it
(`tools/data/norun.txt`):

```python
# tabledriven/vending_view.py
import tkinter as tk
from functools import partial
from table_machine import NoTransition
from vending_machine import (
    FirstDigit,
    Money,
    Quit,
    SecondDigit,
    VendingMachine,
)

def show() -> None:
    vm = VendingMachine()
    root = tk.Tk()
    root.title("Vending Machine")
    display = tk.Label(root, width=34, anchor="w")
    display.grid(row=0, column=0, columnspan=4, sticky="we")
    buttons: list[list[tk.Button]] = []

    def render() -> None:
        display.config(
            text=f"Inserted {vm.amount}c   {vm.message}")
        for r, row in enumerate(vm.items):
            for c, slot in enumerate(row):
                out = slot.quantity == 0
                qty = "OUT" if out else f"x{slot.quantity}"
                buttons[r][c].config(
                    text=f"{r}{c}\n{slot.price}c\n{qty}",
                    state="disabled" if out else "normal")

    def send(event: object) -> None:
        try:
            vm.handle(event)
        except NoTransition:
            vm.message = "not allowed yet"
        render()

    def select(r: int, c: int) -> None:
        send(FirstDigit(f"row {r}", r))
        send(SecondDigit(f"col {c}", c))

    tk.Button(root, text="+25c",
              command=lambda: send(Money("quarter", 25))
              ).grid(row=1, column=0, sticky="we")
    tk.Button(root, text="+$1",
              command=lambda: send(Money("dollar", 100))
              ).grid(row=1, column=1, sticky="we")
    tk.Button(root, text="Refund",
              command=lambda: send(Quit())
              ).grid(row=1, column=2, columnspan=2,
                     sticky="we")

    for r in range(4):
        button_row: list[tk.Button] = []
        for c in range(4):
            b = tk.Button(root, width=6, height=3,
                          command=partial(select, r, c))
            b.grid(row=2 + r, column=c)
            button_row.append(b)
        buttons.append(button_row)

    render()
    root.mainloop()

if __name__ == "__main__":
    show()
```

`send()` hands each event to `handle()` and catches the `NoTransition` that a rejected click raises
(a selection before any money, say),
so the GUI shows a message instead of the traceback `tkinter` would otherwise print.

The button loop builds sixteen commands with `partial(select, r, c)` rather than a lambda.
Sixteen lambdas closing over `r` and `c` would all read the loop's final values,
the [late-binding trap](28_Patterns--Function_Objects.md#the-late-binding-trap).
The three fixed buttons use lambdas safely, since the one name they capture,
`send`, keeps one value for the life of the window.

## Which Design Should You Use?

The two designs answer the same question, which state comes next,
and put the answer in different places.

Each-state-decides suits a machine whose states do something and have few transitions apiece.
The state class holds both the action and the transitions,
so reading `mouse_trap_states.py`'s `Luring` tells you what luring does and which states can follow it.
Adding a state is one class.
The design reads best when the transitions are obvious from the state's own name.
An action that must run on every entry into one state belongs in that state's `run()`,
written once; sounding a chime whenever the trap reaches `Holding` is such an action.

Inside that design, `match` statements and per-state tables differ in which code handles an unrecognized input.
With `match`, each state's `case _` sets its own policy,
in the method you are reading.
With tables, `TableState.next()` sets one policy for every state,
and each class shrinks to its `run()`.
The tables read better as the states multiply,
because every state's transitions have the same shape and sit together at the bottom of the file.

One-table suits a machine you build from a diagram, whose inputs carry data,
or whose transitions need conditions.
Everything is in one place, in the same order as the diagram.
Adding a state or an input is an entry in the table and a method or two.
The states shrink to `Enum` members, bare names,
so an action that runs on every entry into one state has to live in the table.
It repeats on every row that leads there,
or routes through a helper you write yourself.

The deciding question is which you would rather read: one state's transitions,
gathered in that state, or the whole machine's, gathered in one table.
A machine with a few states works in either design,
and a machine you drew as a diagram first belongs in the table.

With either design you write for yourself what a library supplies.
Mature libraries such as `transitions` and `python-statemachine` supply guards,
callbacks, and hierarchical states.
Using one adds a dependency.
Choose one of the two designs here when you cannot take that dependency,
or want the mechanism visible in your own code.
Choose a library once the machine needs more than a page of code.

## Exercises

1.  Using [*State*](26_Patterns--Surrogate.md#state),
    make a class called `UnpredictablePerson` that changes the kind of response to its `hello()` method depending on its current `Mood`.
    Add another kind of `Mood` called `Prozac`.
2.  Turn exercise 1's `UnpredictablePerson` into a state machine using `state_machine.py`,
    the first design, where each state decides the next one.
3.  Create a *StateMachine* system in which the current state and the input together determine the next state.
    Use a `dict` to map a `str` naming a state to its state object.
    Give each state subclass its own transition table,
    which its `next_state()` method consults.
    Feed the machine a sequence of single words,
    such as a text file with one word per line.
4.  Modify the previous exercise so that you can configure the state machine by editing a single transition table.
5.  Write a `mouse_move_generator()`,
    a [generator](23_Patterns--Iterators.md#generators)
    that yields valid `MouseAction` moves in sequence,
    where each possible move depends on the previous one
    (it is another state machine).
    Have it accept an `int` for the number of moves to produce, then stop.
6.  Apply the table-driven `StateMachine` from `tabledriven/table_machine.py` to a washing-machine problem.
    Give one `(state, input)` pair two rows told apart by a condition,
    such as a load too heavy for the fast spin.
    Then press `Start` in the middle of a cycle,
    an input that state has no row for,
    and decide what the caller does with the `NoTransition`:
    ignore the press or stop the machine.
    Say which policy suits a washing machine, and why.
7.  Create an elevator state machine using `tabledriven/table_machine.py`.
    Give the "doors closing" state two rows for the same input,
    one guarded by a door-obstruction condition.
8.  Create a heating/air-conditioning system using `tabledriven/table_machine.py`.
    A single `TemperatureReading` input must be able to lead to heating,
    cooling, or idle, decided entirely by conditions on one `(state, input)` key.
9.  Build a two-state machine that collects `Money`,
    modeled on `vending_machine.py`'s.
    Add a `Nickel` class deriving from `Money` and feed one in without touching the table.
    Explain the exception, then make it work two ways: by adding a row,
    and by making `Nickel` an instance of `Money` rather than a subclass.
    Say which you would keep.
