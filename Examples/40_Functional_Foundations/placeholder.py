# placeholder.py
from functools import Placeholder, partial

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

percent = partial(clamp, 0, Placeholder, 100)  # type: ignore
print(percent(150), percent(-5), percent(42))  # type: ignore
#: 100 0 42
print(percent.args)
#: (0, Placeholder, 100)
