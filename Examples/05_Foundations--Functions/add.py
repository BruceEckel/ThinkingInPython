# add.py
from exceptions import expect

def add(arg1, arg2):
    return arg1 + arg2

print(add(42, 47))
#: 89
print(add("spam ", "eggs"))
#: spam eggs
expect(TypeError, add, 42, "spam")
#: [TypeError]
#: unsupported operand type(s) for +: 'int' and 'str'
