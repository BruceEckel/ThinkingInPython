# demo_exceptions.py
from exceptions import ignore

with ignore(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs: the error jumps straight to __exit__
print("survived")
#: before
#: ignoring ZeroDivisionError('division by zero')
#: survived

with ignore():  # No argument means ALL
    print("before")
    raise KeyError("anything")
print("survived")
#: before
#: ignoring KeyError('anything')
#: survived

with ignore() as x:
    print(f"{x = }")
#:
