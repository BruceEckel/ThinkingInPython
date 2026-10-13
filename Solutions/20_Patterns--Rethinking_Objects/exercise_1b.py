# exercise_1b.py
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Plugged:
    def __init__(
        self, numbers: list[int], tags: list[str]
    ) -> None:
        self._numbers = numbers
        self._bob = Bob()
        self._tags = tags

    @property
    def numbers(self) -> list[int]:
        return self._numbers.copy()

    @property
    def bob(self) -> Bob:
        return deepcopy(self._bob)

    @property
    def tags(self) -> list[str]:
        return self._tags.copy()

plugged = Plugged([1, 2], ["a", "b"])
plugged.tags.append("z")
print(plugged.tags)
#: ['a', 'b']
