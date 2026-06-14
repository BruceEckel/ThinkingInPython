# State Machines

While *State* has a way to allow the client programmer to change the
implementation, *StateMachine* imposes a structure to automatically
change the implementation from one object to the next. The current
implementation represents the state that a system is in, and the system
behaves differently from one state to the next (because it uses
*State*). Basically, this is a "state machine" using objects.

The code that moves the system from one state to the next is often a
*Template Method*, as seen in the following framework for a basic state
machine.

Each state can be `run()` to perform its behavior, and (in this
design) you can also pass it an "input" object so it can tell you what
new state to move to based on that "input". The key distinction between
this design and the next is that here, each `State` object decides
what other states it can move to, based on the "input", whereas in the
subsequent design all of the state transitions are held in a single
table. Another way to put it is that here, each `State` object has its
own little `State` table, and in the subsequent design there is a
single master state transition table for the whole system:

```python
# State.py
# A State has an operation, and can be moved
# into the next State given an Input:

class State:
    def run(self):
        assert 0, "run not implemented"
    def next(self, input):
        assert 0, "next not implemented"
```

This class is clearly unnecessary, but it allows us to say that
something is a `State` object in code, and provide a slightly
different error message when all the methods are not implemented. We
could have gotten basically the same effect by saying:

    class State: pass

because we would still get exceptions if `run()` or `next()` were
called for a derived type, and they hadn't been implemented.

The `StateMachine` keeps track of the current state, which is
initialized by the constructor. The `runAll()` method takes a list of
`Input` objects. This method not only moves to the next state, but it
also calls `run()` for each state object; thus you can see it's an
expansion of the idea of the `State` pattern, since `run()` does
something different depending on the state that the system is in:

```python
# StateMachine.py
# Takes a list of Inputs to move from State to
# State using a template method.

class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        self.currentState.run()
    # Template method:
    def runAll(self, inputs):
        for i in inputs:
            print(i)
            self.currentState = self.currentState.next(i)
            self.currentState.run()
```

I've also treated `runAll()` as a template method. This is typical,
but certainly not required; you could conceivably want to override it,
but typically the behavior change will occur in `State`'s `run()`
instead.

At this point the basic framework for this style of *StateMachine* (where each
state decides the next states) is complete. As an example, I'll use a fancy
mousetrap that can move through several states in the process of trapping a
mouse^[No mice were harmed in the creation of this example.]. The mouse
classes and information are stored in the `mouse` package, including a class
representing all the possible moves that a mouse can make, which will be the
inputs to the state machine:

```python
# mouse/MouseAction.py

class MouseAction:
    appears: "MouseAction"
    runsAway: "MouseAction"
    enters: "MouseAction"
    escapes: "MouseAction"
    trapped: "MouseAction"
    removed: "MouseAction"

    def __init__(self, action: str) -> None:
        self.action = action
    def __str__(self) -> str: return self.action
    def __eq__(self, other: object) -> bool:
        return (isinstance(other, MouseAction)
                and self.action == other.action)
    # Necessary when __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self) -> int:
        return hash(self.action)

# Static fields; an enumeration of instances:
MouseAction.appears = MouseAction("mouse appears")
MouseAction.runsAway = MouseAction("mouse runs away")
MouseAction.enters = MouseAction("mouse enters trap")
MouseAction.escapes = MouseAction("mouse escapes")
MouseAction.trapped = MouseAction("mouse trapped")
MouseAction.removed = MouseAction("mouse removed")
```

You'll note that `__cmp__()` has been overidden to implement a
comparison between `action` values. Also, each possible move by a
mouse is enumerated as a `MouseAction` object, all of which are static
fields in `MouseAction`.

For creating test code, a sequence of mouse inputs is provided from a
text file:

```python
# mouse/MouseMoves.txt
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

With these tools in place, it's now possible to create the first version
of the mousetrap program. Each `State` subclass defines its `run()`
behavior, and also establishes its next state with an `if-else`
clause:

```python
# mousetrap1/MouseTrapTest.py
# State Machine pattern using 'if' statements
# to determine the next state.
import sys
sys.path += ['..', '../mouse']
from State import State
from StateMachine import StateMachine
from MouseAction import MouseAction  # type: ignore
# A different subclass for each state:

class Waiting(State):
    def run(self):
        print("Waiting: Broadcasting cheese smell")

    def next(self, input):
        if input == MouseAction.appears:
            return MouseTrap.luring
        return MouseTrap.waiting

