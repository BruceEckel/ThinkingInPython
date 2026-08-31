# exercise_8.py
def inner() -> int:
    return sum(i * i for i in range(100_000))

def outer() -> int:
    return inner() + inner()

print(outer() > 0)
#: True
