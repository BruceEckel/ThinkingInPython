# dataclass_features.py
from dataclasses import KW_ONLY, asdict, astuple, dataclass, replace

@dataclass(frozen=True)
class Point:
    x: int
    y: int

@dataclass(frozen=True)
class Line:
    points: list[Point]

@dataclass
class Config:
    source: str
    # Everything after this must be passed by keyword:
    _: KW_ONLY
    verbose: bool = False
    retries: int = 3

p = Point(10, 20)
print(asdict(p))   # Nested dict
## {'x': 10, 'y': 20}
print(astuple(p))  # Nested tuple
## (10, 20)
line = Line([Point(2, 7), Point(10, 4)])
print(asdict(line))  # Recurses into the list of Points
## {'points': [{'x': 2, 'y': 7}, {'x': 10, 'y': 4}]}
print(replace(p, x=1))  # Copy with one field changed
## Point(x=1, y=20)
print(Config("data.csv", retries=5))
## Config(source='data.csv', verbose=False, retries=5)
