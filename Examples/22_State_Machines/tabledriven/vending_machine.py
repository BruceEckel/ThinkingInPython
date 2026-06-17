# tabledriven/vending_machine.py
# A vending machine expressed entirely as a transition table.
from enum import Enum, auto

from state_machine import StateMachine, Table


class State(Enum):
    QUIESCENT = auto()
    COLLECTING = auto()
    SELECTING = auto()
    UNAVAILABLE = auto()
    WANT_MORE = auto()


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


class FirstDigit(Digit):
    pass
class SecondDigit(Digit):
    pass


class ItemSlot:
    def __init__(self, price: int, quantity: int) -> None:
        self.price = price
        self.quantity = quantity


class VendingMachine(StateMachine):
    def __init__(self) -> None:
        self.amount = 0    # money inserted, in cents
        self.row = 0       # the first selection digit
        self.message = ""  # last action, for a view to display
        # A 4x4 grid of items; column c costs (c + 1) * 25 cents:
        self.items = [[ItemSlot((c + 1) * 25, 5) for c in range(4)]
                      for _ in range(4)]
        self.items[3][0] = ItemSlot(25, 0)  # one sold-out slot
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
                (self.too_expensive, self.clear, State.COLLECTING),
                (self.sold_out, self.clear, State.UNAVAILABLE),
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

    # Actions record a message instead of printing, so the model never
    # touches the screen; a view reads vm.message and displays it.
    def add_money(self, money: Money) -> None:
        self.amount += money.value
        self.message = f"Total = {self.amount}"

    def choose_row(self, digit: FirstDigit) -> None:
        self.row = digit.value
        self.message = f"Row {digit}"

    def clear(self, col: SecondDigit) -> None:
        slot = self._slot(col)
        self.message = (f"Clearing selection: costs {slot.price}, "
                        f"quantity {slot.quantity}")

    def dispense(self, col: SecondDigit) -> None:
        slot = self._slot(col)
        slot.quantity -= 1
        self.amount -= slot.price
        self.message = f"Dispensing; amount remaining {self.amount}"

    def refund(self, event: object) -> None:
        self.message = f"Returning {self.amount}"
        self.amount = 0


if __name__ == "__main__":
    events = [
        Money("quarter", 25), Money("quarter", 25),
        Money("dollar", 100),
        FirstDigit("A", 0), SecondDigit("two", 1),    # buy [0][1]
        FirstDigit("A", 0), SecondDigit("two", 1),    # buy it again
        FirstDigit("C", 2), SecondDigit("three", 2),  # too expensive
        FirstDigit("D", 3), SecondDigit("one", 0),    # sold out
        Quit(),  # refund and reset
    ]
    machine = VendingMachine()
    for event in events:
        machine.handle(event)
        print(f"{event}: {machine.message}")  # a plain text view
