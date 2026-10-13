# immutable.py
from dataclasses import FrozenInstanceError, dataclass
from exceptions import expect

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
    expect(FrozenInstanceError, setattr,
           immutable.bob, "name", "Ralph")
#: Immutable(numbers=(1, 2), bob=Bob(name='Bob'))
#: [FrozenInstanceError] cannot assign to field 'name'
