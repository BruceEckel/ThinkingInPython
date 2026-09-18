# exercise_2.py
from dataclasses import FrozenInstanceError, dataclass
from exceptions import expect, expected

@dataclass(frozen=True)
class Immutable:
    numbers: list[int]

data = Immutable([1, 2])
data.numbers.append(999)  # No error, from ty or from Python
print(data)
#: Immutable(numbers=[1, 2, 999])
with expected(FrozenInstanceError):
    data.numbers = [3]  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'numbers'
# The list field makes the instance unhashable
expect(TypeError, hash, data)
#: [TypeError] unhashable type: 'list'
