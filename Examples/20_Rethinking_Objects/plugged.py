# plugged.py
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Plugged:
    def __init__(self, numbers: list[int]) -> None:
        self._numbers = numbers
        self._bob = Bob()

    @property
    def numbers(self) -> list[int]:
        return self._numbers.copy()  # Isolate by returning a copy

    @property
    def bob(self) -> Bob:
        return deepcopy(self._bob)

if __name__ == "__main__":
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates the copy
    plugged.bob.name = "Ralph"  # Ditto
    print(plugged.numbers, plugged.bob)
#: [1, 2] Bob(name='Bob')
