# exercise_5.py
from dataclasses import dataclass, field

@dataclass
class Cart:
    items: list[str] = field(default_factory=list)

a, b = Cart(), Cart()
a.items.append("apple")
print(a.items, b.items)
#: ['apple'] []
