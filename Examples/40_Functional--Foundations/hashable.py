# hashable.py
from dataclasses import dataclass
from exceptions import expected
from record import record

@record
class Point:
    x: int
    y: int

@dataclass
class MutablePoint:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# The unfrozen twin has no hash, so it cannot be a key:
with expected(TypeError):
    hash(MutablePoint(3, 4))
#: [TypeError] unhashable type: 'MutablePoint'
