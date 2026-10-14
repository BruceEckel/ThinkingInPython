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

A `State` is a record holding the message its `run()` prints and the function that,
given an input, names the next `State`:

```python
# state.py
from collections.abc import Callable
from record import record

@record
class State:
    message: str
    next: Callable[[object], State]

    def run(self) -> None:
        print(self.message)
```

`next` is a stored function rather than a method,
so the call `state.next(input_)` passes the input alone, with no `self`.
The field's annotation names `State` inside its own class body;
annotations are evaluated lazily, so the name resolves.
The input is typed `object`,
so a function can accept any input and `match` on it.

In this style of *State Machine*, each state decides the next state.
As an example, consider a mousetrap that can move through several states while trapping a mouse.
The possible moves a mouse can make are the inputs to the state machine:

```python
# mouse.py
from enum import StrEnum

class Mouse(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"
```

Each mouse move is a member of the `Mouse` [enumeration](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too).
Because `Mouse` is a [`StrEnum`](12_Techniques--Data_Classes_as_Types.md#enum-mix-ins),
each member is a `str`.
`step()` prints `mouse appears` rather than `Mouse.APPEARS`.

`mouse_moves.py` holds the sequence of mouse inputs.
Its nine moves exercise every transition in the trap,
and the type checker rejects a misspelled member before the program runs:

```python
# mouse_moves.py
from typing import Final
from mouse import Mouse

MOVES: Final[list[Mouse]] = [
    Mouse.APPEARS, Mouse.RUNS_AWAY, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.ESCAPES, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.TRAPPED, Mouse.REMOVED,
]
```

### The Mousetrap

Each state of the trap is a `State` record:
the message its `run()` prints and the function that names its successor.
`TrapState` is an `Enum` whose members are those records:

```python
# trap_states.py
from enum import Enum
from mouse import Mouse
from state import State

def waiting(input_: object) -> TrapState:
    match input_:
        case Mouse.APPEARS:
            return TrapState.LURING
        case _:
            return TrapState.WAITING

def luring(input_: object) -> TrapState:
    match input_:
        case Mouse.RUNS_AWAY:
            return TrapState.WAITING
        case Mouse.ENTERS:
            return TrapState.TRAPPING
        case _:
            return TrapState.LURING

def trapping(input_: object) -> TrapState:
    match input_:
        case Mouse.ESCAPES:
            return TrapState.WAITING
        case Mouse.TRAPPED:
            return TrapState.HOLDING
        case _:
            return TrapState.TRAPPING

def holding(input_: object) -> TrapState:
    match input_:
        case Mouse.REMOVED:
            return TrapState.WAITING
        case _:
            return TrapState.HOLDING

class TrapState(State, Enum):
    WAITING = ("Broadcasting cheese smell", waiting)
    LURING = ("Presenting Cheese, door open", luring)
    TRAPPING = ("Closing door", trapping)
    HOLDING = ("Mouse caught", holding)

    def __str__(self) -> str:
        return self.name.capitalize()
```

Each transition function performs a `match` on the input,
with a `case` for every input its state recognizes,
and names the member the trap enters next.
The default `case _` returns the function's own member,
so the state stays the same.
A function body runs after the whole module has loaded,
so a `TrapState` named inside one resolves too.

`TrapState` mixes `State` into `Enum`.
Each member's value is a tuple,
and `Enum` passes the tuple to `State`'s constructor,
so `TrapState.WAITING` is a `TrapState` member and a `State` at once,
with `message` and `next` as attributes.
`__str__()` returns the member's name in the form the trace prints,
so `WAITING` prints as `Waiting`, and `step()` prints each state through it.

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
The parameter is `input_`, with a trailing underscore,
because a bare `input` shadows the builtin `input()`.
It then prints the transition (the old state, the input, and the new state)
and calls `run()` for the new state.
A state prints as its name, through the `__str__()` that `TrapState` defines.
`run_all()` is a convenience outside the class:
it feeds any iterable of inputs to `step()`, one at a time.
This is the *State* pattern combined with automated transitions,
producing *State Machine*.

The behavior of `run()` depends on the current state.
`step()` defines the flow,
while each `State`'s `run()` and `next()` supply the varying behavior.

This split has a name.
A machine whose action belongs to the state, and takes no input,
is a *Moore machine*: what a state does depends on the state alone,
and the input chooses the successor.
`run()` takes no argument for that reason.

`trap_states_demo.py` runs a trap through every move in `MOVES`,
then feeds a fresh trap the one input for which `waiting()` has no `case`:

```python
# trap_states_demo.py
from mouse import Mouse
from mouse_moves import MOVES
from state_machine import StateMachine, run_all
from trap_states import TrapState

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

# ESCAPES has no case in waiting(), so case _
# fires and the machine stays at Waiting:
trap = StateMachine(TrapState.WAITING)
#: Broadcasting cheese smell
trap.step(Mouse.ESCAPES)
#: Waiting mouse escapes -> Waiting
#: Broadcasting cheese smell
```

`StateMachine`'s constructor runs the initial state,
so constructing the machine starts the engine.
[*Template Method* discourages that choice](25_Patterns--Template_Method.md#dont-start-the-engine-in-the-constructor).
Two facts make that choice safe here:
the call is the constructor's last statement,
and no state's `run()` reads anything off the machine.

`test_trap_states.py` holds the trap to two facts the trace shows:
the nine moves bring it back to `Waiting`,
and every state answers every move with a state:

```python
# test_trap_states.py
from mouse import Mouse
from mouse_moves import MOVES
from state_machine import StateMachine, run_all
from trap_states import TrapState

def test_nine_moves_return_to_waiting() -> None:
    trap = StateMachine(TrapState.WAITING)
    run_all(trap, MOVES)
    assert trap.current_state is TrapState.WAITING

def test_every_state_answers_every_move() -> None:
    for state in TrapState:
        for move in Mouse:
            assert state.next(move) in TrapState
```

The second test iterates the enum,
so a state added to `TrapState` joins the test with no edit to the test.

Two consequences follow from the mixin.
`Enum` folds members with equal values into one,
and a record's equality compares its fields,
so two members with the same message and the same function collapse into a single member with two names.
Every state therefore needs a function of its own.
The type checker reads `next` from the record's field and checks the engine's call `state.next(input_)` against it.
It leaves a member's tuple uncompared with the fields:
a tuple holding the message alone, or the two in the wrong order,
passes `ty` and fails at import or at run time.
Pyright reports both.

### An Unexpected Input

Every one of the nine moves in `MOVES` matches a transition out of the current state.
The demo then feeds `Mouse.ESCAPES` to a fresh trap in `Waiting`,
and the trap prints `Broadcasting cheese smell` a second time.
The figure traces the nine moves:

![](_images/state_story)

In each row the current state's `next()` returns the successor,
so the machine moves from member to member and leaves every decision to the states.

The `case _` arm returns the current state,
so an unrecognized input keeps the machine in its current state.
Staying in the same state has a visible effect.
`step()` calls `run()` on whatever state `next()` returns,
so returning the current state runs that state's action a second time.
The other policy is to raise an exception from `case _`,
so an input for which the state has no `case` stops the program and reports itself.

Either policy can be right, so choose one on purpose.
Staying in the same state suits a machine fed from a source that includes inputs meant for something else.
Raising an exception suits a table you are still building,
where a missing entry is a bug the exception reports.
The table-driven engine in `tabledriven/table_machine.py` raises an exception for that reason.

## Table-Driven State Machine

The each-state-decides design keeps each state's transitions with that state,
in its `next` function.
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

The action on a rule takes the input,
so what the machine does depends on the state and the input together.
That is a *Mealy machine*, the other classical shape.
The first design's `run()` acts per state and sees no input,
while a rule's `action` acts per transition and reads the input that fired it.

The mousetrap's inputs are `Mouse` members, bare names.
The vending machine's inputs carry values: what a coin is worth,
which row or column the user pressed.
Each input becomes an object of its own class,
and the table keys on that class rather than on a value.

This design reuses two names with new meanings.
`tabledriven/table_machine.py` holds a different `StateMachine` from the one in `state_machine.py`.
`State` is now an `Enum` of names rather than the record the mousetrap's states are.
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
`NoTransition` derives from `RuntimeError`,
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
`Mouse` is a `StrEnum` so that the trace prints each input as its value,
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

## Which Design Should You Use?

The two designs answer the same question, which state comes next,
and put the answer in different places.

Each-state-decides suits a machine whose states do something and have few transitions apiece.
The row holds the action and its function holds the transitions,
so reading `trap_states.py`'s `LURING` and `luring()` tells you what luring does and which states can follow it.
Adding a state is one row and one function.
The design reads best when the transitions are obvious from the state's own name.

An action that must run on every entry into one state belongs in that state's `run()`,
written once.
Sounding a chime whenever the trap reaches `Holding` is such an action.
That is the Moore shape: the action belongs to the state.

One-table suits a machine you build from a diagram, whose inputs carry data,
or whose transitions need conditions.
Everything is in one place, in the same order as the diagram.
Adding a state or an input is a rule in the list and a method or two.

In the one-table design the states are `Enum` members, bare names,
so an action that runs on every entry into one state must go in the table.
You repeat the action on every rule that leads to that state,
or write a helper that those rules call.
That is the Mealy shape: the action belongs to the transition,
and in return it can read the input that caused the transition.

In both designs the states are `Enum` members.
`list(TrapState)` enumerates every state,
and a parameter typed `TrapState` accepts a member and rejects anything else.
A member is one frozen record shared by every machine that uses it,
so a state that keeps data of its own has nowhere to put it.
Such a state is a class with a `run()` and a `next()` of its own,
and an engine that drives both a class and a record types its parameter as a Protocol naming those two methods.

The first design's constructor calls the initial state's `run()`,
but the constructor in `table_machine.py` stores `initial` and returns.
In the one-table design,
an action the machine needs at startup is a call you make before the first input.

The deciding question is which you would rather read: one state's transitions,
gathered in that state's function, or the whole machine's,
gathered in one table.
A machine with a few states works in either,
and a machine you drew as a diagram first belongs in the table.

With either design you write for yourself what a library supplies.
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
2.  Turn exercise 1's `UnpredictablePerson` into a state machine in the shape of `trap_states.py`:
    a `Mood` enum of rows,
    each carrying its greeting and its transition function,
    with the inputs as a `StrEnum` and `state_machine.py`'s engine running it.
    Say what a mood gains and loses as an enum member rather than a class.
3.  Create a *State Machine* system in which the current state and the input together determine the next state.
    Make the states an `Enum` of rows, as in `trap_states.py`,
    where each row's transition function consults that state's own `dict`,
    mapping a word to the name of the next state.
    Feed the machine a sequence of single words,
    such as a text file with one word per line.
4.  Modify the previous exercise so that you can configure the state machine by editing a single transition table.
5.  Write a `mouse_move_generator()`,
    a [generator](23_Patterns--Iterators.md#generators)
    that yields valid `Mouse` moves in sequence,
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
