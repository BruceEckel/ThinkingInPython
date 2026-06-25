# simple2.py
from typing import override
from simple_class import Simple

class Simple2(Simple):  # Simple2 inherits Simple
    def __init__(self, str):
        print("Inside Simple2 constructor")
        # Call the base-class constructor with super():
        super().__init__(str)
    def display(self):
        self.show("Called from display()")
    @override
    def show(self, msg=""):
        print("Overridden show() method")
        # Call the base-class method from inside
        # the overridden method:
        super().show(msg)

class Different:
    def show(self):
        print("Not derived from Simple")
