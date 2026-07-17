# representation.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # Falls back to __repr__
#: Point(3, 4)
print([p, p])
#: [Point(3, 4), Point(3, 4)]
