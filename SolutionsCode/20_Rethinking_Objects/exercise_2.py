# exercise_2.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Immutable:
    numbers: list[int]

data = Immutable([1, 2])
data.numbers.append(999)  # No error, from ty or from Python
print(data)
#: Immutable(numbers=[1, 2, 999])
try:
    data.numbers = [3]  # type: ignore
except Exception as e:
    print(e)
#: cannot assign to field 'numbers'
try:
    # The list field makes the instance unhashable
    hash(data)
except TypeError as e:
    print(e)
#: unhashable type: 'list'
