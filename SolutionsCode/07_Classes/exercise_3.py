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

class Simple2(Simple):
    @override
    def show(self, msg=""):
        print("Overridden show() method")
        super().show(msg)

class Simple3(Simple2):
    @override
    def show(self, msg=""):
        print("Simple3 show() method")
        super().show(msg)

Simple3("x").show_twice()
#: Simple3 show() method
#: Overridden show() method
#: x
#: Simple3 show() method
#: Overridden show() method
#: x
