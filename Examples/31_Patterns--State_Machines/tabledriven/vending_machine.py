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

# tabledriven/vending_machine.py (continued)
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

# tabledriven/vending_machine.py (continued)
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
