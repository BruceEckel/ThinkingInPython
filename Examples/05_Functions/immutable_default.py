# immutable_default.py

def show(items=()):  # An empty tuple is safe: it can't be mutated
    for item in items:
        print(item)
    print(f"({len(items)} items)")

show()
#: (0 items)
show(["a", "b"])
#: a
#: b
#: (2 items)
