# exercise_8.py
count = 0

def writes_global():
    count += 1  # type: ignore  # noqa: F823, F841

def rebinds():
    print(count)  # type: ignore  # noqa: F823
    count = 99
    print(count)

try:
    writes_global()
except UnboundLocalError as e:
    print(str(e).partition(" where")[0])
#: cannot access local variable 'count'
try:
    rebinds()
except UnboundLocalError as e:
    print(str(e).partition(" where")[0])
#: cannot access local variable 'count'
