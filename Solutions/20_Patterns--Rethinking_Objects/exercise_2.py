# exercise_2.py
from dataclasses import dataclass
from exceptions import expect

@dataclass
class Bob:
    name: str = "Bob"

@dataclass(frozen=True)
class Immutable:
    numbers: tuple[int, ...]
    bob: Bob

immutable = Immutable((1, 2), Bob())
# No error, from ty or from Python:
immutable.bob.name = "Ralph"
print(immutable)
#: Immutable(numbers=(1, 2), bob=Bob(name='Ralph'))
# The mutable Bob makes the instance unhashable
expect(TypeError, hash, immutable)
#: [TypeError] unhashable type: 'Bob'
