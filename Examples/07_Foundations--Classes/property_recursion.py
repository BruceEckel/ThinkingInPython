# property_recursion.py
from exceptions import expect

class Circle:
    def __init__(self, radius):
        self.radius = radius  # Calls the setter

    @property
    def radius(self):
        return self.radius  # Calls itself again

    @radius.setter
    def radius(self, value):
        self.radius = value  # Calls itself again

expect(RecursionError, Circle, 10)
#: [RecursionError] maximum recursion depth exceeded
