# asdict_astuple.py
from dataclasses import asdict, astuple, dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(10, 20)
print(asdict(p))
#: {'x': 10, 'y': 20}
print(astuple(p))
#: (10, 20)

@dataclass(frozen=True)
class Line:
    points: list[Point]

line = Line([Point(2, 7), Point(10, 4)])
print(asdict(line))  # Recurses into the list of Points
#: {'points': [{'x': 2, 'y': 7}, {'x': 10, 'y': 4}]}
