# exercise_3.py
from typing import NamedTuple

class Fraction(NamedTuple):
    numerator: int
    denominator: int

f = Fraction(3, 4)
print(f)
#: Fraction(numerator=3, denominator=4)
print(f[0], f[1])
#: 3 4
num, denom = f
print(num, denom)
#: 3 4
