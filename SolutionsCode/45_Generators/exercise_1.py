# exercise_1.py
from collections.abc import Generator
from typing import NewType

Prompt = NewType("Prompt", str)
Amount = NewType("Amount", int)
Total = NewType("Total", int)

def tally() -> Generator[Prompt, Amount, Total]:
    total = 0
    for n in (1, 2, 3):
        amount = yield Prompt(f"amount {n} of 3")
        total += amount
    return Total(total)

t = tally()
print(next(t))
#: amount 1 of 3
print(t.send(Amount(10)))
#: amount 2 of 3
print(t.send(Amount(20)))
#: amount 3 of 3
try:
    t.send(Amount(12))
except StopIteration as stop:
    total: Total = stop.value
print(total)
#: 42
