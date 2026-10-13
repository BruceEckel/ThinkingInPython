# slope_nonzero.py
from exceptions import expected
from nonzero import NonZero, slope

print(slope(10, NonZero(2)))
#: 5.0
with expected(ValueError):
    NonZero(0)
#: [ValueError] NonZero cannot hold 0
