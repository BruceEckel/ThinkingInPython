# demo_exceptions.py
from exceptions import expected

with expected(ZeroDivisionError):
    print("before")
    1 / 0
    # Never runs: the error jumps to __exit__
    print("after")
#: before
#: [ZeroDivisionError] division by zero
print("survived")
#: survived

with expected():  # No argument means ALL
    print("before")
    raise KeyError("anything")
#: before
#: [KeyError] 'anything'
print("survived")
#: survived

with expected() as x:
    print(f"{x = }")
#: x = None
