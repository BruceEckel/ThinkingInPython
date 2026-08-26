# immutable_default.py

# An empty tuple is safe: it can't be mutated
def show(items=()):
    for item in items:
        print(item)
    print(f"({len(items)} items)")

show()
#: (0 items)
show(["a", "b"])
#: a
#: b
#: (2 items)
