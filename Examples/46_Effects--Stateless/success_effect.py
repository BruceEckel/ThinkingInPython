# success_effect.py
from collections.abc import Generator
from stateless import success

effect = success(42)
print(effect)
#: SuccessEffect(value=42)
print(isinstance(effect, Generator))
#: True
try:
    next(effect)
except StopIteration as stop:
    print(stop.value)
#: 42
