# property_recursion.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # Calls the setter

    @property
    def radius(self):
        return self.radius  # Calls itself again

    @radius.setter
    def radius(self, value):
        self.radius = value  # Calls itself again

try:
    Circle(10)
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
