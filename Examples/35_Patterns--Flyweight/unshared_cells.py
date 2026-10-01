# unshared_cells.py
from record import record

@record
class Cell:
    symbol: str
    name: str
    walkable: bool
    row: int
    col: int

left = Cell(".", "grass", True, 0, 0)
right = Cell(".", "grass", True, 0, 1)
print(left == right)
#: False
