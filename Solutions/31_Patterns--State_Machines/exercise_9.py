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
#: [NoTransition] no rule from <State.COLLECTING: 2> on
#: Nickel

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
