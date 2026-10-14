# State Machines

> Many systems are in one of a known set of states at any moment.
> The current state together with an input decides the next state.
> A *State Machine* names the states and defines their transitions.

Recall [*State*](26_Patterns--Surrogate.md#state):
a surrogate forwards calls to one of several implementations,
and the client programmer chooses an implementation.
*State Machine* adds a structure that makes the switch automatically,
from one implementation to the next.
The system behaves differently as it moves from state to state.

A [*Template Method*](25_Patterns--Template_Method.md)
is often used to change states.
You call `run()` on a state to perform its behavior.
Providing an input to `next()` moves the machine into its subsequent state.

We look at two designs.
In the first, each `State` object decides its own next state.
In the second, a single table holds all transitions.

## Each State Decides

A `State` runs its operation and, given an input, names the next `State`:

```python
# state.py
from typing import Protocol

class State(Protocol):
    def run(self) -> None: ...
    def next(self, input_: object, /) -> State: ...
```

The parameter is `input_`, with a trailing underscore,
because a bare `input` would shadow the builtin `input()`.
The `/` after it makes the parameter positional-only.
A function stored in an attribute takes its argument by position alone,
and the chapter's last design stores `next` that way,
so the Protocol asks for no more than a stored function gives.

The `StateMachine` holds the current state and advances it on each input:

```python
# state_machine.py
from collections.abc import Iterable
from state import State

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
```

The constructor sets the initial state and runs it.
`step()` takes one input, asks the current state for its successor,
and moves there.
It then prints the transition (the old state, the input, and the new state)
and calls `run()` for the new state.
A state prints as its name, through a `__str__()` each state class defines.
`run_all()` is a convenience outside the class:
it feeds any iterable of inputs to `step()`, one at a time.
This is the *State* pattern combined with automated transitions,
producing *State Machine*.

The behavior of `run()` depends on the current state.
`step()` defines the flow,
while each `State`'s `run()` and `next()` supply the varying behavior.

In this style of *State Machine*, each state decides the next state.
As an example, consider a mousetrap that can move through several states while trapping a mouse.
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

Each mouse move is a `MouseAction` [enumeration](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too).
Because `MouseAction` is a [`StrEnum`](12_Techniques--Data_Classes_as_Types.md#enum-mix-ins),
each member is a `str`.
`step()` prints `mouse appears` rather than `MouseAction.APPEARS`.

`mouse_moves.py` holds the sequence of mouse inputs.
Its nine moves exercise every transition in the trap,
and the type checker rejects a misspelled member before the program runs:

```python
# mouse_moves.py
from typing import Final
from mouse_action import MouseAction as M

MOVES: Final[list[M]] = [
    M.APPEARS, M.RUNS_AWAY, M.APPEARS, M.ENTERS,
    M.ESCAPES, M.APPEARS, M.ENTERS, M.TRAPPED,
    M.REMOVED,
]
```

### One State Class per Behavior

In this first version of the mousetrap program,
each state class defines its `run()` behavior and decides its next state with a `match` statement:

```python
# mouse_trap_states.py
from typing import ClassVar
from mouse_action import MouseAction
from state import State
from state_machine import StateMachine

class Waiting:
    def run(self) -> None:
        print("Broadcasting cheese smell")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.APPEARS:
                return MouseTrap.luring
            case _:
                return self

class Luring:
    def run(self) -> None:
        print("Presenting Cheese, door open")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.RUNS_AWAY:
                return MouseTrap.waiting
            case MouseAction.ENTERS:
                return MouseTrap.trapping
            case _:
                return self

class Trapping:
    def run(self) -> None:
        print("Closing door")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.ESCAPES:
                return MouseTrap.waiting
            case MouseAction.TRAPPED:
                return MouseTrap.holding
            case _:
                return self

class Holding:
    def run(self) -> None:
        print("Mouse caught")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.REMOVED:
                return MouseTrap.waiting
            case _:
                return self

class MouseTrap(StateMachine):
    waiting: ClassVar[State] = Waiting()
    luring: ClassVar[State] = Luring()
    trapping: ClassVar[State] = Trapping()
    holding: ClassVar[State] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)
```

`MouseTrap` holds all possible states as class attributes and sets up the initial state.
Each `next()` performs a `match` on the input,
providing a `case` for every input the state recognizes.
The default `case _` returns `self`, so the state doesn't change.
Each class's `__str__()` returns its own name, which is what `step()` prints.

`StateMachine`'s constructor runs the initial state,
so constructing the machine starts the engine.
[*Template Method* discourages that choice](25_Patterns--Template_Method.md#dont-start-the-engine-in-the-constructor).
Two facts make that choice safe here:
`MouseTrap.__init__()` assigns nothing after its `super().__init__()` call,
and no state's `run()` reads anything off the machine.

None of the four state classes inherits from `State`.
Each satisfies the Protocol by defining `run()` and `next()`,
and a class that leaves one out fails the type checker where the program uses it as a `State`.

`mouse_trap_states_demo.py` runs a `MouseTrap` through every move in `MOVES`:

```python
# mouse_trap_states_demo.py
from mouse_action import MouseAction
from mouse_moves import MOVES
from mouse_trap_states import MouseTrap
from state_machine import run_all

run_all(MouseTrap(), MOVES)
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse runs away -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse escapes -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse trapped -> Holding
#: Mouse caught
#: Holding mouse removed -> Waiting
#: Broadcasting cheese smell

# ESCAPES has no case in Waiting, so case _
# fires and the machine stays at Waiting:
trap = MouseTrap()
#: Broadcasting cheese smell
trap.step(MouseAction.ESCAPES)
#: Waiting mouse escapes -> Waiting
#: Broadcasting cheese smell
```

### A Table Inside Each State

A machine with many states means many `match` statements,
spread across many classes.
A second approach puts a table inside each `State` object,
mapping the input object to the next state.
The base class holds the lookup,
and each state supplies its own table and its own `run()`:

```python
# table_state.py
from abc import ABC, abstractmethod
from state import State

class NoTransition(RuntimeError):
    "This state's table has no entry for the input."

class TableState(ABC):
    def __init__(self) -> None:
        self.transitions: dict[object, State] = {}

    @abstractmethod
    def run(self) -> None: ...

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        try:
            return self.transitions[input_]
        except KeyError:
            raise NoTransition(
                f"{type(self).__name__}: "
                f"no transition on {input_}") from None
```

`TableState` is an `ABC` rather than a Protocol because the base has code to share.
Both `next()` and `run()` have the signatures the `State` Protocol names,
so the unchanged `StateMachine` from `state_machine.py` drives a `TableState`.
The base also supplies the `__str__()` the trace prints,
so the four subclasses inherit it.

The constructor starts each state with an empty `transitions` table,
and module-level code fills it after every state object exists.
A lookup that finds no entry,
in a table nobody filled or in one missing that input,
raises `NoTransition` from the `except` clause.

The `KeyError` that `next()` catches carries the input as its key,
and the `NoTransition` message includes the same input,
so a chained traceback would show it twice.
`next()` raises `NoTransition` [`from None`](04_Foundations--Control_Flow.md#exception-chaining),
which drops the chained `KeyError`.

The state classes and the `MouseTrap` that instantiates them must be defined before the state tables,
so the table entries can name the other states.
Module-level code fills in the tables after every state object exists:

```python
# mouse_trap_tables.py
from typing import ClassVar, override
from mouse_action import MouseAction
from state_machine import StateMachine
from table_state import TableState

class Waiting(TableState):
    @override
    def run(self) -> None:
        print("Broadcasting cheese smell")

class Luring(TableState):
    @override
    def run(self) -> None:
        print("Presenting Cheese, door open")

class Trapping(TableState):
    @override
    def run(self) -> None:
        print("Closing door")

class Holding(TableState):
    @override
    def run(self) -> None:
        print("Mouse caught")

class MouseTrap(StateMachine):
    waiting: ClassVar[TableState] = Waiting()
    luring: ClassVar[TableState] = Luring()
    trapping: ClassVar[TableState] = Trapping()
    holding: ClassVar[TableState] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)

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
```

The demo feeds a fresh trap the one input for which `Waiting` has no entry,
and `expect()` shows the exception:

```python
# mouse_trap_tables_demo.py
from exceptions import expect
from mouse_action import MouseAction
from mouse_trap_tables import MouseTrap
from table_state import NoTransition

# ESCAPES is not a key in Waiting.transitions:
trap = MouseTrap()
#: Broadcasting cheese smell
expect(NoTransition, trap.step, MouseAction.ESCAPES)
#: [NoTransition] Waiting: no transition on mouse escapes
```

With many `State` classes to maintain,
the tables read more easily than the `match` statements.

Over the nine `MOVES`, both versions print the same trace,
and `test_mouse_traps.py` holds them to it:

```python
# test_mouse_traps.py
import mouse_trap_states
import mouse_trap_tables
import pytest
from mouse_moves import MOVES
from state_machine import run_all

def test_both_versions_print_the_same_trace(
        capsys: pytest.CaptureFixture[str]) -> None:
    run_all(mouse_trap_states.MouseTrap(), MOVES)
    by_match = capsys.readouterr().out
    run_all(mouse_trap_tables.MouseTrap(), MOVES)
    by_table = capsys.readouterr().out
    assert by_match == by_table
```

### An Unexpected Input

Every one of the nine moves in `MOVES` matches a transition out of the current state.
Each demo file feeds `MouseAction.ESCAPES` to a fresh trap in `Waiting`.
Neither `Waiting`'s `match` nor its table names that input.
Version 1 prints `Broadcasting cheese smell` a second time.
Version 2 raises `NoTransition: Waiting: no transition on mouse escapes`.
The figure traces the run both versions share, then this one input:

![](_images/state_story)

The trace at the top covers the nine shared moves.
In each row the current state's `next()` returns the successor,
so the machine moves from object to object and leaves every decision to the states.
Below the trace, the one input on which the versions differ appears twice,
once under each policy.

Version 1's `case _` arms return the current state,
so an unrecognized input keeps the machine in its current state.
Staying in the same state has a visible effect.
`step()` calls `run()` on whatever state `next()` returns,
so returning the current state runs that state's action a second time.
Version 2's table holds the explicit transitions alone,
and its `next()` raises an exception on every other input.

Either policy can be right, so choose one on purpose.
Staying in the same state suits a machine fed from a source that includes inputs meant for something else.
Raising an exception suits a table you are still building,
where a missing entry is a bug the exception reports.
The table-driven engine in `tabledriven/table_machine.py` raises an exception for the same reason.

## Table-Driven State Machine

The each-state-decides design keeps each state's transitions with that state,
in its `next()` or in its table.
A fully table-driven design represents the entire machine as a single transition table.
All the behavior is then in one place,
so you can build and maintain the table from a state-transition diagram.
The example is a vending machine, built in two steps: a general-purpose engine,
then the vending machine's table.

For a given current state and input, a rule records three things:
whether a condition must pass, what action runs during the transition,
and what state comes next:

    Rule(state, InputType, next_state, action, condition)

A condition is any callable returning a `bool`, an action is any callable,
and the rules are a list the engine groups into an ordinary `dict`.

The mousetrap's inputs are `MouseAction` members, bare names.
The vending machine's inputs carry values: what a coin is worth,
which row or column the user pressed.
Each input becomes an object of its own class,
and the table keys on that class rather than on a value.

This design reuses two names with new meanings.
`tabledriven/table_machine.py` holds a different `StateMachine` from the one in `state_machine.py`.
`State` is now an `Enum` of names rather than a `Protocol` the state classes satisfy.
The states in this design are bare names.
The table holds all the behavior.

The name `table_machine.py` differs from the first engine's `state_machine.py` on purpose.
Python [caches each module under its import name](06_Foundations--Modules_and_Packages.md),
so a program that imports two files named `state_machine.py` gets the first one both times,
with no error.

### The Engine

For the current state and the type of the incoming input,
the engine tries the candidate rules in order,
takes the first whose condition passes (or has no condition),
runs that rule's action, and moves to the next state:

```python
# tabledriven/table_machine.py
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

A `Rule` reads as a sentence: from `state`, on an input of `input_type`,
go to `next_state`, running `action` if the rule has one,
provided `condition` passes if the rule has one.
A state is an `Enum` member,
so a misspelled state is a type error rather than a silent dead end.
`Rule` is generic in `I`, the input class, and `input_type` is `type[I]`:
a rule that names `Column` as its input type has `I` of `Column`,
and the checker then requires that rule's `action` and `condition` to accept a `Column`.

The constructor groups the rules by `(state, input_type)` into a dictionary,
so `handle()` finds the candidates for the current state and the input's class in one lookup.
The engine holds the rules as `Rule[Any]`:
it calls each condition and action with whatever input arrived,
and the input class was checked where the rule was built.

The listing writes `StateMachine` by hand rather than as a `@dataclass`.
A generated `__init__()` names each parameter after its field and stores it unchanged.
This constructor takes `rules` and stores `table`,
and its parameter is `initial` while the attribute `handle()` updates is `state`.

Several rules can share one `(state, input_type)` key.
Their conditions tell them apart.
The engine tries them in the order the list gives them,
so a single input can lead to different states depending on a test.
A rule whose condition is `None` matches every time,
so it belongs last in its group, as the `else` for the rules above it.

When every condition in a group returns `False`,
`handle()` raises the same `NoTransition` a missing key raises.
Like `table_state.py`'s, this `NoTransition` derives from `RuntimeError`,
so a caller can catch the specific failure instead of every `RuntimeError` an action method might raise.

### A Vending Machine

One table now defines the whole machine.
The conditions and actions are ordinary methods, stored in the table.
The machine collects money, takes a selection as a row and then a column,
then either dispenses the item, reports it sold out,
or clears a selection that costs more than the money inserted.

![The vending machine's five states and the inputs that move it between them](_images/vending_story)

`Money` moves the machine from `QUIESCENT` to `COLLECTING`,
and more `Money` keeps it there.
A `Row` moves it to `SELECTING`.
A `Column` moves it to one of three states, decided by price and stock.
`Quit` refunds from any of the other states back to `QUIESCENT`.

The states are an `Enum`,
so the type checker reports a misspelled state name before the program runs.
A misspelled string would pass every check,
and the engine would raise a `NoTransition` at runtime.
`MouseAction` is a `StrEnum` so that the trace prints each input as its value,
`mouse appears`.
The vending machine's states need no value,
since the demo prints a state by its `name`,
so a plain `Enum` with `auto()` serves:

```python
# tabledriven/vending_machine.py
from dataclasses import dataclass
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()
    SELECTING = auto()
    UNAVAILABLE = auto()
    WANT_MORE = auto()

@record
class Money:
    name: str
    value: int

    def __str__(self) -> str:
        return self.name

class Quit:
    def __str__(self) -> str:
        return "Quit"

class Row(Enum):
    A = 0
    B = 1
    C = 2
    D = 3

    def __str__(self) -> str:
        return self.name

@record
class Column:
    value: int
    def __str__(self) -> str:
        return f"col {self.value}"

@dataclass
class Slot:
    price: int
    quantity: int

class VendingMachine(StateMachine):
    def __init__(self) -> None:
        self.amount = 0  # Money inserted, in cents
        self.row = Row.A  # The selected row
        # Last action, for the caller to show
        self.message = ""
        # A 4x4 grid; column c costs (c + 1) * 25 cents:
        self.slots = [[Slot((c + 1) * 25, 5)
                       for c in range(4)]
                      for _ in range(4)]
        # One sold-out slot
        self.slots[3][0] = Slot(25, 0)
        paid = [s for s in State
                if s is not State.QUIESCENT]
        rules = [
            Rule(State.QUIESCENT, Money, State.COLLECTING,
                 self.add_money),
            Rule(State.COLLECTING, Money, State.COLLECTING,
                 self.add_money),
            Rule(State.SELECTING, Column, State.COLLECTING,
                 self.clear, self.too_expensive),
            Rule(State.SELECTING, Column, State.UNAVAILABLE,
                 self.clear, self.sold_out),
            Rule(State.SELECTING, Column, State.WANT_MORE,
                 self.dispense),
            *[Rule(s, Quit, State.QUIESCENT, self.refund)
              for s in paid],
            *[Rule(s, Row, State.SELECTING, self.choose_row)
              for s in paid if s is not State.SELECTING],
        ]
        super().__init__(State.QUIESCENT, rules)

    def _slot(self, col: Column) -> Slot:
        return self.slots[self.row.value][col.value]

    # Conditions:
    def too_expensive(self, col: Column) -> bool:
        return self._slot(col).price > self.amount

    def sold_out(self, col: Column) -> bool:
        return self._slot(col).quantity == 0

    def add_money(self, money: Money) -> None:
        self.amount += money.value
        self.message = f"Total = {self.amount}"

    def choose_row(self, row: Row) -> None:
        self.row = row
        prices = [slot.price
                  for slot in self.slots[row.value]]
        self.message = f"{min(prices)}c to {max(prices)}c"

    def clear(self, col: Column) -> None:
        slot = self._slot(col)
        self.message = (f"Cleared: {slot.price}c, "
                        f"{slot.quantity} left")

    def dispense(self, col: Column) -> None:
        slot = self._slot(col)
        slot.quantity -= 1
        self.amount -= slot.price
        self.message = (
            f"Dispensing; remaining {self.amount}")

    def refund(self, input_: object) -> None:
        self.message = f"Returning {self.amount}"
        self.amount = 0
```

The inputs `Money` and `Column` are records,
values the machine reads and leaves as they are.
`Row` is an `Enum` whose four members name the rows,
so a row outside the grid is a type error at the call rather than an index error inside `_slot()`.
`Slot` stays a mutable `@dataclass`,
because `dispense()` decrements its `quantity` in place.

The engine's lookup keys on the exact `type(input_)`,
so finding the rules takes one dictionary lookup rather than an `isinstance()` test against each rule.
That exactness lets the table keep separate entries for `Row` and `Column`,
two input classes that each carry a grid index.
The same exactness excludes a further subclass.
An input whose class derives from `Money` matches none of `Money`'s rules,
because the key is the input's exact class.

The rules go in `__init__()` rather than in the class body,
because each rule holds a bound method.
`self.add_money` holds a reference to this machine,
so each `VendingMachine`'s rules call methods that read and write its own `amount` and `slots`.
`Quit` refunds from every paid state,
and a `Row` selects from every paid state but `SELECTING`,
which is waiting for a `Column`.
Those seven rules come from two comprehensions over `paid` rather than seven lines that differ in one member.

The engine passes the input to both the condition and the action,
so `refund()` takes an argument it ignores.
Each method declares the specific input type it handles,
and those types differ from rule to rule.
`Rule[I]` ties the input type to the methods on the same rule:
naming `Column` makes `I` `Column`,
so the checker requires `clear()` and `too_expensive()` to accept a `Column`.
If you pair `Column` with `choose_row()`, written for a `Row`,
`ty` reports `invalid-argument-type` on that rule.
`refund()` accepts `object`, so it pairs with any input type.

The list is bound to `rules`, with no annotation, before the call.
Written inline as the argument,
the list would take the parameter's `Sequence[Rule[Any]]` as its expected type,
and that `Any` would reach into every `Rule(...)` and make its `I` `Any`,
so the checker would accept any method on any rule.

Adding a state or an input is now a local change:
a rule in the list and a method or two.
Nothing here needs a `switch`, reflection,
or a `Condition`/`Transition` class hierarchy.
The language's first-class functions and its `dict` supply what those mechanisms exist to provide.

`vending_demo.py` feeds a `VendingMachine` a list of inputs.
For each input it prints the transition in the mousetrap's form,
the state before, the input, and the state after,
followed by the message the action left:

```python
# tabledriven/vending_demo.py
from vending_machine import (Column, Money, Quit, Row,
                             VendingMachine)

inputs = [
    Money("quarter", 25), Money("quarter", 25),
    Money("dollar", 100),
    # Buy A, col 1
    Row.A, Column(1),
    # Buy it again
    Row.A, Column(1),
    # Too expensive
    Row.C, Column(2),
    # Sold out
    Row.D, Column(0),
    Quit(),  # Refund and reset
    Money("dime", 10),
    Row.D, Column(0),
]
machine = VendingMachine()
for input_ in inputs:
    before = machine.state
    machine.handle(input_)
    print(f"{before.name} {input_} -> "
          f"{machine.state.name}: {machine.message}")
#: QUIESCENT quarter -> COLLECTING: Total = 25
#: COLLECTING quarter -> COLLECTING: Total = 50
#: COLLECTING dollar -> COLLECTING: Total = 150
#: COLLECTING A -> SELECTING: 25c to 100c
#: SELECTING col 1 -> WANT_MORE: Dispensing; remaining 100
#: WANT_MORE A -> SELECTING: 25c to 100c
#: SELECTING col 1 -> WANT_MORE: Dispensing; remaining 50
#: WANT_MORE C -> SELECTING: 25c to 100c
#: SELECTING col 2 -> COLLECTING: Cleared: 75c, 5 left
#: COLLECTING D -> SELECTING: 25c to 100c
#: SELECTING col 0 -> UNAVAILABLE: Cleared: 25c, 0 left
#: UNAVAILABLE Quit -> QUIESCENT: Returning 50
#: QUIESCENT dime -> COLLECTING: Total = 10
#: COLLECTING D -> SELECTING: 25c to 100c
#: SELECTING col 0 -> COLLECTING: Cleared: 25c, 0 left
```

The sold-out and too-expensive clears both start from `SELECTING` on a column,
both print `Cleared`, and end in different states.
Too expensive returns to `COLLECTING` with the money still inserted,
while sold out goes to `UNAVAILABLE`.
The state after the arrow names the condition.
The message alone leaves you inferring the condition from the quantity.

The last three inputs insert a dime and pick the same sold-out slot again,
this time with too little money for it as well.
Both conditions are now true.
`too_expensive()` comes first in the `(State.SELECTING, Column)` list,
so the engine takes the `too_expensive()` rule.
The machine reports `COLLECTING`, as though more money would sell the item,
although the slot is empty and no amount of money would.
If you swap the rule order, the same input reports `UNAVAILABLE` instead.
Both results follow from the engine's [ordering rule](#the-engine).
The engine runs the first rule whose condition passes,
whether or not a later rule matters more.

### Testing the Vending Machine

Because the machine is deterministic,
a test can drive it through a sequence of inputs and check which state it reaches.
The cases worth testing are:

- A successful purchase
- The too-expensive conditional branch
- The sold-out conditional branch
- A refund
- The error when no transition matches

```python
# tabledriven/test_vending.py
import pytest
from table_machine import NoTransition
from vending_machine import (Column, Money, Quit, Row,
                             State, VendingMachine)

def feed(vm: VendingMachine, *inputs: object) -> None:
    for input_ in inputs:
        vm.handle(input_)

def test_buy_dispenses_and_spends() -> None:
    vm = VendingMachine()
    assert vm.slots[0][1].price == 50
    feed(vm, Money("quarter", 25), Money("quarter", 25),
         Row.A, Column(1))
    assert vm.state is State.WANT_MORE
    assert vm.amount == 0  # 50 in, 50 spent
    # One dispensed from five
    assert vm.slots[0][1].quantity == 4
    assert vm.message == "Dispensing; remaining 0"

def test_too_expensive_clears_back_to_collecting() -> None:
    vm = VendingMachine()
    assert vm.slots[0][1].price == 50
    # 25c in
    feed(vm, Money("quarter", 25), Row.A, Column(1))
    assert vm.state is State.COLLECTING
    assert vm.amount == 25  # Money kept
    assert vm.slots[0][1].quantity == 5  # Nothing dispensed

def test_sold_out_clears_to_unavailable() -> None:
    vm = VendingMachine()
    # [3][0] is sold out
    feed(vm, Money("quarter", 25), Row.D, Column(0))
    assert vm.state is State.UNAVAILABLE
    assert vm.amount == 25  # Money kept
    assert vm.slots[3][0].quantity == 0  # Nothing dispensed

def test_quit_refunds_and_resets() -> None:
    vm = VendingMachine()
    feed(vm, Money("dollar", 100), Quit())
    assert vm.state is State.QUIESCENT
    assert vm.amount == 0

def test_no_transition_raises() -> None:
    vm = VendingMachine()
    assert vm.state is State.QUIESCENT
    with pytest.raises(NoTransition):
        vm.handle(Quit())
```

## States as `Enum` Members

`enum_states.py` is the first design again,
with each state as a row of data rather than a class, run by the same engine.
`Row` is a record that satisfies `State`: its `run()` prints a stored message,
and its `next` is a stored function rather than a method.
`TrapState` is an `Enum` whose members are `Row`s:

```python
# enum_states.py
from collections.abc import Callable
from enum import Enum
from mouse_action import MouseAction as M
from record import record

type Transition = Callable[[object], TrapState]

@record
class Row:
    message: str
    next: Transition

    def run(self) -> None:
        print(self.message)

def waiting(input_: object) -> TrapState:
    match input_:
        case M.APPEARS:
            return TrapState.LURING
        case _:
            return TrapState.WAITING

def luring(input_: object) -> TrapState:
    match input_:
        case M.RUNS_AWAY:
            return TrapState.WAITING
        case M.ENTERS:
            return TrapState.TRAPPING
        case _:
            return TrapState.LURING

def trapping(input_: object) -> TrapState:
    match input_:
        case M.ESCAPES:
            return TrapState.WAITING
        case M.TRAPPED:
            return TrapState.HOLDING
        case _:
            return TrapState.TRAPPING

def holding(input_: object) -> TrapState:
    match input_:
        case M.REMOVED:
            return TrapState.WAITING
        case _:
            return TrapState.HOLDING

class TrapState(Row, Enum):
    WAITING = ("Broadcasting cheese smell", waiting)
    LURING = ("Presenting Cheese, door open", luring)
    TRAPPING = ("Closing door", trapping)
    HOLDING = ("Mouse caught", holding)

    def __str__(self) -> str:
        return self.name.capitalize()
```

A `Row` holds the message its `run()` prints and the function its `next` names.
The `Transition` alias names `TrapState` above the class statement that creates it.
A `type` alias evaluates its right side lazily,
so the forward reference resolves when the checker or the program reads the alias.
The four transition functions are the first design's `next()` methods pulled out of their classes:
`waiting()` matches on the input the way `Waiting.next()` in `mouse_trap_states.py` does,
and names the member the trap enters next.
A function body runs after the whole module has loaded,
so a `TrapState` named inside one resolves too.

`TrapState` mixes `Row` into `Enum`.
Each member's value is a tuple,
and `Enum` passes the tuple to `Row`'s constructor,
so `TrapState.WAITING` is a `TrapState` member and a `Row` at once,
with `message` and `next` as attributes.
The engine's call `state.next(input_)` reads the same whether `next` is a method or a stored function.
The type checker accepts the row as a `State` because `State.next()` declares its parameter positional-only:
a stored function takes its argument by position alone,
where a method's parameter would also accept the keyword form `input_=`.
`__str__()` returns the member's name in the form the trace prints,
so `WAITING` prints as `Waiting`.

`enum_states_demo.py` runs the rows through the first design's engine,
and the trace is `mouse_trap_states_demo.py`'s, line for line:

```python
# enum_states_demo.py
from enum_states import TrapState
from mouse_moves import MOVES
from state_machine import StateMachine, run_all

run_all(StateMachine(TrapState.WAITING), MOVES)
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse runs away -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse escapes -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse trapped -> Holding
#: Mouse caught
#: Holding mouse removed -> Waiting
#: Broadcasting cheese smell
```

`test_enum_states.py` holds the rows to that trace:

```python
# test_enum_states.py
import mouse_trap_states
import pytest
from enum_states import TrapState
from mouse_moves import MOVES
from state_machine import StateMachine, run_all

def test_rows_print_the_class_trace(
        capsys: pytest.CaptureFixture[str]) -> None:
    run_all(mouse_trap_states.MouseTrap(), MOVES)
    by_class = capsys.readouterr().out
    run_all(StateMachine(TrapState.WAITING), MOVES)
    by_row = capsys.readouterr().out
    assert by_class == by_row
```

Two consequences follow from the mixin.
`Enum` folds members with equal values into one,
and a record's equality compares its fields,
so two members with the same message and the same function collapse into a single member with two names.
Every state therefore needs a function of its own.
The type checker reads `next` from the record's field,
so the engine's `state.next(input_)` checks against `State` the way a method call does.
It leaves a member's tuple uncompared with the fields:
a tuple holding the message alone, or the two in the wrong order,
passes `ty` and fails at import or at run time.
Pyright reports both.

Against `mouse_trap_states.py`, what changes is where a state lives.
A class with two methods becomes a row holding a message and a function,
and the `ClassVar` holder on `MouseTrap` becomes the enum.
The Protocol, the engine, and the trace stay the same.

## Which Design Should You Use?

The three designs answer the same question, which state comes next,
and put the answer in different places.

Each-state-decides suits a machine whose states do something and have few transitions apiece.
The state class holds both the action and the transitions,
so reading `mouse_trap_states.py`'s `Luring` tells you what luring does and which states can follow it.
Adding a state is one class.
The design reads best when the transitions are obvious from the state's own name.

An action that must run on every entry into one state belongs in that state's `run()`,
written once.
Sounding a chime whenever the trap reaches `Holding` is such an action.

Inside the each-state-decides design,
`match` statements and per-state tables differ in which code handles an unrecognized input.
With `match`, each state's `case _` sets its own policy, in the method you read.
With tables, `TableState.next()` sets one policy for every state,
and each class defines `run()` and inherits `next()`.
The tables read better as the states multiply,
because every state's transitions have the same shape and appear together at the bottom of the file.

One-table suits a machine you build from a diagram, whose inputs carry data,
or whose transitions need conditions.
Everything is in one place, in the same order as the diagram.
Adding a state or an input is a rule in the list and a method or two.

In the one-table design the states are `Enum` members, bare names,
so an action that runs on every entry into one state must go in the table.
You repeat the action on every rule that leads to that state,
or write a helper that those rules call.

States as `Enum` members is the first design with records in place of classes.
Each member names its own successors, as `Luring` does,
and carries its action as data, and the first design's engine runs both.
The enum supplies what four loose classes cannot:
`list(TrapState)` enumerates every state,
and a parameter typed `TrapState` accepts a member and rejects anything else.
The shape suits a machine whose states each do one thing and whose transitions are a `match` apiece.
A state that keeps data of its own has nowhere to put it,
since a member is one frozen record shared by every machine that uses it,
and such a state is a class.

The first design's constructor calls the initial state's `run()`,
but the constructor in `table_machine.py` stores `initial` and returns.
In the one-table design,
an action the machine needs at startup is a call you make before the first input.

The deciding question is which you would rather read: one state's transitions,
gathered in that state, the whole machine's, gathered in one table,
or each state as one enum row holding its action and its successors.
A machine with a few states works in any of the three,
and a machine you drew as a diagram first belongs in the table.

With any of these designs you write for yourself what a library supplies.
Mature libraries such as `transitions` and `python-statemachine` supply guards,
callbacks, and hierarchical states.
Using a library adds a dependency.
Choose one of the designs here when you cannot take that dependency,
or want the mechanism visible in your own code.
Choose a library once the machine needs more than a page of code.

## Exercises

Try each exercise before opening its [solution](../Solutions/31_Patterns--State_Machines/).

1.  Using [*State*](26_Patterns--Surrogate.md#state),
    make a class called `UnpredictablePerson` that changes the kind of response to its `hello()` method depending on its current `Mood`.
    Add another kind of `Mood` called `Prozac`.
2.  Turn exercise 1's `UnpredictablePerson` into a state machine using `state_machine.py`,
    the first design, where each state decides the next one.
3.  Create a *State Machine* system in which the current state and the input together determine the next state.
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
    Give one `(state, input)` pair two rules told apart by a condition,
    such as a load too heavy for the fast spin.
    Then press `Start` in the middle of a cycle,
    an input for which that state has no rule,
    and decide what the caller does with the `NoTransition`:
    ignore the press or stop the machine.
    Say which policy suits a washing machine, and why.
7.  Create an elevator state machine using `tabledriven/table_machine.py`.
    Give the "doors closing" state two rules for the same input,
    one guarded by a door-obstruction condition.
8.  Create a heating/air-conditioning system using `tabledriven/table_machine.py`.
    A single `TemperatureReading` input must be able to lead to heating,
    cooling, or idle, decided entirely by conditions on one `(state, input)` key.
9.  Build a two-state machine that collects `Money`,
    modeled on `vending_machine.py`'s.
    Add a `Nickel` class deriving from `Money` and feed one in without touching the table.
    Explain the exception, then make it work two ways: by adding a rule,
    and by making `Nickel` an instance of `Money` rather than a subclass.
    Say which you would keep.
10. Rewrite exercise 2's mood machine in the shape of `enum_states.py`:
    a `Mood` enum of rows,
    each carrying its greeting and its transition function,
    with the inputs as a `StrEnum` and `state_machine.py`'s engine running it.
    Say what a mood gains and loses as an enum member rather than a class.
