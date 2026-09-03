# first_any.py
from typing import Any

def first_any(items: list) -> Any:
    return items[0]

n = first_any([10, 20, 30])
try:
    n.nonexistent_method()
except AttributeError as e:
    print(e)
#: 'int' object has no attribute 'nonexistent_method'
