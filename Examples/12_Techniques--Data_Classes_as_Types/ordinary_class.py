# ordinary_class.py
from comparison import show
from exceptions import expect

class A:
    x: int
    s: str

show(A())
#: [Attributes]
#:   None
#: [Methods]
#:   None

print(A.__annotations__)
#: {'x': <class 'int'>, 's': <class 'str'>}
expect(AttributeError, getattr, A(), "x")
#: [AttributeError] 'A' object has no attribute 'x'
