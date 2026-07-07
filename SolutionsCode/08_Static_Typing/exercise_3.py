# exercise_3.py
def first[T](items: list[T]) -> T:
    return items[0]

def last[T](items: list[T]) -> T:
    return items[-1]

print(last([10, 20, 30]))
#: 30
print(last(["a", "b", "c"]))
#: c
