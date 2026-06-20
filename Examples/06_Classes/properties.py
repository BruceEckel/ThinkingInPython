# properties.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # A plain attribute

    @property
    def area(self):           # Used like an attribute, not a call
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.radius)  # 10
print(c.area)    # 314.159: Properties don't use parentheses
