# demo_messenger.py
from dataclasses import replace
from messenger import Messenger

m = Messenger("iris", 12, 3.14)
print(m)
#: Messenger(name='iris', number=12, depth=3.14)
print(m.name, m.number, m.depth)
#: iris 12 3.14

# The generated __eq__ compares by field value:
print(Messenger("iris", 1) == Messenger("iris", 1))
#: True
print(Messenger("iris", 1) == Messenger("iris", 2))
#: False

mc = replace(m, depth=9.9)  # Copy with one field changed
print(m)
#: Messenger(name='iris', number=12, depth=3.14)
print(mc)
#: Messenger(name='iris', number=12, depth=9.9)

m.name = "hermes"  # Data classes are mutable by default
print(m)
#: Messenger(name='hermes', number=12, depth=3.14)
