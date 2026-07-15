# demo_messenger.py
from dataclasses import replace
from messenger import Messenger

m = Messenger("foo", 12, 3.14)
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(m.name, m.number, m.depth)
#: foo 12 3.14

# The generated __eq__ compares by field value:
print(Messenger("xx", 1) == Messenger("xx", 1))
#: True
print(Messenger("xx", 1) == Messenger("xx", 2))
#: False

mc = replace(m, depth=9.9)  # Copy with one field changed
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(mc)
#: Messenger(name='foo', number=12, depth=9.9)

m.name = "bar"  # Data classes are mutable by default
print(m)
#: Messenger(name='bar', number=12, depth=3.14)
