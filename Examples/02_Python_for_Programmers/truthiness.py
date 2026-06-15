# truthiness.py

for value in [0, 1, "", "hi", [], [1], None]:
    print(repr(value), "->", bool(value))

items = []
if not items:
    print("empty")        # an empty list is falsy

name = "" or "default"    # 'or' returns the first truthy operand
print(name)               # default
