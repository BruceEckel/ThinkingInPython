# frozen_messenger.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Messenger:
    name: str
    number: int
    depth: float = 0.0

m = Messenger("foo", 12, 3.14)
print(m)
#: Messenger(name='foo', number=12, depth=3.14)

# m.name = "bar" raises dataclasses.FrozenInstanceError

cache = {m: "value"}  # Frozen instances are hashable
print(cache[m])
#: value
