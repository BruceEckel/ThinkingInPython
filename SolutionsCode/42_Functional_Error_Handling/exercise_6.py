# exercise_6.py
def func_a(i: int) -> int | None:
    if i == 1:
        return None
    return i

def func_b(i: int) -> int | None:
    if i == 2:
        return None
    return i

def func_c(i: int) -> int | None:
    try:
        1 / (i - 3)
    except ZeroDivisionError:
        return None
    return i

def composed(i: int) -> int | None:
    a = func_a(i)
    if a is None:
        return None
    b = func_b(a)
    if b is None:
        return None
    return func_c(b)

for i in range(5):
    print(i, composed(i))
#: 0 0
#: 1 None
#: 2 None
#: 3 None
#: 4 4
