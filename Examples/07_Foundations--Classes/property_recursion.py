# property_recursion.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # calls the setter

    @property
    def radius(self):
        return self.radius  # calls itself again

    @radius.setter
    def radius(self, value):
        self.radius = value  # calls itself again

try:
    Circle(10)
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
