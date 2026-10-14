# enum_mixins.py
from enum import Enum, StrEnum

class Direction(tuple, Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def step(self, x: int, y: int) -> tuple[int, int]:
        dx, dy = self
        return x + dx, y + dy

print(Direction.UP.step(3, 3))
#: (3, 4)
print(Direction((0, -1)), Direction.LEFT.value)
#: Direction.DOWN (-1, 0)
print(isinstance(Direction.RIGHT, tuple), len(Direction))
#: True 4

class Level(StrEnum):
    INFO = "info"
    WARNING = "warning"

print(f"{Level.INFO}: ready", Level.WARNING.upper())
#: info: ready WARNING
