# State Machines

Recall [*State*](26_Surrogate.md#state):
a surrogate object that forwards calls to a swappable implementation.
While *State* allows the client programmer to change the implementation,
*StateMachine* imposes a structure to automatically change the implementation from one object to the next.
The current implementation represents the state a system occupies,
and the system behaves differently from one state to the next
(because it uses *State*).

The code that moves the system from one state to the next is often a [*Template Method*](25_Template_Method.md),
as the following framework for a basic state machine shows.
You can `run()` each state to perform its behavior, and (in this design)
also pass it an "input" object so it can tell you which state to enter next.
This design and the next differ in one key way: here,
each `State` object makes that decision on its own,
whereas in the subsequent design a single table holds all of the state transitions.

## Each State Decides

```python
# state.py
# A State has an operation, and can be moved
# into the next State given an Input:

class State:
    def run(self) -> None:
        raise NotImplementedError("run not implemented")
    def next(self, event: object) -> State:
        raise NotImplementedError("next not implemented")
```

Python does not require this class.
It is worth its few lines because it names `State` as a type in annotations,
and because it produces a better error message when a derived class leaves a method out.
You could get nearly the same effect by saying:

    class State: pass

because calling `run()` or `next()` on a derived type that hasn't implemented them still raises an exception.
Without the base, the failure is an `AttributeError` at the call.
With it, a `NotImplementedError` that names what is missing.
[Surrogate](26_Surrogate.md#proxy) shows the third option:
make `State` an `ABC` with `@abstractmethod` on both methods,
and constructing an incomplete subclass fails outright.
The version here fails later than that, at the call rather than at construction,
which is enough for a design where every state comes into existence once,
as a class attribute.

The `StateMachine` keeps track of the current state,
which the constructor initializes.
The `run_all()` method takes a sequence of input objects.
For each one it moves to the next state, then calls that state's `run()`.
It expands the *State* pattern:
`run()` does something different depending on the state the system occupies:

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
[Template Method](25_Template_Method.md) puts the varying steps in a subclass.
Here they come from the `State` objects the machine holds.
The constructor also runs the initial state,
the construction-starts-the-engine choice that [drew a warning in that chapter](25_Template_Method.md#dont-start-the-engine-in-the-constructor).
It is safe here for two reasons that are easy to lose:
`MouseTrap.__init__()` assigns nothing after its `super().__init__()` call,
and no state's `run()` reads anything off the machine.
A `State` whose `run()` reads attributes off the machine revives the trap.

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
([Data Classes as Types](12_Data_Classes_as_Types.md#enums-are-types-too) introduces `Enum`).
Because it is a `StrEnum`, each member *is* a `str`,
and compares equal to and prints as its value.
That is why `print(event)` in `run_all()` shows `mouse appears` rather than `MouseAction.APPEARS`.
The members still hash and look up correctly, so they work as dictionary keys,
and `MouseAction("mouse appears")` returns the matching member,
which is how the code below parses the test input.

A text file supplies the sequence of mouse inputs:

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
mouse appears
mouse runs away
mouse appears
mouse enters trap
mouse trapped
mouse removed
```

### One State Class per Behavior

Here's the first version of the mousetrap program.
Each `State` subclass defines its `run()` behavior,
and also establishes its next state with a `match` statement:

```python
# mouse_trap.py
from pathlib import Path
from typing import ClassVar, override
from mouse_action import MouseAction
from state import State
from state_machine import StateMachine

class Waiting(State):
    @override
    def run(self) -> None:
        print("Waiting: Broadcasting cheese smell")

    @override
    def next(self, event: object) -> State:
        match event:
            case MouseAction.APPEARS:
                return MouseTrap.luring
            case _:
                return MouseTrap.waiting

class Luring(State):
    @override
    def run(self) -> None:
        print("Luring: Presenting Cheese, door open")

    @override
    def next(self, event: object) -> State:
        match event:
            case MouseAction.RUNS_AWAY:
                return MouseTrap.waiting
            case MouseAction.ENTERS:
                return MouseTrap.trapping
            case _:
                return MouseTrap.luring

class Trapping(State):
    @override
    def run(self) -> None:
        print("Trapping: Closing door")

    @override
    def next(self, event: object) -> State:
        match event:
            case MouseAction.ESCAPES:
                return MouseTrap.waiting
            case MouseAction.TRAPPED:
                return MouseTrap.holding
            case _:
                return MouseTrap.trapping

class Holding(State):
    @override
    def run(self) -> None:
        print("Holding: Mouse caught")

    @override
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
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse runs away
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse trapped
#: Holding: Mouse caught
#: mouse removed
#: Waiting: Broadcasting cheese smell
```

`MouseTrap` holds all the possible states as class attributes and sets up the initial state.
The code at the bottom of the file builds a `MouseTrap` and runs it through the whole sequence of moves read from the text file.

### A Table Inside Each State

The `match` statements inside `next()` work,
but a machine with many states means many of them, spread across many classes.
Another approach puts a table inside each `State` object,
listing the next state for each input.
You cannot write a table inside its class,
because its entries name the other states,
which do not all exist until every class definition runs.
Define the classes first, then fill in the tables at module level,
after all the state objects exist.

The `TableState` class implements `State` and adds a `transitions` dict mapping each input to its next state
(so the same `StateMachine` class from the previous example still serves).
Its `next()` looks the input up in that `dict`.
`TableState.__init__()` gives every state that empty dict:
a state whose table you forgot to fill then reports `Waiting has no transition for ...` rather than an `AttributeError`.
The subclasses now define only their `run()` behavior.
The transitions live in the tables filled in at the bottom of the file:

```python
# mouse_trap2.py
# A better mousetrap using tables
from pathlib import Path
from typing import ClassVar, override
from mouse_action import MouseAction
from state import State
from state_machine import StateMachine

class TableState(State):
    def __init__(self) -> None:
        self.transitions: dict[object, State] = {}

    @override
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
MouseTrap().run_all([MouseAction(m) for m in moves[:9]])
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
```

The demonstration stops after the first nine moves,
which between them exercise every transition in the trap.
The rest of the input file only repeats them,
so the output continues as in the first version.

If you must create and maintain many `State` classes,
the tables improve on the `match` statements,
since reading the transitions from a table is easier.
`next()` raises its `RuntimeError` `from None` rather than chaining,
which drops a `KeyError` that would repeat the event the message names.

### An Unexpected Input

The two versions also answer a question this input file does not ask:
what happens on an unexpected input?
They answer it differently.
Version 1's `case _` arms return the current state,
so an input a state does not recognize raises no exception and the machine stays put.
Staying put is not the same as doing nothing:
`run_all()` calls `run()` on whatever state `next()` returns,
so a transition back to the current state runs that state's action a second time.
Version 2's table holds only the explicit transitions,
and its `next()` raises an exception on anything else.
Neither is wrong, but the choice deserves to be deliberate.
Ignoring suits a machine fed from a noisy source that includes events not meant for it.
Failing fast suits a table you are still building,
where a missing entry is a bug you want flagged,
and the table-driven engine below adopts the same policy.

## Table-Driven State Machine

The previous design keeps each state's transitions inside the state class.
A fully table-driven design can go further and represent the entire machine as a single transition table.
All the behavior then lives in one place,
so you can build and maintain it directly from a state-transition diagram.

For a given current state and input, a transition row answers three questions:
whether a condition must pass, what action runs during the transition,
and what state comes next.
As a table:

    {(current_state, InputType): [(condition, action, next_state), ...]}

The original Java version of this example needed two extra class hierarchies,
`Condition` and `Transition`,
because the Java of the time had no way to store a method as a value.
Python functions are first-class, so those hierarchies vanish.
A condition is any callable returning a `bool`, an action is any callable,
and the table is an ordinary `dict`.

The inputs change shape too.
The mousetrap's inputs are `MouseAction` members, names with nothing attached.
A vending machine's inputs carry values: what a coin is worth,
which digit the user pressed.
So each input becomes an object of its own class,
and the table keys on that class rather than on a value.
An enum fixes its members in advance,
so it can carry only the values you knew about when you wrote it,
and every member of one enum arrives under the same dispatch key.

The names restart here.
`tabledriven/table_machine.py` holds a different `StateMachine` from the one above,
and `State` is now an `Enum` of names rather than a base class with behavior.
The file has a different name from the first engine's `state_machine.py` on purpose.
Python caches a module in `sys.modules` under its import name,
and a later `import` takes the cached module without looking at any file.
Two files named `state_machine.py` in one program therefore collapse into one:
whichever imported first wins,
and the second import silently gets the wrong module.
The states in this design do nothing.
The table holds all the behavior.

### The Engine

For the current state and the type of the incoming event,
the engine walks the candidate transitions in order,
takes the first whose condition passes (or has no condition),
runs that transition's action, and moves to the next state:

```python
# tabledriven/table_machine.py
# A generic table-driven state machine.
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

The listing writes `StateMachine` out by hand rather than as a `@dataclass` because its constructor renames what it stores:
the caller passes `initial`, but the attribute is `state`,
the position `handle()` updates.
A generated `__init__()` cannot rename the parameter.
`NoTransition` derives from `RuntimeError`,
so a caller can catch the specific failure instead of every `RuntimeError` an action method might raise.

Several candidate transitions can share one `(state, input)` key.
Their conditions tell them apart.
The engine tries them top to bottom,
which is how a single input can lead to different states depending on a test.
A row whose condition is `None` matches every time,
so it belongs last in its group,
as the `else` to which the earlier rows fall through.
A group with no such catch-all row can still match nothing:
if every condition returns `False`,
`handle()` falls through to the same `NoTransition` a missing key raises.
The lookup keys on `type(event)` exactly: a dictionary probe,
not an `isinstance()` walk.
That lets the vending machine below treat `FirstDigit` and `SecondDigit` as distinct inputs even though both derive from `Digit`,
and it cuts the other way too:
if you define a further subclass of an event type,
it matches none of its parent's rows.
An event's dispatch class must appear in the table by name.
A subclass will not do.

Both callables receive the event, whether they need it or not,
which is why `refund()` takes an argument it ignores.
The `Callable[..., bool]` and `Callable[..., None]` annotations leave the parameters as `...` because each method declares the specific event type it handles,
and no one signature covers them all.
That `...` costs you a check.
Nothing verifies that a row's condition and action accept the event class named in that row's key,
so pairing a `SecondDigit` key with a method written for a `FirstDigit` type-checks clean and then quietly does the wrong thing at runtime.

### A Vending Machine

One table now defines the whole machine.
The machine collects money, takes a two-digit selection,
then either dispenses the item, reports it sold out,
or clears a selection that costs more than the money inserted.
The conditions and actions are ordinary methods, stored directly in the table.

![Five states, QUIESCENT, COLLECTING, SELECTING, UNAVAILABLE, and WANT_MORE; money loops COLLECTING back on itself, a first digit moves to SELECTING, and a second digit branches three ways on price and stock, while Quit refunds from any of the other states back to QUIESCENT](_images/stateMachine)

The states are an `Enum`,
so the type checker catches a misspelled state name instead of letting it fail silently at runtime.
`MouseAction`'s values match lines of the input file.
Nothing parses these states from text,
so `Enum` with `auto()` serves in place of `StrEnum`:

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
```

The two `Cleared` lines read alike and end in different states:
too expensive returns to `COLLECTING` with the money still inserted,
while sold out goes to `UNAVAILABLE`.
Only the state shows which condition fired.

`__init__()` builds the table, rather than the class body,
because each entry is a bound method.
`self.add_money` carries this machine with it,
so each `VendingMachine` gets a table wired to its own money and stock.

Adding a state or an input is now a local change:
an entry in the table and a method or two.
Nothing here needs a `switch`, reflection,
or a `Condition`/`Transition` class hierarchy.
The language's first-class functions and its `dict` supply what those patterns existed to provide.

Because the machine is deterministic,
a test can drive it through a sequence of events and check which state it reaches.
The cases worth pinning down are a successful purchase,
the two conditional branches (too expensive and sold out), a refund,
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

Because the actions set `vm.message` instead of printing,
the model draws nothing, and the same machine can drive more than one view.
The text demo in `vending_machine.py` reads `message` and prints it.
Contrast `run_all()` in the first design,
which prints its input from inside the framework.
That is convenient for a book listing and wrong for a reusable machine:
it fixes one output device into the engine.
Recording a message instead pushes the choice out to whoever is watching.

Using `tkinter`, you can build a GUI for the vending machine.
The panel reads `amount`, the stock, and `message` and shows them on screen.
The coin and item buttons turn presses into events for `handle()`,
and the GUI catches a click that the state machine rejects
(a selection before any money, say) and shows it rather than crashing.
The button loop builds sixteen commands with `partial(select, r, c)`,
not with a lambda: sixteen lambdas closing over `r` and `c` all see the loop's final values,
the late-binding trap from [Function Objects](28_Function_Objects.md#command-choosing-the-operation-at-runtime)
(the three fixed buttons above use lambdas safely, since they close over nothing that varies).
Because it requires user interaction the harness skips it
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

## Which Design Should You Use?

The two designs answer the same question and put the answer in different places.

Each-state-decides suits a machine whose states do something and have few transitions apiece.
The state class owns both halves,
so reading `Luring` tells you what luring does and where it can go next,
and adding a state is one class.
It reads best when the transitions are obvious from the state's own name.

One-table suits a machine you build from a diagram, whose inputs carry data,
or whose transitions need conditions.
Everything is in one place, in the same order as the diagram,
and adding a state or an input is an entry in the table and a method or two.
The states shrink to `Enum` members with no behavior.

The tell is which reading you would rather do: the transitions for one state,
gathered in that state, or every transition in the machine,
gathered in one table.
A machine small enough to hold in your head goes either way,
and a machine that arrived as a diagram belongs in the table.

## Exercises

1.  Using [State](26_Surrogate.md#state),
    make a class called `UnpredictablePerson` which changes the kind of response to its `hello()` method depending on its current `Mood`.
    Add an additional kind of `Mood` called `Prozac`.
2.  Apply the table-driven `StateMachine` from `tabledriven/table_machine.py` to a washing-machine problem.
    Give one `(state, input)` pair two rows told apart by a condition,
    such as a load too heavy for the fast spin.
3.  Create a *StateMachine* system whereby the current state along with the input determines the next state.
    Use a `dict` to map a `str` naming a state to its state object.
    Give each state subclass its own transition table,
    which its `next_state()` method consults.
    Feed the machine a sequence of single words,
    such as a text file with one word per line.
4.  Modify the previous exercise so that you can configure the state machine by editing a single transition table.
5.  Modify the "mood" exercise (exercise 1)
    so that it becomes a state machine using `state_machine.py`,
    the first design, where each state decides the next one.
6.  Create an elevator state machine using `tabledriven/table_machine.py`.
    Give the "doors closing" state two rows for the same input,
    one guarded by a door-obstruction condition.
7.  Create a heating/air-conditioning system using `tabledriven/table_machine.py`.
    A single `TemperatureReading` input must be able to lead to heating,
    cooling, or idle, decided entirely by conditions on one `(state, input)` key.
8.  Write a `mouse_move_generator()` ([Iterators](23_Iterators.md#generators))
    that yields valid `MouseAction` moves in sequence,
    where each possible move depends on the previous one
    (it is another state machine).
    Have it accept an `int` for the number of moves to produce, then stop.
9.  Add a `Nickel` class deriving from `Money` to `vending_machine.py` and feed one to the machine without touching the table.
    Explain the exception, then make it work two ways: by adding a row,
    and by making `Nickel` an instance of `Money` rather than a subclass.
    Say which you would keep.
