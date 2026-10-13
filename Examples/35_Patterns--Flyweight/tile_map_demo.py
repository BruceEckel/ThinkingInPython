# tile_map_demo.py
from tile_map import parse_map

field = parse_map("""
    ..~~..
    ..~~.#
    ......
    ##..~~
""")
cells = [*row for row in field]
print(len(cells), len({id(t) for t in cells}))
#: 24 3
print(field[0][2] is field[3][5])
#: True
print(field[0][2].label(0, 2))
#: water at (0, 2)
print(field[3][5].label(3, 5))
#: water at (3, 5)
