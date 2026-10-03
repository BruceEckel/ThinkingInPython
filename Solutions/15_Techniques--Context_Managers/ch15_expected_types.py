# ch15_expected_types.py
from exceptions import expected

with expected((ZeroDivisionError, TypeError)):
    print("before")
    raise TypeError("not a number")
#: before
#: [TypeError] not a number
print("survived")
#: survived

with expected((ZeroDivisionError, TypeError)):
    print("before")
    1 / 0
#: before
#: [ZeroDivisionError] division by zero
print("survived")
#: survived
