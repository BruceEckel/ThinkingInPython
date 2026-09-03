# composing_exceptions.py

def func_a(i: int) -> int:
    if i == 1:
        raise ValueError(f"func_a({i})")
    return i

def func_b(i: int) -> int:
    if i == 2:
        raise ValueError(f"func_b({i})")
    return i

def func_c(i: int) -> int:
    _ = 1 / (i - 3)  # raises when i == 3
    return i

def composed(i: int) -> int:
    return func_c(func_b(func_a(i)))

if __name__ == "__main__":
    for i in range(5):
        try:
            print(i, composed(i))
        except (ValueError, ZeroDivisionError) as e:
            print(i, f"failed: {e}")
#: 0 0
#: 1 failed: func_a(1)
#: 2 failed: func_b(2)
#: 3 failed: division by zero
#: 4 4
