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
    def __init__(self, *, accept_nickels: bool = False) -> None:
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
    print(type(e).__name__, e)
#: NoTransition no transition from <State.COLLECTING: 2> on Nickel

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
