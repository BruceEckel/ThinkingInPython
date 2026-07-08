# immutable.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Bob:
    name: str = "Bob"

@dataclass(frozen=True)
class Immutable:
    numbers: tuple[int, ...]
    bob: Bob

if __name__ == "__main__":
    immutable = Immutable((1, 2), Bob())
    print(immutable)
    # immutable.numbers is a tuple, so it has no append.
    # immutable.bob.name = "Ralph" raises FrozenInstanceError.
#: Immutable(numbers=(1, 2), bob=Bob(name='Bob'))
