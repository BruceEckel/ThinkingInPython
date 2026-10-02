# exercise_8.py
from exceptions import expect

count = 0

def writes_global():
    count += 1  # type: ignore  # noqa: F823, F841

def rebinds():
    print(count)  # type: ignore  # noqa: F823
    count = 99
    print(count)

expect(UnboundLocalError, writes_global)
#: [UnboundLocalError] cannot access local variable 'count'
#: where it is not associated with a value
expect(UnboundLocalError, rebinds)
#: [UnboundLocalError] cannot access local variable 'count'
#: where it is not associated with a value