class Luring(State):
    def run(self):
        print("Luring: Presenting Cheese, door open")

    def next(self, input):
        if input == MouseAction.runsAway:
            return MouseTrap.waiting
        if input == MouseAction.enters:
            return MouseTrap.trapping
        return MouseTrap.luring

class Trapping(State):
    def run(self):
        print("Trapping: Closing door")

    def next(self, input):
        if input == MouseAction.escapes:
            return MouseTrap.waiting
        if input == MouseAction.trapped:
            return MouseTrap.holding
        return MouseTrap.trapping

class Holding(State):
    def run(self):
        print("Holding: Mouse caught")

    def next(self, input):
        if input == MouseAction.removed:
            return MouseTrap.waiting
        return MouseTrap.holding

class MouseTrap(StateMachine):
    waiting: State
    luring: State
    trapping: State
    holding: State

    def __init__(self) -> None:
        # Initial state
        StateMachine.__init__(self, MouseTrap.waiting)

# Static variable initialization:
MouseTrap.waiting = Waiting()
MouseTrap.luring = Luring()
MouseTrap.trapping = Trapping()
MouseTrap.holding = Holding()

with open("../mouse/MouseMoves.txt") as f:
    moves = [line.strip() for line in f
             if line.strip() and not line.startswith('#')]
MouseTrap().runAll([MouseAction(m) for m in moves])
```

The `StateMachine` class simply defines all the possible states as
static objects, and also sets up the initial state. The `UnitTest`
creates a `MouseTrap` and then tests it with all the inputs from a
`MouseMoveList`.

While the use of `if` statements inside the `next()` methods is
perfectly reasonable, managing a large number of these could become
difficult. Another approach is to create tables inside each `State`
object defining the various next states based on the input.

Initially, this seems like it ought to be quite simple. You should be
able to define a static table in each `State` subclass that defines
the transitions in terms of the other `State` objects. However, it
turns out that this approach generates cyclic initialization
dependencies. To solve the problem, I've had to delay the initialization
of the tables until the first time that the `next()` method is called
for a particular `State` object. Initially, the `next()` methods
can appear a little strange because of this.

The `StateT` class is an implementation of `State` (so that the same
`StateMachine` class can be used from the previous example) that adds
a `Map` and a method to initialize the map from a two-dimensional
array. The `next()` method has a base-class implementation which must
be called from the overridden derived class `next()` methods after
they test for a `null Map` (and initialize it if it's `null`):

```python
# mousetrap2/MouseTrap2Test.py
# A better mousetrap using tables
import sys
from typing import Any
sys.path += ['..', '../mouse']
from State import State
from StateMachine import StateMachine
from MouseAction import MouseAction  # type: ignore

class StateT(State):
    def __init__(self) -> None:
        self.transitions: dict[Any, Any] | None = None
    def next(self, input):
        assert self.transitions is not None
        if input in self.transitions:
            return self.transitions[input]
        else:
            raise Exception("Input not supported for current state")

class Waiting(StateT):
    def run(self):
        print("Waiting: Broadcasting cheese smell")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.appears : MouseTrap.luring
            }
        return StateT.next(self, input)

class Luring(StateT):
    def run(self):
        print("Luring: Presenting Cheese, door open")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.enters : MouseTrap.trapping,
              MouseAction.runsAway : MouseTrap.waiting
            }
        return StateT.next(self, input)

class Trapping(StateT):
    def run(self):
        print("Trapping: Closing door")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.escapes : MouseTrap.waiting,
              MouseAction.trapped : MouseTrap.holding
            }
        return StateT.next(self, input)

class Holding(StateT):
    def run(self):
        print("Holding: Mouse caught")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.removed : MouseTrap.waiting
            }
        return StateT.next(self, input)

class MouseTrap(StateMachine):
    waiting: State
    luring: State
    trapping: State
    holding: State

    def __init__(self) -> None:
        # Initial state
        StateMachine.__init__(self, MouseTrap.waiting)

# Static variable initialization:
MouseTrap.waiting = Waiting()
MouseTrap.luring = Luring()
MouseTrap.trapping = Trapping()
MouseTrap.holding = Holding()

with open("../mouse/MouseMoves.txt") as f:
    moves = [line.strip() for line in f
             if line.strip() and not line.startswith('#')]
