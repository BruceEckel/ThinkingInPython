# type_aliases.py
type Coord = tuple[int, int]
type Grid = dict[Coord, str]

def paint(grid: Grid, cell: Coord, color: str) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "red")
print(grid)
#: {(2, 3): 'red'}
