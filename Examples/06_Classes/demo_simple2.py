# demo_simple2.py
from simple2 import Different, Simple2

x = Simple2("Simple2 constructor argument")
## Inside Simple2 constructor
## Inside the Simple constructor
x.display()
## Overridden show() method
## Called from display(): Simple2 constructor argument
x.show()
## Overridden show() method
## Simple2 constructor argument
x.show_twice()  # Inherited from Simple
## Overridden show() method
## Simple2 constructor argument
## Overridden show() method
## Simple2 constructor argument
def f(obj): obj.show() # Local/nested function
f(x)
## Overridden show() method
## Simple2 constructor argument
f(Different())
## Not derived from Simple
