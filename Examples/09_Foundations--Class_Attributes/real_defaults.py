# real_defaults.py
from dataclasses import dataclass

class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # An instance attribute, one per object

@dataclass
class B:
    x: int = 100  # Becomes a constructor default

print(vars(A()), A(7).x)  # Each instance holds x
#: {'x': 100} 7
print(B().x, B(7).x)
#: 100 7
print(vars(B)["x"], vars(B())["x"])
#: 100 100
