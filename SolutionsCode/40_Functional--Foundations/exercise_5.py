# exercise_5.py
from functools import partial
from exceptions import expect

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

at_least_ten = partial(clamp, 10)
print(at_least_ten(3, 100), at_least_ten(50, 100))
#: 10 50
expect(TypeError, partial(clamp, high=100), 0, 5)  # type: ignore
#: [TypeError] clamp() got some positional-only arguments
#: passed as keyword arguments: 'high'
