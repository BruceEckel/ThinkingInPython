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
        self.amount = 0  # money inserted, in cents
        self.row = 0     # the first selection digit
        # A 4x4 grid of items; column c costs (c + 1) * 25 cents:
        self.items = [[ItemSlot((c + 1) * 25, 5) for c in range(4)]
                      for _ in range(4)]
        self.items[3][0] = ItemSlot(25, 0)  # one sold-out slot
        table: Table = {
            ("quiescent", Money):
                [(None, self.add_money, "collecting")],
            ("collecting", Money):
                [(None, self.add_money, "collecting")],
            ("collecting", Quit): [(None, self.refund, "quiescent")],
            ("collecting", FirstDigit):
                [(None, self.choose_row, "selecting")],
            ("selecting", Quit): [(None, self.refund, "quiescent")],
            ("selecting", SecondDigit): [
                (self.too_expensive, self.clear, "collecting"),
                (self.sold_out, self.clear, "unavailable"),
                (None, self.dispense, "want_more"),
            ],
            ("unavailable", Quit): [(None, self.refund, "quiescent")],
            ("unavailable", FirstDigit):
                [(None, self.choose_row, "selecting")],
            ("want_more", Quit): [(None, self.refund, "quiescent")],
            ("want_more", FirstDigit):
                [(None, self.choose_row, "selecting")],
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
