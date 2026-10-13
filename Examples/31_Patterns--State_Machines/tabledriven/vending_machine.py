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
class Key:
    value: int

class Row(Key):
    def __str__(self) -> str:
        return "ABCD"[self.value]

class Column(Key):
    def __str__(self) -> str:
        return f"col {self.value}"

@dataclass
class ItemSlot:
    price: int
    quantity: int

class VendingMachine(StateMachine):
    def __init__(self) -> None:
        self.amount = 0  # Money inserted, in cents
        self.row = 0  # The selected row
        # Last action, for the caller to show
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
            (State.COLLECTING, Row):
                [(None, self.choose_row, State.SELECTING)],
            (State.SELECTING, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.SELECTING, Column): [
                (self.too_expensive, self.clear,
                 State.COLLECTING),
                (self.sold_out, self.clear,
                 State.UNAVAILABLE),
                (None, self.dispense, State.WANT_MORE),
            ],
            (State.UNAVAILABLE, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.UNAVAILABLE, Row):
                [(None, self.choose_row, State.SELECTING)],
            (State.WANT_MORE, Quit):
                [(None, self.refund, State.QUIESCENT)],
            (State.WANT_MORE, Row):
                [(None, self.choose_row, State.SELECTING)],
        }
        super().__init__(State.QUIESCENT, table)

    def _slot(self, col: Column) -> ItemSlot:
        return self.items[self.row][col.value]

    # Conditions:
    def too_expensive(self, col: Column) -> bool:
        return self._slot(col).price > self.amount

    def sold_out(self, col: Column) -> bool:
        return self._slot(col).quantity == 0

    def add_money(self, money: Money) -> None:
        self.amount += money.value
        self.message = f"Total = {self.amount}"

    def choose_row(self, row: Row) -> None:
        self.row = row.value
        prices = [slot.price
                  for slot in self.items[self.row]]
        self.message = (f"Row {row}: {min(prices)}c "
                        f"to {max(prices)}c")

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
