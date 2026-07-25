# color_namedtuple.py
from typing import NamedTuple

class Color(NamedTuple):
    r: int
    g: int
    b: int

red = Color(255, 0, 0)
print(red)
#: Color(r=255, g=0, b=0)
print(red.r, red[0])
#: 255 255
print(red._replace(g=128))
#: Color(r=255, g=128, b=0)
print(red._asdict(), Color._fields)
#: {'r': 255, 'g': 0, 'b': 0} ('r', 'g', 'b')
