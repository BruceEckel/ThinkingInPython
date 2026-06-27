# messenger.py
from dataclasses import dataclass, replace

@dataclass
class Messenger:
    name: str
    number: int
    depth: float = 0.0  # Default value

m = Messenger("foo", 12, 3.14)
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(m.name, m.number, m.depth)
#: foo 12 3.14

# __eq__ is generated, so equal fields compare equal:
print(Messenger("xx", 1) == Messenger("xx", 1))
#: True
print(Messenger("xx", 1) == Messenger("xx", 2))
#: False

mc = replace(m, depth=9.9)  # Copy with one field changed
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(mc)
#: Messenger(name='foo', number=12, depth=9.9)

m.name = "bar"  # A plain data class is mutable
print(m)
#: Messenger(name='bar', number=12, depth=3.14)
