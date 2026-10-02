# exercise_1.py
from exceptions import expect

class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius cannot be negative")
        self._radius = value

    def shrink(self, factor):
        self.radius = self.radius / factor

c = Circle(10)
c.shrink(2)
print(c.radius)
#: 5.0
expect(ValueError, c.shrink, -2)
#: [ValueError] radius cannot be negative
