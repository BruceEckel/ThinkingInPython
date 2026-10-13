# any_show.py
from simple_subclass import Derived

class Different:
    def show(self):
        print("Not derived from Simple")

def f(obj):  # Works on any obj with a show()
    obj.show()

f(Derived("Derived constructor argument"))
#: Inside Derived constructor
#: Inside the Simple constructor
#: Overridden show() method
#: Derived constructor argument
f(Different())
#: Not derived from Simple
