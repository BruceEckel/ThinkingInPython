# exercise_7.py
from collections.abc import Generator
from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True)
class Coin:
    cents: int

@dataclass(frozen=True)
class Digit:
    value: str

type Event = Coin | Digit

PRICES: Final[dict[str, int]] = {"11": 25, "12": 75}
STOCK: Final[dict[str, int]] = {"11": 0, "12": 3}

def machine() -> Generator[str, Event]:
    stock = dict(STOCK)
    amount = 0
    event: Event = yield "QUIESCENT"
    while True:
        while isinstance(event, Coin):
            amount += event.cents
            event = yield "COLLECTING"
        row = event.value  # Not a Coin, so a first Digit
        second = yield "SELECTING"
        # A coin instead of a digit
        if isinstance(second, Coin):
            amount += second.cents
            event = yield "COLLECTING"
            continue
        code = row + second.value
        if stock.get(code, 0) == 0:
            event = yield "UNAVAILABLE"
        elif amount < PRICES.get(code, 0):
            event = yield "WANT_MORE"
        else:
            amount -= PRICES[code]
            stock[code] -= 1
            event = yield "DISPENSED"

m = machine()
print(next(m))
#: QUIESCENT
for event in [Coin(25), Digit("1"), Digit("1"), Digit("1"),
              Digit("2"), Coin(50), Digit("1"), Digit("2")]:
    print(f"{event} -> {m.send(event)}")
#: Coin(cents=25) -> COLLECTING
#: Digit(value='1') -> SELECTING
#: Digit(value='1') -> UNAVAILABLE
#: Digit(value='1') -> SELECTING
#: Digit(value='2') -> WANT_MORE
#: Coin(cents=50) -> COLLECTING
#: Digit(value='1') -> SELECTING
#: Digit(value='2') -> DISPENSED
