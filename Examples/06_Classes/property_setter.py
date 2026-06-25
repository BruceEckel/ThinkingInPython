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

c = Circle(10)
c.radius = 5      # The setter validates, then stores
print(c.radius)
## 5
