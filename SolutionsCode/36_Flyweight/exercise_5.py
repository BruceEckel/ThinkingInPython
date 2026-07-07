# exercise_5.py
from dataclasses import dataclass
from weakref import WeakValueDictionary

type RGB = tuple[int, int, int]

@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int

_pool: WeakValueDictionary[RGB, Color] = WeakValueDictionary()

def make_color(red: int, green: int, blue: int) -> Color:
    key = (red, green, blue)
    found = _pool.get(key)
    if found is None:
        found = Color(red, green, blue)
        _pool[key] = found
    return found

palette = [make_color(r, 0, 0) for r in range(50)]
print(len(_pool))
#: 50
crimson_a = make_color(220, 20, 60)
crimson_b = make_color(220, 20, 60)
print(crimson_a is crimson_b)
#: True
del palette, crimson_a, crimson_b
print(len(_pool))
#: 0
