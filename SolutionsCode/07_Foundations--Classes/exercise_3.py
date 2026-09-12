# exercise_3.py
from typing import override

class Simple:
    def __init__(self, text):
        self.s = text

    def show(self, msg=""):
        if msg:
            print(msg + ":", self.s)
        else:
            print(self.s)

    def show_twice(self):
        self.show()
        self.show()

class Derived(Simple):
    @override
    def show(self, msg=""):
        print("Overridden show() method")
        super().show(msg)

class MoreDerived(Derived):
    @override
    def show(self, msg=""):
        print("MoreDerived show() method")
        super().show(msg)

MoreDerived("x").show_twice()
#: MoreDerived show() method
#: Overridden show() method
#: x
#: MoreDerived show() method
#: Overridden show() method
#: x
