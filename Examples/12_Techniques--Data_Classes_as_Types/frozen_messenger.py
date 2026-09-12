# frozen_messenger.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(frozen=True)
class Messenger:
    name: str
    number: int
    depth: float = 0.0

m = Messenger("iris", 12, 3.14)
print(m)
#: Messenger(name='iris', number=12, depth=3.14)

expect(Exception, setattr, m, "name", "hermes")
#: [FrozenInstanceError] cannot assign to field 'name'

cache = {m: "Ni!"}  # Frozen instances are hashable
print(cache[m])
#: Ni!