mouseMoves = [MouseAction(m) for m in moves]
MouseTrap().runAll(mouseMoves)
```

The rest of the code is identical; the difference is in the `next()`
methods and the `StateT` class.

If you have to create and maintain a lot of `State` classes, this
approach is an improvement, since it's easier to quickly read and
understand the state transitions from looking at the table.

## Table-Driven State Machine

The previous design keeps each state's transitions inside the state class. A
pure state machine can go further and represent the *entire* machine as a
single transition table. All the behavior then lives in one place, so you can
build and maintain it directly from a state-transition diagram.

For a given current state and input, a transition row answers three questions:
is there a condition to check, what action runs during the transition, and what
state do we move to next. As a table:

    {(current_state, InputType): [(condition, action, next_state), ...]}

The original Java version of this example needed two extra class hierarchies,
`Condition` and `Transition`, because in Java a method is not a value you can
store in a table. Python functions are first-class, so those hierarchies
vanish: a condition is any callable returning a bool, an action is any callable,
and the table is an ordinary `dict`.

![Vending machine state diagram](_images/stateMachine)

### The Engine

The engine is tiny. For the current state and the type of the incoming event,
it walks the candidate transitions in order, takes the first whose condition
passes (or has no condition), runs that transition's action, and moves to the
next state:

```python
# tabledriven/state_machine.py
# A generic table-driven state machine.
#
# The whole machine is one transition table. Because Python functions are
# first-class, a transition's condition and action are just callables, so the
# Condition and Transition classes a Java version needs disappear.
from collections.abc import Callable
from typing import Any

# (condition, action, next_state); condition and action may be None.
Transition = tuple[Callable[..., bool] | None, Callable[..., None] | None, str]
Table = dict[tuple[str, type], list[Transition]]


class StateMachine:
    def __init__(self, initial: str, table: Table) -> None:
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
            f"no transition from {self.state!r} on {type(event).__name__}")
```

Several candidate transitions can share one `(state, input)` key, told apart by
their conditions. The engine tries them top to bottom, which is how a single
input can lead to different states depending on a test.

### A Vending Machine

The machine is now entirely a table. It collects money, takes a two-digit
selection, then either dispenses the item, reports it sold out, or clears a
selection that costs more than the money inserted. The conditions and actions
are plain methods, stored directly in the table:

```python
# tabledriven/vending_machine.py
# A vending machine expressed entirely as a transition table.
from state_machine import StateMachine, Table


class Money:
    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return self.name


class Quit:
    def __str__(self) -> str:
        return "Quit"


class Digit:
    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return self.name


class FirstDigit(Digit): pass
class SecondDigit(Digit): pass


class ItemSlot:
    def __init__(self, price: int, quantity: int) -> None:
        self.price = price
        self.quantity = quantity


class VendingMachine(StateMachine):
    def __init__(self) -> None:
        self.amount = 0  # money inserted, in cents
        self.row = 0     # the first selection digit
        # A 4x4 grid of items; column c costs (c + 1) * 25 cents:
        self.items = [[ItemSlot((c + 1) * 25, 5) for c in range(4)]
                      for _ in range(4)]
        self.items[3][0] = ItemSlot(25, 0)  # one sold-out slot
        table: Table = {
            ("quiescent", Money): [(None, self.add_money, "collecting")],
            ("collecting", Money): [(None, self.add_money, "collecting")],
            ("collecting", Quit): [(None, self.refund, "quiescent")],
            ("collecting", FirstDigit): [(None, self.choose_row, "selecting")],
            ("selecting", Quit): [(None, self.refund, "quiescent")],
            ("selecting", SecondDigit): [
                (self.too_expensive, self.clear, "collecting"),
                (self.sold_out, self.clear, "unavailable"),
                (None, self.dispense, "want_more"),
            ],
            ("unavailable", Quit): [(None, self.refund, "quiescent")],
            ("unavailable", FirstDigit): [(None, self.choose_row, "selecting")],
            ("want_more", Quit): [(None, self.refund, "quiescent")],
            ("want_more", FirstDigit): [(None, self.choose_row, "selecting")],
        }
        super().__init__("quiescent", table)

    def _slot(self, col: SecondDigit) -> ItemSlot:
        return self.items[self.row][col.value]

    # Conditions:
    def too_expensive(self, col: SecondDigit) -> bool:
        return self._slot(col).price > self.amount

    def sold_out(self, col: SecondDigit) -> bool:
        return self._slot(col).quantity == 0

    # Actions:
    def add_money(self, money: Money) -> None:
        self.amount += money.value
        print(f"Total = {self.amount}")

    def choose_row(self, digit: FirstDigit) -> None:
        self.row = digit.value
        print(f"Row {digit}")

    def clear(self, col: SecondDigit) -> None:
        slot = self._slot(col)
        print(f"Clearing selection: costs {slot.price}, "
              f"quantity {slot.quantity}")

    def dispense(self, col: SecondDigit) -> None:
        slot = self._slot(col)
        slot.quantity -= 1
        self.amount -= slot.price
        print(f"Dispensing; amount remaining {self.amount}")

    def refund(self, event: object) -> None:
        print(f"Returning {self.amount}")
        self.amount = 0


