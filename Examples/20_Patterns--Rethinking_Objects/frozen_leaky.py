# frozen_leaky.py
from dataclasses import FrozenInstanceError, dataclass
from exceptions import expect, ignore

@dataclass(frozen=True)
class FrozenLeaky:
    numbers: list[int]  # A mutable field in a frozen class

fl = FrozenLeaky([1, 2])
fl.numbers.append(999)  # frozen=True does not stop this
print(fl.numbers)
#: [1, 2, 999]
with ignore(FrozenInstanceError):
    fl.numbers = []  # type: ignore
#: FrozenInstanceError("cannot assign to field 'numbers'")
# A list field makes the whole instance unhashable
expect(TypeError, hash, fl)
#: [TypeError] unhashable type: 'list'
