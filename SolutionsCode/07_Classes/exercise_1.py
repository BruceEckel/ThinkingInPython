# exercise_1.py
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
try:
    c.shrink(-2)
except ValueError as e:
    print("caught:", e)
#: caught: radius cannot be negative
