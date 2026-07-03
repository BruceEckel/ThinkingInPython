# generics.py

def first[T](items: list[T]) -> T:
    return items[0]

n = first([10, 20, 30])  # Here T is int
print(n + 1)
#: 11
s = first(["a", "b"])    # Here T is str
print(s.upper())
#: A