if __name__ == "__main__":
    events = [
        Money("quarter", 25), Money("quarter", 25), Money("dollar", 100),
        FirstDigit("A", 0), SecondDigit("two", 1),    # buy item [0][1]
        FirstDigit("A", 0), SecondDigit("two", 1),    # buy it again
        FirstDigit("C", 2), SecondDigit("three", 2),  # too expensive
        FirstDigit("D", 3), SecondDigit("one", 0),    # sold out
        Quit(),                                        # refund and reset
    ]
    machine = VendingMachine()
    for event in events:
        machine.handle(event)
```

Adding a state or an input is now a local change: an entry in the table and a
method or two. There is no `switch`, no reflection, and no `Condition` or
`Transition` class hierarchy. The language's first-class functions and its
`dict` supply what those patterns existed to provide.


## Tools

Another approach, as your state machine gets bigger, is to use an
automation tool whereby you configure a table and let the tool generate
the state machine code for you. This can be created yourself using a
language like Python, but there are also free, open-source tools such as
*Libero*, at <http://www.imatix.com>.

## Exercises

1.  Create an example of the "virtual proxy."
2.  Create an example of the "Smart reference" proxy where you keep
    count of the number of method calls to a particular object.
3.  Create a program similar to certain DBMS systems that only allow a
    certain number of connections at any time. To implement this, use a
    singleton-like system that controls the number of "connection"
    objects that it creates. When a user is finished with a connection,
    the system must be informed so that it can check that connection
    back in to be reused. To guarantee this, provide a proxy object
    instead of a reference to the actual connection, and design the
    proxy so that it will cause the connection to be released back to
    the system.
4.  Using the *State*, make a class called `UnpredictablePerson` which
    changes the kind of response to its `hello()` method depending on
    what kind of `Mood` it's in. Add an additional kind of `Mood`
    called `Prozac`.
5.  Create a simple copy-on write implementation.
6.  Apply `TransitionTable.py` to the "Washer" problem.
7.  Create a *StateMachine* system whereby the current state along with
    input information determines the next state that the system will be
    in. To do this, each state must store a reference back to the proxy
    object (the state controller) so that it can request the state
    change. Use a `HashMap` to create a table of states, where the key
    is a `String` naming the new state and the value is the new state
    object. Inside each state subclass override a method `nextState(
    )` that has its own state-transition table. The input to
    `nextState()` should be a single word that comes from a text file
    containing one word per line.
8.  Modify the previous exercise so that the state machine can be
    configured by creating/modifying a single multi-dimensional array.
9.  Modify the "mood" exercise from the previous session so that it
    becomes a state machine using StateMachine.py
10. Create an elevator state machine system using StateMachine.py
11. Create a heating/air-conditioning system using StateMachine.py
12. A *generator* is an object that produces other objects, just like a
    factory, except that the generator function doesn't require any
    arguments. Create a `MouseMoveGenerator` which produces correct
    `MouseMove` actions as outputs each time the generator function is
    called (that is, the mouse must move in the proper sequence, thus
    the possible moves are based on the previous move; it's another
    state machine). Add a method to produce an iterator, but this method
    should take an `int` argument that specifies the number of moves
    to produce before `hasNext()` returns `false`.

Both *Proxy* and *State* provide a surrogate class that you use in your
code; the real class that does the work is hidden behind this surrogate
class. When you call a method in the surrogate, it simply turns around
and calls the method in the implementing class. These two patterns are
so similar that the *Proxy* is simply a special case of *State*. One is
tempted to just lump the two together into a pattern called *Surrogate*,
but the term "proxy" has a long-standing and specialized meaning, which
probably explains the reason for the two different patterns.

The basic idea is simple: from a base class, the surrogate is derived
along with the class or classes that provide the actual implementation:

![image description](_images/surrogate)

When a surrogate object is created, it is given an implementation to
which to send all of the method calls.

Structurally, the difference between *Proxy* and *State* is simple: a
*Proxy* has only one implementation, while *State* has more than one.
The application of the patterns is considered (in *Design Patterns*) to
be distinct: *Proxy* is used to control access to its implementation,
while *State* allows you to change the implementation dynamically.
However, if you expand your notion of "controlling access to
implementation" then the two fit neatly together.

## Proxy

If we implement *Proxy* by following the above diagram, it looks like
this:

```python
# ProxyDemo.py
# Simple demonstration of the Proxy pattern.

