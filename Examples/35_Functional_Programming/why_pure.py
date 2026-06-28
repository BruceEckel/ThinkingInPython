# why_pure.py
def slope(rise: int, run: int) -> float:
    return rise / run

# No setup or teardown: assert the result directly:
assert slope(10, 2) == 5.0
assert slope(9, 3) == 3.0
print("ok")
#: ok
