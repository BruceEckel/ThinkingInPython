# hashable.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
## 5.0
# A list has no stable hash, so it cannot be a key:
try:
    hash([3, 4])
except TypeError as e:
    print(e)
## unhashable type: 'list'