class Implementation:
    def f(self):
        print("Implementation.f()")
    def g(self):
        print("Implementation.g()")
    def h(self):
        print("Implementation.h()")

class Proxy:
    def __init__(self):
        self.__implementation = Implementation()
    # Pass method calls to the implementation:
    def f(self): self.__implementation.f()
    def g(self): self.__implementation.g()
    def h(self): self.__implementation.h()

p = Proxy()
p.f(); p.g(); p.h()
```

It isn't necessary that `Implementation` have the same interface as
`Proxy`; as long as `Proxy` is somehow "speaking for" the class that
it is referring method calls to then the basic idea is satisfied (note
that this statement is at odds with the definition for Proxy in GoF).
However, it is convenient to have a common interface so that
`Implementation` is forced to fulfill all the methods that `Proxy`
needs to call.

Of course, in Python we have a delegation mechanism built in, so it
makes the `Proxy` even simpler to implement:

```python
# ProxyDemo2.py
# Simple demonstration of the Proxy pattern.

class Implementation2:
    def f(self):
        print("Implementation.f()")
    def g(self):
        print("Implementation.g()")
    def h(self):
        print("Implementation.h()")

class Proxy2:
    def __init__(self):
        self.__implementation = Implementation2()
    def __getattr__(self, name):
        return getattr(self.__implementation, name)

p = Proxy2()
p.f(); p.g(); p.h();
```

The beauty of using `__getattr__()` is that `Proxy2` is
completely generic, and not tied to any particular implementation (in
Java, a rather complicated "dynamic proxy" has been invented to
accomplish this same thing).

## State

The *State* pattern adds more implementations to *Proxy*, along with a
way to switch from one implementation to another during the lifetime of
the surrogate:

```python
# StateDemo.py
# Simple demonstration of the State pattern.

class State_d:
    def __init__(self, imp):
        self.__implementation = imp
    def changeImp(self, newImp):
        self.__implementation = newImp
    # Delegate calls to the implementation:
    def __getattr__(self, name):
        return getattr(self.__implementation, name)

class Implementation1:
    def f(self):
        print("Fiddle de dum, Fiddle de dee,")
    def g(self):
        print("Eric the half a bee.")
    def h(self):
        print("Ho ho ho, tee hee hee,")

class Implementation2:
    def f(self):
        print("We're Knights of the Round Table.")
    def g(self):
        print("We dance whene'er we're able.")
    def h(self):
        print("We do routines and chorus scenes")

def run(b):
    b.f()
    b.g()
    b.h()
    b.g()

b = State_d(Implementation1())
run(b)
b.changeImp(Implementation2())
run(b)
```

You can see that the first implementation is used for a bit, then the
second implementation is swapped in and that is used.

The difference between *Proxy* and *State* is in the problems that are
solved. The common uses for *Proxy* as described in *Design Patterns*
are:

1.  `Remote proxy`. This proxies for an object in a different address
    space. A remote proxy is created for you automatically by the RMI
    compiler `rmic` as it creates stubs and skeletons.
2.  `Virtual proxy`. This provides "lazy initialization" to create
    expensive objects on demand.
3.  `Protection proxy`. Used when you don't want the client programmer
    to have full access to the proxied object.
4.  `Smart reference`. To add additional actions when the proxied
    object is accessed. For example, or to keep track of the number of
    references that are held for a particular object, in order to
    implement the *copy-on-write* idiom and prevent object aliasing. A
    simpler example is keeping track of the number of calls to a
    particular method.

You could look at a Python reference as a kind of protection proxy,
since it controls access to the actual object on the heap (and ensures,
for example, that you don't use a `null` reference).

In *Design Patterns*, Proxy and State are not presented as related to each other,
because the two are given different structures. That distinction seems arbitrary
to me. State, in particular, uses a separate implementation hierarchy. That
hierarchy is unnecessary unless you have decided the implementation is not under
your control. That can happen. But if you own all the code, there is no reason not
to benefit from the elegance of a single base class. Proxy need not use the same
base class for its implementation either, as long as the proxy controls access to
the object it fronts for. The specifics aside, in both Proxy and State a surrogate
passes method calls through to an implementation object.
