# property_setter.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # Goes through the setter below

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius cannot be negative")
        self._radius = value

    @property
    def area(self):  # Unchanged from the version above
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.radius)  # The same two lines as before
#: 10
print(c.area)
#: 314.159
c.radius = 5  # Now the setter validates, then stores
print(c.radius)
#: 5
try:
    Circle(-1)
except ValueError as e:
    print(f"Failed: {e}")
#: Failed: radius cannot be negative
