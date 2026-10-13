# shared_mutable.py

class Cart:
    items: list[str] = []  # One list, shared by every Cart

a, b = Cart(), Cart()
a.items.append("apple")  # Mutates, does not assign
print(a.items, b.items)
#: ['apple'] ['apple']
a.items += ["pear"]  # Mutates, then assigns
print(a.items, b.items)
#: ['apple', 'pear'] ['apple', 'pear']
a.items = ["plum"]  # Rebinds a's own attribute
print(a.items, b.items)
#: ['plum'] ['apple', 'pear']
