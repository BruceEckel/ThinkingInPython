# tile_enum_demo.py
from tile_enum import Tile

print(Tile.GRASS is Tile["GRASS"] is Tile("."))
#: True
print(Tile.WATER.value, Tile.WATER.walkable)
#: ~ False
print([t.value for t in Tile])
#: ['.', '~', '#']
