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

try:
    setattr(m, "name", "bar")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: FrozenInstanceError: cannot assign to field 'name'

cache = {m: "Ni!"}  # Frozen instances are hashable
print(cache[m])
#: Ni!
