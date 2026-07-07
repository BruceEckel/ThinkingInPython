# exercise_3.py
from dataclasses import dataclass

@dataclass
class B:
    x: int = 100  # Constructor default, not class attribute

b = B()
b2 = B()
b.x = -1
print(b.x, b2.x)
#: -1 100
