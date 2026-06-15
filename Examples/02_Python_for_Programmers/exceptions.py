# exceptions.py

def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(parse_int("42"))    # 42
print(parse_int("oops"))  # None

def checked_divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b

try:
    checked_divide(1, 0)
except ValueError as e:
    print("caught:", e)
finally:
    print("finally always runs")
