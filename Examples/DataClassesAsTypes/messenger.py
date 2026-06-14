# DataClassesAsTypes/messenger.py
# A data class generates __init__, __repr__, and __eq__ for you.
from dataclasses import dataclass, replace


@dataclass
class Messenger:
    name: str
    number: int
    depth: float = 0.0  # Default value.


if __name__ == "__main__":
    m = Messenger("foo", 12, 3.14)
    print(m)
    print(m.name, m.number, m.depth)

    print(Messenger("xx", 1) == Messenger("xx", 1))  # __eq__ generated.
    print(Messenger("xx", 1) == Messenger("xx", 2))

    mc = replace(m, depth=9.9)  # Copy with one field changed.
    print(m, mc)

    m.name = "bar"  # A plain data class is mutable.
    print(m)
