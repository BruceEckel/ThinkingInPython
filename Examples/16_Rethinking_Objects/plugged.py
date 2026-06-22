# plugged.py
# Plugging the leaks means defensively copying everything a getter
# returns. It works, but every getter has to remember to do it,
# forever.
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
        return self._numbers.copy()  # Hand back a copy, not our list.

    @property
    def bob(self) -> Bob:
        return deepcopy(self._bob)

if __name__ == "__main__":
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates a copy, not ours.
    plugged.bob.name = "Ralph"   # Ditto.
    print(plugged.numbers, plugged.bob)
