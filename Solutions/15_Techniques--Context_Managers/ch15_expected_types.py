# ch15_expected_types.py
from exceptions import expected

with expected((ZeroDivisionError, TypeError)):
    print("before")
    raise TypeError("not a number")
print("survived")
#: before
#: [TypeError] not a number
#: survived

with expected((ZeroDivisionError, TypeError)):
    print("before")
    1 / 0
print("survived")
#: before
#: [ZeroDivisionError] division by zero
#: survived
