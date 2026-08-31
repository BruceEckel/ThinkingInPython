# ordinary_class.py
from comparison import show

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
