# frozen_leaky.py
from dataclasses import FrozenInstanceError, dataclass

@dataclass(frozen=True)
class FrozenLeaky:
    numbers: list[int]  # A mutable field in a frozen class

fl = FrozenLeaky([1, 2])
fl.numbers.append(999)  # frozen=True does not stop this
print(fl.numbers)
#: [1, 2, 999]
try:
    fl.numbers = []  # type: ignore
except FrozenInstanceError as e:
    print(type(e).__name__)
#: FrozenInstanceError
