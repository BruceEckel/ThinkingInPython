# DataClassesAsTypes/dataclass_features.py
# A few data class tools worth knowing: asdict, astuple, replace, KW_ONLY.
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
    _: KW_ONLY            # Everything after this must be passed by keyword.
    verbose: bool = False
    retries: int = 3


if __name__ == "__main__":
    p = Point(10, 20)
    print(asdict(p))                  # Nested dict.
    print(astuple(p))                 # Nested tuple.

    line = Line([Point(2, 7), Point(10, 4)])
    print(asdict(line))               # Recurses into the list of Points.

    print(replace(p, x=1))            # Copy with one field changed.

    print(Config("data.csv", retries=5))
