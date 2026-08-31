# add.py

def add(arg1, arg2):
    return arg1 + arg2

print(add(42, 47))
#: 89
print(add("spam ", "eggs"))
#: spam eggs
try:
    add(42, "spam")
except TypeError as e:
    print(e)
#: unsupported operand type(s) for +: 'int' and 'str'
