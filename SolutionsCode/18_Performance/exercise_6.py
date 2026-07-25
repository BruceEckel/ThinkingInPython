# exercise_6.py

class Point:
    __slots__ = ("x", "y")
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Point3D(Point):  # Declares no __slots__ of its own
    pass

p = Point3D(1, 2)
p.z = 3  # type: ignore
print(vars(p))
#: {'z': 3}
print(hasattr(Point(1, 2), "__dict__"))
#: False
print(Point3D.__slots__)
#: ('x', 'y')
