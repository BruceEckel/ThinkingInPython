# representation_str.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # print() prefers __str__
#: (3, 4)
print(repr(p))
#: Point(3, 4)
print([p])
#: [Point(3, 4)]
