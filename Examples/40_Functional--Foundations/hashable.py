# hashable.py
from dataclasses import dataclass
from exceptions import ignore

@dataclass(frozen=True)
class Point:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# A list has no stable hash, so it cannot be a key:
with ignore(TypeError):
    hash([3, 4])
#: TypeError("unhashable type: 'list'")
