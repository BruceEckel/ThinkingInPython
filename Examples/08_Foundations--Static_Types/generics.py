# generics.py

def first[T](items: list[T]) -> T:
    return items[0]

n = first([10, 20, 30])  # T is int
print(n + 1)
#: 11
# ty: "int" has no attribute "upper":
# n.upper()
s = first(["a", "b"])  # T is str
print(s.upper())
#: A
