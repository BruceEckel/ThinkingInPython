# slope_catch.py

def validate(run: int) -> int:
    if run < 0:
        raise ValueError(f"run cannot be negative: {run}")
    return run

def slope(rise: int, run: int) -> float:
    try:
        return rise / validate(run)
    except ZeroDivisionError:
        return float("inf")

print(slope(10, 2))
#: 5.0
print(slope(10, 0))
#: inf
try:
    slope(10, -1)
except ValueError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: ValueError: run cannot be negative: -1
