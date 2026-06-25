# leaky.py
# Encapsulation with private fields and getters still leaks. A
# getter that returns a mutable object hands the caller a reference
# to the real internals.
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Leaky:
    def __init__(self, numbers: list[int]) -> None:
        self._numbers = numbers  # "Private" by convention
        self._bob = Bob()

    @property
    def numbers(self) -> list[int]:
        return self._numbers

    @property
    def bob(self) -> Bob:
        return self._bob

if __name__ == "__main__":
    leaky = Leaky([1, 2])
    # Both mutate the "private" internals through the getters:
    leaky.numbers.append(999)
    leaky.bob.name = "Ralph"
    print(leaky.numbers, leaky.bob)
## [1, 2, 999] Bob(name='Ralph')
