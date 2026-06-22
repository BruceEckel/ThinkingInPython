# frozen_messenger.py
# frozen=True makes instances immutable and hashable.
from dataclasses import dataclass

@dataclass(frozen=True)
class Messenger:
    name: str
    number: int
    depth: float = 0.0

if __name__ == "__main__":
    m = Messenger("foo", 12, 3.14)
    print(m)

    # m.name = "bar" would raise dataclasses.FrozenInstanceError

    cache = {m: "value"}  # Frozen instances are hashable
    print(cache[m])
