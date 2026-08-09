# why_pure.py
def slope(rise: int, run: int) -> float:
    return rise / run

total = 0
def running_total(n: int) -> int:
    global total
    total += n
    return total

# The pure function needs no setup and no teardown:
assert slope(10, 2) == 5.0
assert slope(10, 2) == 5.0
# The impure one needs a reset before each check:
total = 0
assert running_total(5) == 5
total = 0
assert running_total(5) == 5
print("ok")
#: ok
