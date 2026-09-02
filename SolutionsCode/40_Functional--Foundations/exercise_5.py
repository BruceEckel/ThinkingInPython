# exercise_5.py
import textwrap
from functools import partial

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

at_least_ten = partial(clamp, 10)
print(at_least_ten(3, 100), at_least_ten(50, 100))
#: 10 50
try:
    partial(clamp, high=100)(0, 5)  # type: ignore
except TypeError as e:
    for line in textwrap.wrap(str(e), 57):
        print(line)
#: clamp() got some positional-only arguments passed as
#: keyword arguments: 'high'
