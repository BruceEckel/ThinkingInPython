# simple2.py
from typing import override

from simple_class import Simple


class Simple2(Simple):  # Simple2 inherits Simple
    def __init__(self, str):
        print("Inside Simple2 constructor")
        # Call the base-class constructor with super():
        super().__init__(str)
    def display(self):
        self.show_msg("Called from display()")
    @override
    def show(self):
        print("Overridden show() method")
        # Calling the base-class method from inside
        # the overridden method:
        super().show()

class Different:
    def show(self):
        print("Not derived from Simple")

if __name__ == "__main__":
    x = Simple2("Simple2 constructor argument")
    x.display()
    x.show()
    x.show_msg("Inside main")
    def f(obj): obj.show() # One-line definition
    f(x)
    f(Different())
