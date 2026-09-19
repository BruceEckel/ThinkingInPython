# exercise_6.py
from enum import StrEnum
from typing import Final

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

type Coord = tuple[int, int]
type Row = list[int]

MOD: Final[int] = len(Color)

def cross(cell: Coord, size: int) -> list[Coord]:
    x, y = cell
    around = [(x, y), (x - 1, y), (x + 1, y),
              (x, y - 1), (x, y + 1)]
    return [(a, b) for a, b in around
            if 0 <= a < size and 0 <= b < size]

def system(size: int, target: int) -> list[Row]:
    "One row per cell, with the target in the last column."
    cells = [(x, y) for x in range(size)
             for y in range(size)]
    at = {cell: i for i, cell in enumerate(cells)}
    rows = [[0] * (len(cells) + 1) for _ in cells]
    for cell in cells:
        for other in cross(cell, size):
            rows[at[other]][at[cell]] = 1
    for i, (x, y) in enumerate(cells):
        rows[i][-1] = (target - (x + y)) % MOD
    return rows

def solvable(rows: list[Row]) -> bool:
    width = len(rows[0]) - 1
    pivot = 0
    for col in range(width):
        found = next((r for r in range(pivot, len(rows))
                      if rows[r][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = pow(rows[pivot][col], -1, MOD)
        rows[pivot] = [v * scale % MOD for v in rows[pivot]]
        for r, row in enumerate(rows):
            if r != pivot and row[col]:
                factor = row[col]
                rows[r] = [(a - factor * b) % MOD for a, b
                           in zip(row, rows[pivot])]
        pivot += 1
    # A row of zeros with a nonzero target is 0 == 1
    return all(any(row[:-1]) or row[-1] == 0
               for row in rows)

def reachable(size: int) -> list[Color]:
    return [color for target, color in enumerate(Color)
            if solvable(system(size, target))]

for size in range(3, 9):
    names = ", ".join(reachable(size))
    print(f"{size}x{size}: {names or 'nothing'}")
#: 3x3: skyblue, palegreen, khaki
#: 4x4: skyblue, palegreen, khaki
#: 5x5: nothing
#: 6x6: skyblue, palegreen, khaki
#: 7x7: skyblue, palegreen, khaki
#: 8x8: palegreen
