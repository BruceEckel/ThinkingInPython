# demo_subclass.py
from simple_subclass import Derived

x = Derived("Derived constructor argument")
#: Inside Derived constructor
#: Inside the Simple constructor
x.display()
#: Overridden show() method
#: Called from display(): Derived constructor argument
x.show_twice()  # Inherited from Simple
#: Overridden show() method
#: Derived constructor argument
#: Overridden show() method
#: Derived constructor argument
